# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from psycopg2 import IntegrityError
from datetime import timedelta
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
    #campo virtual no existe en la BDD - Existe en la tabla sessions
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




#nombre del modelo en python
class Session(models.Model):
    #nombre del modelo en odoo@
    _name = 'openacademy.session'

    #Cuando se hace un Many2one se muestra esta campo
    name = fields.Char(required=True)
    
    #datetime_test = fields.Datetime(default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
    datetime_test = fields.Datetime(default=fields.Datetime.now())
    
    seats = fields.Integer(string="Number of seats")
    instructor_id = fields.Many2one('res.partner', string="Instructor", 
        domain=['|',('instructor', '=', True), 
        ('category_id.name', 'like', 'Teacher')] )
    #crea un select para se seleccione el curso
    course_id = fields.Many2one('openacademy.course', ondelete='cascade',
                                 string="Course", required=True)
    #crea una tabla intermedia
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
    #crea el campo calculado en la tabla
    taken_seats = fields.Float(compute='_taken_seats', store=True)
    #campo para borrado logico
    active = fields.Boolean(default=True)
    

    #--------necesario para la vista calendar--------
    start_date = fields.Date(default=fields.Date.today())
    duration = fields.Float(digits=(6,2), help="Duration in days")
    #calculamos la fecha fin
    end_date = fields.Date(store=True, compute='_get_end_date',
                            inverse="_set_end_date")
    
    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for record in self.filtered('start_date'):
            start_date = fields.Date.from_string(record.start_date)
            record.end_date = start_date + timedelta(days=record.duration, seconds=-1)
            #(start_date + timedelta(days=record.duration, seconds=-1)).strftime('%A')

    def _set_end_date(self):
        for record in self.filtered('start_date'):
            start_date = fields.Date.from_string(record.start_date)
            end_date = fields.Date.from_string(record.end_date)
            record.duration = (end_date - start_date).days + 1

    #----------necesario para la vista graph----------
    attendees_count = fields.Integer(
        string="Attendees count", compute='_get_attendees_count', store=True)

    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for record in self:
            record.attendees_count = len(record.attendee_ids)

    #----------necesario para la vista kanbah----------
    color = fields.Integer()

    #----------necesario para la vista gant----------
    hours = fields.Float(string="Duration in hours",
                         compute='_get_hours', inverse='_set_hours')

    @api.depends('duration')
    def _get_hours(self):
        for record in self:
            record.hours = record.duration * 24

    def _set_hours(self):
        for record in self:
            record.duration = record.hours / 24

    

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




