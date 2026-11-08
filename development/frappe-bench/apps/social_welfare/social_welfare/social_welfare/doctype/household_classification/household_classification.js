frappe.ui.form.on("Household Classification", {
    refresh(frm) {
        frm.set_intro(frm.doc.is_legacy ? "Dữ liệu cũ chưa có ngày hiệu lực. Cần rà soát và tạo kỳ có căn cứ trước khi sử dụng." : "Lưu riêng từng kỳ phân loại. Bản ghi đã lưu không được sửa hoặc xóa; các kỳ của cùng hộ không được chồng lấn.", frm.doc.is_legacy ? "orange" : "blue");
        if (frm.is_new() && frappe.model.can_create("Household")) {
            frm.add_custom_button("Tạo hộ gia đình trước", () => frappe.new_doc("Household"));
        }
        if (!frm.is_new()) frm.disable_form();
        if (!frm.is_new() && !frm.doc.is_void && (frappe.session.user === "Administrator" || frappe.user_roles.includes("Social Welfare Manager"))) {
            frm.add_custom_button("Hủy hiệu lực", () => frappe.prompt({ fieldname: "reason", label: "Lý do hủy hiệu lực (giữ nguyên bản ghi để truy vết)", fieldtype: "Small Text", reqd: 1 }, async values => {
                await frappe.call({ method: "social_welfare.api.void_classification", args: { name: frm.doc.name, reason: values.reason } });
                frm.reload_doc();
            }, "Hủy hiệu lực phân loại", "Xác nhận"));
        }
        if (frm.doc.is_void) frm.set_intro("Đã hủy hiệu lực: " + frm.doc.void_reason, "orange");
    },
});
