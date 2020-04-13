# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Parter(models.Model):
    #_name = 'openacademy.partner'
    _inherit = 'res.partner'

    instructor = fields.Boolean(default=False)
    session_ids = fields.Many2many(
    	'openacademy.session', string="Attended Sessions",
    	readonly=True)
    other_field = fields.Boolean(default=True, string="Campo Afeter")
    other_field2 = fields.Boolean(default=True, string="Campo Before")