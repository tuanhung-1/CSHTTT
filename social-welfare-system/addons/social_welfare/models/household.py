from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SocialHousehold(models.Model):
    _name = "social.household"
    _description = "Social Welfare Household"
    _rec_name = "household_code"

    _household_code_unique = models.Constraint(
        "UNIQUE (household_code)",
        "Household code must be unique.",
    )

    household_code = fields.Char(
        string="Household Code",
        required=True
    )

    citizen_ids = fields.One2many(
        "social.citizen",
        "household_id",
        string="Household Members",
    )

    head_citizen_id = fields.Many2one(
        "social.citizen",
        string="Head of Household",
        domain="[('household_id', '=', id)]",
        ondelete="set null",
    )

    head_name = fields.Char(
        string="Head Name (Legacy)",
        required=True,
    )

    address = fields.Char(
        string="Address"
    )

    member_count = fields.Integer(
        string="Number of Members",
        compute="_compute_member_count",
        store=True,
    )

    average_income = fields.Float(
        string="Average Income"
    )

    poverty_status = fields.Selection(
        [
            ("poor", "Poor Household"),
            ("near_poor", "Near-poor Household"),
            ("normal", "Normal"),
        ],
        string="Household Classification",
        default="normal"
    )

    @api.model_create_multi
    def create(self, vals_list):
        codes = [vals.get("household_code") for vals in vals_list]
        present_codes = [code for code in codes if code]
        if len(present_codes) != len(set(present_codes)):
            raise ValidationError("Household code must be unique.")
        for household_code in present_codes:
            if self.search_count([("household_code", "=", household_code)]):
                raise ValidationError("Household code must be unique.")
        return super().create(vals_list)

    def write(self, vals):
        household_code = vals.get("household_code")
        if household_code and (
            len(self) > 1
            or self.search_count(
                [
                    ("household_code", "=", household_code),
                    ("id", "not in", self.ids),
                ]
            )
        ):
            raise ValidationError("Household code must be unique.")
        return super().write(vals)

    @api.depends("citizen_ids")
    def _compute_member_count(self):
        for household in self:
            household.member_count = len(household.citizen_ids)

    @api.constrains("head_citizen_id")
    def _check_head_citizen_household(self):
        for household in self:
            if (
                household.head_citizen_id
                and household.head_citizen_id.household_id != household
            ):
                raise ValidationError(
                    "The head of household must be a member of this household."
                )
