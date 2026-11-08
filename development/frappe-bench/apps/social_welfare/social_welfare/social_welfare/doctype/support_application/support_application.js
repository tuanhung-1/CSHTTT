frappe.ui.form.on("Support Application", {
    refresh(frm) {
        const guidance = { Draft: "Cán bộ an sinh hoàn thiện hồ sơ rồi chuyển xác minh.", Submitted: "Người xác minh được phân công tiếp nhận hồ sơ.", Reviewing: "Ghi kết quả xác minh rồi trình lãnh đạo.", "Pending Approval": "Lãnh đạo nhập ý kiến và số tiền phê duyệt trước khi quyết định.", Returned: "Cán bộ an sinh bổ sung theo ý kiến lãnh đạo rồi đưa về Nháp để trình lại.", Approved: "Tài chính nhập ghi chú để xác nhận chi. Chức năng này chưa thay thế chứng từ và đối soát.", Rejected: "Hồ sơ bị từ chối. Xem ý kiến của lãnh đạo.", Paid: "Đã ghi nhận người và thời điểm xác nhận chi trả." };
        frm.set_intro(guidance[frm.doc.workflow_state] || guidance.Draft, "blue");
    },
});
