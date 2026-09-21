from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SocialCitizen(models.Model):
    _name = "social.citizen"
    _description = "Citizen"
    _rec_name = "full_name"

    _citizen_code_unique = models.Constraint(
        "UNIQUE (citizen_code)",
        "Citizen code must be unique.",
    )

    citizen_code = fields.Char(
        string="Citizen Code",
        required=True
    )

    full_name = fields.Char(
        string="Full Name",
        required=True
    )

    date_of_birth = fields.Date(
        string="Date of Birth"
    )

    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        string="Gender"
    )

    relationship = fields.Selection(
        [
            ("head", "Head of Household"),
            ("spouse", "Spouse"),
            ("child", "Child"),
            ("parent", "Parent"),
            ("other", "Other"),
        ],
        string="Relationship"
    )

    phone = fields.Char(
        string="Phone"
    )

    household_id = fields.Many2one(
        "social.household",
        string="Household",
        required=True,
        ondelete="cascade"
    )

    @api.model_create_multi
    def create(self, vals_list):
        codes = [vals.get("citizen_code") for vals in vals_list]
        present_codes = [code for code in codes if code]
        if len(present_codes) != len(set(present_codes)):
            raise ValidationError("Citizen code must be unique.")
        for citizen_code in present_codes:
            if self.search_count([("citizen_code", "=", citizen_code)]):
                raise ValidationError("Citizen code must be unique.")
        return super().create(vals_list)

    def write(self, vals):
        citizen_code = vals.get("citizen_code")
        if citizen_code and (
            len(self) > 1
            or self.search_count(
                [
                    ("citizen_code", "=", citizen_code),
                    ("id", "not in", self.ids),
                ]
            )
        ):
            raise ValidationError("Citizen code must be unique.")
        return super().write(vals)

    @api.constrains("household_id", "relationship")
    def _check_single_head_per_household(self):
        for citizen in self.filtered(lambda record: record.relationship == "head"):
            duplicate_head = self.search(
                [
                    ("household_id", "=", citizen.household_id.id),
                    ("relationship", "=", "head"),
                    ("id", "!=", citizen.id),
                ],
                limit=1,
            )
            if duplicate_head:
                raise ValidationError(
                    "A household can have only one citizen marked as head."
                )

    @api.constrains("household_id")
    def _check_selected_head_household(self):
        selected_heads = self.env["social.household"].search(
            [("head_citizen_id", "in", self.ids)]
        )
        for household in selected_heads:
            if household.head_citizen_id.household_id != household:
                raise ValidationError(
                    "A selected head cannot be moved to another household."
                )
