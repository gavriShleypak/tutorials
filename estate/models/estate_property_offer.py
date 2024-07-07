from datetime import timedelta
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class EstatePropertyOfferModel(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offer"
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("refused", "Refused")
        ],
        default="pending"
    )
    partner_id = fields.Many2one('res.partner', string='Buyer', required=True)
    property_id = fields.Many2one('estate.property', string='Property', required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")
    property_type_id = fields.Many2one("estate.property.type", string="Property Type",
                                       related="property_id.property_type_id")

    _sql_constraints = [
        ('price', 'CHECK(price > 0)', 'The price must be strictly positive')
    ]

    @api.depends("validity", "create_date")
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = fields.Date.today() + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            delta = record.date_deadline - fields.Date.today()
            record.validity = delta.days

    def action_confirm(self):
        for record in self:
            record.status = "accepted"
            record.property_id.selling_price = record.price
            record.property_id.partner_id = record.partner_id
            record.property_id.state = 'sold'

    def action_refused(self):
        for record in self:
            record.status = "refused"

    @api.model
    def create(self, vals_list):
        print("here!!!")
        if vals_list.get("property_id") and vals_list.get("price"):
            print("here!!")
            prop = self.env["estate.property"].browse(vals_list["property_id"])
            # We check if the offer is higher than the existing offers
            if prop.offer_ids:
                max_offer = max(prop.mapped("offer_ids.price"))
                if float_compare(vals_list["price"], max_offer, precision_rounding=0.01) <= 0:
                    raise UserError("The offer must be higher than %.2f" % max_offer)
            prop.state = "received"
        return super().create(vals_list)
