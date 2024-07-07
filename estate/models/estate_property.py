from datetime import timedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_is_zero

STATES = [
    ("new", "New"),
    ("offer", "Offer"),
    ("received", "Received"),
    ("offer", "Offer"),
    ("accepted", "Accepted"),
    ("sold", "Sold"),
    ("canceled", "Canceled")
]


class EstatePropertyModel(models.Model):
    _name = "estate.property"
    _description = "Estate property table"
    _order = "id desc"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=fields.Date.today() + timedelta(days=90))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(selection=[
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')
    ]
    )
    active = fields.Boolean('Active', default=True)
    state = fields.Selection(
        selection=STATES,
        default="new"
    )
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    user_id = fields.Many2one('res.users', string='Salesperson', index=True,
                              default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Offers")
    total_area = fields.Integer(compute="_compute_total_area", readonly=True)
    best_price = fields.Float(compute="_compute_best_price", readonly=True, default=0)

    _sql_constraints = [
        ('expected_price', 'CHECK(expected_price > 0)', 'The expected price must be strictly positive'),
        ('selling_price', 'CHECK(selling_price > 0)', 'The selling price must be strictly positive')
    ]

    @api.depends("garden_area", "living_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area

    @api.depends("offer_ids")
    def _compute_best_price(self):
        for prop in self:
            prop.best_price = max(prop.offer_ids.mapped("price")) if prop.offer_ids else 0.0

    @api.onchange("garden")
    def _onchange_partner_id(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = None

    def action_sold(self):
        for record in self:
            if record.state == "canceled":
                raise (UserError("Canceled property cannot be sold"))
            else:
                record.state = "sold"
        return True

    def action_canceled(self):
        for record in self:
            if record.state == "sold":
                raise (UserError("Sold property cannot be canceled"))
            else:
                record.state = "canceled"
        return True

    @api.constrains('selling_price', 'expected_price')
    def _check_date_end(self):
        for record in self:
            if float_is_zero(record.selling_price, 0.01):
                continue
            else:
                if record.selling_price < record.expected_price * 0.9:
                    raise ValidationError("Selling price cannot be under 90% of the expected price")
        return True

    @api.ondelete(at_uninstall=False)
    def _unlink_fail_if_bad_status(self):
        if self.state != "new" and self.state != "canceled":
            raise UserError("To delete property it must be New or Canceled")
