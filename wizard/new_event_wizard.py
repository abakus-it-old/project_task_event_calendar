from openerp import models, fields, api, _
from openerp.osv import osv
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)

class new_event_wizard(models.TransientModel):
    _name = 'project.task.new.event.wizard'

    def _default_task(self):
        task_ids = self.env['project.task'].browse(self._context.get('active_ids'))
        if len(task_ids) > 0:
            task = task_ids[0]
            return task.id

    def _default_attendees(self):
        task_ids = self.env['project.task'].browse(self._context.get('active_ids'))
        if len(task_ids) > 0:
            task = task_ids[0]
            partners = [task.user_id.partner_id.id]
            for p in task.message_follower_ids:
                partners.append(p.partner_id.id)
            return partners

    def _default_name(self):
        task_ids = self.env['project.task'].browse(self._context.get('active_ids'))
        if len(task_ids) > 0:
            task = task_ids[0]
            return task.name

    def _default_start_date(self):
        task_ids = self.env['project.task'].browse(self._context.get('active_ids'))
        if len(task_ids) > 0:
            task = task_ids[0]
            return task.date_deadline

    def _default_duration(self):
        task_ids = self.env['project.task'].browse(self._context.get('active_ids'))
        if len(task_ids) > 0:
            task = task_ids[0]
            return task.planned_hours

    name = fields.Char(string="Name", default=_default_name, required=True)
    start_date = fields.Datetime(string="Start date", default=_default_start_date, required=True)
    duration = fields.Float(string='Duration', default=_default_duration, required=True)
    partner_ids = fields.Many2many('res.partner', 'wizard_calendar_event_res_partner_rel', string='Attendees', default=_default_attendees)
    associated_task = fields.Many2one('project.task', string="Associated Task", default=_default_task)

    def onchange_partner_ids(self, cr, uid, ids, value, context=None):
        """ The basic purpose of this method is to check that destination partners
            effectively have email addresses. Otherwise a warning is thrown.
            :param value: value format: [[6, 0, [3, 4]]]
        """
        res = {'value': {}}

        if not value or not value[0] or not value[0][0] == 6:
            return

        res.update(self.check_partners_email(cr, uid, value[0][2], context=context))
        return res

    def check_partners_email(self, cr, uid, partner_ids, context=None):
        """ Verify that selected partner_ids have an email_address defined.
            Otherwise throw a warning. """
        partner_wo_email_lst = []
        for partner in self.pool['res.partner'].browse(cr, uid, partner_ids, context=context):
            if not partner.email:
                partner_wo_email_lst.append(partner)
        if not partner_wo_email_lst:
            return {}
        warning_msg = _('The following contacts have no email address :')
        for partner in partner_wo_email_lst:
            warning_msg += '\n- %s' % (partner.name)
        return {'warning': {
                'title': _('Email addresses not found'),
                'message': warning_msg,
                }}

    @api.multi
    def create_event(self):
        wizard = self
        if wizard.start_date and wizard.duration > 0 and wizard.name != "":

            _logger.debug("TASK : %s", wizard.associated_task.name)

            partners = []
            for p in wizard.partner_ids:
                partners.append(p.id)

            start = datetime.strptime(wizard.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
            duration = wizard.duration
            _logger.debug("TEST BEFORE CREATING")
            event_id = wizard.env['calendar.event'].create({
                    'name': wizard.name,
                    'start': start.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'stop': (start + timedelta(hours=duration)).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'partner_ids': [(6, 0, partners)],
                    #'stop_date': (start + timedelta(hours=duration)).strftime(DEFAULT_SERVER_DATE_FORMAT),

                    #'stop_datetime': (start + timedelta(hours=duration)).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    #'start_date': start.strftime(DEFAULT_SERVER_DATE_FORMAT),

                    #'associated_task': wizard.associated_task.id
                })
            _logger.debug("TEST AFTER CREATING")
            wizard.associated_task.write({'associated_event': event_id.id})

            return {
                    'type': 'ir.actions.act_window_close',
                   }
        return {'warning': {
                'title': _('All info for event not set'),
                'message': "Name, start date and duration and mandatory.,",
                }}