from odoo import Command, models


class EstateProperty(models.Model):

    # ---------------------------------------- Private Attributes ---------------------------------

    _inherit = "estate.property"

    # ---------------------------------------- Action Methods -------------------------------------

    def action_sold(self):
        res = super().action_sold()
        for prop in self:
            self.env["account.move"].create(
                {
                    "partner_id": prop.partner_id.id,
                    "move_type": "out_invoice",
                    "line_ids": [
                        Command.create({
                            "name": prop.name,
                            "quantity": 1.0,
                            "price_unit": prop.selling_price * 1.06,
                        }),
                    ]
                }
            )
        return res

