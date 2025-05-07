from odoo import api, fields, models, _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class PmrItmsRequestTroubleshooting(models.Model):
    _name = "pmr.itms.request.troubleshooting"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Request Troubleshooting"

    name = fields.Char(string="ITMS ID", required=True, copy=False, readonly=True, default=lambda self: _("New"))
    pmr_itms_personil_it = fields.Many2one('pmr.itms.personil.it', string="IT Personnel", store=True)
    pmr_waiting_note = fields.Text(string="Waiting Note", related="pmr_itms_completion.pmr_waiting_note")
    pmr_itms_request_line_ids_ass_1  = fields.One2many('pmr.itms.request.memo.pembelian.troubleshooting','pmr_itms_request_head_1', tracking=10)
    pmr_itms_departement = fields.Many2one('hr.department', string="Departement", required=True, store=True)
    pmr_itms_user = fields.Many2one('pmr.itms.user', string="User", required=True, store=True)
    pmr_itms_request_troubleshooting = fields.Text(string="Troubleshooting Request", required=True)
    pmr_itms_completion = fields.Many2one('pmr.itms.completion.troubleshooting', string="Completion From")
    pmr_revision = fields.Boolean(string="Is this a revision ?")
    pmr_note_revisi = fields.Text(string="Revision Note")
    x_approval_id = fields.Many2one('amp.approval', string='Approval Ref', copy=False)
    x_approval_state = fields.Selection(default='open',
                                        string='Approval Status', related='x_approval_id.state', store=True,
                                        readonly=False)
    x_approval_log_ids = fields.One2many('amp.approval.log', 'x_itms_id', string='Approval Logs', copy=False)

    def action_create_item_request(self):
        """Membuka tampilan form permintaan item baru dengan data yang telah diisi sebelumnya."""
        self.ensure_one()

        default_lines = []
        for line in self.pmr_itms_request_line_ids_ass_1:
            default_lines.append((0, 0, {
                'pmr_itms_product': f'{line.pmr_itms_product._name},{line.pmr_itms_product.id}' if line.pmr_itms_product else False,
                # 'pmr_item_category': line.pmr_item_category,
                'pmr_itms_jumlah': line.pmr_itms_jumlah,
                'pmr_itms_uom': line.pmr_itms_uom.id,
                'pmr_note': line.pmr_note,
            }))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Item Request',
            'res_model': 'pmr.itms.memo.pengajuan.barang',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {
                'default_pmr_itms_personil_it': self.pmr_itms_personil_it.id,
                'default_pmr_itms_user': self.pmr_itms_user.id,
                'default_pmr_itms_departement_user': self.pmr_itms_departement.id,
                'default_pmr_itms_departement': self.pmr_itms_departement.id,
                'default_pmr_itms_memo_line_ids': default_lines,
            },
        }
        
    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self._generate_sequence()
        return super(PmrItmsRequestTroubleshooting, self).create(vals)

    def _generate_sequence(self):
        """Generate a unique sequence based on year, month, and existing records."""
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month

        prefix = "REQ/TROUBLE"
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

    pmr_itms_attach = fields.Html(string="Attachment")
    pmr_itms_request_date = fields.Datetime(
        string="Request Date", 
        required=True, 
        default=lambda self: fields.Datetime.now()
    )
    itms_status = [
        ('draft', 'Draft'),
        ('open', 'Waiting for Approval'),
        ('appr', 'Approved'),
        ('waiting', 'Waiting'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('completed', 'Completed'),
        ('cancel', 'Cancelled'),
    ]
    state = fields.Selection(itms_status, string="Status", default="draft", compute="_get_itms_status",inverse="_inverse_itms_status",
                                store=True, copy=False, tracking=True)
    x_currency_id = fields.Many2one("res.currency", string="Currency",
                                    default=lambda self: self.env.company.currency_id)
    x_approval_active = fields.Boolean(string='Active ITMS Approval', compute='_compute_approval_active_data', store=True)

    MAPPING_ITMS_APPROVAL_SETTINGS = {
        'ITMS_Trial': {'approval_required': False, 'setting_param': None, 'sequence_code': None},
        'ITMS': {'approval_required': True, 'setting_param': 'pmr_imts.approval.setting.itms', 'sequence_code': 'itms.approval.sequence'},
        'default': {'approval_required': True, 'setting_param': 'pmr_itms.approval.setting.itms', 'sequence_code': 'itms.approval.sequence'},
    }
    
    pmr_itms_re_to_it = fields.Many2one('pmr.itms.role', string="Request To")

    pmr_itms_category = fields.Selection([
        ('software_odoo', 'Software Odoo'), 
        ('software_non_odoo', 'Software Non Odoo'),
        ('website','Website'),
        ('email', 'E-Mail'), 
        ('Network', 'Network'),
        ('hardware', 'Hardware'), 
    ], string="Category", store=True, required=True)

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
            record.x_approval_active = int(self.env['ir.config_parameter'].sudo().get_param('pmr_itms.active.itms.approval', 1))

    def _inverse_itms_status(self):
        pass
    
    @api.onchange('pmr_itms_personil_it')
    def _onchange_pmr_itms_personil_it(self):
        if self.pmr_itms_personil_it:
            self.pmr_itms_re_to_it = self.pmr_itms_personil_it.role_it
        else:
            self.pmr_itms_re_to_it = False

    @api.onchange('pmr_itms_user')
    def _onchange_pmr_itms_user(self):
        if self.pmr_itms_user:
            self.pmr_itms_departement = self.pmr_itms_user.department_id
        else:
            self.pmr_itms_departement = False  

    @api.depends('x_approval_state')
    def _get_itms_status(self):
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
                'setting_param': 'pmr_itms.approval.setting.itms',
                'sequence_code': 'itms.approval.sequence'
            }

            if not approval_settings['approval_required']:
                rec.state = 'appr'
                rec.x_approval_state = 'approved'
            else:
                rec.state = 'open'
                active_itms_approval = int(rec.env['ir.config_parameter'].sudo().get_param('pmr_itms.active.itms.approval', 1))
                if active_itms_approval:
                    rec.create_or_update_approval_itms(approval_settings['setting_param'], approval_settings['sequence_code'])
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
    
    def create_approval_from_itms(self, setting_param, sequence_code):
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
            'model': 'pmr.itms.request.troubleshooting',
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

    def update_approval_from_itms(self, approval_obj, setting_param):
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
            'model': 'pmr.itms.request.troubleshooting',
            'approval_setting_id': approval_setting_id,
            'submitter_id': submitter_id,
            'external_approver': external_approver, 
            'approval_note': approval_note,  
            'desc': detail_desc,
        }

        approval_obj.sudo()._synchronize_approval_data(data)
        self.x_approval_id = approval_obj

    def create_or_update_approval_itms(self, setting_param, sequence_code):
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

        existing_approval_itms = self.env['amp.approval'].search([
            ('x_model', '=', 'pmr.itms.request.troubleshooting'),
            ('x_model_id', '=', self.id),
            ('x_approval_setting_id', '=', approval_setting_id),
        ])

        if not existing_approval_itms:
            self.create_approval_from_itms(setting_param, sequence_code)
        else:
            self.update_approval_from_itms(existing_approval_itms, setting_param)

class PmrItmsAmpApprovalInherit(models.Model):
    _inherit = 'amp.approval'

    @api.depends('x_model', 'x_model_id')
    def _compute_reference_text(self):
        super(PmrItmsAmpApprovalInherit, self)._compute_reference_text()
        for approval in self:
            if approval.x_model == 'pmr.itms.request.troubleshooting':
                itms = self.env['pmr.itms.request.troubleshooting'].browse(approval.x_model_id)
                approval.x_reference_text = itms.display_name or ''
                

    def model_action_to_approve_action(self):
        res = super(PmrItmsAmpApprovalInherit, self).model_action_to_approve_action()
        if self.x_model == 'pmr.itms.request.troubleshooting' and self.state == 'approved':
            model = self.x_model
            model_id = self.x_model_id
            itms_obj = self.env[model].browse(model_id)

            if itms_obj:
                itms_obj.state = 'appr'
                itms_obj.write({'state': 'appr'})

                self.env['pmr.itms.completion.troubleshooting'].create({
                    'pmr_itms_request': itms_obj.id, 
                    'pmr_approval': self.id,
                })
        return res

    def model_action_to_return_action(self):
        res = super(PmrItmsAmpApprovalInherit, self).model_action_to_return_action()
        model = self.x_model
        model_id = self.x_model_id
        model_obj = self.env[model].browse([model_id])
        if self.x_model == 'pmr.itms.request.troubleshooting':
            model_obj.state = 'draft'
        return res

    def model_action_to_reject_action(self):
        res = super(PmrItmsAmpApprovalInherit, self).model_action_to_reject_action()
        model = self.x_model
        model_id = self.x_model_id
        model_obj = self.env[model].browse([model_id])
        if self.x_model == 'pmr.itms.request.troubleshooting':
            model_obj.state = 'draft'
        return res

    def create_approval_log(self, params):
        res = super(PmrItmsAmpApprovalInherit, self).create_approval_log(params)
        if self.x_model == 'pmr.itms.request.troubleshooting' and self.x_model_id:
            res.x_itms_id = self.x_model_id
        return res

class PmrItmsAmpApprovalLogInherit(models.Model):
    _inherit = 'amp.approval.log'

    x_itms_id = fields.Many2one('pmr.itms.request.troubleshooting', string='ITMS Ref', copy=False)

class PmrItmsRequestMemoPembelianTroubleshooting(models.Model):
    _name = "pmr.itms.request.memo.pembelian.troubleshooting"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Request Memo Pembelian Troubleshooting"
    
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
    pmr_itms_request_head_1 = fields.Many2one('pmr.itms.request.troubleshooting', string="ID Memo")
    pmr_itms_memo_head_1_char = fields.Char(string="Memo")
    pmr_itms_product_text = fields.Text(string="Product Description")
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
