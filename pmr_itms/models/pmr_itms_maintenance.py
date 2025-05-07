from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError

class PmrItmsMaintenance(models.Model):
    _name = "pmr.itms.maintenance"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Maintenance"

    name = fields.Char(string="ITMS ID", required=True, copy=False, readonly=True, default=lambda self: _("New"))
    pmr_itms_scheduled_date = fields.Datetime(string="Scheduled Date")
    pmr_itms_d = fields.Char(string="Day")
    pmr_itms_m = fields.Char(string="Month")
    pmr_itms_y = fields.Char(string="Year")
    pmr_itms_user = fields.Many2one('pmr.itms.user', string="User", required=True, store=True)
    pmr_itms_product = fields.Many2one('pmr.itms.product.it', string="PC Name", store=True)
    pmr_itms_ip = fields.Char(string="Ip")
    pmr_itms_departement = fields.Many2one('hr.department', string="Departement", required=True, store=True)
    pmr_itms_maintenance  = fields.One2many('pmr.itms.maintenance.line','pmr_itms_maintenance_line', tracking=10)
    state = fields.Selection([
        ('draft', 'Draft'), 
        ('done', 'Done'), 
        ('cancel', 'Cancelled'),
        ], string='Status', default="draft" , tracking=True)

    @api.onchange('pmr_itms_user')
    def _onchange_pmr_itms_user(self):
        if self.pmr_itms_user:
            self.pmr_itms_departement = self.pmr_itms_user.department_id
            self.pmr_itms_product = self.pmr_itms_user.computer_name
            self.pmr_itms_ip = self.pmr_itms_user.ip_address
        else:
            self.pmr_itms_departement = False
            self.pmr_itms_product = False
            self.pmr_itms_ip = ' '

    def action_cancel(self):
        self.state= 'cancel'

    def action_draft(self):
        self.state = 'draft'

    def action_completed(self):
        self.state= 'done'

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self._generate_sequence()
        return super(PmrItmsMaintenance, self).create(vals)

    def _generate_sequence(self):
        """Generate a unique sequence based on year, month, and existing records."""
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month

        prefix = "MAIN"
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

class PmrItmsMaintenanceLine(models.Model):
    _name = "pmr.itms.maintenance.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Maintenance Line"

    pmr_itms_maintenance_line = fields.Many2one('pmr.itms.maintenance', string="Maintenance")
    pmr_antivirus = fields.Boolean(string="Antivirus")
    pmr_temp_file = fields.Boolean(string="Temp File")
    pmr_file_corrupt = fields.Boolean(string="File Corrupt")
    pmr_perawatan = fields.Boolean(string="Maintenance")
    pmr_backup = fields.Boolean(string="Backup")
    pmr_c = fields.Boolean(string="C")
    pmr_d = fields.Boolean(string="D")
    pmr_e = fields.Boolean(string="E")
    pmr_keterangan = fields.Char(string="Keterangan")
    pmr_itms_personil_it = fields.Many2one('pmr.itms.personil.it', string="IT Personnel", store=True)
    pmr_verifikasi_user = fields.Boolean(string="Verifikasi User")