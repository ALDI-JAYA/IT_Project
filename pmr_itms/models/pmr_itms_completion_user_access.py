from odoo import api, fields, models, _
from datetime import datetime

class PmrItmsCompletionAccess(models.Model):
    _name = "pmr.itms.completion.access"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Completion Troubleshooting"

    name = fields.Char(string="ITMS ID", required=True, copy=False, readonly=True, default=lambda self: _("New"))
    pmr_approval = fields.Many2one('amp.approval', string="Approval No", store=True)
    pmr_approval_note = fields.Text(string="Approval Note", related="pmr_approval.x_approval_log_ids.x_approval_note")
    pmr_itms_request = fields.Many2one('pmr.itms.user.access', string="Request From", store=True)
    pmr_itms_request_user_access = fields.Text(string="User Access Request", related="pmr_itms_request.pmr_itms_note_req")
    pmr_itms_personil_it = fields.Many2one('pmr.itms.personil.it', string="IT Personnel", store=True)
    pmr_itms_link = fields.Char(string="Link Access" , related="pmr_itms_request.pmr_itms_link")
    pmr_analytic_account = fields.Many2one('account.analytic.account', related="pmr_itms_request.pmr_analytic_account")
    pmr_itms_completion_date = fields.Date(string="Completion Date")
    pmr_itms_keterangan = fields.Text(string="Personnel Note")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting'),
        ('in_progress', 'In Progress'), 
        ('done', 'Done'), 
        ('completed', 'Completed'),
        ('cancel', 'Cancelled'),
        ], default='draft', string='Status', tracking=True, store=True)
    pmr_note_revision = fields.Text(string="Note Revisi")

    def action_cancel(self):
        self.state= 'cancel'

    def action_waiting(self):
        self.state = 'waiting'
        if self.pmr_itms_request:
            self.pmr_itms_request.write({'state': 'waiting'})

            self.pmr_itms_request.message_post(
                body=_("The request has been marked as Waiting by %s.") % (self.env.user.name),
                message_type='notification'
            )
    
    def action_in_progress(self):
        self.state = 'in_progress'
        if self.pmr_itms_request:
            self.pmr_itms_request.write({'state': 'in_progress'})

            self.pmr_itms_request.message_post(
                body=_("The request has been marked as In Progress by %s.") % (self.env.user.name),
                message_type='notification'
            )

    def action_draft(self):
        self.state = 'draft'

    def action_completed(self):
        self.state= 'completed'

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self._generate_sequence()
        return super(PmrItmsCompletionAccess, self).create(vals)

    def _generate_sequence(self):
        """Generate a unique sequence based on year, month, and existing records."""
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month

        prefix = "COMP/ACCESS"
        year_str = str(year)
        month_str = f"{month:02d}"

        last_sequence = self.search(
            [("name", "like", f"{prefix}/{year_str}/{month_str}/%")],
            order="name desc",
            limit=1,
        )

        if last_sequence:
            last_sequence_number = int(last_sequence.name.split("/")[-1])
            sequence_number = last_sequence_number + 1
        else:
            sequence_number = 1

        new_sequence = f"{prefix}/{year_str}/{month_str}/{sequence_number:05d}"
        return new_sequence

    def action_mark_done(self):
        """Set the state of the related request to 'done' and generate sequence."""
        for record in self:
            if record.pmr_itms_request:
                record.pmr_itms_request.write({'state': 'done'})

                record.pmr_itms_request.pmr_itms_completion = record.id

                record.pmr_itms_request.message_post(
                    body=_("The request has been marked as Done by %s.") % (self.env.user.name),
                    message_type='notification'
                )
        self.state= 'done'
