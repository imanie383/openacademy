# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from psycopg2 import IntegrityError
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

    _sql_constraints = [
        ('name_description_check',
         'CHECK(name != description)',
         "The title of the course should not be the description"),

        ('name_unique',
         'UNIQUE(name)',
         "The course title must be unique"),
    ]

    #funcion para duplicar un registro
    def copy(self, default=None):
        if default is None:
            default = {}
        copied_count = self.search_count([('name', 'ilike', 'Copy of %s%%' % (self.name))])
        if not copied_count:
            default['name'] = "Copy of %s" % (self.name)
        else:
            default['name'] = "Copy of %s (%s)" % (self.name,copied_count)

        #default['name'] = self.name + '_otro'
        try:
            return super(Course, self).copy(default)
        except IntegrityError:
            pass





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
    #crea el campo calculado en la tabla
    taken_seats = fields.Float(compute='_taken_seats', store=True)
    active = fields.Boolean(default=True)



    #self._fields = obtengo los campos y sus nombres del model
    #self._fields.keys() = obtengo los campos del modelo
    #record.write_uid._fields.keys() = obtengo los campos de la otra tabla ligada por 
    #el campo write_uid
    #record.attendee_ids.ids = ver el
    #dir(record.attendee_ids) = ver las propiedades del objeto

    #campo computed taken_seats
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

    #sslo se maneja en la vista formulario por lo que no necesitas un for
    @api.onchange('seats', 'attendee_ids')
    def _verify_valid_seats(self):
        #if self.seats < 0:
        if self.filtered(lambda r: r.seats < 0):
            selft.active = False
            return {
                'warning': {
                    'title': "Inconrrect 'seats' value",
                    'message': "The number of available seats may not be negative"
                }
            }
        #si cae en cualquier if, ahi termina el proceso, no se ejecuta el siguiente
        #es como un case
        if self.seats < len(self.attendee_ids):
            self.active = False
            return {
                'warning': {
                    'title': "Too many attendees",
                    'message': "Increase seats or remove excess attendees"
                }
            }
        self.active = True

    #en todos necesitas el for menos en el onchange
    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendee(self):
        #puede omitir el lamnda y poner solo el campo
        for record in self.filtered('instructor_id'):
            if record.instructor_id in record.attendee_ids:
                raise exceptions.ValidationError("A session's instructor can't be an attendee")




