# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time

def get_uid(self, *a):
    return self.env.uid
#self.env.cur = curso
#self.env.user = datos del usuario
#self.env.ref = datos de demos
#self.env.context = datos del usuario
#self-env['openacademy.course'].browse(1)


class Course(models.Model):
    _name = 'openacademy.course'

    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    #se usa lamba para que no use simepre el mismo valor
    responsible_id = fields.Many2one(
        'res.users', string="Responsible",
        index=True, ondelete='set null',
        #default=lambda self, *a: self.env.uid)
        default=get_uid)
    session_ids = fields.One2many('openacademy.session', 'course_id')




class Session(models.Model):
    _name = 'openacademy.session'

    name = fields.Char(required=True)
    start_date = fields.Date(default=fields.Date.today())
    #datetime_test = fields.Datetime(default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
    datetime_test = fields.Datetime(default=fields.Datetime.now())
    duration = fields.Float(digits=(6,2), help="Duration in days")
    seats = fields.Integer(string="Number of seats")
    instructor_id = fields.Many2one('res.partner', string="Instructor", 
        domain=['|',('instructor', '=', True), 
        ('category_id.name', 'like', 'Teacher')] )
    course_id = fields.Many2one('openacademy.course', ondelete='cascade',
                                 string="Course", required=True)
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
    taken_seats = fields.Float(compute='_taken_seats')
    active = fields.Boolean(default=True)



    #self._fields = obtengo los campos y sus nombres del model
    #self._fields.keys() = obtengo los campos del modelo
    #record.write_uid._fields.keys() = obtengo los campos de la otra tabla ligada por 
    #el campo write_uid
    #record.attendee_ids.ids = ver el
    #dir(record.attendee_ids) = ver las propiedades del objeto
    @api.depends('seats', 'attendee_ids')
    def _taken_seats(self):
        #import pdb; pdb.set_trace()
        for record in self.filtered(lambda r: r.seats):
            record.taken_seats = 100.0 * len(record.attendee_ids) / record.seats
        # for record in self:
        #     if not record.seats:
        #         record.taken_seats = 0
        #     else:
        #         record.taken_seats = 100.0 * len(record.attendee_ids) / record.seats
