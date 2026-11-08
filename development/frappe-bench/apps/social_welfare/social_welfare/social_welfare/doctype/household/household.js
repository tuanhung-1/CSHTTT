// Copyright (c) 2026, Student Project and contributors
// For license information, please see license.txt

frappe.ui.form.on("Household", {
	setup(frm) {
		frm.set_query("head_citizen", () => ({
			filters: {
				household: frm.is_new() ? "" : frm.doc.name,
			},
		}));
	},
	refresh(frm) {
		frm.toggle_display("head_citizen", !frm.is_new());
		if (frm.is_new()) {
			frm.set_intro("Bước 1/2: Nhập họ tên chủ hộ và lưu hồ sơ hộ. Chưa cần tạo hay chọn Công dân làm chủ hộ. Sau khi lưu, hãy chọn Thêm công dân vào hộ.", "blue");
			frm.fields_dict.classification_history.$wrapper.html('<p class="text-muted">Lưu hồ sơ hộ trước khi thêm lịch sử phân loại.</p>');
			return;
		}
		frm.set_intro("Bước 2/2: Thêm công dân vào hộ. Nếu là chủ hộ, chọn quan hệ Chủ hộ; hệ thống sẽ liên kết công dân đó với hồ sơ hộ.", "blue");
		if (frappe.model.can_create("Citizen")) {
			frm.add_custom_button("Thêm công dân vào hộ", () => frappe.new_doc("Citizen", {
				household: frm.doc.name,
				...(Number(frm.doc.member_count) === 0 ? { full_name: frm.doc.head_name, relationship: "Head" } : {}),
			}));
		}
		if (!frappe.model.can_read("Household Classification")) {
			frm.toggle_display("classification_section", false);
			frm.toggle_display("classification_history", false);
			return;
		}
		if (frappe.model.can_create("Household Classification")) {
			frm.add_custom_button("Thêm kỳ phân loại", () => frappe.new_doc("Household Classification", { household: frm.doc.name }));
		}
		frappe.call({ method: "social_welfare.api.household_history", args: { household: frm.doc.name } }).then(({ message: data }) => {
			const e = frappe.utils.escape_html;
			const labels = { "Poor Household": "Hộ nghèo", "Near-poor Household": "Hộ cận nghèo", Normal: "Không thuộc hộ nghèo/cận nghèo" };
			const current = data.current;
			frm.fields_dict.classification_history.$wrapper.html(`
				<div class="alert ${current ? 'alert-info' : 'alert-warning'}">${current ? `Phân loại hiện tại: <strong>${e(labels[current.classification])}</strong> · ${e(current.period)}` : 'Chưa có phân loại còn hiệu lực hôm nay. Dữ liệu cũ chưa rõ kỳ không được dùng làm căn cứ hiện tại.'}</div>
				${data.history.length ? `<div class="table-responsive"><table class="table table-bordered"><thead><tr><th>Kỳ</th><th>Phân loại</th><th>Khoảng hiệu lực</th><th>Căn cứ</th></tr></thead><tbody>${data.history.map(row => `<tr><td><a href="/desk/household-classification/${encodeURIComponent(row.name)}">${e(row.period)}</a>${row.is_legacy ? '<br><small class="text-warning">Cần rà soát dữ liệu cũ</small>' : ''}${row.is_void ? '<br><small class="text-danger">Đã hủy hiệu lực</small>' : ''}</td><td>${e(labels[row.classification])}</td><td>${row.is_legacy ? 'Chưa xác định' : `${e(frappe.datetime.str_to_user(row.valid_from))} – ${e(frappe.datetime.str_to_user(row.valid_to))}`}</td><td>${e(row.basis || '')}${row.is_void ? `<br><small>Lý do hủy: ${e(row.void_reason)}</small>` : ''}</td></tr>`).join('')}</tbody></table></div>` : '<p class="text-muted">Chưa có lịch sử phân loại. Thêm kỳ mới với ngày hiệu lực và căn cứ đầy đủ.</p>'}`);
		});
	},
});
