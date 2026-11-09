frappe.ui.form.on("Verification Case", {
    refresh(frm) {
        if (frm.is_new()) {
            wardUI.mountActions(frm, []);
            return;
        }
        const e = wardUI.escape;
        const subject = frm.doc.citizen || frm.doc.household;
        const closed = frm.doc.status === "COMPLETED";
        frm.set_intro(closed
            ? "Kết luận đã được lưu làm lịch sử. Cán bộ cập nhật dữ liệu nguồn hoặc gán nhóm theo kết luận, rồi chạy rà soát mới."
            : "Người xác minh được giao đối chiếu hồ sơ, ghi kết luận và căn cứ. Kết quả rà soát gốc không bị sửa.", "blue");
        frm.fields_dict.ward_case_summary.$wrapper.html(`<div class="ward-verification-summary">
            <div><span class="ward-journey-eyebrow">YÊU CẦU XÁC MINH</span><h2>${e(subject)}</h2>
                <p>${e(wardUI.label(frm.doc.question_type))}${frm.doc.target_group ? ` · ${e(frm.doc.target_group)}` : ""} · Ngày cần xác minh ${e(frm.doc.fact_date)}</p></div>
            ${wardUI.status(frm.doc.status)}
        </div><div class="ward-related"><div><strong>Nguồn thông tin</strong><span>Xem đối tượng và kết quả rà soát đã phát sinh yêu cầu.</span></div>
            <button type="button" class="btn btn-default ward-open-subject">Mở ${e(wardUI.label(frm.doc.beneficiary_type))} →</button>
            ${frm.doc.eligibility_result ? '<button type="button" class="btn btn-default ward-open-result">Xem kết quả gốc →</button>' : ""}</div>`);
        frm.fields_dict.ward_case_summary.$wrapper.find(".ward-open-subject").on("click", () => frappe.set_route("Form", frm.doc.beneficiary_type, subject));
        frm.fields_dict.ward_case_summary.$wrapper.find(".ward-open-result").on("click", () => frappe.set_route("Form", "Eligibility Result", frm.doc.eligibility_result));
        const reviewer = frappe.session.user === "Administrator" ||
            (frappe.user_roles.includes("Social Welfare Reviewer") && frm.doc.assigned_reviewer === frappe.session.user);
        wardUI.mountActions(frm, !closed && reviewer ? [{
            label: "Ghi kết luận xác minh", kind: "primary", onClick: () => {
                const fields = [
                    {fieldname: "conclusion", label: "Kết luận", fieldtype: "Select", reqd: 1,
                        options: [{value: "CONFIRMED", label: "Xác nhận có căn cứ"}, {value: "NOT_CONFIRMED", label: "Xác nhận không thuộc / không đúng"}, {value: "INSUFFICIENT", label: "Chưa đủ căn cứ"}]},
                ];
                if (frm.doc.question_type === "TARGET_GROUP") fields.push(
                    {fieldname: "verified_from", label: "Nhóm được xác minh từ ngày", fieldtype: "Date", default: frm.doc.fact_date},
                    {fieldname: "verified_to", label: "Nhóm được xác minh đến ngày", fieldtype: "Date",
                        description: "Chỉ ghi đến ngày có căn cứ xác nhận; ngày này phải bao gồm ngày cần xác minh."},
                );
                else fields.push({fieldname: "verified_value", label: "Giá trị đã xác minh (nếu xác nhận)", fieldtype: "Data"});
                fields.push(
                    {fieldname: "finding", label: "Nội dung kết luận", fieldtype: "Small Text", reqd: 1},
                    {fieldname: "basis", label: "Căn cứ xác minh", fieldtype: "Small Text", reqd: 1,
                        description: "Ghi số giấy tờ, biên bản, nguồn đối chiếu hoặc người cung cấp thông tin."},
                    {fieldname: "evidence_file", label: "Tệp minh chứng riêng tư (nếu có)", fieldtype: "Attach",
                        description: "Tải lên tệp ở chế độ riêng tư bằng tài khoản của bạn."},
                );
                const dialog = new frappe.ui.Dialog({title: "Kết luận hồ sơ xác minh", fields,
                    primary_action_label: "Lưu kết luận", primary_action: async values => {
                        await frappe.call({method: "social_welfare.verification.complete_verification", args: {name: frm.doc.name, ...values}, freeze: true});
                        dialog.hide();
                        frm.reload_doc();
                    },
                });
                dialog.show();
            },
        }] : [], "Kết luận cần nêu rõ nội dung và căn cứ; sau khi lưu sẽ không sửa trực tiếp.");
    },
});
