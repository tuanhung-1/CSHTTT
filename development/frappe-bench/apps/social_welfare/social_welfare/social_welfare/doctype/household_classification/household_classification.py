import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

CLASSIFICATIONS = {"Poor Household", "Near-poor Household", "Normal"}


def get_effective_classification(household, on_date=None):
	"""An unknown legacy period is never treated as current eligibility evidence."""
	date = getdate(on_date or nowdate())
	rows = frappe.get_all(
		"Household Classification",
		filters={
			"household": household,
			"is_legacy": 0,
			"is_void": 0,
			"valid_from": ["<=", date],
			"valid_to": [">=", date],
		},
		fields=["name", "classification", "period", "valid_from", "valid_to", "basis"],
		order_by="valid_from desc",
		limit=1,
	)
	return rows[0] if rows else None


class HouseholdClassification(Document):
	def validate(self):
		if not self.is_new():
			fields = (
				"household",
				"classification",
				"period",
				"valid_from",
				"valid_to",
				"basis",
				"evidence",
				"notes",
				"is_legacy",
			)
			if any(self.has_value_changed(field) for field in fields):
				frappe.throw("Bản ghi lịch sử đã lưu không được sửa. Hãy tạo kỳ phân loại mới.")
			void_fields = ("is_void", "void_reason", "voided_by", "voided_at")
			if (
				any(self.has_value_changed(field) for field in void_fields)
				and frappe.flags.social_welfare_void_classification != self.name
			):
				frappe.throw("Hãy dùng thao tác Hủy hiệu lực có lý do; không sửa trực tiếp lịch sử.")
			return
		if self.is_void or self.void_reason or self.voided_by or self.voided_at:
			frappe.throw("Không tạo bản phân loại mới ở trạng thái đã hủy.")
		if self.classification not in CLASSIFICATIONS:
			frappe.throw("Phân loại hộ không hợp lệ.")
		if self.is_legacy:
			if not frappe.flags.social_welfare_legacy_migration:
				frappe.throw("Chỉ bản chuyển đổi dữ liệu cũ mới được đánh dấu chưa rõ kỳ hiệu lực.")
			return
		if not all((self.period, self.valid_from, self.valid_to, self.basis)):
			frappe.throw("Cần nhập kỳ phân loại, ngày bắt đầu, ngày kết thúc và căn cứ.")
		if getdate(self.valid_from) > getdate(self.valid_to):
			frappe.throw("Ngày bắt đầu hiệu lực không được sau ngày kết thúc.")
		# Lock the parent to serialize concurrent inserts of overlapping periods.
		frappe.db.sql("SELECT name FROM `tabHousehold` WHERE name=%s FOR UPDATE", self.household)
		if frappe.db.exists(
			"Household Classification",
			{
				"household": self.household,
				"is_legacy": 0,
				"is_void": 0,
				"valid_from": ["<=", self.valid_to],
				"valid_to": [">=", self.valid_from],
			},
		):
			frappe.throw("Khoảng hiệu lực bị chồng lấn với lịch sử phân loại đã có của hộ.")

	def on_trash(self):
		frappe.throw("Không được xóa lịch sử phân loại.")
