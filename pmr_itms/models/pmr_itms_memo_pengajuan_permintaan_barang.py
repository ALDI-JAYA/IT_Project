from odoo import api, fields, models, _
from datetime import datetime

class PmrItmsMemoPengajuanPermintaanBarang(models.Model):
    _name = "pmr.itms.memo.pengajuan.permintaan.barang"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Memo Pengajuan Permintaan Barang"

    name = fields.Char(string="ITMS ID", required=True, copy=False, readonly=True, default=lambda self: _("New"))
    request_type = fields.Selection([
        ('demand', 'Demand'),
        ('borrow', 'Borrow'),
    ], string="Request Type", tracking=True, store=True)

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self._generate_sequence()
        return super(PmrItmsMemoPengajuanPermintaanBarang, self).create(vals)

    def _generate_sequence(self):
        """Generate a unique sequence based on year, month, and existing records."""
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month

        prefix = "ASSET/MEMO"
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
    pmr_itms_request_date = fields.Date(string="Date", required=True)
    pmr_itms_user = fields.Many2one('pmr.itms.user', string="User", required=True, store=True)
    pmr_itms_departement_user = fields.Many2one('hr.department', string="Departement", required=True, store=True)
    pmr_itms_memo_line_ids_ass  = fields.One2many('pmr.itms.memo.pengajuan.permintaan.barang.line','pmr_itms_memo_to', tracking=10)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_user', 'In User'),
        ('return', 'Return To IT'),
    ], string="State", default='draft', tracking=True, store=True)

    def action_submit(self):
        self.state= 'in_user'
    
    def action_return(self):
        self.state= 'return'

class PmrItmsMemoPengajuanPermintaanBarangLine(models.Model):
    _name = "pmr.itms.memo.pengajuan.permintaan.barang.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Memo Pengajuan Permintaan Barang"

    pmr_itms_product = fields.Char(string="Item Name")
    pmr_itms_jumlah = fields.Float(string="Quantity")
    pmr_itms_uom = fields.Many2one('uom.uom', string="Uom", store=True)
    pmr_note = fields.Text(string="Note")
    pmr_itms_memo_to = fields.Many2one('pmr.itms.memo.pengajuan.permintaan.barang', string="ID Memo", store=True)
    pmr_itms_product_text = fields.Text(string="Product Description")
    state = fields.Selection(string="State", related='pmr_itms_memo_to.state', store=True)
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