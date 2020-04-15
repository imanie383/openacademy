# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Wizard(models.TransientModel):
	_name = "openacademy.wizard"

	def _default_session(self):
		#se obtiene el objeto sessiones
		session_obj = self.env['openacademy.session']
		# Id activo
		session_ids = self._context.get('active_ids')
		#se hace un recordset basado en un id - session_obj.browse(session_id).campo
		session_records = session_obj.browse(session_ids)
		#import pdb; pdb.set_trace()
		return session_records
		#tambien podias mandar session_id o session_obj.browse(session_ids).id si fuera 1

	# ya debe de estar declarada la funcion para usarla en el campo
	session_ids = fields.Many2many(
		'openacademy.session', required=True, default=_default_session)
	attendee_ids =fields.Many2many('res.partner', required=True)

	@api.multi
	def subscribe(self):
		# | suma quiatando repeditos
		# self.session_id = apunta a la tablta openacademy.session 
		for session in self.session_ids:
			session.attendee_ids |= self.attendee_ids
		#self.session_id.attendee_ids |= self.attendee_ids
		#regresa un diccionario vacio o una accion
		return {}



