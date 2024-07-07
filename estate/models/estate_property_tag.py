from odoo import fields, models


class EstatePropertyTagModel(models.Model):
    _name = "estate.property.tag"
    _description = "Property Tag"
    _order = "name desc"

    name = fields.Char(required=True)
    color = fields.Integer()

    _sql_constraints = [
        ('name', 'unique(name)', "Property tag should be unique")
    ]
