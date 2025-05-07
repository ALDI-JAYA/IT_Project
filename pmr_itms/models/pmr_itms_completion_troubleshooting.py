from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError

class PmrItmsCompletionTroubleshooting(models.Model):
    _name = "pmr.itms.completion.troubleshooting"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Completion Troubleshooting"

    name = fields.Char(string="ITMS ID", required=True, copy=False, readonly=True, default=lambda self: _("New"))
    pmr_approval = fields.Many2one('amp.approval', string="Approval No", store=True)
    pmr_itms_memo_line_ids_ass_1  = fields.One2many('pmr.itms.completion.memo.pembelian.troubleshooting','pmr_itms_memo_head_1', tracking=10)
    pmr_approval_note = fields.Text(string="Approval Note", related="pmr_approval.x_approval_log_ids.x_approval_note")
    pmr_itms_request = fields.Many2one('pmr.itms.request.troubleshooting', string="Request From", store=True)
    pmr_itms_request_troubleshooting = fields.Text(string="Troubleshooting Request", related="pmr_itms_request.pmr_itms_request_troubleshooting")
    pmr_itms_personil_it = fields.Many2one('pmr.itms.personil.it', string="IT Personnel", store=True)
    pmr_itms_need_sparepart = fields.Boolean(string="Are you need component ?")
    pmr_itms_sel_sparepart = fields.Selection([
        ('pembelian', 'Pembelian'), 
        ('permintaan', 'Permintaan'),
    ], string="Category Component", store=True)
    pmr_waiting_note = fields.Text(string="Waiting Note")
    pmr_itms_memo_pembelian = fields.Many2one('pmr.itms.memo.pengajuan.barang', string="Memo User Pembelian")
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
    pmr_itms_category = fields.Selection([
        ('software_odoo', 'Software Odoo'), 
        ('software_non_odoo', 'Software Non Odoo'),
        ('website','Website'),
        ('email', 'E-Mail'), 
        ('Network', 'Network'),
        ('hardware', 'Hardware'), 
    ], string="Category", related='pmr_itms_request.pmr_itms_category')
    pmr_start_date = fields.Datetime(string="Start Date")
    pmr_end_date = fields.Datetime(string="End Date")

    def action_cancel(self):
        self.state= 'cancel'

    def action_waiting(self):
        self.state = 'waiting'
        if self.pmr_itms_request:
            self.pmr_itms_request.write({
                'state': 'waiting',
                'pmr_waiting_note': self.pmr_waiting_note  
            })
            for record in self :
                record.pmr_itms_request.pmr_itms_completion = record.id

                record.pmr_itms_request.message_post(
                    body=_("The request has been marked as Waiting by %s.<br/><strong>Note:</strong> %s") % (self.env.user.name, self.pmr_waiting_note or "No note provided."),
                    message_type='notification'
                )
    
    def action_in_progress(self):
        self.state = 'in_progress'
        if self.pmr_itms_request:
            self.pmr_itms_request.write({'state': 'in_progress'})

            for record in self :
                record.pmr_itms_request.pmr_itms_completion = record.id

                record.pmr_itms_request.message_post(
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
        return super(PmrItmsCompletionTroubleshooting, self).create(vals)

    def _generate_sequence(self):
        """Generate a unique sequence based on year, month, and existing records."""
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month

        prefix = "COMP/TROUBLE"
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
    

    def action_copy_memo_lines(self):
        for record in self:
            if record.pmr_itms_request:
                memo_lines = []

                for line in record.pmr_itms_memo_line_ids_ass_1:
                    # Format field Reference
                    ref_product = (
                        f"{line.pmr_itms_product._name},{line.pmr_itms_product.id}"
                        if line.pmr_itms_product else False
                    )

                    # Cek duplikat
                    existing_line = self.env['pmr.itms.request.memo.pembelian.troubleshooting'].search([
                        ('pmr_itms_product', '=', ref_product),
                        ('pmr_itms_jumlah', '=', line.pmr_itms_jumlah),
                        ('pmr_itms_uom', '=', line.pmr_itms_uom.id),
                        ('pmr_itms_memo_head_1_char', '=', line.pmr_itms_memo_head_1_char),
                        ('pmr_itms_product_text', '=', line.pmr_itms_product_text),
                    ], limit=1)

                    if existing_line:
                        raise UserError('Data sudah ada, tidak dapat ditambahkan lagi.')
                    else:
                        memo_lines.append((0, 0, {
                            'pmr_itms_product': ref_product,
                            'pmr_itms_jumlah': line.pmr_itms_jumlah,
                            'pmr_itms_uom': line.pmr_itms_uom.id,
                            'pmr_note': line.pmr_note,
                            'pmr_itms_memo_head_1_char': line.pmr_itms_memo_head_1_char,
                            'pmr_itms_product_text': line.pmr_itms_product_text,
                        }))

                # Tulis ke field One2many pada record request
                if memo_lines:
                    record.pmr_itms_request.write({
                        'pmr_itms_request_line_ids_ass_1': memo_lines
                    })
                    record.message_post(body='Data berhasil ditambahkan.', message_type='notification')

    
class PmrItmsCompletionMemoPembelianTroubleshooting(models.Model):
    _name = "pmr.itms.completion.memo.pembelian.troubleshooting"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Completion Memo Pembelian Troubleshooting"
    
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
    pmr_itms_memo_head_1 = fields.Many2one('pmr.itms.completion.troubleshooting', string="ID Memo")
    pmr_itms_memo_head_1_char = fields.Char(string="Memo")
    pmr_itms_product_text = fields.Text(string="Product Description")
    state = fields.Selection(string="State", related='pmr_itms_memo_head_1.state', store=True)
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
    ], string="Item Category", store=True)


