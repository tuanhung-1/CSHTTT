# Copyright (c) 2026, Student Project and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import flt, now_datetime

from social_welfare.permissions import FINANCE, LEADER, OFFICER, VERIFIER, is_admin
from social_welfare.social_welfare.doctype.household_classification.household_classification import (
	get_effective_classification,
)


class SupportApplication(Document):
	def before_naming(self):
		if not self.application_code:
			self.application_code = make_autoname("APP-.YYYY.-.#####", doctype=self.doctype)

	def before_insert(self):
		if self.workflow_state != "Draft":
			frappe.throw(_("New applications must start in Draft."))

	def validate(self):
		self.validate_amounts()
		self.validate_household_program_uniqueness()
		self.validate_target_group()
		self.validate_role_fields()
		self.validate_transition()

	def validate_amounts(self):
		if flt(self.requested_amount) < 0:
			frappe.throw(_("Requested amount must be greater than or equal to zero."))
		if flt(self.approved_amount) < 0:
			frappe.throw(_("Approved amount must be greater than or equal to zero."))

	def validate_household_program_uniqueness(self):
		filters = {
			"household": self.household,
			"program": self.program,
			"name": ["!=", self.name],
		}
		if frappe.db.exists("Support Application", filters):
			frappe.throw(_("A household can have only one application for the same program."))

	def validate_target_group(self):
		if not self.household or not self.program:
			return

		target_group = frappe.db.get_value("Support Program", self.program, "target_group")
		current = get_effective_classification(self.household, self.application_date)
		poverty_status = current.classification if current else None
		required_status = {
			"poor": "Poor Household",
			"near_poor": "Near-poor Household",
		}.get(target_group)

		if required_status and poverty_status != required_status:
			frappe.throw(
				"Hộ chưa có phân loại phù hợp và còn hiệu lực tại ngày hồ sơ. Hãy kiểm tra Lịch sử phân loại."
			)

	def validate_role_fields(self):
		if is_admin():
			return
		roles = set(frappe.get_roles())
		previous = self.get_doc_before_save()
		state = previous.workflow_state if previous else "Draft"
		allowed = set()
		if OFFICER in roles and state in {"Draft", "Returned"}:
			allowed.update(
				{"application_code", "household", "program", "application_date", "requested_amount", "reason"}
			)
		if VERIFIER in roles and state in {"Submitted", "Reviewing"}:
			allowed.add("verification_note")
		if LEADER in roles and state == "Pending Approval":
			allowed.update({"review_note", "approved_amount"})
		if FINANCE in roles and state == "Approved":
			allowed.add("payment_note")
		for field in (
			"application_code",
			"household",
			"program",
			"application_date",
			"requested_amount",
			"reason",
			"verification_note",
			"review_note",
			"approved_amount",
			"payment_note",
			"submitted_by",
			"decided_by",
			"decided_at",
			"paid_by",
			"paid_at",
		):
			new = self.get(field)
			changed = self.has_value_changed(field) if previous else new not in (None, "", 0, 0.0)
			if changed and field not in allowed:
				frappe.throw(
					"Bạn không có quyền sửa trường này ở bước hiện tại: " + self.meta.get_label(field),
					frappe.PermissionError,
				)

	def validate_transition(self):
		previous = self.get_doc_before_save()
		if not previous or previous.workflow_state == self.workflow_state:
			return
		transition = (previous.workflow_state, self.workflow_state)
		matrix = {
			("Draft", "Submitted"): OFFICER,
			("Submitted", "Reviewing"): VERIFIER,
			("Reviewing", "Pending Approval"): VERIFIER,
			("Pending Approval", "Approved"): LEADER,
			("Pending Approval", "Rejected"): LEADER,
			("Pending Approval", "Returned"): LEADER,
			("Returned", "Draft"): OFFICER,
			("Rejected", "Draft"): OFFICER,
			("Approved", "Paid"): FINANCE,
		}
		if transition not in matrix:
			frappe.throw("Chuyển trạng thái không hợp lệ.")
		if not is_admin() and matrix[transition] not in frappe.get_roles():
			frappe.throw("Vai trò hiện tại không được thực hiện bước này.", frappe.PermissionError)
		if self.workflow_state == "Submitted":
			self.submitted_by = frappe.session.user
		if self.workflow_state == "Pending Approval" and not self.verification_note:
			frappe.throw("Cần ghi kết quả xác minh trước khi trình lãnh đạo.")
		if self.workflow_state in {"Approved", "Rejected", "Returned"}:
			if not is_admin() and frappe.session.user == previous.submitted_by:
				frappe.throw("Người trình không được tự phê duyệt hồ sơ của mình.", frappe.PermissionError)
			if not self.review_note:
				frappe.throw("Cần nhập ý kiến/lý do quyết định của lãnh đạo.")
			self.decided_by, self.decided_at = frappe.session.user, now_datetime()
		if self.workflow_state == "Paid":
			if not self.payment_note:
				frappe.throw("Cần nhập ghi chú xác nhận chi trả.")
			self.paid_by, self.paid_at = frappe.session.user, now_datetime()
