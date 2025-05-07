from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError

class PmrItmsHandoverIt(models.Model):
    _name = "pmr.itms.handover.it"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Handover"

    name = fields.Char(string="Name", required=True, copy=False, readonly=True, default=lambda self: _("New"))
    pmr_itms_handover_head  = fields.One2many('pmr.itms.handover.it.line','pmr_itms_handover', tracking=10)

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self._generate_sequence()
        return super(PmrItmsHandoverIt, self).create(vals)

    def _generate_sequence(self):
        """Generate a unique sequence based on year, month, and existing records."""
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month

        prefix = "HANDOVER"
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
    pmr_itms_re_to_it = fields.Many2one('pmr.itms.role', string="Role")
    pmr_itms_user = fields.Many2one('pmr.itms.user', string="User", required=True, store=True)
    pmr_itms_to_to_it = fields.Many2one('pmr.itms.role', string="Role")
    pmr_itms_departement = fields.Many2one('hr.department', string="Departement", required=True, store=True)

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

    pmr_no_handover = fields.Char(string="Nomor Asset")

    x_approval_id = fields.Many2one('amp.approval', string='Approval Ref', copy=False)
    x_approval_state = fields.Selection(default='open',
                                        string='Approval Status', related='x_approval_id.state', store=True,
                                        readonly=False)
    x_approval_log_ids = fields.One2many('amp.approval.log', 'x_handover_id', string='Approval Logs', copy=False)
    handover_status = [
        ('draft', 'Draft'),
        ('user_agreement', 'User Aggreement'),
        ('submit', 'Submit'),
        ('open', 'Waiting for Approval'),
        ('appr', 'Approved'),
        ('cancel', 'Cancelled'),
    ]
    state = fields.Selection(handover_status, string="Status", default="draft", compute="_get_handover_status",inverse="_inverse_handover_status",
                                store=True, copy=False, tracking=True)
    x_currency_id = fields.Many2one("res.currency", string="Currency",
                                    default=lambda self: self.env.company.currency_id)
    x_approval_active = fields.Boolean(string='Active handover Approval', compute='_compute_approval_active_data', store=True)

    MAPPING_handover_APPROVAL_SETTINGS = {
        'handover_Trial': {'approval_required': False, 'setting_param': None, 'sequence_code': None},
        'handover': {'approval_required': True, 'setting_param': 'pmr_imts.approval.setting.handover', 'sequence_code': 'handover.approval.sequence'},
        'default': {'approval_required': True, 'setting_param': 'pmr_itms.approval.setting.handover', 'sequence_code': 'handover.approval.sequence'},
    }

    def action_user(self):
        self.state= 'user_agreement'
    
    def action_user_submit(self):
        self.state= 'submit'

    def action_cancel(self):
        self.state= 'cancel'

    def action_completed(self):
        self.state= 'completed'
        for rec in self :
            rec.pmr_handover_completion.state = 'completed'
    
    def action_in_progress(self):
        self.state= 'in_progress'
        for rec in self :
            rec.pmr_handover_completion.state = 'submit'
            self.state= 'in_progress'

    def _compute_approval_active_data(self):
        for record in self:
            record.x_approval_active = int(self.env['ir.config_parameter'].sudo().get_param('pmr_itms.active.handover.approval', 1))

    def _inverse_handover_status(self):
        pass

    @api.depends('x_approval_state')
    def _get_handover_status(self):
        for rec in self:
            if rec.x_approval_state == 'approved':
                rec.state = 'appr'
            elif rec.x_approval_state in ['waiting']:
                rec.state = 'open'
            else:
                rec.state = 'submit'

    def action_submit(self):
        for rec in self:
            approval_settings = {
                'approval_required': True,
                'setting_param': 'pmr_itms.approval.setting.handover',
                'sequence_code': 'handover.approval.sequence'
            }

            if not approval_settings['approval_required']:
                rec.state = 'appr'
                rec.x_approval_state = 'approved'
            else:
                rec.state = 'open'
                active_handover_approval = int(rec.env['ir.config_parameter'].sudo().get_param('pmr_itms.active.handover.approval', 1))
                if active_handover_approval:
                    rec.create_or_update_approval_handover(approval_settings['setting_param'], approval_settings['sequence_code'])
                else:
                    rec.x_approval_state = 'approved'


    def action_reset_to_submit(self):
        for rec in self:
            rec.state = 'submit'
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
    
    def create_approval_from_handover(self, setting_param, sequence_code):
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
            'model': 'pmr.itms.handover.it',
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

    def update_approval_from_handover(self, approval_obj, setting_param):
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
            'model': 'pmr.itms.handover.it',
            'approval_setting_id': approval_setting_id,
            'submitter_id': submitter_id,
            'external_approver': external_approver, 
            'approval_note': approval_note,  
            'desc': detail_desc,
        }

        approval_obj.sudo()._synchronize_approval_data(data)
        self.x_approval_id = approval_obj

    def create_or_update_approval_handover(self, setting_param, sequence_code):
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

        existing_approval_handover = self.env['amp.approval'].search([
            ('x_model', '=', 'pmr.itms.handover.it'),
            ('x_model_id', '=', self.id),
            ('x_approval_setting_id', '=', approval_setting_id),
        ])

        if not existing_approval_handover:
            self.create_approval_from_handover(setting_param, sequence_code)
        else:
            self.update_approval_from_handover(existing_approval_handover, setting_param)

class PmrItmsAmpApprovalInherit(models.Model):
    _inherit = 'amp.approval'

    @api.depends('x_model', 'x_model_id')
    def _compute_reference_text(self):
        super(PmrItmsAmpApprovalInherit, self)._compute_reference_text()
        for approval in self:
            if approval.x_model == 'pmr.itms.handover.it':
                handover = self.env['pmr.itms.handover.it'].browse(approval.x_model_id)
                approval.x_reference_text = handover.display_name or ''
                
    def model_action_to_approve_action(self):
        res = super(PmrItmsAmpApprovalInherit, self).model_action_to_approve_action()
        if self.x_model == 'pmr.itms.handover.it' and self.state == 'approved':
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
        if self.x_model == 'pmr.itms.handover.it':
            model_obj.state = 'submit'
        return res

    def model_action_to_reject_action(self):
        res = super(PmrItmsAmpApprovalInherit, self).model_action_to_reject_action()
        model = self.x_model
        model_id = self.x_model_id
        model_obj = self.env[model].browse([model_id])
        if self.x_model == 'pmr.itms.handover.it':
            model_obj.state = 'submit'
        return res

    def create_approval_log(self, params):
        res = super(PmrItmsAmpApprovalInherit, self).create_approval_log(params)
        if self.x_model == 'pmr.itms.handover.it' and self.x_model_id:
            res.x_handover_id = self.x_model_id
        return res

class PmrHandoverAmpApprovalLogInherit(models.Model):
    _inherit = 'amp.approval.log'

    x_handover_id = fields.Many2one('pmr.itms.handover.it', string='handover Ref', copy=False)

class PmrItmsHandoverItLine(models.Model):
    _name = "pmr.itms.handover.it.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Handover Line"

    pmr_itms_handover = fields.Many2one('pmr.itms.handover.it', string="ID Memo")
    pmr_jenis_perangkat = fields.Text(string="Item")
    pmr_merk_type = fields.Char(string="Merk/Type")
    pmr_quantity_product_it = fields.Float(string="Quantity",required=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)

class StocPickingInherit(models.Model):
    _inherit = 'stock.picking'
    
    pmr_state_handover = fields.Selection([
        ('create', 'Create'), 
        ('send', 'Send'), 
        ], string='Handover Type', tracking=True)
    pmr_asset_number = fields.Many2one('pmr.itms.panitera.asset', string="ID Asset")

    def action_create_handover_it(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Handover From GRN',
            'res_model': 'handover.from.grn',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_picking_id': self.id},
        }
    
    def action_create_item_handover(self):
        default_lines = []
        
        for picking in self: 
            for line in picking.move_ids_without_package:
                default_lines.append((0, 0, {
                    'pmr_jenis_perangkat': line.description_picking,
                    'product_unit_category': line.product_uom.id,
                    'pmr_quantity_product_it': line.quantity_done
                }))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Item Handover',
            'res_model': 'pmr.itms.handover.it',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {
                'default_pmr_itms_handover_head': default_lines,
            },
        }

class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    pmr_item_category = fields.Selection([
        ('pc_laptop', 'PC/Laptop'), 
        ('printer', 'Printer'),
        ('router','Router'),
        ('wifi', 'Wifi'), 
        ('switch', 'Switch'),
        ('motherboard', 'Motherboard'), 
        ('expansion_slot', 'Expansion Slot'),
        ('power_supply', 'Power Supply'),
        ('casing', 'Casing'),
        ('keyboard', 'Keyboard'),
        ('mouse', 'Mouse'),
        ('monitor', 'Monitor'),
        ('processor', 'Processor'),
        ('hardisk', 'Hardisk'),
        ('ram', 'RAM'),
        ('vga', 'VGA'),
        ('antivirus', 'Antivirus'),
        ('office', 'Office'),
        ('os', 'Operating System'),
        ('cad', 'CAD'),
        ('cam', 'CAM'),
        ('software_lain', 'Software Lain Lain'),
    ], string="Item Category")
    
    def action_create_item_inventory(self):
        self.ensure_one()  

        model_map = {
            'pc_laptop': 'pmr.itms.product.it',
            'printer': 'pmr.itms.product.it.printer',
            'router': 'pmr.itms.product.it.router',
            'wifi': 'pmr.itms.product.it.wifi',
            'switch': 'pmr.itms.product.it.switch',
            'motherboard': 'pmr.mainboard',
            'expansion_slot': 'pmr.fdd',
            'power_supply': 'pmr.power.supply',
            'casing': 'pmr.casing',
            'keyboard': 'pmr.keyboard',
            'mouse': 'pmr.mouse',
            'monitor': 'pmr.monitor',
            'processor': 'pmr.processor',
            'hardisk': 'pmr.hardisk',
            'ram': 'pmr.ram',
            'vga': 'pmr.vga',
            'antivirus': 'pmr.antivirus',
            'office': 'pmr.office',
            'os': 'pmr.os',
            'cad': 'pmr.cad',
            'cam': 'pmr.cam',
            'software_lain': 'pmr.software.lain',
        }

        res_model = model_map.get(self.pmr_item_category)
        if not res_model:
            return False  

        default_values = { 
            'name': self.description_picking,
            'pmr_quantity_product_it': self.quantity_done or 0.0,
            'product_unit_category': self.product_uom.id if self.product_uom else False,
            'pmr_create_date': self.pmr_a_x_trans_dttm or fields.Datetime.now(),
        }

        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Item Inventory',
            'res_model': res_model,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new', 
            'context': {'default_' + key: value for key, value in default_values.items()},
        }


