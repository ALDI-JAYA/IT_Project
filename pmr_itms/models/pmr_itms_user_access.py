from odoo import api, fields, models, _
from datetime import datetime
import logging

class PmrItmsUserAccess(models.Model):
    _name = "pmr.itms.user.access"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr access User Access"

    name = fields.Char(string="Access ID", required=True, copy=False, readonly=True, default=lambda self: _("New"))
    pmr_itms_request_date = fields.Datetime(
        string="Request Date", 
        required=True, 
        default=lambda self: fields.Datetime.now()
    )
    pmr_itms_user = fields.Many2one('pmr.itms.user', string="User", required=True, store=True)
    pmr_itms_personil_it = fields.Many2one('pmr.itms.personil.it', string="IT Personnel", store=True)
    pmr_itms_departement = fields.Many2one('hr.department', string="Departement", required=True, store=True)
    pmr_itms_link = fields.Char(string="Link Access", required=True)
    pmr_itms_note_req = fields.Text(string="Note Request", required=True)
    pmr_analytic_account = fields.Many2one('account.analytic.account', string="Analytic Account")
    pmr_itms_authority = fields.Selection([
        ('read', 'Read'), 
        ('write', 'Write'),
        ('full_access','Full Access'),
    ], string="Authority", store=True, required=True)
    
    @api.onchange('pmr_itms_user')
    def _onchange_pmr_itms_user(self):
        if self.pmr_itms_user:
            self.pmr_itms_departement = self.pmr_itms_user.department_id
        else:
            self.pmr_itms_departement = False 
            
    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self._generate_sequence()
        return super(PmrItmsUserAccess, self).create(vals)

    def _generate_sequence(self):
        """Generate a unique sequence based on year, month, and existing records."""
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month

        prefix = "REQ/ACCESS"
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
    x_approval_log_ids = fields.One2many('amp.approval.log', 'x_access_id', string='Approval Logs', copy=False)
    access_status = [
        ('draft', 'Draft'),
        ('open', 'Waiting for Approval'),
        ('appr', 'Approved'),
        ('waiting', 'Waiting'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('completed', 'Completed'),
        ('cancel', 'Cancelled'),
    ]
    state = fields.Selection(access_status, string="Status", default="draft", compute="_get_access_status",inverse="_inverse_access_status",
                                store=True, copy=False, tracking=True)
    x_currency_id = fields.Many2one("res.currency", string="Currency",
                                    default=lambda self: self.env.company.currency_id)
    x_approval_active = fields.Boolean(string='Active access Approval', compute='_compute_approval_active_data', store=True)

    MAPPING_access_APPROVAL_SETTINGS = {
        'access_Trial': {'approval_required': False, 'setting_param': None, 'sequence_code': None},
        'access': {'approval_required': True, 'setting_param': 'pmr_imts.approval.setting.access', 'sequence_code': 'access.approval.sequence'},
        'default': {'approval_required': True, 'setting_param': 'pmr_itms.approval.setting.access', 'sequence_code': 'access.approval.sequence'},
    }

    def action_cancel(self):
        self.state= 'cancel'

    def action_completed(self):
        self.state= 'completed'
        for rec in self :
            rec.pmr_itms_completion.state = 'completed'
    
    def action_in_progress(self):
        self.state= 'in_progress'
        for rec in self :
            rec.pmr_itms_completion.state = 'draft'
            self.state= 'in_progress'

    def _compute_approval_active_data(self):
        for record in self:
            record.x_approval_active = int(self.env['ir.config_parameter'].sudo().get_param('pmr_itms.active.access.approval', 1))

    def _inverse_access_status(self):
        pass

    @api.depends('x_approval_state')
    def _get_access_status(self):
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
                'setting_param': 'pmr_itms.approval.setting.access',
                'sequence_code': 'access.approval.sequence'
            }

            if not approval_settings['approval_required']:
                rec.state = 'appr'
                rec.x_approval_state = 'approved'
            else:
                rec.state = 'open'
                active_access_approval = int(rec.env['ir.config_parameter'].sudo().get_param('pmr_itms.active.access.approval', 1))
                if active_access_approval:
                    rec.create_or_update_approval_access(approval_settings['setting_param'], approval_settings['sequence_code'])
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
    
    def create_approval_from_access(self, setting_param, sequence_code):
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
            'model': 'pmr.itms.user.access',
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

    def update_approval_from_access(self, approval_obj, setting_param):
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
            'model': 'pmr.itms.user.access',
            'approval_setting_id': approval_setting_id,
            'submitter_id': submitter_id,
            'external_approver': external_approver, 
            'approval_note': approval_note,  
            'desc': detail_desc,
        }

        approval_obj.sudo()._synchronize_approval_data(data)
        self.x_approval_id = approval_obj

    def create_or_update_approval_access(self, setting_param, sequence_code):
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

        existing_approval_access = self.env['amp.approval'].search([
            ('x_model', '=', 'pmr.itms.user.access'),
            ('x_model_id', '=', self.id),
            ('x_approval_setting_id', '=', approval_setting_id),
        ])

        if not existing_approval_access:
            self.create_approval_from_access(setting_param, sequence_code)
        else:
            self.update_approval_from_access(existing_approval_access, setting_param)

class PmrAccessAmpApprovalInherit(models.Model):
    _inherit = 'amp.approval'

    @api.depends('x_model', 'x_model_id')
    def _compute_reference_text(self):
        super(PmrAccessAmpApprovalInherit, self)._compute_reference_text()
        for approval in self:
            if approval.x_model == 'pmr.itms.user.access':
                access = self.env['pmr.itms.user.access'].browse(approval.x_model_id)
                approval.x_reference_text = access.display_name or ''
                

    def model_action_to_approve_action(self):
        res = super(PmrAccessAmpApprovalInherit, self).model_action_to_approve_action()
        if self.x_model == 'pmr.itms.user.access' and self.state == 'approved':
            model = self.x_model
            model_id = self.x_model_id
            access_obj = self.env[model].browse(model_id)

            if access_obj:
                access_obj.state = 'appr'
                access_obj.write({'state': 'appr'})

                self.env['pmr.itms.completion.access'].create({
                    'pmr_itms_request': access_obj.id, 
                    'pmr_approval': self.id,
                })
        return res

    def model_action_to_return_action(self):
        res = super(PmrAccessAmpApprovalInherit, self).model_action_to_return_action()
        model = self.x_model
        model_id = self.x_model_id
        model_obj = self.env[model].browse([model_id])
        if self.x_model == 'pmr.itms.user.access':
            model_obj.state = 'draft'
        return res

    def model_action_to_reject_action(self):
        res = super(PmrAccessAmpApprovalInherit, self).model_action_to_reject_action()
        model = self.x_model
        model_id = self.x_model_id
        model_obj = self.env[model].browse([model_id])
        if self.x_model == 'pmr.itms.user.access':
            model_obj.state = 'draft'
        return res

    def create_approval_log(self, params):
        res = super(PmrAccessAmpApprovalInherit, self).create_approval_log(params)
        if self.x_model == 'pmr.itms.user.access' and self.x_model_id:
            res.x_access_id = self.x_model_id
        return res

class PmraccessAmpApprovalLogInherit(models.Model):
    _inherit = 'amp.approval.log'

    x_access_id = fields.Many2one('pmr.itms.user.access', string='access Ref', copy=False)