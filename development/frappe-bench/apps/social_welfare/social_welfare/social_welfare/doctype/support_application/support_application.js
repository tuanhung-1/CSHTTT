frappe.ui.form.on("Support Application", {
    refresh(frm) {
        const guidance = { Draft: "Cán bộ an sinh hoàn thiện hồ sơ rồi chuyển xác minh.", Submitted: "Người xác minh được phân công tiếp nhận hồ sơ.", Reviewing: "Ghi kết quả xác minh rồi trình lãnh đạo.", "Pending Approval": "Lãnh đạo nhập ý kiến và số tiền phê duyệt trước khi quyết định.", Returned: "Cán bộ an sinh bổ sung theo ý kiến lãnh đạo rồi đưa về Nháp để trình lại.", Approved: "Tài chính nhập ghi chú để xác nhận chi. Chức năng này chưa thay thế chứng từ và đối soát.", Rejected: "Hồ sơ bị từ chối. Xem ý kiến của lãnh đạo.", Paid: "Đã ghi nhận người và thời điểm xác nhận chi trả." };
        frm.set_intro(frm.is_new() ? "Tạo hộ gia đình và chương trình hỗ trợ trước khi lập hồ sơ. Với chương trình hộ nghèo/cận nghèo, hộ còn cần một kỳ phân loại có hiệu lực vào ngày hồ sơ." : (guidance[frm.doc.workflow_state] || guidance.Draft), "blue");
        if (frm.is_new() && frappe.model.can_create("Household")) {
            frm.add_custom_button("Tạo hộ gia đình", () => frappe.new_doc("Household"));
        }
        if (frm.is_new() && frappe.model.can_create("Support Program")) {
            frm.add_custom_button("Tạo chương trình hỗ trợ", () => frappe.new_doc("Support Program"));
        }
    },
});
