from openerp import models, fields, api, _
import datetime
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

import logging
_logger = logging.getLogger(__name__)

class project_task(models.Model):
    _inherit = ['project.task']

    associated_event = fields.Many2one('calendar.event', string="Associated Event", index=True)
    associated_event_start_date = fields.Datetime(string='Start Date', compute="_compute_start_date")
    associated_event_duration = fields.Float(string='Duration', compute="_compute_duration")
    #associated_event_partner_ids = fields.Many2many('res.partner', 'project_task_res_partner_rel', compute="_compute_partners", string='Attendees')

    @api.multi
    def _compute_start_date(self):
        if self.associated_event:
            self.associated_event_start_date = self.associated_event.start_datetime

    @api.multi
    def _compute_duration(self):
        if self.associated_event:
            self.associated_event_duration = self.associated_event.duration

    """@api.multi
    def _compute_partners(self):
        _logger.debug("\n\n TEST WILL TRY TO ASSOCIATED PARTNERS")
        if self.associated_event:
            partners = []
            for p in self.associated_event.partner_ids:
                partners.append(p.id)
            self.associated_event_partner_ids = [(6, 0, partners)]
            _logger.debug("\n\n TEST PARTNERS ASSOCIATED")"""

    @api.onchange('associated_event')
    def get_and_set_event_info(self):
        if self.associated_event:
            self.associated_event.write({'associated_task': self.id})
            self.associated_event_start_date = self.associated_event.start_datetime
            self.associated_event_duration = self.associated_event.duration
            """partners = []
            for p in self.associated_event.partner_ids:
                partners.append(p.id)
            self.associated_event_partner_ids = [(6, 0, partners)]"""

    @api.multi
    def quick_create_event(self):
        # Start date
        start = datetime.now()
        if self.date_deadline:
            start = datetime.strptime(self.date_deadline, "%Y-%m-%d")
        # Duration
        duration = 2
        if self.planned_hours > 0:
            duration = self.planned_hours
        # Partners
        partners = [self.user_id.partner_id.id]
        for p in self.message_follower_ids:
            if p.partner_id.id not in partners:
                partners.append(p.partner_id.id)
        # Creation of the event
        event_id = self.env['calendar.event'].create({
            'name': self.name,
            'start': start.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'stop': (start + timedelta(hours=duration)).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'partner_ids': [(6, 0, partners)],
            'associated_task': self.id
        })

        self.associated_event = event_id
        return

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
    def open_event(self):
        if self.associated_event:
            return {
                'type': 'ir.actions.act_window',
                'name': 'calendar.view_calendar_event_form',
                'res_model': 'calendar.event',
                'res_id': self.associated_event.id ,
                'view_type': 'form',
                'view_mode': 'form',
                'target' : 'current',
                }

    @api.multi
    def delete_event(self):
        if self.associated_event:
            self.associated_event.unlink()
