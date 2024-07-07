from odoo import fields, models, api


class EstatePropertyModel(models.Model):
    _name = "estate.property.type"
    _description = "Property type"
    _order = "sequence, name desc"

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=1)
    property_ids = fields.One2many("estate.property", "property_type_id", string="Properties")
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id', string="Types")
    offer_count = fields.Integer(compute="_compute_offer_count")

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            print(self.offer_ids)
            self.offer_count = len(self.offer_ids)
