from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError


class SocialSupportApplication(models.Model):
    _name = "social.support.application"
    _description = "Support Application"
    _rec_name = "application_code"

    _application_code_unique = models.Constraint(
        "UNIQUE (application_code)",
        "Application code must be unique.",
    )
    _household_program_unique = models.Constraint(
        "UNIQUE (household_id, program_id)",
        "A household can have only one application for the same program.",
    )
    _requested_amount_non_negative = models.Constraint(
        "CHECK (requested_amount >= 0)",
        "Requested amount must be greater than or equal to zero.",
    )
    _approved_amount_non_negative = models.Constraint(
        "CHECK (approved_amount >= 0)",
        "Approved amount must be greater than or equal to zero.",
    )

    application_code = fields.Char(
        string="Application Code",
        required=True
    )

    household_id = fields.Many2one(
        "social.household",
        string="Household",
        required=True,
        ondelete="restrict"
    )

    program_id = fields.Many2one(
        "social.support.program",
        string="Support Program",
        required=True,
        ondelete="restrict"
    )

    application_date = fields.Date(
        string="Application Date",
        default=fields.Date.context_today
    )

    requested_amount = fields.Float(
        string="Requested Amount"
    )

    approved_amount = fields.Float(
        string="Approved Amount"
    )

    reason = fields.Text(
        string="Reason for Support"
    )

    review_note = fields.Text(
        string="Review Note"
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("reviewing", "Reviewing"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("paid", "Paid"),
        ],
        string="Status",
        default="draft",
        required=True,
        readonly=True,
        copy=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        default_state = self.default_get(["state"]).get("state", "draft")
        if any(vals.get("state", default_state) != "draft" for vals in vals_list):
            raise UserError(_("New applications must start in Draft."))
        self._validate_application_values(vals_list)
        return super().create(vals_list)

    @api.model
    def _validate_application_values(self, vals_list, records=None):
        records = list(records) if records is not None else [None] * len(vals_list)
        codes = []
        pairs = []

        for vals, record in zip(vals_list, records):
            application_code = vals.get(
                "application_code", record.application_code if record else False
            )
            household_id = vals.get(
                "household_id", record.household_id.id if record else False
            )
            program_id = vals.get(
                "program_id", record.program_id.id if record else False
            )
            requested_amount = vals.get(
                "requested_amount", record.requested_amount if record else 0
            )
            approved_amount = vals.get(
                "approved_amount", record.approved_amount if record else 0
            )

            if requested_amount is not False and requested_amount < 0:
                raise ValidationError(
                    "Requested amount must be greater than or equal to zero."
                )
            if approved_amount is not False and approved_amount < 0:
                raise ValidationError(
                    "Approved amount must be greater than or equal to zero."
                )

            codes.append(application_code)
            pairs.append((household_id, program_id))

            if household_id and program_id:
                household = self.env["social.household"].browse(household_id)
                program = self.env["social.support.program"].browse(program_id)
                if (
                    program.target_group in ("poor", "near_poor")
                    and household.poverty_status != program.target_group
                ):
                    raise ValidationError(
                        "The household classification does not match the program target group."
                    )

        present_codes = [code for code in codes if code]
        if len(present_codes) != len(set(present_codes)):
            raise ValidationError("Application code must be unique.")
        present_pairs = [pair for pair in pairs if all(pair)]
        if len(present_pairs) != len(set(present_pairs)):
            raise ValidationError(
                "A household can have only one application for the same program."
            )

        excluded_ids = [record.id for record in records if record]
        for application_code in present_codes:
            domain = [("application_code", "=", application_code)]
            if excluded_ids:
                domain.append(("id", "not in", excluded_ids))
            if self.search_count(domain):
                raise ValidationError("Application code must be unique.")
        for household_id, program_id in present_pairs:
            domain = [
                ("household_id", "=", household_id),
                ("program_id", "=", program_id),
            ]
            if excluded_ids:
                domain.append(("id", "not in", excluded_ids))
            if self.search_count(domain):
                raise ValidationError(
                    "A household can have only one application for the same program."
                )

    @api.constrains("household_id", "program_id")
    def _check_target_group(self):
        for application in self:
            target_group = application.program_id.target_group
            if (
                target_group in ("poor", "near_poor")
                and application.household_id.poverty_status != target_group
            ):
                raise ValidationError(
                    "The household classification does not match the program target group."
                )

    def _check_workflow_transition(self, target_state):
        transitions = {
            "submitted": ("draft", "officer"),
            "reviewing": ("submitted", "reviewer"),
            "approved": ("reviewing", "reviewer"),
            "rejected": ("reviewing", "reviewer"),
            "paid": ("approved", "reviewer"),
            "draft": ("rejected", "reviewer"),
        }
        if target_state not in transitions:
            raise UserError(_("Invalid application status."))
        source_state, role = transitions[target_state]
        if not (
            self.env.user.has_group("social_welfare.group_social_welfare_%s" % role)
            or self.env.user.has_group("social_welfare.group_social_welfare_manager")
        ):
            raise AccessError(_("You do not have permission to perform this workflow action."))
        if any(record.state != source_state for record in self):
            raise UserError(_(
                "Applications must be in '%(source)s' to move to '%(target)s'.",
                source=source_state, target=target_state,
            ))

    def write(self, vals):
        # Enforce the same rules for imports and direct RPC writes as for buttons.
        if "state" in vals:
            changing = self.filtered(lambda record: record.state != vals["state"])
            if changing:
                changing._check_workflow_transition(vals["state"])
        self._validate_application_values([vals] * len(self), self)
        return super().write(vals)

    def _transition_to(self, target_state):
        return self.write({"state": target_state})

    def action_submit(self):
        return self._transition_to("submitted")

    def action_review(self):
        return self._transition_to("reviewing")

    def action_approve(self):
        return self._transition_to("approved")

    def action_reject(self):
        return self._transition_to("rejected")

    def action_paid(self):
        return self._transition_to("paid")

    def action_reset_draft(self):
        return self._transition_to("draft")
