from openerp import models, fields, api, _
import datetime
from datetime import date
import logging
_logger = logging.getLogger(__name__)

class project_task(models.Model):
    _inherit = ['project.task']

    associated_event = fields.Many2one('calendar.event', string="Associated Event", index=True)
    associated_event_start_date = fields.Datetime(string='Start Date', compute="_compute_event_info")
    associated_event_duration = fields.Float(string='Duration', compute="_compute_event_info")
    associated_event_partner_ids = fields.Many2many('res.partner', 'project_task_res_partner_rel', compute="_compute_event_info", string='Attendees')


    def _compute_event_info(self):
        if self.associated_event:
            self.associated_event_start_date = self.associated_event.start_datetime
            self.associated_event_duration = self.associated_event.duration
            self.associated_event_partner_ids = self.associated_event.partner_ids

    @api.onchange('associated_event')
    def get_and_set_event_info(self):
        if self.associated_event:
            self.associated_event.write({'associated_task': self.id})
            self.associated_event_start_date = self.associated_event.start_datetime
            self.associated_event_duration = self.associated_event.duration
            self.associated_event_partner_ids = self.associated_event.partner_ids

    @api.multi
    def open_create_event_wizard(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Create new event',
            'res_model': 'project.task.new.event.wizard',
            'domain': '',
            'view_mode': 'form',
            'target': 'new',
        }
        return action

    @api.multi
    def delete_event(self):
        if self.associated_event:
            self.associated_event.unlink()
