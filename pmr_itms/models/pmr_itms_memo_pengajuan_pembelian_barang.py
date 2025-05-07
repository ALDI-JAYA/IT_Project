from odoo import api, fields, models, _
from datetime import datetime

class AmpPurchaseRequestInherit(models.Model):
    _inherit = 'amp.purchase.request'

    pmr_itms_memo = fields.Many2one('pmr.itms.memo.pengajuan.barang', string="Memo User")
    pmr_itms_product = fields.Char(string="Item Name")

    def action_submit(self):
        result = super(AmpPurchaseRequestInherit, self).action_submit()

        for record in self:
            if record.pmr_itms_memo:
                memo_lines = record.pmr_itms_memo.pmr_itms_memo_line_ids.filtered(
                    lambda line: line.pmr_itms_product == record.pmr_itms_product
                )
                if memo_lines:
                    memo_lines.write({
                        'pmr_validation_pr': self.name,
                        'pmr_validation_pr_id': record.id
                    })

        return result

class PmrItmsMemoPengajuanBarang(models.Model):
    _name = "pmr.itms.memo.pengajuan.barang"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Memo Pengajuan Barang"

    name = fields.Char(string="ITMS ID", required=True, copy=False, readonly=True, default=lambda self: _("New"))
    request_type = fields.Selection([
        ('demand', 'Demand'),
        ('purchase', 'Purchase'),
    ], string="Request Type", tracking=True, store=True)

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self._generate_sequence()
        return super(PmrItmsMemoPengajuanBarang, self).create(vals)

    def _generate_sequence(self):
        """Generate a unique sequence based on year, month, and existing records."""
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month

        prefix = "PR/MEMO"
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

    pmr_itms_personil_it = fields.Many2one('pmr.itms.personil.it', string="IT Personnel", store=True)
    pmr_itms_departement = fields.Many2one('hr.department', string="Departement", required=True, store=True)
    pmr_itms_request_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_itms_user = fields.Many2one('pmr.itms.user', string="User", required=True, store=True)
    pmr_itms_departement_user = fields.Many2one('hr.department', string="Departement", required=True, store=True)
    pmr_itms_memo_line_ids  = fields.One2many('pmr.itms.memo.pengajuan.barang.line','pmr_itms_memo_head', tracking=10)
    x_approval_id = fields.Many2one('amp.approval', string='Approval Ref', copy=False, store=True)
    x_approval_state = fields.Selection(default='open',
                                        string='Approval Status', related='x_approval_id.state', store=True,
                                        readonly=False)
    @api.onchange('pmr_itms_user')
    def _onchange_pmr_itms_user(self):
        if self.pmr_itms_user:
            self.pmr_itms_departement = self.pmr_itms_user.department_id
        else:
            self.pmr_itms_departement = False 

    x_approval_log_ids = fields.One2many('amp.approval.log', 'x_memo_id', string='Approval Logs', copy=False)
    memo_status = [
        ('draft', 'Draft'),
        ('open', 'Waiting for Approval'),
        ('appr', 'Approved'),
        ('in_user', 'In User'),
        ('return', 'Return To IT'),
        ('cancel', 'Cancelled')
    ]
    state = fields.Selection(memo_status, string="Status", default="draft", compute="_get_memo_status",inverse="_inverse_memo_status",
                                store=True, copy=False, tracking=True)
    x_currency_id = fields.Many2one("res.currency", string="Currency",
                                    default=lambda self: self.env.company.currency_id)
    x_approval_active = fields.Boolean(string='Active ITMS Approval', compute='_compute_approval_active_data', store=True)

    MAPPING_ITMS_APPROVAL_SETTINGS = {
        'ITMS_Trial': {'approval_required': False, 'setting_param': None, 'sequence_code': None},
        'ITMS': {'approval_required': True, 'setting_param': 'pmr_itms.approval.setting.memo', 'sequence_code': 'memo.approval.sequence'},
        'default': {'approval_required': True, 'setting_param': 'pmr_itms.approval.setting.memo', 'sequence_code': 'memo.approval.sequence'},
    }
    pmr_memo_re_to = fields.Selection([
        ('it_support', 'IT Support'), 
        ('it_programmer', 'IT Programmer'),
        ], string='Request To', store=True)

    def action_cancel(self):
        self.state= 'cancel'

    def _compute_approval_active_data(self):
        for record in self:
            record.x_approval_active = int(self.env['ir.config_parameter'].sudo().get_param('pmr_itms.active.memo.approval', 1))

    def _inverse_memo_status(self):
        pass

    @api.depends('x_approval_state')
    def _get_memo_status(self):
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
                'setting_param': 'pmr_itms.approval.setting.memo',
                'sequence_code': 'memo.approval.sequence'
            }

            if not approval_settings['approval_required']:
                rec.state = 'appr'
                rec.x_approval_state = 'approved'
            else:
                rec.state = 'open'
                active_memo_approval = int(rec.env['ir.config_parameter'].sudo().get_param('pmr_itms.active.memo.approval', 1))
                if active_memo_approval:
                    rec.create_or_update_approval_memo(approval_settings['setting_param'], approval_settings['sequence_code'])
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
    
    def create_approval_from_memo(self, setting_param, sequence_code):
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
            'model': 'pmr.itms.memo.pengajuan.barang',
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

    def update_approval_from_memo(self, approval_obj, setting_param):
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
            'model': 'pmr.itms.memo.pengajuan.barang',
            'approval_setting_id': approval_setting_id,
            'submitter_id': submitter_id,
            'external_approver': external_approver, 
            'approval_note': approval_note,  
            'desc': detail_desc,
        }

        approval_obj.sudo()._synchronize_approval_data(data)
        self.x_approval_id = approval_obj

    def create_or_update_approval_memo(self, setting_param, sequence_code):
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

        existing_approval_memo = self.env['amp.approval'].search([
            ('x_model', '=', 'pmr.itms.memo.pengajuan.barang'),
            ('x_model_id', '=', self.id),
            ('x_approval_setting_id', '=', approval_setting_id),
        ])

        if not existing_approval_memo:
            self.create_approval_from_memo(setting_param, sequence_code)
        else:
            self.update_approval_from_memo(existing_approval_memo, setting_param)

class PmrItmsMemoAmpApprovalInherit(models.Model):
    _inherit = 'amp.approval'

    @api.depends('x_model', 'x_model_id')
    def _compute_reference_text(self):
        super(PmrItmsMemoAmpApprovalInherit, self)._compute_reference_text()
        for approval in self:
            if approval.x_model == 'pmr.itms.memo.pengajuan.barang':
                itms = self.env['pmr.itms.memo.pengajuan.barang'].browse(approval.x_model_id)
                approval.x_reference_text = itms.display_name or ''
                
    def model_action_to_approve_action(self):
        res = super(PmrItmsMemoAmpApprovalInherit, self).model_action_to_approve_action()
        if self.x_model == 'pmr.itms.memo.pengajuan.barang' and self.state == 'approved':
            model = self.x_model
            model_id = self.x_model_id
            khj_obj = self.env[model].browse([model_id])
            khj_obj.state = 'appr'
        return res

    def model_action_to_return_action(self):
        res = super(PmrItmsMemoAmpApprovalInherit, self).model_action_to_return_action()
        model = self.x_model
        model_id = self.x_model_id
        model_obj = self.env[model].browse([model_id])
        if self.x_model == 'pmr.itms.memo.pengajuan.barang':
            model_obj.state = 'draft'
        return res

    def model_action_to_reject_action(self):
        res = super(PmrItmsMemoAmpApprovalInherit, self).model_action_to_reject_action()
        model = self.x_model
        model_id = self.x_model_id
        model_obj = self.env[model].browse([model_id])
        if self.x_model == 'pmr.itms.memo.pengajuan.barang':
            model_obj.state = 'draft'
        return res

    def create_approval_log(self, params):
        res = super(PmrItmsMemoAmpApprovalInherit, self).create_approval_log(params)
        if self.x_model == 'pmr.itms.memo.pengajuan.barang' and self.x_model_id:
            res.x_memo_id = self.x_model_id
        return res

class PmrItmsMemoAmpApprovalLogInherit(models.Model):
    _inherit = 'amp.approval.log'

    x_memo_id = fields.Many2one('pmr.itms.memo.pengajuan.barang', string='ITMS Ref', copy=False)

class PmrItmsMemoPengajuanBarangLine(models.Model):
    _name = "pmr.itms.memo.pengajuan.barang.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Memo Pengajuan Barang"

    name = fields.Char(string="Memo Name", compute="_compute_name", store=True)
    # pmr_itms_product = fields.Many2one('pmr.vga',string="Item Name")
    pmr_itms_product = fields.Reference(selection=[
        ('pmr.pc', 'pc'),
        ('pmr.wifi', 'WiFi'),
        ('pmr.switch', 'Switch'),
        ('pmr.router', 'Router'),
        ('pmr.processor', 'Processor'),
        ('pmr.hardisk', 'Hardisk'),
        ('pmr.ram', 'RAM'),
        ('pmr.vga', 'VGA'),
        ('pmr.fdd', 'Expansion Slot'),
        ('pmr.casing', 'Casing'),
        ('pmr.keyboard', 'Keyboard'),
        ('pmr.monitor', 'Monitor'),
        ('pmr.mouse', 'Mouse'),
        ('pmr.printer', 'Printer'),
        ('pmr.mainboard', 'MotherBoard'),
        ('pmr.power.supply', 'Power Supply'),
        ('pmr.lan.card', 'Integrated LAN'),
    ], string="Item Name")
    pmr_itms_jumlah = fields.Float(string="Quantity")
    pmr_itms_uom = fields.Many2one('uom.uom', string="Uom")
    pmr_note = fields.Text(string="Note")
    pmr_itms_memo_head = fields.Many2one('pmr.itms.memo.pengajuan.barang', string="ID Memo")
    pmr_itms_product_text = fields.Text(string="Product Description")
    pmr_validation_pr_id = fields.Many2one('amp.purchase.request',string="PR")
    pmr_validation_pr = fields.Char(string="PR")
    pmr_validation_po = fields.Boolean(string="PO", compute="_compute_pmr_validation_po", store=True)

    @api.depends('pmr_validation_pr_id.x_pr_state')
    def _compute_pmr_validation_po(self):
        for line in self:
            line.pmr_validation_po = (line.pmr_validation_pr_id.x_pr_state == 'po')

    pmr_validation_grn = fields.Boolean(string="GRN", compute="_compute_pmr_validation_grn", store=True)

    @api.depends('pmr_validation_pr_id.x_pr_state')
    def _compute_pmr_validation_grn(self):
        for line in self:
            line.pmr_validation_grn = (line.pmr_validation_pr_id.x_pr_state == 'received')

    state = fields.Selection(string="state", related='pmr_itms_memo_head.state', store=True)
    request_type = fields.Selection(string="state", related='pmr_itms_memo_head.request_type', store=True)
    # pmr_item_category = fields.Selection([
    #     ('pc_laptop', 'PC/Laptop'), 
    #     ('printer', 'Printer'),
    #     ('router','Router'),
    #     ('wifi', 'Wifi'), 
    #     ('switch', 'Switch'),
    #     ('motherboard', 'Motherboard'), 
    #     ('expansion_slot', 'Expansion Slot'),
    #     ('power_supply', 'Power Supply'),
    #     ('casing', 'Casing'),
    #     ('keyboard', 'Keyboard'),
    #     ('mouse', 'Mouse'),
    #     ('monitor', 'Monitor'),
    #     ('processor', 'Processor'),
    #     ('hardisk', 'Hardisk'),
    #     ('ram', 'RAM'),
    #     ('vga', 'VGA'),
    #     ('antivirus', 'Antivirus'),
    #     ('office', 'Office'),
    #     ('os', 'Operating System'),
    #     ('cad', 'CAD'),
    #     ('cam', 'CAM'),
    #     ('software_lain', 'Software Lain Lain'),
    # ], string="Item Category", store=True)

    @api.depends('pmr_itms_memo_head')
    def _compute_name(self):
        """Compute name field based on pmr_itms_memo_head."""
        for record in self:
            record.name = record.pmr_itms_memo_head.name if record.pmr_itms_memo_head else "New"
            
    @api.onchange('pmr_itms_product')
    def _onchange_pmr_itms_product(self):
        if self.pmr_itms_product:
            self.pmr_itms_product_text = f"Product Name: {self.pmr_itms_product.name}"
        else:
            self.pmr_itms_product_text = ""

    def action_create_purchase_request(self):
        """Opens a new purchase request form view with prefilled data."""
        self.ensure_one()  

        product_name = self.pmr_itms_product if self.pmr_itms_product else ''

        memo_id = self.pmr_itms_memo_head.id if self.pmr_itms_memo_head else False

        default_values = { 
            'x_pr_product_qty': self.pmr_itms_jumlah,
            'x_pr_note': self.pmr_note,
            'pmr_itms_memo': memo_id,
            'pmr_itms_product' : self.pmr_itms_product.name,
        }

        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Purchase Request',
            'res_model': 'amp.purchase.request',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new', 
            'context': {'default_' + key: value for key, value in default_values.items()},
        }
    