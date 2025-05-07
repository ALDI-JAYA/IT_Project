from odoo import api, fields, models, _
from datetime import datetime

class PmrItmsPaniteraAsset(models.Model):
    _name = "pmr.itms.panitera.asset"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr asset Panitera Asset"

    pmr_itis_req_asset = fields.Selection([
        ('permintaan_aktiva_tetap_baru', 'Permintaan aktiva tetap Baru'), 
        ('disposal_aktiva_tetap', 'Disposal aktiva tetap'), 
        ], string='Request Asset', tracking=True)
    pmr_asset_number = fields.Many2one('asset.number.it', string="Asset Number")
    pmr_itms_request_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    name = fields.Char(string="Name", required=True, copy=False, readonly=True, default=lambda self: _("New"))
    pmr_itis_no_doc = fields.Char(string="Document No", required=True, copy=False, readonly=True, default=lambda self: _("New"))
    pmr_itis_code_fisik = fields.Char(string="Physical Code", required=True, copy=False, readonly=True, default=lambda self: _("New"))
    pmr_itis_fixed_asset_code = fields.Char(string="Fixed asset code")
    pmr_itis_unit_category = fields.Many2one('pmr.category.unit', string="Unit Category")
    pmr_itis_fixed_asset_code = fields.Char(string="Serial Number")
    pmr_itis_jenis_unit = fields.Many2one('pmr.jenis.unit',string="Unit Type")
    pmr_asset_user = fields.Many2one('pmr.itms.user', string="User", required=True)
    pmr_asset_departement_user = fields.Many2one('hr.department', string="Departement", required=True)
    pmr_location = fields.Many2one('res.company',string="Location" , default=1)
    pmr_itis_description = fields.Char(string="Description")
    pmr_itms_personil_it = fields.Many2one('pmr.itms.personil.it', string="IT Personnel", store=True)
    pmr_itms_panset  = fields.One2many('pmr.itms.panitera.asset.line','pmr_itms_panset_line', tracking=10)
    x_pr_account_expense_id = fields.Many2one(
        'account.account', 
        string='Expense Account', 
        default=370
    )

    def action_generate_asset_number(self):
        """ Generate and assign asset number with the format 402ITTXXXX """
        prefix = "402ITT"

        last_asset = self.env['asset.number.it'].search([], order="pmr_create_date desc, id desc", limit=1)
        
        if last_asset:
            last_seq = int(last_asset.name[-4:]) 
        else:
            last_seq = 259  

        new_seq = last_seq + 1
        new_asset_number = f"{prefix}{new_seq:04d}"

        asset_record = self.env['asset.number.it'].create({'name': new_asset_number})

        self.pmr_asset_number = asset_record.id

        asset_lines = []
        for line in self.pmr_itms_panset:
            asset_lines.append((0, 0, {
                'pmr_itis_product': line.pmr_itis_product,
                'pmr_itis_po_number': line.pmr_itis_po_number.id,
                'pmr_quantity_product_it': line.pmr_quantity_product_it,
                'product_unit_category': line.product_unit_category.id,
                'pmr_itms_panset_line': asset_record.id,  
            }))

        asset_record.pmr_itms_panset = asset_lines

        return {
            'effect': {
                'fadeout': 'slow',
                'message': f'Nomor aset berhasil dibuat: {new_asset_number}',
                'type': 'rainbow_man',
            }
        }

    @api.onchange('pmr_asset_user')
    def _onchange_pmr_asset_user(self):
        if self.pmr_asset_user:
            self.pmr_asset_departement_user = self.pmr_asset_user.department_id
        else:
            self.pmr_asset_departement_user = False

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self._generate_sequence()
        return super(PmrItmsPaniteraAsset, self).create(vals)

    def _generate_sequence(self):
        """Generate a unique sequence based on year, month, and existing records."""
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month

        prefix = "AKTV/IT"
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
    x_approval_log_ids = fields.One2many('amp.approval.log', 'x_asset_id', string='Approval Logs', copy=False)
    asset_status = [
        ('draft', 'Draft'),
        ('open', 'Waiting for Approval'),
        ('appr', 'Approved'),
        ('cancel', 'Cancelled'),
    ]
    state = fields.Selection(asset_status, string="Status", default="draft", compute="_get_asset_status",inverse="_inverse_asset_status",
                                store=True, copy=False, tracking=True)
    x_currency_id = fields.Many2one("res.currency", string="Currency",
                                    default=lambda self: self.env.company.currency_id)
    x_approval_active = fields.Boolean(string='Active asset Approval', compute='_compute_approval_active_data', store=True)

    MAPPING_asset_APPROVAL_SETTINGS = {
        'asset_Trial': {'approval_required': False, 'setting_param': None, 'sequence_code': None},
        'asset': {'approval_required': True, 'setting_param': 'pmr_imts.approval.setting.asset', 'sequence_code': 'asset.approval.sequence'},
        'default': {'approval_required': True, 'setting_param': 'pmr_asset.approval.setting.asset', 'sequence_code': 'asset.approval.sequence'},
    }
    pmr_asset_re_to = fields.Selection([
        ('it_support', 'IT Support'), 
        ('it_programmer', 'IT Programmer'),
        ], string='Request To', store=True)

    pmr_asset_category = fields.Selection([
        ('software_odoo', 'Software Odoo'), 
        ('software_non_odoo', 'Software Non Odoo'),
        ('website','Website'),
        ('email', 'E-Mail'), 
        ('Network', 'Network'),
        ('hardware', 'Hardware'), 
    ], string="Category", store=True)

    def action_cancel(self):
        self.state= 'cancel'

    def action_completed(self):
        self.state= 'completed'
        for rec in self :
            rec.pmr_asset_completion.state = 'completed'
    
    def action_in_progress(self):
        self.state= 'in_progress'
        for rec in self :
            rec.pmr_asset_completion.state = 'draft'
            self.state= 'in_progress'

    def _compute_approval_active_data(self):
        for record in self:
            record.x_approval_active = int(self.env['ir.config_parameter'].sudo().get_param('pmr_asset.active.asset.approval', 1))

    def _inverse_asset_status(self):
        pass

    @api.depends('x_approval_state')
    def _get_asset_status(self):
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
                'setting_param': 'pmr_asset.approval.setting.asset',
                'sequence_code': 'asset.approval.sequence'
            }

            if not approval_settings['approval_required']:
                rec.state = 'appr'
                rec.x_approval_state = 'approved'
            else:
                rec.state = 'open'
                active_asset_approval = int(rec.env['ir.config_parameter'].sudo().get_param('pmr_asset.active.asset.approval', 1))
                if active_asset_approval:
                    rec.create_or_update_approval_asset(approval_settings['setting_param'], approval_settings['sequence_code'])
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
    
    def create_approval_from_asset(self, setting_param, sequence_code):
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
            'model': 'pmr.itms.panitera.asset',
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

    def update_approval_from_asset(self, approval_obj, setting_param):
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
            'model': 'pmr.itms.panitera.asset',
            'approval_setting_id': approval_setting_id,
            'submitter_id': submitter_id,
            'external_approver': external_approver, 
            'approval_note': approval_note,  
            'desc': detail_desc,
        }

        approval_obj.sudo()._synchronize_approval_data(data)
        self.x_approval_id = approval_obj

    def create_or_update_approval_asset(self, setting_param, sequence_code):
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

        existing_approval_asset = self.env['amp.approval'].search([
            ('x_model', '=', 'pmr.itms.panitera.asset'),
            ('x_model_id', '=', self.id),
            ('x_approval_setting_id', '=', approval_setting_id),
        ])

        if not existing_approval_asset:
            self.create_approval_from_asset(setting_param, sequence_code)
        else:
            self.update_approval_from_asset(existing_approval_asset, setting_param)

class PmrItmsAmpApprovalInherit(models.Model):
    _inherit = 'amp.approval'

    @api.depends('x_model', 'x_model_id')
    def _compute_reference_text(self):
        super(PmrItmsAmpApprovalInherit, self)._compute_reference_text()
        for approval in self:
            if approval.x_model == 'pmr.itms.panitera.asset':
                asset = self.env['pmr.itms.panitera.asset'].browse(approval.x_model_id)
                approval.x_reference_text = asset.display_name or ''
                
    def model_action_to_approve_action(self):
        res = super(PmrItmsAmpApprovalInherit, self).model_action_to_approve_action()
        if self.x_model == 'pmr.itms.panitera.asset' and self.state == 'approved':
            model = self.x_model
            model_id = self.x_model_id
            khj_obj = self.env[model].browse([model_id])
            khj_obj.state = 'appr'
        return res

    def model_action_to_return_action(self):
        res = super(PmrItmsAmpApprovalInherit, self).model_action_to_return_action()
        model = self.x_model
        model_id = self.x_model_id
        model_obj = self.env[model].browse([model_id])
        if self.x_model == 'pmr.itms.panitera.asset':
            model_obj.state = 'draft'
        return res

    def model_action_to_reject_action(self):
        res = super(PmrItmsAmpApprovalInherit, self).model_action_to_reject_action()
        model = self.x_model
        model_id = self.x_model_id
        model_obj = self.env[model].browse([model_id])
        if self.x_model == 'pmr.itms.panitera.asset':
            model_obj.state = 'draft'
        return res

    def create_approval_log(self, params):
        res = super(PmrItmsAmpApprovalInherit, self).create_approval_log(params)
        if self.x_model == 'pmr.itms.panitera.asset' and self.x_model_id:
            res.x_asset_id = self.x_model_id
        return res

class PmrassetAmpApprovalLogInherit(models.Model):
    _inherit = 'amp.approval.log'

    x_asset_id = fields.Many2one('pmr.itms.panitera.asset', string='Asset Ref', copy=False)

class PmrItmsPaniteraAssetLine(models.Model):
    _name = "pmr.itms.panitera.asset.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr asset Panitera Asset Line"

    pmr_itis_product = fields.Char(string="Item")
    pmr_itis_po_number = fields.Many2one('purchase.order',string="PO Number")
    pmr_quantity_product_it = fields.Float(string="Quantity",required=True)
    product_unit_category = fields.Many2one('uom.uom', string="Uom", required=True, store=True)
    pmr_itms_panset_line = fields.Many2one('pmr.itms.panitera.asset', string="ID Memo", store=True)
