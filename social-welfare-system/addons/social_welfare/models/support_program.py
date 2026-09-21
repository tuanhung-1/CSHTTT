from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SocialSupportProgram(models.Model):
    _name = "social.support.program"
    _description = "Social Support Program"
    _rec_name = "name"

    _code_unique = models.Constraint(
        "UNIQUE (code)",
        "Program code must be unique.",
    )
    _support_amount_non_negative = models.Constraint(
        "CHECK (support_amount >= 0)",
        "Support amount must be greater than or equal to zero.",
    )
    _date_range_valid = models.Constraint(
        "CHECK (start_date <= end_date)",
        "Start date must be earlier than or equal to end date.",
    )

    code = fields.Char(
        string="Program Code",
        required=True
    )

    name = fields.Char(
        string="Program Name",
        required=True
    )

    description = fields.Text(
        string="Description"
    )

    start_date = fields.Date(
        string="Start Date",
        required=True
    )

    end_date = fields.Date(
        string="End Date",
        required=True
    )

    support_amount = fields.Float(
        string="Standard Support Amount"
    )

    target_group = fields.Selection(
        [
            ("poor", "Poor Household"),
            ("near_poor", "Near-poor Household"),
            ("disaster", "Disaster-affected Household"),
            ("policy", "Policy Beneficiary"),
            ("other", "Other"),
        ],
        string="Target Group"
    )

    active = fields.Boolean(
        string="Active",
        default=True
    )

    @api.model
    def _validate_program_values(self, vals, record=None):
        support_amount = vals.get(
            "support_amount", record.support_amount if record else 0
        )
        if support_amount is not False and support_amount < 0:
            raise ValidationError(
                "Support amount must be greater than or equal to zero."
            )

        start_date = vals.get("start_date", record.start_date if record else False)
        end_date = vals.get("end_date", record.end_date if record else False)
        if start_date and end_date:
            start_date = fields.Date.to_date(start_date)
            end_date = fields.Date.to_date(end_date)
            if start_date > end_date:
                raise ValidationError(
                    "Start date must be earlier than or equal to end date."
                )

    @api.model_create_multi
    def create(self, vals_list):
        codes = [vals.get("code") for vals in vals_list]
        present_codes = [code for code in codes if code]
        if len(present_codes) != len(set(present_codes)):
            raise ValidationError("Program code must be unique.")
        for code in present_codes:
            if self.search_count([("code", "=", code)]):
                raise ValidationError("Program code must be unique.")
        for vals in vals_list:
            self._validate_program_values(vals)
        return super().create(vals_list)

    def write(self, vals):
        code = vals.get("code")
        if code and (
            len(self) > 1
            or self.search_count([("code", "=", code), ("id", "not in", self.ids)])
        ):
            raise ValidationError("Program code must be unique.")
        for program in self:
            self._validate_program_values(vals, program)
        return super().write(vals)
