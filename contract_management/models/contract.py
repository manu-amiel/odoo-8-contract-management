# -*- coding: utf-8 -*-
from logging import getLogger
from openerp import SUPERUSER_ID, models, fields, api, tools


logger = getLogger(__name__)


class Contract(models.Model):
    _name = 'cm.contract'

    name = fields.Char(string='Name', required=True, select=True)
    description = fields.Text(string='Description')
    create_id = fields.Many2one(string='Author', comodel_name='res.users', related='create_uid', auto_join=True, select=True)
    worker_id = fields.Many2one(string='Worker', comodel_name='res.users', auto_join=True, select=True)
    publish_date = fields.Date(string='Publish date', select=True, readonly=True)
    close_date = fields.Date(string='Close date', select=True, readonly=True)
    reject_date = fields.Date(string='Reject date', select=True, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('assigned', 'Assigned'),
        ('complete', 'Complete'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed')
    ], string='Status', select=True, default='draft', readonly=True, required=True)
    is_manager = fields.Boolean(string='Is manager ?', help="Indicates if user is in manager role", compute='compute_fields')
    is_worker = fields.Boolean(string='Is worker ?', help="Indicates if user is in worker role", compute='compute_fields')
    is_author = fields.Boolean(string='Is author ?', help="Indicates if user is in author role", compute='compute_fields')

    @api.depends('state', 'create_id')
    def compute_fields(self):
        """ Compute functional fields
        :return: void
        """

        for c in self:
            c.is_manager = self.env.user.has_group('contract_management.group_cm_manager')
            c.is_worker = self.env.user.has_group('contract_management.group_cm_worker')
            c.is_author = self.env.user.has_group('contract_management.group_cm_author')

    def action_wkf(self, state):
        """ Set state to contract from workflow actions
        :param state: Contract state
        :return: True
        """

        # Get it from Date field rather than the datetime module, because it provides us
        # the correct one based on the user timezone (server time is UTC).
        today = fields.Date.today()
        values = {'state': state}
        email_to = None

        # No need to send mail on publish
        if state != 'published':
            # Building message depending on action and recipient
            user = self.env.user
            subject = 'Contract {}'
            body = 'Contract "%s" was {}{}' % self.name

            # `Revised` state
            if self.state == 'complete' and state == 'assigned':
                email_to = self.worker_id.email
                subject = subject.format('is revised')
                body = body.format(state, ' by %s' % self.env.user.name)
            elif state == 'assigned':
                values.update(worker_id=self.env.user.id)
                email_to = self.create_id.email
                subject = subject.format('is assigned')
                body = body.format(state, ' to user %s' % self.worker_id.name)
            # The workflow allows author to reject a non-assigned contract, so...
            elif state == 'rejected':
                values.update(reject_date=today)
                if self.worker_id:
                    email_to = self.worker_id.email
                    subject = subject.format('is rejected')
                    body = body.format(state, '')
            elif state == 'complete':
                email_to = self.create_id.email
                subject = subject.format('is complete')
                # No information is provided for manager who complete a contract
                # which is assigned to another worker.
                # Sending an email mentioning worker has completed the contract while it was a manager
                # who did it, is not correct (in my opinion ^^).
                body = body.format(state, ' by %s' % self.worker_id.name if self.worker_id == user else user.name)
            elif state == 'closed':
                values.update(close_date=today)
                email_to = self.worker_id.email
                subject = subject.format('done')
                body = body.format(state, '')
            else:
                pass

            # Sending mail
            if email_to:
                mail_server_pool = self.env['ir.mail_server']
                email_from = tools.config.get('email_from', False) or self.env['res.users'].browse(SUPERUSER_ID).email or 'someone@somewhere.com'
                email_msg = mail_server_pool.build_email(email_from, [email_to], subject, body)
                logger.info(mail_server_pool.send_email(email_msg))
        else:
            values.update(publish_date=today)

        self.write(values)

        return True

    @api.multi
    def write(self, vals):

        # Set state to assigned if worker_id as been changed
        if 'worker_id' in vals:
            vals.update(state='assigned')

        return super(Contract, self).write(vals)
