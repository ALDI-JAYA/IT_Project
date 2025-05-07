from odoo import api, fields, models, _
from datetime import datetime

class PmrItmsCompletionDevelopment(models.Model):
    _name = "pmr.itms.completion.development"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Completion com_development"

    name = fields.Char(string="ITMS ID", required=True, copy=False, readonly=True, default=lambda self: _("New"))
    pmr_approval = fields.Many2one('amp.approval', string="Approval No", store=True)
    pmr_approval_note = fields.Text(string="Approval Note", related="pmr_approval.x_approval_log_ids.x_approval_note")
    pmr_itms_request = fields.Many2one('pmr.itms.request.development', string="Request From", store=True)
    pmr_itms_request_development = fields.Char(string="Development Request", related="pmr_itms_request.pmr_itms_request_development_request")
    pmr_itms_request_development_note = fields.Text(string="Development Request Note", related="pmr_itms_request.pmr_itms_request_development_request_note")
    pmr_itms_personil_it = fields.Many2one('pmr.itms.personil.it', string="IT Personnel", store=True)
    pmr_start_date = fields.Datetime(string="Start Date", store=True)
    pmr_end_date = fields.Datetime(string="End Date", store=True)
    pmr_itms_keterangan = fields.Text(string="Personnel Note")
    pmr_note_revision = fields.Text(string="Note Revisi")
    pmr_itms_frontend  = fields.One2many('pmr.itms.completion.development.frontend','pmr_itms_dev_head_front', tracking=10)
    pmr_itms_backend  = fields.One2many('pmr.itms.completion.development.backend','pmr_itms_dev_head_back', tracking=10)
    pmr_itms_frontend_non  = fields.One2many('pmr.itms.completion.development.frontend.non','pmr_itms_dev_head_front_non', tracking=10)
    pmr_itms_backend_non  = fields.One2many('pmr.itms.completion.development.backend.non','pmr_itms_dev_head_back_non', tracking=10)
    pmr_itms_frontend_web  = fields.One2many('pmr.itms.completion.development.frontend.web','pmr_itms_dev_head_front_web', tracking=10)
    pmr_itms_backend_web  = fields.One2many('pmr.itms.completion.development.backend.web','pmr_itms_dev_head_back_web', tracking=10)
    pmr_itms_category = fields.Selection([
        ('software_odoo', 'Software Odoo'), 
        ('software_non_odoo', 'Software Non Odoo'),
        ('website','Website'),
    ], string="Sotware Category", store=True, related='pmr_itms_request.pmr_itms_category')

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
    def create(self, vals) :
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self._generate_sequence()
        return super(PmrItmsCompletionDevelopment, self).create(vals)

    def _generate_sequence(self):
        """Generate a unique sequence based on year, month, and existing records."""
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month

        prefix = "COMP/DEV"
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

    x_approval_id = fields.Many2one('amp.approval', string='Approval Ref', copy=False)
    x_approval_state = fields.Selection(default='open',
                                        string='Approval Status', related='x_approval_id.state', store=True,
                                        readonly=False)
    
    x_approval_log_ids = fields.One2many('amp.approval.log', 'x_com_dev_id', string='Approval Logs', copy=False)
    com_dev_status = [
        ('draft', 'Draft'),
        ('open', 'Waiting for Approval'),
        ('appr', 'Approved'),
        ('waiting', 'Waiting'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('completed', 'Completed'),
        ('cancel', 'Cancelled'),
    ]
    state = fields.Selection(com_dev_status, string="Status", default="draft", compute="_get_com_dev_status",inverse="_inverse_com_dev_status",
                                store=True, copy=False, tracking=True)
    x_currency_id = fields.Many2one("res.currency", string="Currency",
                                    default=lambda self: self.env.company.currency_id)
    x_approval_active = fields.Boolean(string='Active ITMS Approval', compute='_compute_approval_active_data', store=True)

    MAPPING_ITMS_APPROVAL_SETTINGS = {
        'ITMS_Trial': {'approval_required': False, 'setting_param': None, 'sequence_code': None},
        'ITMS': {'approval_required': True, 'setting_param': 'pmr_itms.approval.setting.com.dev', 'sequence_code': 'com.dev.approval.sequence'},
        'default': {'approval_required': True, 'setting_param': 'pmr_itms.approval.setting.com.dev', 'sequence_code': 'com.dev.approval.sequence'},
    }
    pmr_com_dev_re_to = fields.Selection([
        ('it_support', 'IT Support'), 
        ('it_programmer', 'IT Programmer'),
        ], string='Request To', store=True)

    def action_cancel(self):
        self.state= 'cancel'

    def _compute_approval_active_data(self):
        for record in self:
            record.x_approval_active = int(self.env['ir.config_parameter'].sudo().get_param('pmr_itms.active.com.dev.approval', 1))

    def _inverse_com_dev_status(self):
        pass

    @api.depends('x_approval_state')
    def _get_com_dev_status(self):
        for rec in self:
            if rec.x_approval_state == 'approved':
                rec.state = 'appr'
            elif rec.x_approval_state in ['waiting']:
                rec.state = 'open'
            else:
                rec.state = 'draft'

    def action_submit(self):
        for rec in self:
            approval_settings = {
                'approval_required': True,
                'setting_param': 'pmr_itms.approval.setting.com.dev',
                'sequence_code': 'com.dev.approval.sequence'
            }

            if rec.pmr_itms_request:  
                rec.pmr_itms_request.state = 'openit'

            if not approval_settings['approval_required']:
                rec.state = 'appr'
                rec.x_approval_state = 'approved'
            else:
                rec.state = 'open'
                active_com_dev_approval = int(rec.env['ir.config_parameter'].sudo().get_param('pmr_itms.active.com.dev.approval', 1))
                if active_com_dev_approval:
                    rec.create_or_update_approval_com_dev(approval_settings['setting_param'], approval_settings['sequence_code'])
                else:
                    rec.x_approval_state = 'approved'


    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'
            from_approval = self.env.context.get('from_approval', False)
            if not from_approval:
                approval_obj = self.env['amp.approval']
                if rec.x_approval_id:
                    approval_obj += rec.x_approval_id

                for appr in approval_obj:
                    prev_approval_obj_state = appr.state
                    appr.state = 'open'
                    new_approval_obj_state = appr.state

                    params = {
                        'approval': appr,
                        'actor': self.env.user,
                        'actor_group': 'submitter',
                        'actor_action': 'edit',
                        'prev_state': prev_approval_obj_state,
                        'new_state': new_approval_obj_state,
                    }

                    appr.create_approval_log(params)
    
    def create_approval_from_com_dev(self, setting_param, sequence_code):
        approval_setting_id = int(self.env['ir.config_parameter'].sudo().get_param(setting_param, 0))
        submitter_id = self.env.user.id
        approval_note = ''  
        detail_desc = self.name

        external_approver = {
            'x_level': 1,
            'x_user_id': self.env.user.id, 
        }

        vals = {
            'code': sequence_code,
            'model': 'pmr.itms.completion.development',
            'model_id': self.id,
            'submitter_id': submitter_id,
            'currency_id': self.x_currency_id.id,
            'estimated_value': 0,
            'doc_date': fields.Date.today(),
            'approval_setting_id': approval_setting_id,
            'external_approver': external_approver,  
            'approval_note': approval_note,  
            'desc': detail_desc,
        }
        approval_obj = self.env['amp.approval'].create_approval(vals)
        self.x_approval_id = approval_obj

    def update_approval_from_com_dev(self, approval_obj, setting_param):
        approval_setting_id = int(self.env['ir.config_parameter'].sudo().get_param(setting_param, 0))
        submitter_id = self.env.user.id
        approval_note = ''  
        detail_desc = self.name

        external_approver = {
            'x_level': 1,
            'x_user_id': self.env.user.id, 
        }

        data = {
            'doc_currency_id': self.x_currency_id.id,
            'estimate_value': 0,
            'doc_date': fields.Date.today(), 
            'model': 'pmr.itms.completion.development',
            'approval_setting_id': approval_setting_id,
            'submitter_id': submitter_id,
            'external_approver': external_approver, 
            'approval_note': approval_note,  
            'desc': detail_desc,
        }

        approval_obj.sudo()._synchronize_approval_data(data)
        self.x_approval_id = approval_obj

    def create_or_update_approval_com_dev(self, setting_param, sequence_code):
        approval_setting_id = int(self.env['ir.config_parameter'].sudo().get_param(setting_param, 0))
        
        if self.x_approval_id:
            prev_approval_state = self.x_approval_id.state
            self.x_approval_id.state = 'cancel'
            new_approval_state = 'cancel'
            approval_obj = self.x_approval_id.sudo()

            params = {
                'approval': approval_obj,
                'actor': self.env.user,
                'actor_group': 'submitter',
                'actor_action': 'cancel',
                'prev_state': prev_approval_state,
                'new_state': new_approval_state,
            }
            approval_obj.create_approval_log(params)

        existing_approval_com_dev = self.env['amp.approval'].search([
            ('x_model', '=', 'pmr.itms.completion.development'),
            ('x_model_id', '=', self.id),
            ('x_approval_setting_id', '=', approval_setting_id),
        ])

        if not existing_approval_com_dev:
            self.create_approval_from_com_dev(setting_param, sequence_code)
        else:
            self.update_approval_from_com_dev(existing_approval_com_dev, setting_param)

class PmrItmsComDevAmpApprovalInherit(models.Model):
    _inherit = 'amp.approval'

    @api.depends('x_model', 'x_model_id')
    def _compute_reference_text(self):
        super(PmrItmsComDevAmpApprovalInherit, self)._compute_reference_text()
        for approval in self:
            if approval.x_model == 'pmr.itms.completion.development':
                itms = self.env['pmr.itms.completion.development'].browse(approval.x_model_id)
                approval.x_reference_text = itms.display_name or ''
                
    def model_action_to_approve_action(self):
        res = super(PmrItmsComDevAmpApprovalInherit, self).model_action_to_approve_action()
        if self.x_model == 'pmr.itms.completion.development' and self.state == 'approved':
            model = self.x_model
            model_id = self.x_model_id
            khj_obj = self.env[model].browse([model_id])
            khj_obj.state = 'appr'
        return res

    def model_action_to_approve_action(self):
        res = super(PmrItmsComDevAmpApprovalInherit, self).model_action_to_approve_action()
        
        if self.x_model == 'pmr.itms.completion.development' and self.state == 'approved':
            model = self.x_model
            model_id = self.x_model_id
            completion_dev_obj = self.env[model].browse([model_id])

            completion_dev_obj.state = 'appr'

            if completion_dev_obj.pmr_itms_request:
                completion_dev_obj.pmr_itms_request.state = 'apprit' 
        
        return res

    def model_action_to_reject_action(self):
        res = super(PmrItmsComDevAmpApprovalInherit, self).model_action_to_reject_action()
        model = self.x_model
        model_id = self.x_model_id
        model_obj = self.env[model].browse([model_id])
        if self.x_model == 'pmr.itms.completion.development':
            model_obj.state = 'draft'
        return res

    def create_approval_log(self, params):
        res = super(PmrItmsComDevAmpApprovalInherit, self).create_approval_log(params)
        if self.x_model == 'pmr.itms.completion.development' and self.x_model_id:
            res.x_com_dev_id = self.x_model_id
        return res

class PmrItmsCompletionDevelopmentFrontend(models.Model):
    _name = "pmr.itms.completion.development.frontend"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Completion Development Frontend"

    pmr_itms_dev_head_front = fields.Many2one('pmr.itms.completion.development', string="Frontend")
    pmr_name_frontend = fields.Char(string="Create/Update Frontend Side")
    field_id = fields.Many2one('ir.model.fields', string="Field")
    view_id = fields.Many2one('ir.ui.view', string="View")
    pmr_frontend_category = fields.Selection([
        ('field', 'Field'),
        ('attribute','Attribute'),
        ('tree_view', 'Tree View'), 
        ('form_view', 'Form View'),
        ('kanban_view','Kanban View'),
        ('pivot_view','Pivot View'),
        ('qweb','Qweb'),
        ('json','Json'),
        ('css','CSS'),
        ('js','Javacript'),
    ], string="View Category", store=True)

class PmrItmsCompletionDevelopmentBackend(models.Model):
    _name = "pmr.itms.completion.development.backend"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Completion Backend" 

    pmr_itms_dev_head_back = fields.Many2one('pmr.itms.completion.development', string="Backend")
    pmr_name_backend = fields.Char(string="Create/Update Backend Side")
    model_id = fields.Many2one('ir.model', string="Model")
    
class PmrItmsCompletionDevelopmentFrontendNonOdoo(models.Model):
    _name = "pmr.itms.completion.development.frontend.non"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Completion Development Frontend Non Odoo"

    pmr_itms_dev_head_front_non = fields.Many2one('pmr.itms.completion.development', string="Frontend")
    pmr_name_frontend = fields.Char(string="Create/Update Frontend Side")
    pmr_name_frontend_prog = fields.Char(string="Programming Languange")

class PmrItmsCompletionDevelopmentBackendNonOdoo(models.Model):
    _name = "pmr.itms.completion.development.backend.non"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Completion Backend Non Odoo" 

    pmr_itms_dev_head_back_non = fields.Many2one('pmr.itms.completion.development', string="Backend")
    pmr_name_backend = fields.Char(string="Create/Update Backend Side")
    pmr_name_backend_prog = fields.Char(string="Programming Languange")

class PmrItmsCompletionDevelopmentFrontendWebsite(models.Model):
    _name = "pmr.itms.completion.development.frontend.web"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Completion Development Frontend Website"

    pmr_itms_dev_head_front_web = fields.Many2one('pmr.itms.completion.development', string="Frontend")
    pmr_name_frontend = fields.Char(string="Create/Update Frontend Side")
    pmr_name_frontend_prog = fields.Char(string="Programming Languange")
   

class PmrItmsCompletionDevelopmentBackendWebsite(models.Model):
    _name = "pmr.itms.completion.development.backend.web"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Completion Backend Non Odoo" 

    pmr_itms_dev_head_back_web = fields.Many2one('pmr.itms.completion.development', string="Backend")
    pmr_name_backend = fields.Char(string="Create/Update Backend Side")
    pmr_name_backend_prog = fields.Char(string="Programming Languange")


class PmrItmsAmpApprovalLogInherit(models.Model):
    _inherit = 'amp.approval.log'

    x_com_dev_id = fields.Many2one('pmr.itms.completion.development', string='ITMS Ref', copy=False)

    