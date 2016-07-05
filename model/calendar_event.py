from openerp import models, fields, api
import datetime
from datetime import date

class calendar_event(models.Model):
    _inherit = ['calendar.event']

    associated_task = fields.Many2one('project.task', string="Associated Task", index=True)

