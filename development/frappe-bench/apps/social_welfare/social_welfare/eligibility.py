"""Deterministic, explainable screening of household and citizen beneficiaries."""

import json
from contextlib import contextmanager

import frappe
from frappe.utils import getdate, now_datetime, nowdate

from social_welfare.permissions import OFFICER, is_admin
from social_welfare.verification import negative_target_group_verified
from social_welfare.social_welfare.doctype.household_classification.household_classification import (
	get_effective_classification,
)


@contextmanager
def bulk_action(value):
	previous = frappe.flags.social_welfare_bulk_action
	frappe.flags.social_welfare_bulk_action = value
	try:
		yield
	finally:
		frappe.flags.social_welfare_bulk_action = previous


def require_officer():
	if not is_admin() and OFFICER not in frappe.get_roles():
		frappe.throw("Chỉ cán bộ an sinh được rà soát và lập đợt trình.", frappe.PermissionError)


def active_groups(beneficiary_type, name, cutoff):
	field = "citizen" if beneficiary_type == "Citizen" else "household"
	assignments = frappe.get_all(
		"Target Group Assignment",
		filters={field: name, "status": "ACTIVE", "valid_from": ["<=", cutoff], "valid_to": [">=", cutoff]},
		pluck="target_group",
	)
	return sorted(set(assignments))


def has_prior_disbursement(program, beneficiary_type, name):
	field = "citizen" if beneficiary_type == "Citizen" else "household"
	return bool(frappe.db.sql(
		f"SELECT d.name FROM `tabDisbursement` d JOIN `tabApproval Batch` b ON b.name=d.approval_batch "
		f"WHERE b.support_program=%s AND d.beneficiary_type=%s AND d.`{field}`=%s "
		"AND d.status IN ('PENDING','PAID') LIMIT 1",
		(program, beneficiary_type, name),
	))


def candidate_snapshot(beneficiary_type, name, cutoff):
	if beneficiary_type == "Citizen":
		citizen = frappe.db.get_value("Citizen", name, ["full_name", "household"], as_dict=True)
		household_name = citizen.household
		label = citizen.full_name
	else:
		household_name = name
		label = frappe.db.get_value("Household", name, "head_name")
	household = frappe.db.get_value("Household", household_name, ["residential_group", "address"], as_dict=True)
	classification = get_effective_classification(household_name, cutoff)
	return {
		"name": name,
		"label": label,
		"household": household_name,
		"classification": classification.classification if classification else None,
		"classification_record": classification.name if classification else None,
		"target_groups": active_groups(beneficiary_type, name, cutoff),
		"residential_group": household.residential_group if household else None,
		"address": household.address if household else None,
	}


def evaluate(actual, operator, expected, missing_behavior="NEED_VERIFICATION"):
	if actual is None or actual == "" or actual == []:
		if operator == "NOT_EXISTS":
			return "PASS"
		return "UNKNOWN" if missing_behavior == "NEED_VERIFICATION" else "FAIL"
	values = actual if isinstance(actual, list) else [actual]
	expected_values = [part.strip() for part in (expected or "").split(",") if part.strip()]
	if operator == "EXISTS":
		passed = bool(values)
	elif operator == "NOT_EXISTS":
		passed = not bool(values)
	elif operator == "EQ":
		passed = expected in values
	elif operator == "IN":
		passed = bool(set(str(value) for value in values) & set(expected_values))
	else:
		frappe.throw("Phép kiểm tra chính sách không hỗ trợ: " + str(operator))
	return "PASS" if passed else "FAIL"


def evaluate_candidate(program, rules, beneficiary_type, name, cutoff):
	snapshot = candidate_snapshot(beneficiary_type, name, cutoff)
	details = []
	if beneficiary_type == "Citizen":
		required_group = program.target_group_ref
		if required_group:
			result = "PASS" if required_group in snapshot["target_groups"] else "FAIL"
			details.append({"rule_code": "PROGRAM_TARGET", "rule_name": "Nhóm đối tượng chương trình", "actual_value": ", ".join(snapshot["target_groups"]), "expected_value": required_group, "evaluation": result, "reason": "Có nhóm còn hiệu lực" if result == "PASS" else "Không có nhóm còn hiệu lực"})
	elif program.target_group in ("poor", "near_poor"):
		expected = "Poor Household" if program.target_group == "poor" else "Near-poor Household"
		result = evaluate(snapshot["classification"], "EQ", expected)
		details.append({"rule_code": "PROGRAM_TARGET", "rule_name": "Phân loại hộ của chương trình", "actual_value": snapshot["classification"] or "", "expected_value": expected, "evaluation": result, "reason": "Phân loại tại ngày chốt" if result == "PASS" else "Phân loại thiếu hoặc không phù hợp"})
	for rule in rules:
		if rule.condition_type == "CLASSIFICATION":
			actual = snapshot["classification"]
		elif rule.condition_type == "TARGET_GROUP":
			actual = snapshot["target_groups"]
		elif rule.condition_type == "RESIDENCY":
			actual = snapshot["residential_group"] or snapshot["address"]
		elif rule.condition_type == "DUPLICATE":
			actual = ["EXISTING"] if has_prior_disbursement(program.name, beneficiary_type, name) else []
		else:
			frappe.throw("Loại điều kiện chính sách không hỗ trợ: " + str(rule.condition_type))
		verified_negative = False
		if rule.condition_type == "TARGET_GROUP" and not actual and rule.operator in {"EQ", "IN"}:
			expected_groups = [part.strip() for part in (rule.expected_value or "").split(",") if part.strip()]
			verified_negative = bool(expected_groups) and all(
				negative_target_group_verified(beneficiary_type, name, group, cutoff) for group in expected_groups
			)
		outcome = "FAIL" if verified_negative else evaluate(actual, rule.operator, rule.expected_value, rule.missing_behavior)
		details.append({"rule_code": rule.rule_code, "rule_name": rule.rule_name, "actual_value": ", ".join(str(value) for value in actual) if isinstance(actual, list) else str(actual or ""), "expected_value": rule.expected_value or "", "evaluation": outcome, "reason": "Đã xác minh không thuộc nhóm đối tượng tại ngày chốt" if verified_negative else (rule.message or {"PASS": "Đạt", "FAIL": "Không đạt", "UNKNOWN": "Cần xác minh dữ liệu"}[outcome])})
		if not rule.is_required:
			details[-1]["reason"] += " (tham khảo, không chặn kết quả)"
	blocking = [detail for detail in details if detail["rule_code"] == "PROGRAM_TARGET"] + [
		detail for detail, rule in zip(details[len(details) - len(rules):], rules) if rule.is_required
	]
	if any(detail["evaluation"] == "FAIL" for detail in blocking):
		status = "NOT_ELIGIBLE"
	elif any(detail["evaluation"] == "UNKNOWN" for detail in blocking):
		status = "NEED_VERIFICATION"
	else:
		status = "ELIGIBLE"
	return status, details, snapshot


def iter_candidates(beneficiary_type):
	start = 0
	while True:
		rows = frappe.get_all(beneficiary_type, filters={"is_archived": 0}, pluck="name", order_by="name asc", offset=start, limit=200)
		if not rows:
			break
		yield from rows
		start += len(rows)


@frappe.whitelist(methods=["POST"])
def screen_program(program_name):
	require_officer()
	program = frappe.get_doc("Support Program", program_name)
	program.check_permission("read")
	if not program.active or program.is_archived:
		frappe.throw("Chương trình chưa hoạt động hoặc đã lưu trữ.")
	if not program.policy_version:
		frappe.throw("Cần chọn phiên bản chính sách trước khi rà soát hàng loạt.")
	cutoff = getdate(program.cutoff_date or nowdate())
	if getdate(program.start_date) > cutoff or getdate(program.end_date) < cutoff:
		frappe.throw("Ngày chốt phải nằm trong khoảng triển khai của chương trình.")
	version = frappe.get_doc("Policy Version", program.policy_version)
	if version.status != "ACTIVE" or not version.approved_by or not version.approved_on:
		frappe.throw("Chỉ dùng phiên bản chính sách đã phê duyệt và ACTIVE.")
	if getdate(version.effective_from) > cutoff or (version.effective_to and getdate(version.effective_to) < cutoff):
		frappe.throw("Phiên bản chính sách không có hiệu lực tại ngày chốt.")
	rules = frappe.get_all("Policy Rule", filters={"policy_version": version.name}, fields=["rule_code", "rule_name", "condition_type", "operator", "expected_value", "missing_behavior", "priority", "is_required", "message"], order_by="priority asc, name asc")
	if not rules:
		frappe.throw("Phiên bản chưa có quy tắc xét hưởng.")
	frappe.db.sql("SELECT name FROM `tabSupport Program` WHERE name=%s FOR UPDATE", program.name)
	run = frappe.get_doc({"doctype": "Eligibility Run", "support_program": program.name, "policy_version": version.name, "cutoff_date": cutoff, "status": "QUEUED", "started_by": frappe.session.user, "started_at": now_datetime(), "rule_snapshot": json.dumps([dict(rule) for rule in rules], default=str, ensure_ascii=False)})
	with bulk_action("create"):
		run.insert(ignore_permissions=True)
	run.status = "RUNNING"
	with bulk_action(run.name):
		run.save(ignore_permissions=True)
	frappe.db.set_value("Support Program", program.name, "screening_status", "RUNNING")
	counts = {"ELIGIBLE": 0, "NOT_ELIGIBLE": 0, "NEED_VERIFICATION": 0}
	for name in iter_candidates(program.beneficiary_type):
		status, details, snapshot = evaluate_candidate(program, rules, program.beneficiary_type, name, cutoff)
		result = frappe.get_doc({"doctype": "Eligibility Result", "eligibility_run": run.name, "beneficiary_type": program.beneficiary_type, "household": name if program.beneficiary_type == "Household" else None, "citizen": name if program.beneficiary_type == "Citizen" else None, "result_status": status, "reason_summary": "; ".join(detail["rule_name"] + ": " + detail["evaluation"] for detail in details if detail["evaluation"] != "PASS") or "Đạt các điều kiện bắt buộc", "evaluated_at": now_datetime(), "input_snapshot": json.dumps(snapshot, default=str, ensure_ascii=False), "rule_details": details})
		with bulk_action("create"):
			result.insert(ignore_permissions=True)
		counts[status] += 1
	run.status = "COMPLETED"
	run.total_count = sum(counts.values())
	run.eligible_count = counts["ELIGIBLE"]
	run.not_eligible_count = counts["NOT_ELIGIBLE"]
	run.need_verification_count = counts["NEED_VERIFICATION"]
	run.completed_at = now_datetime()
	with bulk_action(run.name):
		run.save(ignore_permissions=True)
	frappe.db.set_value("Support Program", program.name, "screening_status", "COMPLETED")
	return run.name


@frappe.whitelist()
def get_run_results(run_name):
	run = frappe.get_doc("Eligibility Run", run_name)
	run.check_permission("read")
	return frappe.get_list("Eligibility Result", filters={"eligibility_run": run_name}, fields=["name", "beneficiary_type", "household", "citizen", "result_status", "reason_summary"], order_by="result_status asc, name asc", limit=5000)
