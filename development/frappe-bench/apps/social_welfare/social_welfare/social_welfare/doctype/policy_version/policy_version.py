import frappe
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime

from social_welfare.permissions import LEADER, is_admin


class PolicyVersion(Document):
	def validate(self):
		if self.effective_to and getdate(self.effective_from) > getdate(self.effective_to):
			frappe.throw("Khoảng hiệu lực của phiên bản không hợp lệ.")
		if frappe.db.exists("Policy Version", {"policy": self.policy, "version_number": self.version_number, "name": ["!=", self.name]}):
			frappe.throw("Số phiên bản đã tồn tại cho chính sách này.")
		previous = self.get_doc_before_save()
		if previous and previous.status != "DRAFT":
			protected = ("policy", "version_number", "effective_from", "effective_to", "legal_reference", "document_file")
			if any(self.has_value_changed(field) for field in protected):
				frappe.throw("Phiên bản đã kích hoạt không được sửa nội dung; hãy tạo phiên bản mới.")
		if self.status == "ACTIVE" and (not previous or previous.status != "ACTIVE"):
			if not is_admin() and LEADER not in frappe.get_roles():
				frappe.throw("Chỉ lãnh đạo được kích hoạt phiên bản chính sách.", frappe.PermissionError)
			if not frappe.db.get_value("Policy", self.policy, "is_active"):
				frappe.throw("Chính sách đang ngừng áp dụng.")
			from frappe.utils import getdate as parse_date
			for row in frappe.get_all("Policy Version", filters={"policy": self.policy, "status": "ACTIVE", "name": ["!=", self.name]}, fields=["effective_from", "effective_to"]):
				if parse_date(row.effective_from) <= parse_date(self.effective_to or "9999-12-31") and parse_date(row.effective_to or "9999-12-31") >= parse_date(self.effective_from):
					frappe.throw("Phiên bản ACTIVE bị chồng khoảng hiệu lực.")
			if not frappe.db.exists("Policy Rule", {"policy_version": self.name}):
				frappe.throw("Phiên bản cần ít nhất một quy tắc trước khi kích hoạt.")
			self.approved_by, self.approved_on = frappe.session.user, now_datetime()
		if previous and previous.status == "ACTIVE" and self.status not in ("ACTIVE", "EXPIRED"):
			frappe.throw("Phiên bản ACTIVE chỉ được chuyển sang EXPIRED.")
		if previous and previous.status == "ACTIVE" and self.status == "EXPIRED" and not is_admin() and LEADER not in frappe.get_roles():
			frappe.throw("Chỉ lãnh đạo được kết thúc phiên bản chính sách.", frappe.PermissionError)
		if previous and previous.status == "EXPIRED" and self.status != "EXPIRED":
			frappe.throw("Phiên bản hết hiệu lực không được kích hoạt lại.")

	def on_trash(self):
		frappe.throw("Không xóa phiên bản chính sách để giữ lịch sử rà soát.")
