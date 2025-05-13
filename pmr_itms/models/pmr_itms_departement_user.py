from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class PmrItmsUser(models.Model):
    _name = "pmr.itms.user"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr ITMS User"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]

    name = fields.Char(string="Name", required=True, tracking=True)
    email = fields.Char(string="Email", tracking=True)
    department_id = fields.Many2one('hr.department', string="Department", store=True)
    computer_name = fields.Many2one('pmr.itms.product.it',string="Computer Name")
    device_type = fields.Many2one('pmr.device.model', string="Device Model", store=True)
    user_directory = fields.Selection([
        ('local', 'User Lokal'),
        ('active', 'User Active Directory')
    ], string="User Directory", tracking=True, store=True)
    device_model = fields.Char(string="Device Merk", tracking=True)
    serial_number = fields.Char(string="Serial Number", tracking=True)
    ip_address = fields.Char(string="IP Address")
    motherboard_type = fields.Many2one('pmr.motherboard.type', string="PMR Motherboard Type", store=True)
    pmr_mainboard = fields.Many2one('pmr.mainboard',string="Motherboard", store=True)
    pmr_processor = fields.Many2one('pmr.processor', string="Processor", store=True)
    pmr_hardisk_1 = fields.Many2one('pmr.hardisk', string="Hardisk 1", store=True)
    pmr_hardisk_2 = fields.Many2one('pmr.hardisk', string="Hardisk 2", store=True)
    pmr_hardisk_3 = fields.Many2one('pmr.hardisk', string="Hardisk 3", store=True)
    pmr_hardisk_4 = fields.Many2one('pmr.hardisk', string="Hardisk 4", store=True)
    pmr_ram_1 = fields.Many2one('pmr.ram', string="RAM 1", store=True)
    pmr_ram_2 = fields.Many2one('pmr.ram', string="RAM 2", store=True)
    pmr_ram_3 = fields.Many2one('pmr.ram', string="RAM 3", store=True)
    pmr_ram_4 = fields.Many2one('pmr.ram', string="RAM 4", store=True)
    pmr_vga_1 = fields.Many2one('pmr.vga', string="VGA 1", store=True)
    pmr_vga_2 = fields.Many2one('pmr.vga', string="VGA 1", store=True)
    pmr_operating_system = fields.Many2one('pmr.os', string="Operating System", store=True)
    pmr_sn_operating_system = fields.Char(string="Product Key")
    pmr_sn_office = fields.Char(string="Product Key")
    pmr_antivirus = fields.Many2one('pmr.antivirus',string="Antivirus", store=True)
    pmr_sn_antivirus = fields.Char(string="Activation Code")
    pmr_date_antivirus = fields.Datetime(string="Date Antivirus")
    pmr_anydesk = fields.Char(string="Anydesk")
    pmr_anydesk_pass = fields.Char(string="Anydesk Pass")
    pmr_radmin = fields.Char(string="Radmin")
    pmr_radmin_pass = fields.Char(string="Radmin Pass")
    pmr_administrator = fields.Char(string="Administrator Local")
    pmr_administrator_pass = fields.Char(string="Administrator Local Pass")
    pmr_spark = fields.Char(string="Spark")
    pmr_spark_pass = fields.Char(string="Spark Pass")
    pmr_local_email = fields.Char(string="Email")
    pmr_local_email_pass = fields.Char(string="Email Pass")
    access_level = fields.Selection([
        ('admin', 'Admin'),
        ('user', 'User')
    ], string="Access Level", default='user', tracking=True, store=True)
    username = fields.Char(string="Username")
    password = fields.Char(string="Password")
    vpn_access = fields.Boolean(string="VPN Access")
    system_access = fields.Many2many('ir.module.module', string="System Access")
    pmr_office = fields.Many2one('pmr.office', string="Office", store=True)
    pmr_software_lain = fields.Many2many('pmr.software.lain', string="Software Lain Lain", store=True)
    pmr_sn_software_lain = fields.Text(string="Product Key", compute="_compute_pmr_sn_software_lain", store=True, readonly=False)
    office_location = fields.Char(string="Office Location")
    ip_type = fields.Selection([
        ('dhcp', 'DHCP'),
        ('static', 'Static'),
    ], string="IP Type", tracking=True, store=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ], string="Status", default='active', tracking=True)
    notes = fields.Text(string="Additional Notes")
    pmr_vga_type_1 = fields.Char(string="Type", compute="_compute_vga_type", store=True)
    pmr_vga_type_2 = fields.Char(string="Type", compute="_compute_vga_type", store=True)

    @api.onchange('pmr_antivirus', 'name')
    def _onchange_pmr_antivirus(self):
        if self.pmr_antivirus and self.name:
            license_record = self.env['pmr.license.antivirus'].search([
                ('pmr_itms_user', '=', self.name),
                ('pmr_itms_license_antivirus', '=', self.pmr_antivirus.id)
            ], limit=1)
            self.pmr_sn_antivirus = license_record.name if license_record else False
        else:
            self.pmr_sn_antivirus = False
    
    @api.onchange('pmr_office', 'name')
    def _onchange_pmr_office(self):
        if self.pmr_office and self.name:
            license_record = self.env['pmr.license.office'].search([
                ('pmr_itms_user', '=', self.name),
                ('pmr_itms_license_office', '=', self.pmr_office.id)
            ], limit=1)
            self.pmr_sn_office = license_record.name if license_record else False
        else:
            self.pmr_sn_office = False
    
    @api.onchange('pmr_operating_system', 'name')
    def _onchange_pmr_operating_system(self):
        if self.pmr_operating_system and self.name:
            license_record = self.env['pmr.license.os'].search([
                ('pmr_itms_user', '=', self.name),
                ('pmr_itms_license_os', '=', self.pmr_operating_system.id)
            ], limit=1)
            self.pmr_sn_operating_system = license_record.name if license_record else False
        else:
            self.pmr_sn_operating_system = False

    @api.depends('pmr_software_lain')
    def _compute_pmr_sn_software_lain(self):
        for record in self:
            software_names = record.pmr_software_lain.mapped('name')
            if software_names:
                record.pmr_sn_software_lain = '\n'.join(f"{name} :" for name in software_names)
            else:
                record.pmr_sn_software_lain = ''

    @api.depends('pmr_vga_1', 'pmr_vga_1.pmr_onboard', 'pmr_vga_1.pmr_pci',
                 'pmr_vga_2', 'pmr_vga_2.pmr_onboard', 'pmr_vga_2.pmr_pci')
    def _compute_vga_type(self):
        for record in self:
            vga_1_types = []
            if record.pmr_vga_1:
                if record.pmr_vga_1.pmr_onboard:
                    vga_1_types.append("Onboard")
                if record.pmr_vga_1.pmr_pci:
                    vga_1_types.append("External")
            record.pmr_vga_type_1 = " dan ".join(vga_1_types) if vga_1_types else ""

            vga_2_types = []
            if record.pmr_vga_2:
                if record.pmr_vga_2.pmr_onboard:
                    vga_2_types.append("Onboard")
                if record.pmr_vga_2.pmr_pci:
                    vga_2_types.append("External")
            record.pmr_vga_type_2 = " dan ".join(vga_2_types) if vga_2_types else ""

class PmrItmsPersonilIt(models.Model):
    _name = "pmr.itms.personil.it"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Personil IT"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Personil IT", required=True, store=True, tracking=True)
    email = fields.Char(string="Email", required=True, store=True, tracking=True)
    role_it = fields.Many2one('pmr.itms.role', string="Role")
    start_date = fields.Date(string="Start Date", help="Date when the person started in this role")
    is_active = fields.Boolean(string="Active", default=True)
    skills = fields.Text(string="Skills", help="Technical skills and certifications")
    notes = fields.Text(string="Notes", help="Additional notes about the person") 

class PmrItmsProductItSwitch(models.Model):
    _name = "pmr.itms.product.it.switch"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Product IT"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Personil IT", required=True, store=True)
    pmr_barcode = fields.Many2one('pmr.barcode', String="Barcode")
    product_location_unit = fields.Many2one('pmr.location.unit', string="Location", store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_umur_product = fields.Integer(string="Product Age", compute="_compute_pmr_umur_product", store=True)
    pmr_umur_product_str = fields.Char(string="Product Age (Text)", compute="_compute_pmr_umur_product_str", store=True)
    pmr_umur_product_str_year = fields.Char(string="Product Age (Text)", compute="_compute_pmr_umur_product_str_year", store=True)
    pmr_itms_departement = fields.Many2one('hr.department', string="Departement", required=True, store=True)
    pmr_itms_user = fields.Many2one('pmr.itms.user', string="User", required=True)
    pmr_quantity_product_it = fields.Float(string="Quantity", required=True, default=1)
    pmr_asset = fields.Boolean(string="Asset", default=False)
    pmr_no_asset = fields.Char(string="Nomor Asset")
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    product_category = fields.Many2one('pmr.product.category', string="Category", store=True)
    product_sub_category = fields.Many2one('pmr.product.sub.category', string="Sub Category", store=True)
    pmr_nama_switch = fields.Many2one('pmr.itms.inventory.it',string="Nama Switch", domain=[('category', '=', 'switch')], store=True)
    pmr_jenis_switch = fields.Char(string="Jenis Switch", store=True)
    pmr_jumlah_port = fields.Float(string="Jumlah Port")
    pmr_kecepatan_port = fields.Char(string="Kecepatan Port", store=True)
    pmr_switching_capacity = fields.Char(string="Switching Capacity")
    product_type = fields.Selection([
        ('pc_laptop', 'PC'),
        ('laptop', 'Laptop'),
        ('printer', 'Printer'),
        ('router', 'Router'),
        ('wifi', 'Wifi'),
        ('switch', 'Switch'),
        ('sotware', 'Software'),
    ], string="Device Type", default="switch", tracking=True, store=True)
    state = fields.Selection([
        ('aktif', 'Aktif'),
        ('non', 'Non Aktif'),
    ], string="State", default="non", tracking=True, store=True)

    @api.onchange('pmr_nama_switch')
    def _onchange_pmr_nama_switch(self):
        if self.pmr_nama_switch:
            self.pmr_jenis_switch = self.pmr_nama_switch.pmr_jenis_switch
            self.pmr_jumlah_port = self.pmr_nama_switch.pmr_jumlah_port
            self.pmr_kecepatan_port = self.pmr_nama_switch.pmr_kecepatan_port
            self.pmr_switching_capacity = self.pmr_nama_switch.pmr_switching_capacity

    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product(self):
        """Calculates product age and ensures the result is not negative."""
        today_date = date.today() 
        for record in self:
            if record.pmr_create_date:
                create_date = record.pmr_create_date.date()
                record.pmr_umur_product = max((today_date - create_date).days, 0)
            else:
                record.pmr_umur_product = 0  
    
    @api.depends('pmr_umur_product')
    def _compute_pmr_umur_product_str(self):
        """Change pmr_umur_product to a string with the format 'X days'."""
        for record in self:
            record.pmr_umur_product_str = f"{record.pmr_umur_product} days"
    
    @api.depends('pmr_umur_product')
    def _compute_pmr_umur_product_str_year(self):
        """Convert pmr_umur_product into years format (X years, X months)."""
        for record in self:
            years = record.pmr_umur_product // 365
            months = (record.pmr_umur_product % 365) // 30  
            if years > 0 and months > 0:
                record.pmr_umur_product_str_year = f"{years} years {months} months"
            elif years > 0:
                record.pmr_umur_product_str_year = f"{years} years"
            elif months > 0:
                record.pmr_umur_product_str_year = f"{months} months"
            else:
                record.pmr_umur_product_str_year = "0 days"
    def action_switch(self):
        for record in self:
            self.env['pmr.itms.inventory.movement'].create({
                'name_product': record.pmr_name_switch.display_name if record.pmr_name_switch else record.name,
                'pmr_itms_departement': record.pmr_itms_departement.id,
                'pmr_itms_user': record.pmr_itms_user.id,
                'pmr_quantity_product_it': -abs(record.pmr_quantity_product_it),
                'product_unit_category': record.product_unit_category.id,
                'product_location_unit': record.pmr_name_switch.product_location_unit.id,
            })
            record.state = 'non'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sukses',
                'message': 'Data berhasil dikirim',
                'sticky': False,
            }
        }
    
    def action_reject(self):
        self.state= 'reject'

    def action_repair(self):
        self.state = 'repair'

    def action_good(self):
        self.state= 'good'
    
    def generate_pc_laptop_sequence(self):
        for record in self:
            if record.product_type == 'switch':
                current_date = record.pmr_create_date or datetime.now()
                year_month = current_date.strftime('%y%m')

                last_barcode = self.env['pmr.barcode'].search([
                    ('name', 'like', f"{year_month}%SW")
                ], order='name desc', limit=1)

                if last_barcode:
                    last_sequence = int(last_barcode.name[4:9]) + 1
                else:
                    last_sequence = 1

                sequence_str = str(last_sequence).zfill(5)
                barcode_name = f"{year_month}{sequence_str}SW"

                barcode = self.env['pmr.barcode'].create({
                    'name': barcode_name,
                    'pmr_create_date': current_date,  
                    'pmr_inventory_it': record.name  
                })

                record.pmr_barcode = barcode.id

    def action_generate_barcode(self):
        self.generate_pc_laptop_sequence()

class PmrItmsProductItAccessories(models.Model):
    _name = "pmr.itms.product.it.accessories"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Product IT"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Personil IT", required=True, store=True)
    pmr_barcode = fields.Many2one('pmr.barcode', String="Barcode")
    product_location_unit = fields.Many2one('pmr.location.unit', string="Location", store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_umur_product = fields.Integer(string="Product Age (Hari)", compute="_compute_pmr_umur_product", store=True)
    pmr_umur_product_str = fields.Char(string="Product Age (Full)", compute="_compute_pmr_umur_product_str", store=True)
    pmr_umur_product_str_year = fields.Char(string="Product Age (Tahun)", compute="_compute_pmr_umur_product_str_year", store=True) 
    pmr_itms_departement = fields.Many2one('hr.department', string="Departement", required=True, store=True)
    pmr_itms_user = fields.Many2one('pmr.itms.user', string="User", required=True)
    pmr_quantity_product_it = fields.Float(string="Quantity", required=True,default=1)
    pmr_asset = fields.Boolean(string="Asset", default=False)
    pmr_no_asset = fields.Char(string="Nomor Asset")
    pmr_name_accesories = fields.Char(string="Nama Accesories", compute="_compute_pmr_name_accesories",store=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    product_category = fields.Many2one('pmr.product.category', string="Category",store=True)
    product_sub_category = fields.Many2one('pmr.product.sub.category', string="Sub Category", store=True)
    name_casing = fields.Many2one('pmr.itms.inventory.it', string="Casing",domain=[('category', '=', 'casing')], store=True)
    name_hardisk = fields.Many2one('pmr.itms.inventory.it', string="Hardisk",domain=[('category', '=', 'hardisk')], store=True)
    name_keyboard = fields.Many2one('pmr.itms.inventory.it', string="Keyboard",domain=[('category', '=', 'keyboard')], store=True)
    name_monitor = fields.Many2one('pmr.itms.inventory.it', string="Monitor",domain=[('category', '=', 'monitor')], store=True)
    name_mouse = fields.Many2one('pmr.itms.inventory.it', string="Mouse",domain=[('category', '=', 'mosue')], store=True)
    name_mobo = fields.Many2one('pmr.itms.inventory.it', string="Motherboard",domain=[('category', '=', 'mainboard')], store=True)
    name_processor = fields.Many2one('pmr.itms.inventory.it', string="Processor",domain=[('category', '=', 'processor')], store=True)
    name_psu = fields.Many2one('pmr.itms.inventory.it', string="Power Supply",domain=[('category', '=', 'power_supply')], store=True)
    name_ram = fields.Many2one('pmr.itms.inventory.it', string="RAM",domain=[('category', '=', 'ram')], store=True)
    name_vga = fields.Many2one('pmr.itms.inventory.it', string="VGA",domain=[('category', '=', 'vga')], store=True)
    name_fdd = fields.Many2one('pmr.itms.inventory.it', string="Expansion Slot",domain=[('category', '=', 'fdd')], store=True)
    name_lan = fields.Many2one('pmr.itms.inventory.it', string="Integrated LAN",domain=[('category', '=', 'Integrated_LAN')], store=True)
    pmr_onboard = fields.Boolean(string="On Board")
    pmr_pci = fields.Boolean(string="External")
    product_type = fields.Selection([
        ('casing', 'Casing'),
        ('hardisk', 'Hardisk'),
        ('keyboard', 'Keyboard'),
        ('monitor', 'Monitor'),
        ('mouse', 'Mouse'),
        ('motherboard', 'Motherboard'),
        ('psu', 'Power Supply'),
        ('processor', 'Proessor'),
        ('ram', 'RAM'),
        ('vga', 'VGA'),
        ('lan', 'Integrated LAN'),
        ('fdd', 'Expansion Slot'),
    ], string="Device Type", default="sparepart", tracking=True, store=True)
    state = fields.Selection([
        ('non', 'Non Aktif'),
        ('aktif', 'Aktif'),
    ], string="State", default="non", tracking=True, store=True)
    
    @api.onchange('name_vga', 'name_fdd', 'name_lan')
    def _onchange_component_fields(self):
        # Reset nilai default dulu
        self.pmr_onboard = False
        self.pmr_pci = False

        # Cek VGA
        if self.name_vga:
            self.pmr_onboard = self.name_vga.pmr_onboard or self.pmr_onboard
            self.pmr_pci = self.name_vga.pmr_pci or self.pmr_pci

        # Cek FDD
        if self.name_fdd:
            self.pmr_pci = self.name_fdd.pmr_pci or self.pmr_pci

        # Cek LAN
        if self.name_lan:
            self.pmr_onboard = self.name_lan.pmr_onboard or self.pmr_onboard

    # def _set_pc_accesories_fields(self):
    #     self.pmr_onboard = self.pmr_name_vga.pmr_onboard
    #     self.pmr_pci = self.pmr_name_vga.pmr_pci
        
    @api.onchange('name_monitor', 'name_mouse', 'name_mobo', 'name_processor', 'name_psu', 'name_vga')
    def _onchange_product_names(self):
        product = (
            self.name_monitor or self.name_mouse or self.name_mobo or
            self.name_processor or self.name_psu or self.name_vga
        )
        if product and product.product_unit_category:
            self.product_unit_category = product.product_unit_category
        else:
            self.product_unit_category = False


    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product(self):
        """Calculates product age and ensures the result is not negative."""
        today_date = date.today() 
        for record in self:
            if record.pmr_create_date:
                create_date = record.pmr_create_date.date()
                record.pmr_umur_product = max((today_date - create_date).days, 0)
            else:
                record.pmr_umur_product = 0  
    def _compute_pmr_name_accesories(self):
        for record in self:
            accessories = []
            if record.name_casing:
                accessories.append(record.name_casing.name)
            if record.name_hardisk:
                accessories.append(record.name_hardisk.name)
            if record.name_keyboard:
                accessories.append(record.name_keyboard.name)
            if record.name_monitor:
                accessories.append(record.name_monitor.name)
            if record.name_mouse:
                accessories.append(record.name_mouse.name)
            if record.name_mobo:
                accessories.append(record.name_mobo.name)
            if record.name_processor:
                accessories.append(record.name_processor.name)
            if record.name_psu:
                accessories.append(record.name_psu.name)
            if record.name_ram:
                accessories.append(record.name_ram.name)
            if record.name_vga:
                accessories.append(record.name_vga.name)

            record.pmr_name_accesories = ', '.join(accessories)

    @api.model
    def _cron_update_product_accesories_age(self):
        records = self.search([])
        for rec in records:
            if rec.pmr_create_date:
                today = date.today()
                create_date = rec.pmr_create_date.date()
                delta = relativedelta(today, create_date)
                days = (today - create_date).days

                rec.pmr_umur_product = days
                rec.pmr_umur_product_str = f"{delta.years} tahun, {delta.months} bulan, {delta.days} hari"
                rec.pmr_umur_product_str_year = f"{delta.years} tahun"

    def action_run_cron_manual(self):
        """Menjalankan cron secara manual"""
        self.env['pmr.itms.product.it.accessories']._cron_update_product_accesories_age()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Berhasil',
                'message': 'Jadwal diaktifkan.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_disable_cron(self):
        """Menonaktifkan cron dari ir.cron"""
        cron = self.env.ref('pmr_itms.ir_cron_update_product_accesories_age', raise_if_not_found=False)
        if cron:
            cron.write({'active': False})
            message = "Jadwal berhasil dinonaktifkan."
        else:
            message = "Jadwal tidak ditemukan."
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Info',
                'message': message,
                'type': 'warning',
                'sticky': False,
            }
        }

    def action_enable_cron(self):
        """Mengaktifkan ulang cron"""
        cron = self.env.ref('pmr_itms.ir_cron_update_product_accesories_age', raise_if_not_found=False)
        if cron:
            cron.write({'active': True})
            message = "Jadwal berhasil diaktifkan."
        else:
            message = "Jadwal tidak ditemukan."
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Info',
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }

    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product(self):
        for rec in self:
            if rec.pmr_create_date:
                today = fields.Date.context_today(rec)
                create_date = rec.pmr_create_date.date()
                age_days = (today - create_date).days
                rec.pmr_umur_product = age_days
            else:
                rec.pmr_umur_product = 0

    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product_str(self):
        for rec in self:
            if rec.pmr_create_date:
                today = fields.Date.context_today(rec)
                create_date = rec.pmr_create_date.date()
                delta = relativedelta(today, create_date)

                rec.pmr_umur_product_str = f"{delta.years} tahun, {delta.months} bulan, {delta.days} hari"
                rec.pmr_umur_product_str_year = f"{delta.years} tahun"
            else:
                rec.pmr_umur_product_str = "-"
                rec.pmr_umur_product_str_year = "-"
    
    def generate_pc_laptop_sequence(self):
        for record in self:
            if record.product_type == 'switch':
                current_date = record.pmr_create_date or datetime.now()
                year_month = current_date.strftime('%y%m')

                last_barcode = self.env['pmr.barcode'].search([
                    ('name', 'like', f"{year_month}%SW")
                ], order='name desc', limit=1)

                if last_barcode:
                    last_sequence = int(last_barcode.name[4:9]) + 1
                else:
                    last_sequence = 1

                sequence_str = str(last_sequence).zfill(5)
                barcode_name = f"{year_month}{sequence_str}SW"

                barcode = self.env['pmr.barcode'].create({
                    'name': barcode_name,
                    'pmr_create_date': current_date,  
                    'pmr_inventory_it': record.name  
                })

                record.pmr_barcode = barcode.id

    def action_generate_barcode(self):
        self.generate_pc_laptop_sequence()

class PmrItmsProductItWifi(models.Model):
    _name = "pmr.itms.product.it.wifi"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Product IT"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Personil IT", required=True, store=True)
    pmr_barcode = fields.Many2one('pmr.barcode', String="Barcode")
    product_location_unit = fields.Many2one('pmr.location.unit', string="Location", store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_umur_product = fields.Integer(string="Product Age (Hari)", compute="_compute_pmr_umur_product", store=True)
    pmr_umur_product_str = fields.Char(string="Product Age (Full)", compute="_compute_pmr_umur_product_str", store=True)
    pmr_umur_product_str_year = fields.Char(string="Product Age (Tahun)", compute="_compute_pmr_umur_product_str_year", store=True)
    pmr_itms_departement = fields.Many2one('hr.department', string="Departement", required=True, store=True)
    pmr_itms_user = fields.Many2one('pmr.itms.user', string="User", required=True)
    pmr_quantity_product_it = fields.Float(string="Quantity", required=True, default=1)
    pmr_asset = fields.Boolean(string="Asset", default=False)
    pmr_no_asset = fields.Char(string="Nomor Asset")
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    product_category = fields.Many2one('pmr.product.category', string="Category", store=True)
    product_sub_category = fields.Many2one('pmr.product.sub.category', string="Sub Category", store=True)
    pmr_name_wifi = fields.Many2one('pmr.itms.inventory.it',string="Nama Wifi", domain=[('category', '=', 'wifi')], store=True)
    pmr_frekuensi_wifi = fields.Char(string="Frekuensi WIFI", store=True)
    pmr_keamanan = fields.Char(string="Keamanan Wifi")
    product_type = fields.Selection([
        ('pc_laptop', 'PC'),
        ('laptop', 'Laptop'),
        ('printer', 'Printer'),
        ('router', 'Router'),
        ('wifi', 'Wifi'),
        ('switch', 'Switch'),
        ('sotware', 'Software'),
    ], string="Device Type", default="wifi", tracking=True, store=True)
    state = fields.Selection([
        ('non', 'Non Aktif'),
        ('aktif', 'Aktif'),
    ], string="State", default="non", tracking=True, store=True)

    @api.onchange('pmr_name_wifi')
    def _onchange_pmr_name_wifi(self):
        if self.pmr_name_wifi:
            self.pmr_frekuensi_wifi = self.pmr_name_wifi.pmr_frekuensi_wifi
            self.pmr_keamanan = self.pmr_name_wifi.pmr_keamanan

    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product(self):
        """Calculates product age and ensures the result is not negative."""
        today_date = date.today() 
        for record in self:
            if record.pmr_create_date:
                create_date = record.pmr_create_date.date()
                record.pmr_umur_product = max((today_date - create_date).days, 0)
            else:
                record.pmr_umur_product = 0  
    
    @api.depends('pmr_umur_product')
    def _compute_pmr_umur_product_str(self):
        """Change pmr_umur_product to a string with the format 'X days'."""
        for record in self:
            record.pmr_umur_product_str = f"{record.pmr_umur_product} days"
    
    @api.depends('pmr_umur_product')
    def _compute_pmr_umur_product_str_year(self):
        """Convert pmr_umur_product into years format (X years, X months)."""
        for record in self:
            years = record.pmr_umur_product // 365
            months = (record.pmr_umur_product % 365) // 30  
            if years > 0 and months > 0:
                record.pmr_umur_product_str_year = f"{years} years {months} months"
            elif years > 0:
                record.pmr_umur_product_str_year = f"{years} years"
            elif months > 0:
                record.pmr_umur_product_str_year = f"{months} months"
            else:
                record.pmr_umur_product_str_year = "0 days"
    
    def action_wifi(self):
        for record in self:
            self.env['pmr.itms.inventory.movement'].create({
                'name_product': record.pmr_name_wifi.display_name if record.pmr_name_wifi else record.name,
                'pmr_itms_departement': record.pmr_itms_departement.id,
                'pmr_itms_user': record.pmr_itms_user.id,
                'pmr_quantity_product_it': -abs(record.pmr_quantity_product_it),
                'product_unit_category': record.product_unit_category.id,
                'product_location_unit': record.pmr_name_wifi.product_location_unit.id,
            })
            record.state = 'non'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sukses',
                'message': 'Data berhasil dikirim',
                'sticky': False,
            }
        }

    @api.model
    def _cron_update_product_wifi_age(self):
        records = self.search([])
        for rec in records:
            if rec.pmr_create_date:
                today = date.today()
                create_date = rec.pmr_create_date.date()
                delta = relativedelta(today, create_date)
                days = (today - create_date).days

                rec.pmr_umur_product = days
                rec.pmr_umur_product_str = f"{delta.years} tahun, {delta.months} bulan, {delta.days} hari"
                rec.pmr_umur_product_str_year = f"{delta.years} tahun"

    def action_run_cron_manual(self):
        """Menjalankan cron secara manual"""
        self.env['pmr.itms.product.it.wifi']._cron_update_product_wifi_age()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Berhasil',
                'message': 'Jadwal diaktifkan.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_disable_cron(self):
        """Menonaktifkan cron dari ir.cron"""
        cron = self.env.ref('pmr_itms.ir_cron_pmr_update_product_wifi_age', raise_if_not_found=False)
        if cron:
            cron.write({'active': False})
            message = "Jadwal berhasil dinonaktifkan."
        else:
            message = "Jadwal tidak ditemukan."
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Info',
                'message': message,
                'type': 'warning',
                'sticky': False,
            }
        }

    def action_enable_cron(self):
        """Mengaktifkan ulang cron"""
        cron = self.env.ref('pmr_itms.ir_cron_pmr_update_product_wifi_age', raise_if_not_found=False)
        if cron:
            cron.write({'active': True})
            message = "Jadwal berhasil diaktifkan."
        else:
            message = "Jadwal tidak ditemukan."
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Info',
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }

    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product(self):
        for rec in self:
            if rec.pmr_create_date:
                today = fields.Date.context_today(rec)
                create_date = rec.pmr_create_date.date()
                age_days = (today - create_date).days
                rec.pmr_umur_product = age_days
            else:
                rec.pmr_umur_product = 0

    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product_str(self):
        for rec in self:
            if rec.pmr_create_date:
                today = fields.Date.context_today(rec)
                create_date = rec.pmr_create_date.date()
                delta = relativedelta(today, create_date)

                rec.pmr_umur_product_str = f"{delta.years} tahun, {delta.months} bulan, {delta.days} hari"
                rec.pmr_umur_product_str_year = f"{delta.years} tahun"
            else:
                rec.pmr_umur_product_str = "-"
                rec.pmr_umur_product_str_year = "-"
    
    def generate_pc_laptop_sequence(self):
        for record in self:
            if record.product_type == 'wifi':
                current_date = record.pmr_create_date or datetime.now()
                year_month = current_date.strftime('%y%m')

                last_barcode = self.env['pmr.barcode'].search([
                    ('name', 'like', f"{year_month}%AP")
                ], order='name desc', limit=1)

                if last_barcode:
                    last_sequence = int(last_barcode.name[4:9]) + 1
                else:
                    last_sequence = 1

                sequence_str = str(last_sequence).zfill(5)
                barcode_name = f"{year_month}{sequence_str}AP"

                barcode = self.env['pmr.barcode'].create({
                    'name': barcode_name,
                    'pmr_create_date': current_date,  
                    'pmr_inventory_it': record.name  
                })

                record.pmr_barcode = barcode.id

    def action_generate_barcode(self):
        self.generate_pc_laptop_sequence()

class PmrItmsProductItRouter(models.Model):
    _name = "pmr.itms.product.it.router"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Product IT"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Personil IT", required=True, store=True)
    pmr_barcode = fields.Many2one('pmr.barcode', String="Barcode")
    product_location_unit = fields.Many2one('pmr.location.unit', string="Location", store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_umur_product = fields.Integer(string="Product Age (Hari)", compute="_compute_pmr_umur_product", store=True)
    pmr_umur_product_str = fields.Char(string="Product Age (Full)", compute="_compute_pmr_umur_product_str", store=True)
    pmr_umur_product_str_year = fields.Char(string="Product Age (Tahun)", compute="_compute_pmr_umur_product_str_year", store=True)
    pmr_itms_departement = fields.Many2one('hr.department', string="Departement", required=True, store=True)
    pmr_itms_user = fields.Many2one('pmr.itms.user', string="User", required=True)
    pmr_quantity_product_it = fields.Float(string="Quantity", required=True, default=1)
    pmr_asset = fields.Boolean(string="Asset", default=False)
    pmr_no_asset = fields.Char(string="Nomor Asset")
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    product_category = fields.Many2one('pmr.product.category', string="Category", store=True)
    product_sub_category = fields.Many2one('pmr.product.sub.category', string="Sub Category", store=True)
    pmr_name_router = fields.Many2one('pmr.itms.inventory.it',domain=[('category', '=', 'router')],string="Nama Router", store=True)
    pmr_hardware_router = fields.Char(string="Hardware Router", store=True)
    pmr_konektivitas_router = fields.Char(string="Konektivitas", store=True)
    pmr_fitur_tambahan_router = fields.Char(string="Fitur Tambahan Router", store=True)
    product_type = fields.Selection([
        ('pc_laptop', 'PC'),
        ('laptop', 'Laptop'),
        ('printer', 'Printer'),
        ('router', 'Router'),
        ('wifi', 'Wifi'),
        ('switch', 'Switch'),
        ('sotware', 'Software'),
    ], string="Device Type", default="router", tracking=True, store=True)
    state = fields.Selection([
        ('non', 'Non Aktif'),
        ('aktif', 'Aktif'),
    ], string="State", default="non", tracking=True, store=True)
    @api.onchange('pmr_name_router')
    def _onchange_pmr_name_router(self):
        if self.pmr_name_router:
            self.pmr_hardware_router = self.pmr_name_router.pmr_hardware_router
            self.pmr_konektivitas_router = self.pmr_name_router.pmr_konektivitas_router
            self.pmr_fitur_tambahan_router = self.pmr_name_router.pmr_fitur_tambahan_router

    # @api.onchange('pmr_name_router')
    # def _onchange_pmr_name_router(self):
    #     if self.pmr_name_router:
    #         self._set_router_fields()
    #     else:
    #         self.product_unit_category = False  
    #         self.pmr_hardware_router = False  
    #         self.pmr_konektivitas_router = False
    #         self.pmr_fitur_tambahan_router = False

    # def _set_router_fields(self):
    #     self.product_unit_category = self.pmr_name_router.product_unit_category 
    #     self.pmr_hardware_router = self.pmr_name_router.pmr_hardware_router 
    #     self.pmr_konektivitas_router = self.pmr_name_router.pmr_konektivitas_router
    #     self.pmr_fitur_tambahan_router = self.pmr_name_router.pmr_fitur_tambahan_router

    # @api.model
    # def create(self, vals):
    #     record = super(PmrItmsProductItRouter, self).create(vals)
    #     if record.pmr_name_router:
    #         record._set_router_fields()
    #     return record

    # def write(self, vals):
    #     res = super(PmrItmsProductItRouter, self).write(vals)
    #     if 'pmr_name_router' in vals:
    #         for record in self:
    #             if record.pmr_name_router:
    #                 record._set_router_fields()


    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product(self):
        """Calculates product age and ensures the result is not negative."""
        today_date = date.today() 
        for record in self:
            if record.pmr_create_date:
                create_date = record.pmr_create_date.date()
                record.pmr_umur_product = max((today_date - create_date).days, 0)
            else:
                record.pmr_umur_product = 0  
    
    @api.depends('pmr_umur_product')
    def _compute_pmr_umur_product_str(self):
        """Change pmr_umur_product to a string with the format 'X days'."""
        for record in self:
            record.pmr_umur_product_str = f"{record.pmr_umur_product} days"
    
    @api.depends('pmr_umur_product')
    def _compute_pmr_umur_product_str_year(self):
        """Convert pmr_umur_product into years format (X years, X months)."""
        for record in self:
            years = record.pmr_umur_product // 365
            months = (record.pmr_umur_product % 365) // 30  
            if years > 0 and months > 0:
                record.pmr_umur_product_str_year = f"{years} years {months} months"
            elif years > 0:
                record.pmr_umur_product_str_year = f"{years} years"
            elif months > 0:
                record.pmr_umur_product_str_year = f"{months} months"
            else:
                record.pmr_umur_product_str_year = "0 days"

    def action_router(self):
        for record in self:
            self.env['pmr.itms.inventory.movement'].create({
                'name_product': record.pmr_name_router.display_name if record.pmr_name_router else record.name,
                'pmr_itms_departement': record.pmr_itms_departement.id,
                'pmr_itms_user': record.pmr_itms_user.id,
                'pmr_quantity_product_it': -abs(record.pmr_quantity_product_it),
                'product_unit_category': record.product_unit_category.id,
                'product_location_unit': record.pmr_name_router.product_location_unit.id,
            })
            record.state = 'aktif'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sukses',
                'message': 'Data berhasil dikirim',
                'sticky': False,
            }
        }
    
    @api.model
    def _cron_update_product_router_age(self):
        records = self.search([])
        for rec in records:
            if rec.pmr_create_date:
                today = date.today()
                create_date = rec.pmr_create_date.date()
                delta = relativedelta(today, create_date)
                days = (today - create_date).days

                rec.pmr_umur_product = days
                rec.pmr_umur_product_str = f"{delta.years} tahun, {delta.months} bulan, {delta.days} hari"
                rec.pmr_umur_product_str_year = f"{delta.years} tahun"

    def action_run_cron_manual(self):
        """Menjalankan cron secara manual"""
        self.env['pmr.itms.product.it.router']._cron_update_product_router_age()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Berhasil',
                'message': 'Jadwal diaktifkan.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_disable_cron(self):
        """Menonaktifkan cron dari ir.cron"""
        cron = self.env.ref('pmr_itms.ir_cron_pmr_update_product_router_age', raise_if_not_found=False)
        if cron:
            cron.write({'active': False})
            message = "Jadwal berhasil dinonaktifkan."
        else:
            message = "Jadwal tidak ditemukan."
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Info',
                'message': message,
                'type': 'warning',
                'sticky': False,
            }
        }

    def action_enable_cron(self):
        """Mengaktifkan ulang cron"""
        cron = self.env.ref('pmr_itms.ir_cron_pmr_update_product_router_age', raise_if_not_found=False)
        if cron:
            cron.write({'active': True})
            message = "Jadwal berhasil diaktifkan."
        else:
            message = "Jadwal tidak ditemukan."
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Info',
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }
    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product(self):
        for rec in self:
            if rec.pmr_create_date:
                today = fields.Date.context_today(rec)
                create_date = rec.pmr_create_date.date()
                age_days = (today - create_date).days
                rec.pmr_umur_product = age_days
            else:
                rec.pmr_umur_product = 0

    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product_str(self):
        for rec in self:
            if rec.pmr_create_date:
                today = fields.Date.context_today(rec)
                create_date = rec.pmr_create_date.date()
                delta = relativedelta(today, create_date)

                rec.pmr_umur_product_str = f"{delta.years} tahun, {delta.months} bulan, {delta.days} hari"
                rec.pmr_umur_product_str_year = f"{delta.years} tahun"
            else:
                rec.pmr_umur_product_str = "-"
                rec.pmr_umur_product_str_year = "-"
    def generate_pc_laptop_sequence(self):
        for record in self:
            if record.product_type == 'router':
                current_date = record.pmr_create_date or datetime.now()
                year_month = current_date.strftime('%y%m')

                last_barcode = self.env['pmr.barcode'].search([
                    ('name', 'like', f"{year_month}%RTR")
                ], order='name desc', limit=1)

                if last_barcode:
                    last_sequence = int(last_barcode.name[4:9]) + 1
                else:
                    last_sequence = 1

                sequence_str = str(last_sequence).zfill(5)
                barcode_name = f"{year_month}{sequence_str}RTR"

                barcode = self.env['pmr.barcode'].create({
                    'name': barcode_name,
                    'pmr_create_date': current_date,  
                    'pmr_inventory_it': record.name  
                })

                record.pmr_barcode = barcode.id

    def action_generate_barcode(self):
        self.generate_pc_laptop_sequence()
    
class PmrItmsProductItPrinter(models.Model):
    _name = "pmr.itms.product.it.printer"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Product IT"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Personil IT", required=True, store=True)
    active = fields.Boolean(string="Active", default=True)
    pmr_barcode = fields.Many2one('pmr.barcode', string="Barcode")
    product_location_unit = fields.Many2one('pmr.location.unit', string="Location", store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_umur_product = fields.Integer(string="Product Age (Hari)", compute="_compute_pmr_umur_product", store=True)
    pmr_umur_product_str = fields.Char(string="Product Age (Full)", compute="_compute_pmr_umur_product_str", store=True)
    pmr_umur_product_str_year = fields.Char(string="Product Age (Tahun)", compute="_compute_pmr_umur_product_str_year", store=True)
    pmr_itms_departement = fields.Many2one('hr.department', string="Departement", required=True, store=True)
    pmr_itms_user = fields.Many2one('pmr.itms.user', string="User", required=True)
    pmr_quantity_product_it = fields.Float(string="Quantity", required=True, default=1)
    pmr_asset = fields.Boolean(string="Asset", default=False)
    pmr_no_asset = fields.Char(string="Nomor Asset")
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    product_category = fields.Many2one('pmr.product.category', string="Category", store=True)
    product_sub_category = fields.Many2one('pmr.product.sub.category', string="Sub Category", store=True)
    pmr_name_printer = fields.Many2one('pmr.itms.inventory.it',string="Nama Printer", domain=[('category', '=', 'printer')], store=True)
    pmr_jenis_printer = fields.Char(string="Jenis Printer", store=True)
    pmr_kecepatan_cetak = fields.Char(string="Kecepatan Cetak", store=True)
    pmr_konektivitas_printer = fields.Char(string="Konektivitas", store=True)
    pmr_ukuran_kertas = fields.Char(string="Ukuran Kertas", store=True)
    pmr_fitur_tambahan = fields.Char(string="Fitur Tambahan", store=True)
    pmr_ip_printer = fields.Char(string="IP Printer")
    product_type = fields.Selection([
        ('pc_laptop', 'PC'),
        ('laptop', 'Laptop'),
        ('printer', 'Printer'),
        ('router', 'Router'),
        ('wifi', 'Wifi'),
        ('switch', 'Switch'),
        ('sotware', 'Software'),
    ], string="Device Type", default="printer", tracking=True, store=True)
    state = fields.Selection([
        ('non', 'Non Aktif'),
        ('aktif', 'Aktif'),
    ], string="State", default="non", tracking=True, store=True)

    @api.onchange('pmr_name_printer')
    def _onchange_pmr_name_printer(self):
        if self.pmr_name_printer:
            self.pmr_jenis_printer = self.pmr_name_printer.pmr_jenis_printer
            self.pmr_kecepatan_cetak = self.pmr_name_printer.pmr_kecepatan_cetak
            self.pmr_konektivitas_printer = self.pmr_name_printer.pmr_konektivitas_printer
            self.pmr_ukuran_kertas = self.pmr_name_printer.pmr_ukuran_kertas
            self.pmr_fitur_tambahan = self.pmr_name_printer.pmr_fitur_tambahan

    @api.model
    def _cron_update_product_age(self):
        records = self.search([])
        for rec in records:
            if rec.pmr_create_date:
                today = date.today()
                create_date = rec.pmr_create_date.date()
                delta = relativedelta(today, create_date)
                days = (today - create_date).days

                rec.pmr_umur_product = days
                rec.pmr_umur_product_str = f"{delta.years} tahun, {delta.months} bulan, {delta.days} hari"
                rec.pmr_umur_product_str_year = f"{delta.years} tahun"

    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product(self):
        for rec in self:
            if rec.pmr_create_date:
                today = fields.Date.context_today(rec)
                create_date = rec.pmr_create_date.date()
                age_days = (today - create_date).days
                rec.pmr_umur_product = age_days
            else:
                rec.pmr_umur_product = 0

    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product_str(self):
        for rec in self:
            if rec.pmr_create_date:
                today = fields.Date.context_today(rec)
                create_date = rec.pmr_create_date.date()
                delta = relativedelta(today, create_date)

                rec.pmr_umur_product_str = f"{delta.years} tahun, {delta.months} bulan, {delta.days} hari"
                rec.pmr_umur_product_str_year = f"{delta.years} tahun"
            else:
                rec.pmr_umur_product_str = "-"
                rec.pmr_umur_product_str_year = "-"

    def action_run_cron_manual(self):
        """Menjalankan cron secara manual"""
        self.env['pmr.itms.product.it.printer']._cron_update_product_age()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Berhasil',
                'message': 'Jadwal diaktifkan.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_disable_cron(self):
        """Menonaktifkan cron dari ir.cron"""
        cron = self.env.ref('pmr_itms.ir_cron_pmr_update_product_age', raise_if_not_found=False)
        if cron:
            cron.write({'active': False})
            message = "Cron berhasil dinonaktifkan."
        else:
            message = "Cron tidak ditemukan."
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Info',
                'message': message,
                'type': 'warning',
                'sticky': False,
            }
        }

    def action_enable_cron(self):
        """Mengaktifkan ulang cron"""
        cron = self.env.ref('pmr_itms.ir_cron_pmr_update_product_age', raise_if_not_found=False)
        if cron:
            cron.write({'active': True})
            message = "Cron berhasil diaktifkan."
        else:
            message = "Cron tidak ditemukan."
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Info',
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_not(self):
        for record in self:
            self.env['pmr.itms.inventory.movement'].create({
                'name_product': record.pmr_name_printer.display_name if record.pmr_name_printer else record.name,
                'pmr_itms_departement': record.pmr_itms_departement.id,
                'pmr_itms_user': record.pmr_itms_user.id,
                'pmr_quantity_product_it': -abs(record.pmr_quantity_product_it),
                'product_unit_category': record.product_unit_category.id,
                'product_location_unit': record.pmr_name_printer.product_location_unit.id,
            })
            record.state = 'aktif'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sukses',
                'message': 'Data berhasil dikirim ke Inventory Movement',
                'sticky': False,
            }
        }
    
    def generate_pc_laptop_sequence(self):
        for record in self:
            if record.product_type == 'printer':
                current_date = record.pmr_create_date or datetime.now()
                year_month = current_date.strftime('%y%m')

                last_barcode = self.env['pmr.barcode'].search([
                    ('name', 'like', f"{year_month}%PRT")
                ], order='name desc', limit=1)

                if last_barcode:
                    last_sequence = int(last_barcode.name[4:9]) + 1
                else:
                    last_sequence = 1

                sequence_str = str(last_sequence).zfill(5)
                barcode_name = f"{year_month}{sequence_str}PRT"

                barcode = self.env['pmr.barcode'].create({
                    'name': barcode_name,
                    'pmr_create_date': current_date,  
                    'pmr_inventory_it': record.name  
                })

                record.pmr_barcode = barcode.id

    def action_generate_barcode(self):
        self.generate_pc_laptop_sequence()

class PmrItmsProductIt(models.Model):
    _name = "pmr.itms.product.it"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Product IT"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Personil IT", required=True, store=True)
    pmr_barcode = fields.Many2one('pmr.barcode', String="Barcode")
    product_location_unit = fields.Many2one('pmr.location.unit', string="Location", store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_umur_product = fields.Integer(string="Product Age (Hari)", compute="_compute_pmr_umur_product", store=True)
    pmr_umur_product_str = fields.Char(string="Product Age (Full)", compute="_compute_pmr_umur_product_str", store=True)
    pmr_umur_product_str_year = fields.Char(string="Product Age (Tahun)", compute="_compute_pmr_umur_product_str_year", store=True)
    pmr_itms_departement = fields.Many2one('hr.department', string="Departement", required=True, store=True)
    pmr_itms_user = fields.Many2one('pmr.itms.user', string="User", required=True)
    pmr_origin_po = fields.Char(string="PO Number")
    pmr_name_pc_laptop = fields.Many2one('pmr.itms.inventory.it',string="Nama CPU/Laptop", domain=[('category', '=', 'pc')], store=True)
    pmr_office_location = fields.Char(string="Location")
    pmr_ip_address = fields.Char(string="IP Adress")
    pmr_quantity_product_it = fields.Float(string="Quantity",required=True, default=1)
    pmr_asset = fields.Boolean(string="Asset", default=False)
    pmr_no_asset = fields.Char(string="Nomor Asset")
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    product_category = fields.Many2one('pmr.product.category', string="Category", store=True)
    product_sub_category = fields.Many2one('pmr.product.sub.category', string="Sub Category", store=True)
    pmr_processor = fields.Char(string="Processor", store=True)
    pmr_mainboard = fields.Char(string="Motherboard", store=True)
    pmr_processor_adjustment = fields.Boolean(string="Adjustment Processor")
    pmr_processor_bool_replacement = fields.Boolean(string="Replacement Processor")
    pmr_processor_replacement = fields.Many2one('pmr.itms.inventory.it',string="Nama Processor", domain=[('category', '=', 'processor')], store=True)
    pmr_processor_bool_upgrade = fields.Boolean(string="Upgrade Processor")
    pmr_processor_upgrade = fields.Many2one('pmr.itms.inventory.it',string="Nama Processor", domain=[('category', '=', 'processor')], store=True)
    pmr_mainboard = fields.Char(string="Motherboard", store=True)
    pmr_mainboard_adjustment = fields.Boolean(string="Adjustment Mainboard")
    pmr_mainboard_bool_replacement = fields.Boolean(string="Replacement Motherboard")
    pmr_mainboard_replacement = fields.Many2one('pmr.itms.inventory.it',string="Nama Motherboard", domain=[('category', '=', 'motherboard')], store=True)
    pmr_mainboard_bool_upgrade = fields.Boolean(string="Upgrade Motherboard")
    pmr_mainboard_upgrade = fields.Many2one('pmr.itms.inventory.it',string="Nama Motherboard", domain=[('category', '=', 'motherboard')], store=True)
    pmr_hardisk_1 = fields.Char(string="Hardisk 1", store=True)
    pmr_hardisk_1_adjustment = fields.Boolean(string="Adjustment Hardisk 1")
    pmr_hardisk_bool_replacement_1 = fields.Boolean(string="Replacement Hardisk 1")
    pmr_hardisk_1_replacement = fields.Many2one('pmr.itms.inventory.it',string="Nama Hardisk Replacment", domain=[('category', '=', 'hardisk')], store=True)
    pmr_hardisk_bool_upgrade_1 = fields.Boolean(string="Upgrade Hardisk 1")
    pmr_hardisk_1_upgrade = fields.Many2one('pmr.itms.inventory.it',string="Nama Hardisk Upgrade", domain=[('category', '=', 'hardisk')], store=True)
    pmr_hardisk_2 = fields.Char(string="Hardisk 2", store=True)
    pmr_hardisk_2_adjustment = fields.Boolean(string="Adjustment Hardisk 2")
    pmr_hardisk_bool_replacement_2 = fields.Boolean(string="Replacement Hardisk 2")
    pmr_hardisk_2_replacement = fields.Many2one('pmr.itms.inventory.it',string="Nama Hardisk Replacment", domain=[('category', '=', 'hardisk')], store=True)
    pmr_hardisk_bool_upgrade_2 = fields.Boolean(string="Upgrade Hardisk 2")
    pmr_hardisk_2_upgrade = fields.Many2one('pmr.itms.inventory.it',string="Nama Hardisk Upgrade", domain=[('category', '=', 'hardisk')], store=True)
    pmr_hardisk_3 = fields.Char(string="Hardisk 3", store=True)
    pmr_hardisk_3_adjustment = fields.Boolean(string="Adjustment Hardisk 3")
    pmr_hardisk_bool_replacement_3 = fields.Boolean(string="Replacement Hardisk 3")
    pmr_hardisk_3_replacement = fields.Many2one('pmr.itms.inventory.it',string="Nama Hardisk Replacment", domain=[('category', '=', 'hardisk')], store=True)
    pmr_hardisk_bool_upgrade_3 = fields.Boolean(string="Upgrade Hardisk 3")
    pmr_hardisk_3_upgrade = fields.Many2one('pmr.itms.inventory.it',string="Nama Hardisk Upgrade", domain=[('category', '=', 'hardisk')], store=True)
    pmr_hardisk_4 = fields.Char(string="Hardisk 4", store=True)
    pmr_hardisk_4_adjustment = fields.Boolean(string="Adjustment Hardisk 4")
    pmr_hardisk_bool_replacement_4 = fields.Boolean(string="Replacement Hardisk 4")
    pmr_hardisk_4_replacement = fields.Many2one('pmr.itms.inventory.it',string="Nama Hardisk Replacment", domain=[('category', '=', 'hardisk')], store=True)
    pmr_hardisk_bool_upgrade_4 = fields.Boolean(string="Upgrade Hardisk 4")
    pmr_hardisk_4_upgrade = fields.Many2one('pmr.itms.inventory.it',string="Nama Hardisk Upgrade", domain=[('category', '=', 'hardisk')], store=True)
    pmr_ram_1 = fields.Char(string="RAM 1", store=True)
    pmr_ram_1_adjustment = fields.Boolean(string="Adjustment RAM 1")
    pmr_ram_bool_replacement_1 = fields.Boolean(string="Replacement RAM 1")
    pmr_ram_1_replacement = fields.Many2one('pmr.itms.inventory.it',string="Nama RAM 1 Replacment", domain=[('category', '=', 'ram')], store=True)
    pmr_ram_bool_upgrade_1 = fields.Boolean(string="Upgrade RAM 1")
    pmr_ram_1_upgrade = fields.Many2one('pmr.itms.inventory.it',string="Nama RAM 1 Upgrade", domain=[('category', '=', 'ram')], store=True)
    pmr_ram_2 = fields.Char(string="RAM 2", store=True)
    pmr_ram_2_adjustment = fields.Boolean(string="Adjustment RAM 2")
    pmr_ram_bool_replacement_2 = fields.Boolean(string="Replacement RAM 2")
    pmr_ram_2_replacement = fields.Many2one('pmr.itms.inventory.it',string="Nama RAM 2 Replacment", domain=[('category', '=', 'ram')], store=True)
    pmr_ram_bool_upgrade_2 = fields.Boolean(string="Upgrade RAM 2")
    pmr_ram_2_upgrade = fields.Many2one('pmr.itms.inventory.it',string="Nama RAM 2 Upgrade", domain=[('category', '=', 'ram')], store=True)
    pmr_ram_3 = fields.Char(string="RAM 3", store=True)
    pmr_ram_3_adjustment = fields.Boolean(string="Adjustment RAM 3")
    pmr_ram_bool_replacement_3 = fields.Boolean(string="Replacement RAM 3")
    pmr_ram_3_replacement = fields.Many2one('pmr.itms.inventory.it',string="Nama RAM 3 Replacment", domain=[('category', '=', 'ram')], store=True)
    pmr_ram_bool_upgrade_3 = fields.Boolean(string="Upgrade RAM 3")
    pmr_ram_3_upgrade = fields.Many2one('pmr.itms.inventory.it',string="Nama RAM 3 Upgrade", domain=[('category', '=', 'ram')], store=True)
    pmr_ram_4 = fields.Char(string="RAM 4", store=True)
    pmr_ram_4_adjustment = fields.Boolean(string="Adjustment RAM 4")
    pmr_ram_bool_replacement_4 = fields.Boolean(string="Replacement RAM 4")
    pmr_ram_4_replacement = fields.Many2one('pmr.itms.inventory.it',string="Nama RAM 4 Replacment", domain=[('category', '=', 'ram')], store=True)
    pmr_ram_bool_upgrade_4 = fields.Boolean(string="Upgrade RAM 4")
    pmr_ram_4_upgrade = fields.Many2one('pmr.itms.inventory.it',string="Nama RAM 4 Upgrade", domain=[('category', '=', 'ram')], store=True)
    pmr_vga_1 = fields.Char(string="VGA 1", store=True)
    pmr_vga_1_adjustment = fields.Boolean(string="Adjustment VGA 1")
    pmr_vga_bool_replacement_1 = fields.Boolean(string="Replacement VGA 1")
    pmr_vga_1_replacement = fields.Many2one('pmr.vga', string="VGA 1 Replacment", store=True)
    pmr_vga_bool_upgrade_1 = fields.Boolean(string="Upgrade VGA 1")
    pmr_vga_1_upgrade = fields.Many2one('pmr.vga', string="VGA 1 Upgrade", store=True)
    pmr_vga_2 = fields.Char(string="VGA 2", store=True)
    pmr_vga_2_adjustment = fields.Boolean(string="Adjustment VGA 2")
    pmr_vga_bool_replacement_2 = fields.Boolean(string="Replacement VGA 2")
    pmr_vga_2_replacement = fields.Many2one('pmr.vga', string="VGA 2 Replacement", store=True)
    pmr_vga_bool_upgrade_2 = fields.Boolean(string="Upgrade VGA 2")
    pmr_vga_2_upgrade = fields.Many2one('pmr.vga', string="VGA 2 Upgrade", store=True)
    pmr_dvd_room_boolean = fields.Boolean(string="CD/DVD Room")
    pmr_ups_boolean = fields.Boolean(string="UPS")
    pmr_fdd = fields.Char(string="Expansion Slot", store=True)
    pmr_hdmi_boolean = fields.Boolean(string="HDMI")
    pmr_lan_card = fields.Char(string="Integrated LAN", store=True)
    pmr_casing = fields.Char(string="Casing", store=True)
    pmr_casing_adjustment = fields.Boolean(string="Adjustment Casing")
    pmr_casing_bool_replacement = fields.Boolean(string="Replacement casing")
    pmr_casing_replacement = fields.Many2one('pmr.itms.inventory.it',string="Nama Casing Replacment", domain=[('category', '=', 'casing')], store=True)
    pmr_casing_bool_upgrade = fields.Boolean(string="Upgrade Casing")
    pmr_casing_upgrade = fields.Many2one('pmr.itms.inventory.it',string="Nama Casing Upgrade", domain=[('category', '=', 'casing')], store=True)
    pmr_power_supply = fields.Char(string="Power Supply", store=True)
    pmr_power_supply_adjustment = fields.Boolean(string="Adjustment Power Supply")
    pmr_power_supply_bool_replacement = fields.Boolean(string="Replacement Power Supply")
    pmr_power_supply_replacement = fields.Many2one('pmr.itms.inventory.it',string="Nama Power Supply replacment", domain=[('category', '=', 'power_supply')], store=True)
    pmr_power_supply_bool_upgrade = fields.Boolean(string="Upgrade Power Supply")
    pmr_power_supply_upgrade = fields.Many2one('pmr.itms.inventory.it',string="Nama Power Supply Upgrade", domain=[('category', '=', 'power_supply')], store=True)
    pmr_keyboard = fields.Char(string="Keyboard", store=True)
    pmr_keyboard_adjustment = fields.Boolean(string="Adjustment Keyboard")
    pmr_keyboard_bool_replacement = fields.Boolean(string="Replacement Keyboard")
    pmr_keyboard_replacement = fields.Many2one('pmr.itms.inventory.it',string="Nama Keyboard replacment", domain=[('category', '=', 'keyboard')], store=True)
    pmr_keyboard_bool_upgrade = fields.Boolean(string="Upgrade Keyboard")
    pmr_keyboard_upgrade = fields.Many2one('pmr.itms.inventory.it',string="Nama Keyboard Upgrade", domain=[('category', '=', 'keyboard')], store=True)
    pmr_mouse = fields.Char(string="Mouse", store=True)
    pmr_mouse_adjustment = fields.Boolean(string="Adjustment Mouse")
    pmr_mouse_bool_replacement = fields.Boolean(string="Replacement Mouse")
    pmr_mouse_replacement = fields.Many2one('pmr.itms.inventory.it',string="Nama Mouse replacment", domain=[('category', '=', 'mouse')], store=True)
    pmr_mouse_bool_upgrade = fields.Boolean(string="Upgrade Mouse")
    pmr_mouse_upgrade = fields.Many2one('pmr.itms.inventory.it',string="Nama Mouse Upgrade", domain=[('category', '=', 'mouse')], store=True)
    pmr_monitor = fields.Char(string="Monitor", store=True)
    pmr_monitor_adjustment = fields.Boolean(string="Adjustment Monitor")
    pmr_monitor_bool_replacement = fields.Boolean(string="Replacement Monitor")
    pmr_monitor_replacement = fields.Many2one('pmr.itms.inventory.it',string="Nama Monitor Replacment", domain=[('category', '=', 'monitor')], store=True)
    pmr_monitor_bool_upgrade = fields.Boolean(string="Upgrade Monitor")
    pmr_monitor_upgrade = fields.Many2one('pmr.itms.inventory.it',string="Nama Monitor Upgrade", domain=[('category', '=', 'monitor')], store=True)
    pmr_ups = fields.Many2one('pmr.ups', string="UPS", store=True)
    pmr_printer = fields.Many2one('pmr.itms.inventory.it',string="Nama Printer", domain=[('category', '=', 'printer')], store=True)
    pmr_operating_system = fields.Many2one('pmr.os', string="Operating System", store=True)
    pmr_sn_operating_system = fields.Char(string="SN Operating System", store=True)
    pmr_office = fields.Many2one('pmr.office', string="Office", store=True)
    pmr_cad = fields.Many2one('pmr.cad', string="CAD", store=True)
    pmr_cam = fields.Many2one('pmr.cam', string="CAM", store=True)
    pmr_antivirus = fields.Many2one('pmr.antivirus',string="Antivirus", store=True)
    product_type = fields.Selection([
        ('pc_laptop', 'PC'),
        ('laptop', 'Laptop'),
    ], string="Device Type", tracking=True, store=True)
    state = fields.Selection([
        ('non', 'Non Aktif'),
        ('aktif', 'Aktif'),
    ], string="State", default="non", tracking=True, store=True)
    pmr_program_lain = fields.Many2many('pmr.software.lain',string="Software Lain")
    pmr_vga_type_1 = fields.Char(string="Type", store=True)
    pmr_vga_type_2 = fields.Char(string="Type", store=True)
    pmr_vga_type_1_replace = fields.Char(string="Type Replace 1", compute="_compute_vga_type", store=True)
    pmr_vga_type_2_replace = fields.Char(string="Type Replace 2", compute="_compute_vga_type", store=True)
    pmr_vga_type_1_upgrade = fields.Char(string="Type Upgrade 1", compute="_compute_vga_type", store=True)
    pmr_vga_type_2_upgrade = fields.Char(string="Type Upgrade 2", compute="_compute_vga_type", store=True)
    pmr_lan_card_type = fields.Char(string="Type", store=True)
    pmr_fdd_type = fields.Char(string="Type", compute="_compute_fdd_type", store=True)
    pmr_usb_2_0_port =fields.Boolean(string="USB 2.0 Port")
    pmr_usb_3_0_port =fields.Boolean(string="USB 3.0 Port")
    pmr_vga_port =fields.Boolean(string="VGA Port")
    pmr_hdmi_port =fields.Boolean(string="HDMI Port")
    pmr_display_port =fields.Boolean(string="Display Port")
    pmr_rj45_port =fields.Boolean(string="RJ45 Port")
    pmr_3_in_1_audio_port =fields.Boolean(string="3-in-1 Audio Port")
    pmr_io_interface = fields.Char(string="I/O Interface", default="I/O Interface")
    pmr_log_notes = fields.Text(string="Log Notes")

    # @api.model
    # def create(self, vals):
    #     if vals.get('pmr_name_pc_laptop'):
    #         pc_laptop = self.env['pmr.itms.product.it'].browse(vals['pmr_name_pc_laptop'])
    #         vals.update({
    #             'pmr_processor': pc_laptop.pmr_processor,
    #             'pmr_mainboard': pc_laptop.pmr_mainboard,
    #             'pmr_power_supply': pc_laptop.pmr_power_supply,
    #             'pmr_mouse': pc_laptop.pmr_mouse,
    #             'pmr_casing': pc_laptop.pmr_casing,
    #             'pmr_keyboard': pc_laptop.pmr_keyboard,
    #             'pmr_monitor': pc_laptop.pmr_monitor,
    #             'pmr_lan_card': pc_laptop.pmr_lan_card,
    #             'pmr_lan_card_type': pc_laptop.pmr_lan_card_type,
    #             'pmr_fdd': pc_laptop.pmr_fdd,
    #             'pmr_dvd_room_boolean': pc_laptop.pmr_dvd_room_boolean,
    #             'pmr_hdmi_boolean': pc_laptop.pmr_hdmi_boolean,
    #             'pmr_ups_boolean': pc_laptop.pmr_ups_boolean,
    #             'pmr_usb_2_0_port': pc_laptop.pmr_usb_2_0_port,
    #             'pmr_usb_3_0_port': pc_laptop.pmr_usb_3_0_port,
    #             'pmr_vga_port': pc_laptop.pmr_vga_port,
    #             'pmr_hdmi_port': pc_laptop.pmr_hdmi_port,
    #             'pmr_display_port': pc_laptop.pmr_display_port,
    #             'pmr_rj45_port': pc_laptop.pmr_rj45_port,
    #             'pmr_3_in_1_audio_port': pc_laptop.pmr_3_in_1_audio_port,
    #             'pmr_ram_1': pc_laptop.pmr_ram_1,
    #             'pmr_ram_2': pc_laptop.pmr_ram_2,
    #             'pmr_ram_3': pc_laptop.pmr_ram_3,
    #             'pmr_ram_4': pc_laptop.pmr_ram_4,
    #             'pmr_hardisk_1': pc_laptop.pmr_hardisk_1,
    #             'pmr_hardisk_2': pc_laptop.pmr_hardisk_2,
    #             'pmr_hardisk_3': pc_laptop.pmr_hardisk_3,
    #             'pmr_hardisk_4': pc_laptop.pmr_hardisk_4,
    #             'pmr_vga_1': pc_laptop.pmr_vga_1,
    #             'pmr_vga_2': pc_laptop.pmr_vga_2,
    #             'pmr_vga_type_1': pc_laptop.pmr_vga_type_1,
    #             'pmr_vga_type_2': pc_laptop.pmr_vga_type_2,
    #         })
    #     return super(PmrItmsProductIt, self).create(vals)

    # def write(self, vals):
    #     if vals.get('pmr_name_pc_laptop'):
    #         pc_laptop = self.env['pmr.itms.product.it'].browse(vals['pmr_name_pc_laptop'])
    #         vals.update({
    #             'pmr_processor': pc_laptop.pmr_processor,
    #             'pmr_mainboard': pc_laptop.pmr_mainboard,
    #             'pmr_power_supply': pc_laptop.pmr_power_supply,
    #             'pmr_mouse': pc_laptop.pmr_mouse,
    #             'pmr_casing': pc_laptop.pmr_casing,
    #             'pmr_keyboard': pc_laptop.pmr_keyboard,
    #             'pmr_monitor': pc_laptop.pmr_monitor,
    #             'pmr_lan_card': pc_laptop.pmr_lan_card,
    #             'pmr_lan_card_type': pc_laptop.pmr_lan_card_type,
    #             'pmr_fdd': pc_laptop.pmr_fdd,
    #             'pmr_dvd_room_boolean': pc_laptop.pmr_dvd_room_boolean,
    #             'pmr_hdmi_boolean': pc_laptop.pmr_hdmi_boolean,
    #             'pmr_ups_boolean': pc_laptop.pmr_ups_boolean,
    #             'pmr_usb_2_0_port': pc_laptop.pmr_usb_2_0_port,
    #             'pmr_usb_3_0_port': pc_laptop.pmr_usb_3_0_port,
    #             'pmr_vga_port': pc_laptop.pmr_vga_port,
    #             'pmr_hdmi_port': pc_laptop.pmr_hdmi_port,
    #             'pmr_display_port': pc_laptop.pmr_display_port,
    #             'pmr_rj45_port': pc_laptop.pmr_rj45_port,
    #             'pmr_3_in_1_audio_port': pc_laptop.pmr_3_in_1_audio_port,
    #             'pmr_ram_1': pc_laptop.pmr_ram_1,
    #             'pmr_ram_2': pc_laptop.pmr_ram_2,
    #             'pmr_ram_3': pc_laptop.pmr_ram_3,
    #             'pmr_ram_4': pc_laptop.pmr_ram_4,
    #             'pmr_hardisk_1': pc_laptop.pmr_hardisk_1,
    #             'pmr_hardisk_2': pc_laptop.pmr_hardisk_2,
    #             'pmr_hardisk_3': pc_laptop.pmr_hardisk_3,
    #             'pmr_hardisk_4': pc_laptop.pmr_hardisk_4,
    #             'pmr_vga_1': pc_laptop.pmr_vga_1,
    #             'pmr_vga_2': pc_laptop.pmr_vga_2,
    #             'pmr_vga_type_1': pc_laptop.pmr_vga_type_1,
    #             'pmr_vga_type_2': pc_laptop.pmr_vga_type_2,
    #         })
    #     return super(PmrItmsProductIt, self).write(vals)
    
    @api.onchange('pmr_name_pc_laptop')
    def _onchange_pmr_name_pc_laptop(self):
        if self.pmr_name_pc_laptop:
            self.pmr_processor = self.pmr_name_pc_laptop.pmr_processor
            self.pmr_mainboard = self.pmr_name_pc_laptop.pmr_mainboard
            self.pmr_power_supply = self.pmr_name_pc_laptop.pmr_power_supply
            self.pmr_mouse = self.pmr_name_pc_laptop.pmr_mouse
            self.pmr_casing = self.pmr_name_pc_laptop.pmr_casing
            self.pmr_keyboard = self.pmr_name_pc_laptop.pmr_keyboard
            self.pmr_monitor = self.pmr_name_pc_laptop.pmr_monitor
            self.pmr_lan_card = self.pmr_name_pc_laptop.pmr_lan_card
            self.pmr_lan_card_type = self.pmr_name_pc_laptop.pmr_lan_card_type
            self.pmr_fdd = self.pmr_name_pc_laptop.pmr_fdd
            self.pmr_dvd_room_boolean = self.pmr_name_pc_laptop.pmr_dvd_room_boolean
            self.pmr_hdmi_boolean = self.pmr_name_pc_laptop.pmr_hdmi_boolean
            self.pmr_ups_boolean = self.pmr_name_pc_laptop.pmr_ups_boolean
            self.pmr_usb_2_0_port = self.pmr_name_pc_laptop.pmr_usb_2_0_port
            self.pmr_usb_3_0_port = self.pmr_name_pc_laptop.pmr_usb_3_0_port
            self.pmr_vga_port = self.pmr_name_pc_laptop.pmr_vga_port
            self.pmr_hdmi_port = self.pmr_name_pc_laptop.pmr_hdmi_port
            self.pmr_display_port = self.pmr_name_pc_laptop.pmr_display_port
            self.pmr_rj45_port = self.pmr_name_pc_laptop.pmr_rj45_port
            self.pmr_3_in_1_audio_port = self.pmr_name_pc_laptop.pmr_3_in_1_audio_port
            self.pmr_ram_1 = self.pmr_name_pc_laptop.pmr_ram_1
            self.pmr_ram_2 = self.pmr_name_pc_laptop.pmr_ram_2
            self.pmr_ram_3 = self.pmr_name_pc_laptop.pmr_ram_3
            self.pmr_ram_4 = self.pmr_name_pc_laptop.pmr_ram_4
            self.pmr_hardisk_1 = self.pmr_name_pc_laptop.pmr_hardisk_1
            self.pmr_hardisk_2 = self.pmr_name_pc_laptop.pmr_hardisk_2
            self.pmr_hardisk_3 = self.pmr_name_pc_laptop.pmr_hardisk_3
            self.pmr_hardisk_4 = self.pmr_name_pc_laptop.pmr_hardisk_4
            self.pmr_vga_1 = self.pmr_name_pc_laptop.pmr_vga_1
            self.pmr_vga_2 = self.pmr_name_pc_laptop.pmr_vga_2
            self.pmr_vga_type_1 = self.pmr_name_pc_laptop.pmr_vga_type_1
            self.pmr_vga_type_2 = self.pmr_name_pc_laptop.pmr_vga_type_2

    # @api.onchange('pmr_name_pc_laptop')
    # def _onchange_pmr_name_pc_laptop(self):
    #     if self.pmr_name_pc_laptop:
    #         self._set_pc_laptop_fields()
    #     else:
    #         self.product_unit_category = False  
    #         self.pmr_processor = False  
    #         self.pmr_mainboard = False  
    #         self.pmr_power_supply = False  
    #         self.pmr_mouse = False  
    #         self.pmr_casing = False  
    #         self.pmr_keyboard = False  
    #         self.pmr_monitor = False  
    #         self.pmr_lan_card = False  
    #         self.pmr_lan_card_type = False  
    #         self.pmr_fdd = False  
    #         self.pmr_dvd_room_boolean = False  
    #         self.pmr_hdmi_boolean = False  
    #         self.pmr_ups_boolean = False  
    #         self.pmr_usb_2_0_port = False  
    #         self.pmr_usb_3_0_port = False  
    #         self.pmr_vga_port = False  
    #         self.pmr_hdmi_port = False  
    #         self.pmr_display_port = False
    #         self.pmr_rj45_port = False
    #         self.pmr_3_in_1_audio_port = False
    #         self.pmr_ram_1 = False
    #         self.pmr_ram_2 = False
    #         self.pmr_ram_3 = False
    #         self.pmr_ram_4 = False
    #         self.pmr_hardisk_1 = False
    #         self.pmr_hardisk_2 = False
    #         self.pmr_hardisk_3 = False
    #         self.pmr_hardisk_4 = False
    #         self.pmr_vga_1 = False
    #         self.pmr_vga_2 = False
    #         self.pmr_vga_type_1 = False
    #         self.pmr_vga_type_2 = False

    # def _set_pc_laptop_fields(self):
    #     self.product_unit_category = self.pmr_name_pc_laptop.product_unit_category 
    #     self.pmr_processor = self.pmr_name_pc_laptop.pmr_processor.name if self.pmr_name_pc_laptop.pmr_processor else ''
    #     self.pmr_mainboard = self.pmr_name_pc_laptop.pmr_mainboard.name if self.pmr_name_pc_laptop.pmr_mainboard else ''
    #     self.pmr_power_supply = self.pmr_name_pc_laptop.pmr_power_supply.name if self.pmr_name_pc_laptop.pmr_power_supply else ''
    #     self.pmr_mouse = self.pmr_name_pc_laptop.pmr_mouse.name if self.pmr_name_pc_laptop.pmr_mouse else ''
    #     self.pmr_casing = self.pmr_name_pc_laptop.pmr_casing.name if self.pmr_name_pc_laptop.pmr_casing else ''
    #     self.pmr_keyboard = self.pmr_name_pc_laptop.pmr_keyboard.name if self.pmr_name_pc_laptop.pmr_keyboard else ''
    #     self.pmr_monitor = self.pmr_name_pc_laptop.pmr_monitor.name if self.pmr_name_pc_laptop.pmr_monitor else ''
    #     self.pmr_lan_card = self.pmr_name_pc_laptop.pmr_lan_card.name if self.pmr_name_pc_laptop.pmr_lan_card else ''
    #     self.pmr_lan_card_type = self.pmr_name_pc_laptop.pmr_lan_card_type
    #     self.pmr_fdd = self.pmr_name_pc_laptop.pmr_fdd.name if self.pmr_name_pc_laptop.pmr_fdd else ''
    #     self.pmr_ram_1 = self.pmr_name_pc_laptop.pmr_ram_1.name if self.pmr_name_pc_laptop.pmr_ram_1 else ''
    #     self.pmr_ram_2 = self.pmr_name_pc_laptop.pmr_ram_2.name if self.pmr_name_pc_laptop.pmr_ram_2 else ''
    #     self.pmr_ram_3 = self.pmr_name_pc_laptop.pmr_ram_3.name if self.pmr_name_pc_laptop.pmr_ram_3 else ''
    #     self.pmr_ram_4 = self.pmr_name_pc_laptop.pmr_ram_4.name if self.pmr_name_pc_laptop.pmr_ram_4 else ''
    #     self.pmr_hardisk_1 = self.pmr_name_pc_laptop.pmr_hardisk_1.name if self.pmr_name_pc_laptop.pmr_hardisk_1 else ''
    #     self.pmr_hardisk_2 = self.pmr_name_pc_laptop.pmr_hardisk_2.name if self.pmr_name_pc_laptop.pmr_hardisk_2 else ''
    #     self.pmr_hardisk_3 = self.pmr_name_pc_laptop.pmr_hardisk_3.name if self.pmr_name_pc_laptop.pmr_hardisk_3 else ''
    #     self.pmr_hardisk_4 = self.pmr_name_pc_laptop.pmr_hardisk_4.name if self.pmr_name_pc_laptop.pmr_hardisk_4 else ''
    #     self.pmr_vga_1 = self.pmr_name_pc_laptop.pmr_vga_1.name if self.pmr_name_pc_laptop.pmr_vga_1 else ''
    #     self.pmr_vga_2 = self.pmr_name_pc_laptop.pmr_vga_2.name if self.pmr_name_pc_laptop.pmr_vga_2 else ''
    #     self.pmr_vga_type_1 = self.pmr_name_pc_laptop.pmr_vga_type_1
    #     self.pmr_vga_type_2 = self.pmr_name_pc_laptop.pmr_vga_type_2
    #     self.pmr_dvd_room_boolean = self.pmr_name_pc_laptop.pmr_dvd_room_boolean
    #     self.pmr_hdmi_boolean = self.pmr_name_pc_laptop.pmr_hdmi_boolean
    #     self.pmr_ups_boolean = self.pmr_name_pc_laptop.pmr_hdmi_boolean
    #     self.pmr_usb_2_0_port = self.pmr_name_pc_laptop.pmr_usb_2_0_port
    #     self.pmr_usb_3_0_port = self.pmr_name_pc_laptop.pmr_usb_3_0_port
    #     self.pmr_vga_port = self.pmr_name_pc_laptop.pmr_vga_port
    #     self.pmr_hdmi_port = self.pmr_name_pc_laptop.pmr_hdmi_port
    #     self.pmr_display_port = self.pmr_name_pc_laptop.pmr_display_port
    #     self.pmr_rj45_port = self.pmr_name_pc_laptop.pmr_rj45_port
    #     self.pmr_3_in_1_audio_port = self.pmr_name_pc_laptop.pmr_rj45_port

    # @api.model
    # def create(self, vals):
    #     record = super(PmrItmsProductIt, self).create(vals)

    #     if record.pmr_name_pc_laptop:
    #         record._set_pc_laptop_fields()

    #     return record

    # def write(self, vals):
    #     res = super(PmrItmsProductIt, self).write(vals)

    #     if 'pmr_name_pc_laptop' in vals:
    #         for record in self:
    #             if record.pmr_name_pc_laptop:
    #                 record._set_pc_laptop_fields()

    #     return res
    def action_pc(self):
        for record in self:
            self.env['pmr.itms.inventory.movement'].create({
                'name_product': record.pmr_name_pc_laptop.display_name if record.pmr_name_pc_laptop else record.name,
                'pmr_itms_departement': record.pmr_itms_departement.id,
                'pmr_itms_user': record.pmr_itms_user.id,
                'pmr_quantity_product_it': -abs(record.pmr_quantity_product_it),
                'product_unit_category': record.product_unit_category.id,
                'product_location_unit': record.pmr_name_pc_laptop.product_location_unit.id,
            })
            record.state = 'non'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sukses',
                'message': 'Data berhasil dikirim',
                'sticky': False,
            }
        }
    @api.depends('pmr_vga_1_replacement', 'pmr_vga_1_replacement.pmr_onboard', 'pmr_vga_1_replacement.pmr_pci',
                'pmr_vga_2_replacement', 'pmr_vga_2_replacement.pmr_onboard', 'pmr_vga_2_replacement.pmr_pci',
                'pmr_vga_1_upgrade', 'pmr_vga_1_upgrade.pmr_onboard', 'pmr_vga_1_upgrade.pmr_pci',
                'pmr_vga_2_upgrade', 'pmr_vga_2_upgrade.pmr_onboard', 'pmr_vga_2_upgrade.pmr_pci',)
    def _compute_vga_type(self):
        for record in self:            
            vga_1_types_replace = []
            if record.pmr_vga_1_replacement:
                if record.pmr_vga_1_replacement.pmr_onboard:
                    vga_1_types_replace.append("Onboard")
                if record.pmr_vga_1_replacement.pmr_pci:
                    vga_1_types_replace.append("External")
            record.pmr_vga_type_1_replace = " dan ".join(vga_1_types_replace) if vga_1_types_replace else ""

            vga_1_types_upgrade = []
            if record.pmr_vga_1_upgrade:
                if record.pmr_vga_1_upgrade.pmr_onboard:
                    vga_1_types_upgrade.append("Onboard")
                if record.pmr_vga_1_upgrade.pmr_pci:
                    vga_1_types_upgrade.append("External")
            record.pmr_vga_type_1_upgrade = " dan ".join(vga_1_types_upgrade) if vga_1_types_upgrade else ""

            vga_2_types_replace = []
            if record.pmr_vga_2_replacement:
                if record.pmr_vga_2_replacement.pmr_onboard:
                    vga_2_types_replace.append("Onboard")
                if record.pmr_vga_2_replacement.pmr_pci:
                    vga_2_types_replace.append("External")
            record.pmr_vga_type_2_replace = " dan ".join(vga_2_types_replace) if vga_2_types_replace else ""

            vga_2_types_upgrade = []
            if record.pmr_vga_2_upgrade:
                if record.pmr_vga_2_upgrade.pmr_onboard:
                    vga_2_types_upgrade.append("Onboard")
                if record.pmr_vga_2_upgrade.pmr_pci:
                    vga_2_types_upgrade.append("External")
            record.pmr_vga_type_2_upgrade = " dan ".join(vga_2_types_upgrade) if vga_2_types_upgrade else ""

    @api.onchange('pmr_itms_user')
    def _onchange_pmr_itms_user(self):
        if self.pmr_itms_user:
            self.pmr_ip_address = self.pmr_itms_user.ip_address 
            self.pmr_office_location = self.pmr_itms_user.office_location
        else:
            self.pmr_ip_address = False  
            self.pmr_office_location = False

    @api.onchange('pmr_processor_upgrade')
    def _onchange_pmr_processor_upgrade(self):
        """Handle upgrade of pmr_processor with colored text."""
        if self.pmr_processor_upgrade:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_processor or "There isn't any"
            new_processor = self.pmr_processor_upgrade
            log_entry = f"[{timestamp}] 🟢 Upgrade Processor: {previous_processor} → {new_processor.name}"

            self.pmr_processor = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_processor_replacement')
    def _onchange_pmr_processor_replacement(self):
        """Handle replacement of pmr_processor with colored text."""
        if self.pmr_processor_replacement:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_processor or "There isn't any"
            new_processor = self.pmr_processor_replacement 
            log_entry = f"[{timestamp}] 🔴 Replacement Processor: {previous_processor} → {new_processor.name}"

            self.pmr_processor = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_mainboard_upgrade')
    def _onchange_pmr_mainboard_upgrade(self):
        """Handle upgrade of pmr_mainboard with colored text."""
        if self.pmr_mainboard_upgrade:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_mainboard or "There isn't any"
            new_processor = self.pmr_mainboard_upgrade
            log_entry = f"[{timestamp}] 🟢 Upgrade Mainboard: {previous_processor} → {new_processor.name}"

            self.pmr_mainboard = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_mainboard_replacement')
    def _onchange_pmr_mainboard_replacement(self):
        """Handle replacement of pmr_mainboard with colored text."""
        if self.pmr_mainboard_replacement:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_mainboard or "There isn't any"
            new_processor = self.pmr_mainboard_replacement
            log_entry = f"[{timestamp}] 🔴 Replacement Mainboard: {previous_processor} → {new_processor.name}"

            self.pmr_mainboard = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_ram_1_upgrade')
    def _onchange_pmr_ram_1_upgrade(self):
        """Handle upgrade of pmr_ram_1 with colored text."""
        if self.pmr_ram_1_upgrade:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_ram_1 or "There isn't any"
            new_processor = self.pmr_ram_1_upgrade
            log_entry = f"[{timestamp}] 🟢 Upgrade RAM 1: {previous_processor} → {new_processor.name}"

            self.pmr_ram_1 = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_ram_1_replacement')
    def _onchange_pmr_ram_1_replacement(self):
        """Handle replacement of pmr_ram_1 with colored text."""
        if self.pmr_ram_1_replacement:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_ram_1 or "There isn't any"
            new_processor = self.pmr_ram_1_replacement
            log_entry = f"[{timestamp}] 🔴 Replacement RAM 1: {previous_processor} → {new_processor.name}"

            self.pmr_ram_1 = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"
    
    @api.onchange('pmr_ram_2_upgrade')
    def _onchange_pmr_ram_2_upgrade(self):
        """Handle upgrade of pmr_ram_1 with colored text."""
        if self.pmr_ram_2_upgrade:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_ram_2 or "There isn't any"
            new_processor = self.pmr_ram_2_upgrade
            log_entry = f"[{timestamp}] 🟢 Upgrade RAM 2: {previous_processor} → {new_processor.name}"

            self.pmr_ram_2 = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_ram_2_replacement')
    def _onchange_pmr_ram_2_replacement(self):
        """Handle replacement of pmr_ram_2 with colored text."""
        if self.pmr_ram_2_replacement:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_ram_2 or "There isn't any"
            new_processor = self.pmr_ram_2_replacement
            log_entry = f"[{timestamp}] 🔴 Replacement RAM 2: {previous_processor} → {new_processor.name}"

            self.pmr_ram_2 = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_ram_3_upgrade')
    def _onchange_pmr_ram_3_upgrade(self):
        """Handle upgrade of pmr_ram_1 with colored text."""
        if self.pmr_ram_3_upgrade:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_ram_3 or "There isn't any"
            new_processor = self.pmr_ram_3_upgrade
            log_entry = f"[{timestamp}] 🟢 Upgrade RAM 3: {previous_processor} → {new_processor.name}"

            self.pmr_ram_3 = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_ram_3_replacement')
    def _onchange_pmr_ram_3_replacement(self):
        """Handle replacement of pmr_ram_3 with colored text."""
        if self.pmr_ram_3_replacement:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_ram_3 or "There isn't any"
            new_processor = self.pmr_ram_3_replacement
            log_entry = f"[{timestamp}] 🔴 Replacement RAM 3: {previous_processor} → {new_processor.name}"

            self.pmr_ram_3 = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"
    
    @api.onchange('pmr_ram_4_upgrade')
    def _onchange_pmr_ram_4_upgrade(self):
        """Handle upgrade of pmr_ram_1 with colored text."""
        if self.pmr_ram_4_upgrade:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_ram_4 or "There isn't any"
            new_processor = self.pmr_ram_4_upgrade
            log_entry = f"[{timestamp}] 🟢 Upgrade RAM 4: {previous_processor} → {new_processor.name}"

            self.pmr_ram_4 = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_ram_4_replacement')
    def _onchange_pmr_ram_4_replacement(self):
        """Handle replacement of pmr_ram_4 with colored text."""
        if self.pmr_ram_4_replacement:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_ram_4 or "There isn't any"
            new_processor = self.pmr_ram_4_replacement
            log_entry = f"[{timestamp}] 🔴 Replacement RAM 4: {previous_processor} → {new_processor.name}"

            self.pmr_ram_4 = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"
    
    @api.onchange('pmr_power_supply_upgrade')
    def _onchange_pmr_power_supply_upgrade(self):
        """Handle upgrade of pmr_ram_1 with colored text."""
        if self.pmr_power_supply_upgrade:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_power_supply or "There isn't any"
            new_processor = self.pmr_power_supply_upgrade
            log_entry = f"[{timestamp}] 🟢 Upgrade Power Supply: {previous_processor} → {new_processor.name}"

            self.pmr_power_supply = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_power_supply_replacement')
    def _onchange_pmr_power_supply_replacement(self):
        """Handle replacement of pmr_power_supply with colored text."""
        if self.pmr_power_supply_replacement:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_power_supply or "There isn't any"
            new_processor = self.pmr_power_supply_replacement
            log_entry = f"[{timestamp}] 🔴 Replacement Power Supply: {previous_processor} → {new_processor.name}"

            self.pmr_power_supply = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"
    
    @api.onchange('pmr_vga_1_upgrade')
    def _onchange_pmr_vga_1_upgrade(self):
        """Handle upgrade of pmr_ram_1 with colored text."""
        if self.pmr_vga_1_upgrade:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_vga_1 = self.pmr_vga_1 or "There isn't any"
            new_vga_1 = self.pmr_vga_1_upgrade
            log_entry = f"[{timestamp}] 🟢 Upgrade VGA 1: {previous_vga_1} → {new_vga_1.name}"

            self.pmr_vga_1 = new_vga_1.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_vga_1_replacement')
    def _onchange_pmr_vga_1_replacement(self):
        """Handle replacement of pmr_vga_1 with colored text."""
        if self.pmr_vga_1_replacement:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_vga_1 = self.pmr_vga_1 or "There isn't any"
            new_vga_1 = self.pmr_vga_1_replacement
            log_entry = f"[{timestamp}] 🔴 Replacement VGA 1: {previous_vga_1} → {new_vga_1.name}"

            self.pmr_vga_1 = new_vga_1.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_vga_2_upgrade')
    def _onchange_pmr_vga_2_upgrade(self):
        """Handle upgrade of pmr_ram_2 with colored text."""
        if self.pmr_vga_2_upgrade:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_vga_2 or "There isn't any"
            new_processor = self.pmr_vga_2_upgrade
            log_entry = f"[{timestamp}] 🟢 Upgrade VGA 2: {previous_processor} → {new_processor.name}"

            self.pmr_vga_2 = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_vga_2_replacement')
    def _onchange_pmr_vga_2_replacement(self):
        """Handle replacement of pmr_vga_2 with colored text."""
        if self.pmr_vga_2_replacement:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_vga_2 or "There isn't any"
            new_processor = self.pmr_vga_2_replacement
            log_entry = f"[{timestamp}] 🔴 Replacement VGA 2: {previous_processor} → {new_processor.name}"

            self.pmr_vga_2 = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_hardisk_1_upgrade')
    def _onchange_pmr_hardisk_1_upgrade(self):
        """Handle upgrade of pmr_ram_2 with colored text."""
        if self.pmr_hardisk_1_upgrade:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_hardisk_1 or "There isn't any"
            new_processor = self.pmr_hardisk_1_upgrade
            log_entry = f"[{timestamp}] 🟢 Upgrade Hardisk 1: {previous_processor} → {new_processor.name}"

            self.pmr_hardisk_1 = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_hardisk_1_replacement')
    def _onchange_pmr_hardisk_1_replacement(self):
        """Handle replacement of pmr_hardisk_1 with colored text."""
        if self.pmr_hardisk_1_replacement:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_hardisk_1 or "There isn't any"
            new_processor = self.pmr_hardisk_1_replacement
            log_entry = f"[{timestamp}] 🔴 Replacement Hardisk 1: {previous_processor} → {new_processor.name}"

            self.pmr_hardisk_1 = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_hardisk_2_upgrade')
    def _onchange_pmr_hardisk_2_upgrade(self):
        """Handle upgrade of pmr_ram_2 with colored text."""
        if self.pmr_hardisk_2_upgrade:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_hardisk_2 or "There isn't any"
            new_processor = self.pmr_hardisk_2_upgrade
            log_entry = f"[{timestamp}] 🟢 Upgrade Hardisk 2: {previous_processor} → {new_processor.name}"

            self.pmr_hardisk_2 = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_hardisk_2_replacement')
    def _onchange_pmr_hardisk_2_replacement(self):
        """Handle replacement of pmr_hardisk_2 with colored text."""
        if self.pmr_hardisk_2_replacement:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_hardisk_2 or "There isn't any"
            new_processor = self.pmr_hardisk_2_replacement
            log_entry = f"[{timestamp}] 🔴 Replacement Hardisk 2: {previous_processor} → {new_processor.name}"

            self.pmr_hardisk_2 = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_hardisk_3_upgrade')
    def _onchange_pmr_hardisk_3_upgrade(self):
        """Handle upgrade of pmr_ram_2 with colored text."""
        if self.pmr_hardisk_3_upgrade:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_hardisk_3 or "There isn't any"
            new_processor = self.pmr_hardisk_3_upgrade
            log_entry = f"[{timestamp}] 🟢 Upgrade Hardisk 3: {previous_processor} → {new_processor.name}"

            self.pmr_hardisk_3 = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_hardisk_3_replacement')
    def _onchange_pmr_hardisk_3_replacement(self):
        """Handle replacement of pmr_hardisk_3 with colored text."""
        if self.pmr_hardisk_3_replacement:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_hardisk_3 or "There isn't any"
            new_processor = self.pmr_hardisk_3_replacement
            log_entry = f"[{timestamp}] 🔴 Replacement Hardisk 3: {previous_processor} → {new_processor.name}"

            self.pmr_hardisk_3 = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_hardisk_4_upgrade')
    def _onchange_pmr_hardisk_4_upgrade(self):
        """Handle upgrade of pmr_ram_2 with colored text."""
        if self.pmr_hardisk_4_upgrade:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_hardisk_4 or "There isn't any"
            new_processor = self.pmr_hardisk_4_upgrade
            log_entry = f"[{timestamp}] 🟢 Upgrade Hardisk 4: {previous_processor} → {new_processor.name}"

            self.pmr_hardisk_4 = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_hardisk_4_replacement')
    def _onchange_pmr_hardisk_4_replacement(self):
        """Handle replacement of pmr_hardisk_4 with colored text."""
        if self.pmr_hardisk_4_replacement:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_hardisk_4 or "There isn't any"
            new_processor = self.pmr_hardisk_4_replacement
            log_entry = f"[{timestamp}] 🔴 Replacement Hardisk 4: {previous_processor} → {new_processor.name}"

            self.pmr_hardisk_4 = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"
    
    @api.onchange('pmr_casing_upgrade')
    def _onchange_pmr_casing_upgrade(self):
        """Handle upgrade of pmr_casing with colored text."""
        if self.pmr_casing_upgrade:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_casing or "There isn't any"
            new_processor = self.pmr_casing_upgrade
            log_entry = f"[{timestamp}] 🟢 Upgrade Casing: {previous_processor} → {new_processor.name}"

            self.pmr_casing = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_casing_replacement')
    def _onchange_pmr_casing_replacement(self):
        """Handle replacement of pmr_casing with colored text."""
        if self.pmr_casing_replacement:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_casing or "There isn't any"
            new_processor = self.pmr_casing_replacement
            log_entry = f"[{timestamp}] 🔴 Replacement Casing: {previous_processor} → {new_processor.name}"

            self.pmr_casing = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"
    
    @api.onchange('pmr_keyboard_upgrade')
    def _onchange_pmr_keyboard_upgrade(self):
        """Handle upgrade of pmr_keyboard with colored text."""
        if self.pmr_keyboard_upgrade:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_keyboard or "There isn't any"
            new_processor = self.pmr_keyboard_upgrade
            log_entry = f"[{timestamp}] 🟢 Upgrade Keyboard: {previous_processor} → {new_processor.name}"

            self.pmr_keyboard = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_keyboard_replacement')
    def _onchange_pmr_keyboard_replacement(self):
        """Handle replacement of pmr_keyboard with colored text."""
        if self.pmr_keyboard_replacement:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_keyboard or "There isn't any"
            new_processor = self.pmr_keyboard_replacement
            log_entry = f"[{timestamp}] 🔴 Replacement Keyboard: {previous_processor} → {new_processor.name}"

            self.pmr_keyboard = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"
    
    @api.onchange('pmr_monitor_upgrade')
    def _onchange_pmr_monitor_upgrade(self):
        """Handle upgrade of pmr_monitor with colored text."""
        if self.pmr_monitor_upgrade:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_monitor or "There isn't any"
            new_processor = self.pmr_monitor_upgrade
            log_entry = f"[{timestamp}] 🟢 Upgrade Monitor: {previous_processor} → {new_processor.name}"

            self.pmr_monitor = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_monitor_replacement')
    def _onchange_pmr_monitor_replacement(self):
        """Handle replacement of pmr_monitor with colored text."""
        if self.pmr_monitor_replacement:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_monitor or "There isn't any"
            new_processor = self.pmr_monitor_replacement
            log_entry = f"[{timestamp}] 🔴 Replacement Monitor: {previous_processor} → {new_processor.name}"

            self.pmr_monitor = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"
    
    @api.onchange('pmr_mouse_upgrade')
    def _onchange_pmr_mouse_upgrade(self):
        """Handle upgrade of pmr_mouse with colored text."""
        if self.pmr_mouse_upgrade:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_mouse or "There isn't any"
            new_processor = self.pmr_mouse_upgrade
            log_entry = f"[{timestamp}] 🟢 Upgrade Mouse: {previous_processor} → {new_processor.name}"

            self.pmr_mouse = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.onchange('pmr_mouse_replacement')
    def _onchange_pmr_mouse_replacement(self):
        """Handle replacement of pmr_mouse with colored text."""
        if self.pmr_mouse_replacement:
            timestamp = fields.Datetime.now().strftime('%d-%m-%Y')
            previous_processor = self.pmr_mouse or "There isn't any"
            new_processor = self.pmr_mouse_replacement
            log_entry = f"[{timestamp}] 🔴 Replacement Mouse: {previous_processor} → {new_processor.name}"

            self.pmr_mouse = new_processor.name
            self.pmr_log_notes = (self.pmr_log_notes or '').strip() + f"\n\n{log_entry}"

    @api.depends('pmr_fdd', 'pmr_fdd.pmr_onboard', 'pmr_fdd.pmr_pci')
    def _compute_lan_card_type(self):
        for record in self:
            lan_card_types = []
            if record.pmr_fdd:
                if record.pmr_fdd.pmr_pci:
                    lan_card_types.append("External")
            record.pmr_fdd_type = lan_card_types if lan_card_types else ""

    @api.model
    def _cron_update_product_cpu_age(self):
        records = self.search([])
        for rec in records:
            if rec.pmr_create_date:
                today = date.today()
                create_date = rec.pmr_create_date.date()
                delta = relativedelta(today, create_date)
                days = (today - create_date).days

                rec.pmr_umur_product = days
                rec.pmr_umur_product_str = f"{delta.years} tahun, {delta.months} bulan, {delta.days} hari"
                rec.pmr_umur_product_str_year = f"{delta.years} tahun"

    def action_run_cron_manual(self):
        """Menjalankan cron secara manual"""
        self.env['pmr.itms.product.it']._cron_update_product_cpu_age()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Berhasil',
                'message': 'Jadwal diaktifkan.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_disable_cron(self):
        """Menonaktifkan cron dari ir.cron"""
        cron = self.env.ref('pmr_itms.ir_cron_pmr_update_product_cpu_age', raise_if_not_found=False)
        if cron:
            cron.write({'active': False})
            message = "Jadwal berhasil dinonaktifkan."
        else:
            message = "Jadwal tidak ditemukan."
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Info',
                'message': message,
                'type': 'warning',
                'sticky': False,
            }
        }

    def action_enable_cron(self):
        """Mengaktifkan ulang cron"""
        cron = self.env.ref('pmr_itms.ir_cron_pmr_update_product_cpu_age', raise_if_not_found=False)
        if cron:
            cron.write({'active': True})
            message = "Jadwal berhasil diaktifkan."
        else:
            message = "Jadwal tidak ditemukan."
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Info',
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }

    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product(self):
        for rec in self:
            if rec.pmr_create_date:
                today = fields.Date.context_today(rec)
                create_date = rec.pmr_create_date.date()
                age_days = (today - create_date).days
                rec.pmr_umur_product = age_days
            else:
                rec.pmr_umur_product = 0

    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product_str(self):
        for rec in self:
            if rec.pmr_create_date:
                today = fields.Date.context_today(rec)
                create_date = rec.pmr_create_date.date()
                delta = relativedelta(today, create_date)

                rec.pmr_umur_product_str = f"{delta.years} tahun, {delta.months} bulan, {delta.days} hari"
                rec.pmr_umur_product_str_year = f"{delta.years} tahun"
            else:
                rec.pmr_umur_product_str = "-"
                rec.pmr_umur_product_str_year = "-"

    # @api.depends('pmr_create_date')
    # def _compute_pmr_umur_product(self):
    #     """Calculates product age and ensures the result is not negative."""
    #     today_date = date.today() 
    #     for record in self:
    #         if record.pmr_create_date:
    #             create_date = record.pmr_create_date.date()
    #             record.pmr_umur_product = max((today_date - create_date).days, 0)
    #         else:
    #             record.pmr_umur_product = 0  
    
    # @api.depends('pmr_umur_product')
    # def _compute_pmr_umur_product_str(self):
    #     """Change pmr_umur_product to a string with the format 'X days'."""
    #     for record in self:
    #         record.pmr_umur_product_str = f"{record.pmr_umur_product} days"
    
    def generate_pc_laptop_sequence(self):
        for record in self:
            if record.product_type in ['pc_laptop', 'laptop']:
                suffix = "PC" if record.product_type == 'pc_laptop' else "LP"

                current_date = record.pmr_create_date or datetime.now()
                year_month = current_date.strftime('%y%m')

                last_barcode = self.env['pmr.barcode'].search([
                    ('name', 'like', f"{year_month}%{suffix}")
                ], order='name desc', limit=1)

                if last_barcode:
                    last_sequence = int(last_barcode.name[4:9]) + 1
                else:
                    last_sequence = 1

                sequence_str = str(last_sequence).zfill(5)
                barcode_name = f"{year_month}{sequence_str}{suffix}"

                barcode = self.env['pmr.barcode'].create({
                    'name': barcode_name,
                    'pmr_create_date': current_date,
                    'pmr_inventory_it': record.name  
                })

                record.pmr_barcode = barcode.id

    def action_generate_barcode(self):
        self.generate_pc_laptop_sequence()

    @api.depends('pmr_umur_product')
    def _compute_pmr_umur_product_str_year(self):
        """Convert pmr_umur_product into years format (X years, X months)."""
        for record in self:
            years = record.pmr_umur_product // 365
            months = (record.pmr_umur_product % 365) // 30  
            if years > 0 and months > 0:
                record.pmr_umur_product_str_year = f"{years} years {months} months"
            elif years > 0:
                record.pmr_umur_product_str_year = f"{years} years"
            elif months > 0:
                record.pmr_umur_product_str_year = f"{months} months"
            else:
                record.pmr_umur_product_str_year = "0 days"

class PmrItmsProductItAntivirus(models.Model):
    _name = "pmr.itms.product.it.antivirus"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Product IT Software"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    name = fields.Char(string="Personil IT", required=True, store=True)
    pmr_barcode = fields.Many2one('pmr.barcode', String="Barcode")
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_umur_product = fields.Integer(string="Product Age(Days)", compute="_compute_pmr_umur_product", store=True)
    pmr_umur_product_str = fields.Char(string="Product Age (Full)", compute="_compute_pmr_umur_product_str", store=True)
    pmr_umur_product_str_year = fields.Char(string="Product Age (Years)", compute="_compute_pmr_umur_product_str_year", store=True)
    pmr_itms_departement = fields.Many2one('hr.department', string="Departement", required=True, store=True)
    pmr_itms_user = fields.Many2one('pmr.itms.user', string="User", required=True)
    pmr_quantity_product_it = fields.Float(string="Quantity", required=True, default=1)
    pmr_asset = fields.Boolean(string="Asset", default=False)
    pmr_no_asset = fields.Char(string="Nomor Asset")
    pmr_no_sn= fields.Char(string="Serial Number")
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    pmr_antivirus = fields.Many2one('pmr.antivirus',string="Antivirus", store=True)
    product_category = fields.Many2one('pmr.product.category', string="Category",store=True)
    product_sub_category = fields.Many2one('pmr.product.sub.category', string="Sub Category", store=True)
    state = fields.Selection([
        ('not', 'Not State'),
        ('reject', 'Reject'),
        ('repair', 'Repair'),
        ('good', 'Good'),
    ], string="State", default="not", tracking=True, store=True)

    @api.model
    def _cron_update_product_age(self):
        records = self.search([])
        for rec in records:
            if rec.pmr_create_date:
                today = date.today()
                create_date = rec.pmr_create_date.date()
                delta = relativedelta(today, create_date)
                days = (today - create_date).days

                rec.pmr_umur_product = days
                rec.pmr_umur_product_str = f"{delta.years} tahun, {delta.months} bulan, {delta.days} hari"
                rec.pmr_umur_product_str_year = f"{delta.years} tahun"

    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product(self):
        for rec in self:
            if rec.pmr_create_date:
                today = fields.Date.context_today(rec)
                create_date = rec.pmr_create_date.date()
                age_days = (today - create_date).days
                rec.pmr_umur_product = age_days
            else:
                rec.pmr_umur_product = 0

    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product_str(self):
        for rec in self:
            if rec.pmr_create_date:
                today = fields.Date.context_today(rec)
                create_date = rec.pmr_create_date.date()
                delta = relativedelta(today, create_date)

                rec.pmr_umur_product_str = f"{delta.years} tahun, {delta.months} bulan, {delta.days} hari"
                rec.pmr_umur_product_str_year = f"{delta.years} tahun"
            else:
                rec.pmr_umur_product_str = "-"
                rec.pmr_umur_product_str_year = "-"
    
    def action_reject(self):
        self.state= 'reject'

    def action_repair(self):
        self.state = 'repair'

    def action_good(self):
        self.state= 'good'
    
    def generate_pc_laptop_sequence(self):
        for record in self:
            if record.product_type == 'switch':
                current_date = record.pmr_create_date or datetime.now()
                year_month = current_date.strftime('%y%m')

                last_barcode = self.env['pmr.barcode'].search([
                    ('name', 'like', f"{year_month}%SW")
                ], order='name desc', limit=1)

                if last_barcode:
                    last_sequence = int(last_barcode.name[4:9]) + 1
                else:
                    last_sequence = 1

                sequence_str = str(last_sequence).zfill(5)
                barcode_name = f"{year_month}{sequence_str}SW"

                barcode = self.env['pmr.barcode'].create({
                    'name': barcode_name,
                    'pmr_create_date': current_date,  
                    'pmr_inventory_it': record.name  
                })

                record.pmr_barcode = barcode.id

    def action_generate_barcode(self):
        self.generate_pc_laptop_sequence()

class PmrItmsProductItOffice(models.Model):
    _name = "pmr.itms.product.it.office"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Product IT Software"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Personil IT", required=True, store=True)
    pmr_barcode = fields.Many2one('pmr.barcode', String="Barcode")
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_umur_product = fields.Integer(string="Product Age", compute="_compute_pmr_umur_product", store=True)
    pmr_umur_product_str = fields.Char(string="Product Age (Text)", compute="_compute_pmr_umur_product_str", store=True)
    pmr_umur_product_str_year = fields.Char(string="Product Age (Text)", compute="_compute_pmr_umur_product_str_year", store=True)
    pmr_itms_departement = fields.Many2one('hr.department', string="Departement", required=True, store=True)
    pmr_itms_user = fields.Many2one('pmr.itms.user', string="User", required=True)
    pmr_quantity_product_it = fields.Float(string="Quantity", required=True, default=1)
    pmr_asset = fields.Boolean(string="Asset", default=False)
    pmr_no_asset = fields.Char(string="Nomor Asset")
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    product_category = fields.Many2one('pmr.product.category', string="Category",store=True)
    product_sub_category = fields.Many2one('pmr.product.sub.category', string="Sub Category", store=True)
    state = fields.Selection([
        ('not', 'Not State'),
        ('reject', 'Reject'),
        ('repair', 'Repair'),
        ('good', 'Good'),
    ], string="State", default="not", tracking=True, store=True)

    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product(self):
        """Calculates product age and ensures the result is not negative."""
        today_date = date.today() 
        for record in self:
            if record.pmr_create_date:
                create_date = record.pmr_create_date.date()
                record.pmr_umur_product = max((today_date - create_date).days, 0)
            else:
                record.pmr_umur_product = 0  
    
    @api.depends('pmr_umur_product')
    def _compute_pmr_umur_product_str(self):
        """Change pmr_umur_product to a string with the format 'X days'."""
        for record in self:
            record.pmr_umur_product_str = f"{record.pmr_umur_product} days"
    
    @api.depends('pmr_umur_product')
    def _compute_pmr_umur_product_str_year(self):
        """Convert pmr_umur_product into years format (X years, X months)."""
        for record in self:
            years = record.pmr_umur_product // 365
            months = (record.pmr_umur_product % 365) // 30  
            if years > 0 and months > 0:
                record.pmr_umur_product_str_year = f"{years} years {months} months"
            elif years > 0:
                record.pmr_umur_product_str_year = f"{years} years"
            elif months > 0:
                record.pmr_umur_product_str_year = f"{months} months"
            else:
                record.pmr_umur_product_str_year = "0 days"
    
    def action_reject(self):
        self.state= 'reject'

    def action_repair(self):
        self.state = 'repair'

    def action_good(self):
        self.state= 'good'
    
    def generate_pc_laptop_sequence(self):
        for record in self:
            if record.product_type == 'switch':
                current_date = record.pmr_create_date or datetime.now()
                year_month = current_date.strftime('%y%m')

                last_barcode = self.env['pmr.barcode'].search([
                    ('name', 'like', f"{year_month}%SW")
                ], order='name desc', limit=1)

                if last_barcode:
                    last_sequence = int(last_barcode.name[4:9]) + 1
                else:
                    last_sequence = 1

                sequence_str = str(last_sequence).zfill(5)
                barcode_name = f"{year_month}{sequence_str}SW"

                barcode = self.env['pmr.barcode'].create({
                    'name': barcode_name,
                    'pmr_create_date': current_date,  
                    'pmr_inventory_it': record.name  
                })

                record.pmr_barcode = barcode.id

    def action_generate_barcode(self):
        self.generate_pc_laptop_sequence()

class PmrItmsProductItCad(models.Model):
    _name = "pmr.itms.product.it.cad"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Product IT Software"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Personil IT", required=True, store=True)
    pmr_barcode = fields.Many2one('pmr.barcode', String="Barcode")
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_umur_product = fields.Integer(string="Product Age", compute="_compute_pmr_umur_product", store=True)
    pmr_umur_product_str = fields.Char(string="Product Age (Text)", compute="_compute_pmr_umur_product_str", store=True)
    pmr_umur_product_str_year = fields.Char(string="Product Age (Text)", compute="_compute_pmr_umur_product_str_year", store=True)
    pmr_itms_departement = fields.Many2one('hr.department', string="Departement", required=True, store=True)
    pmr_itms_user = fields.Many2one('pmr.itms.user', string="User", required=True)
    pmr_quantity_product_it = fields.Float(string="Quantity", required=True, default=1)
    pmr_asset = fields.Boolean(string="Asset", default=False)
    pmr_no_asset = fields.Char(string="Nomor Asset")
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    product_category = fields.Many2one('pmr.product.category', string="Category",store=True)
    product_sub_category = fields.Many2one('pmr.product.sub.category', string="Sub Category", store=True)
    state = fields.Selection([
        ('not', 'Not State'),
        ('reject', 'Reject'),
        ('repair', 'Repair'),
        ('good', 'Good'),
    ], string="State", default="not", tracking=True, store=True)

    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product(self):
        """Calculates product age and ensures the result is not negative."""
        today_date = date.today() 
        for record in self:
            if record.pmr_create_date:
                create_date = record.pmr_create_date.date()
                record.pmr_umur_product = max((today_date - create_date).days, 0)
            else:
                record.pmr_umur_product = 0  
    
    @api.depends('pmr_umur_product')
    def _compute_pmr_umur_product_str(self):
        """Change pmr_umur_product to a string with the format 'X days'."""
        for record in self:
            record.pmr_umur_product_str = f"{record.pmr_umur_product} days"
    
    @api.depends('pmr_umur_product')
    def _compute_pmr_umur_product_str_year(self):
        """Convert pmr_umur_product into years format (X years, X months)."""
        for record in self:
            years = record.pmr_umur_product // 365
            months = (record.pmr_umur_product % 365) // 30  
            if years > 0 and months > 0:
                record.pmr_umur_product_str_year = f"{years} years {months} months"
            elif years > 0:
                record.pmr_umur_product_str_year = f"{years} years"
            elif months > 0:
                record.pmr_umur_product_str_year = f"{months} months"
            else:
                record.pmr_umur_product_str_year = "0 days"
    
    def action_reject(self):
        self.state= 'reject'

    def action_repair(self):
        self.state = 'repair'

    def action_good(self):
        self.state= 'good'
    
    def generate_pc_laptop_sequence(self):
        for record in self:
            if record.product_type == 'switch':
                current_date = record.pmr_create_date or datetime.now()
                year_month = current_date.strftime('%y%m')

                last_barcode = self.env['pmr.barcode'].search([
                    ('name', 'like', f"{year_month}%SW")
                ], order='name desc', limit=1)

                if last_barcode:
                    last_sequence = int(last_barcode.name[4:9]) + 1
                else:
                    last_sequence = 1

                sequence_str = str(last_sequence).zfill(5)
                barcode_name = f"{year_month}{sequence_str}SW"

                barcode = self.env['pmr.barcode'].create({
                    'name': barcode_name,
                    'pmr_create_date': current_date,  
                    'pmr_inventory_it': record.name  
                })

                record.pmr_barcode = barcode.id

    def action_generate_barcode(self):
        self.generate_pc_laptop_sequence()

class PmrItmsProductItCam(models.Model):
    _name = "pmr.itms.product.it.cam"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Product IT Software"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Personil IT", required=True, store=True)
    pmr_barcode = fields.Many2one('pmr.barcode', String="Barcode")
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_umur_product = fields.Integer(string="Product Age", compute="_compute_pmr_umur_product", store=True)
    pmr_umur_product_str = fields.Char(string="Product Age (Text)", compute="_compute_pmr_umur_product_str", store=True)
    pmr_umur_product_str_year = fields.Char(string="Product Age (Text)", compute="_compute_pmr_umur_product_str_year", store=True)
    pmr_itms_departement = fields.Many2one('hr.department', string="Departement", required=True, store=True)
    pmr_itms_user = fields.Many2one('pmr.itms.user', string="User", required=True)
    pmr_quantity_product_it = fields.Float(string="Quantity", required=True, default=1)
    pmr_asset = fields.Boolean(string="Asset", default=False)
    pmr_no_asset = fields.Char(string="Nomor Asset")
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    product_category = fields.Many2one('pmr.product.category', string="Category",store=True)
    product_sub_category = fields.Many2one('pmr.product.sub.category', string="Sub Category", store=True)
    state = fields.Selection([
        ('not', 'Not State'),
        ('reject', 'Reject'),
        ('repair', 'Repair'),
        ('good', 'Good'),
    ], string="State", default="not", tracking=True, store=True)

    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product(self):
        """Calculates product age and ensures the result is not negative."""
        today_date = date.today() 
        for record in self:
            if record.pmr_create_date:
                create_date = record.pmr_create_date.date()
                record.pmr_umur_product = max((today_date - create_date).days, 0)
            else:
                record.pmr_umur_product = 0  
    
    @api.depends('pmr_umur_product')
    def _compute_pmr_umur_product_str(self):
        """Change pmr_umur_product to a string with the format 'X days'."""
        for record in self:
            record.pmr_umur_product_str = f"{record.pmr_umur_product} days"
    
    @api.depends('pmr_umur_product')
    def _compute_pmr_umur_product_str_year(self):
        """Convert pmr_umur_product into years format (X years, X months)."""
        for record in self:
            years = record.pmr_umur_product // 365
            months = (record.pmr_umur_product % 365) // 30  
            if years > 0 and months > 0:
                record.pmr_umur_product_str_year = f"{years} years {months} months"
            elif years > 0:
                record.pmr_umur_product_str_year = f"{years} years"
            elif months > 0:
                record.pmr_umur_product_str_year = f"{months} months"
            else:
                record.pmr_umur_product_str_year = "0 days"
    
    def action_reject(self):
        self.state= 'reject'

    def action_repair(self):
        self.state = 'repair'

    def action_good(self):
        self.state= 'good'
    
    def generate_pc_laptop_sequence(self):
        for record in self:
            if record.product_type == 'switch':
                current_date = record.pmr_create_date or datetime.now()
                year_month = current_date.strftime('%y%m')

                last_barcode = self.env['pmr.barcode'].search([
                    ('name', 'like', f"{year_month}%SW")
                ], order='name desc', limit=1)

                if last_barcode:
                    last_sequence = int(last_barcode.name[4:9]) + 1
                else:
                    last_sequence = 1

                sequence_str = str(last_sequence).zfill(5)
                barcode_name = f"{year_month}{sequence_str}SW"

                barcode = self.env['pmr.barcode'].create({
                    'name': barcode_name,
                    'pmr_create_date': current_date,  
                    'pmr_inventory_it': record.name  
                })

                record.pmr_barcode = barcode.id

    def action_generate_barcode(self):
        self.generate_pc_laptop_sequence()

class PmrItmsProductItOs(models.Model):
    _name = "pmr.itms.product.it.os"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Product IT Software"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Personil IT", required=True, store=True)
    pmr_barcode = fields.Many2one('pmr.barcode', String="Barcode")
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_umur_product = fields.Integer(string="Product Age", compute="_compute_pmr_umur_product", store=True)
    pmr_umur_product_str = fields.Char(string="Product Age (Text)", compute="_compute_pmr_umur_product_str", store=True)
    pmr_umur_product_str_year = fields.Char(string="Product Age (Text)", compute="_compute_pmr_umur_product_str_year", store=True)
    pmr_itms_departement = fields.Many2one('hr.department', string="Departement", required=True, store=True)
    pmr_itms_user = fields.Many2one('pmr.itms.user', string="User", required=True)
    pmr_quantity_product_it = fields.Float(string="Quantity", required=True, default=1)
    pmr_asset = fields.Boolean(string="Asset", default=False)
    pmr_no_asset = fields.Char(string="Nomor Asset")
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    product_category = fields.Many2one('pmr.product.category', string="Category",store=True)
    product_sub_category = fields.Many2one('pmr.product.sub.category', string="Sub Category", store=True)
    state = fields.Selection([
        ('not', 'Not State'),
        ('reject', 'Reject'),
        ('repair', 'Repair'),
        ('good', 'Good'),
    ], string="State", default="not", tracking=True, store=True)

    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product(self):
        """Calculates product age and ensures the result is not negative."""
        today_date = date.today() 
        for record in self:
            if record.pmr_create_date:
                create_date = record.pmr_create_date.date()
                record.pmr_umur_product = max((today_date - create_date).days, 0)
            else:
                record.pmr_umur_product = 0  
    
    @api.depends('pmr_umur_product')
    def _compute_pmr_umur_product_str(self):
        """Change pmr_umur_product to a string with the format 'X days'."""
        for record in self:
            record.pmr_umur_product_str = f"{record.pmr_umur_product} days"
    
    @api.depends('pmr_umur_product')
    def _compute_pmr_umur_product_str_year(self):
        """Convert pmr_umur_product into years format (X years, X months)."""
        for record in self:
            years = record.pmr_umur_product // 365
            months = (record.pmr_umur_product % 365) // 30  
            if years > 0 and months > 0:
                record.pmr_umur_product_str_year = f"{years} years {months} months"
            elif years > 0:
                record.pmr_umur_product_str_year = f"{years} years"
            elif months > 0:
                record.pmr_umur_product_str_year = f"{months} months"
            else:
                record.pmr_umur_product_str_year = "0 days"
    
    def action_reject(self):
        self.state= 'reject'

    def action_repair(self):
        self.state = 'repair'

    def action_good(self):
        self.state= 'good'
    
    def generate_pc_laptop_sequence(self):
        for record in self:
            if record.product_type == 'switch':
                current_date = record.pmr_create_date or datetime.now()
                year_month = current_date.strftime('%y%m')

                last_barcode = self.env['pmr.barcode'].search([
                    ('name', 'like', f"{year_month}%SW")
                ], order='name desc', limit=1)

                if last_barcode:
                    last_sequence = int(last_barcode.name[4:9]) + 1
                else:
                    last_sequence = 1

                sequence_str = str(last_sequence).zfill(5)
                barcode_name = f"{year_month}{sequence_str}SW"

                barcode = self.env['pmr.barcode'].create({
                    'name': barcode_name,
                    'pmr_create_date': current_date,  
                    'pmr_inventory_it': record.name  
                })

                record.pmr_barcode = barcode.id

    def action_generate_barcode(self):
        self.generate_pc_laptop_sequence()

class PmrItmsProductItSoftwareLain(models.Model):
    _name = "pmr.itms.product.it.sl"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Product IT Software"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Personil IT", required=True, store=True)
    pmr_barcode = fields.Many2one('pmr.barcode', String="Barcode")
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_umur_product = fields.Integer(string="Product Age", compute="_compute_pmr_umur_product", store=True)
    pmr_umur_product_str = fields.Char(string="Product Age (Text)", compute="_compute_pmr_umur_product_str", store=True)
    pmr_umur_product_str_year = fields.Char(string="Product Age (Text)", compute="_compute_pmr_umur_product_str_year", store=True)
    pmr_itms_departement = fields.Many2one('hr.department', string="Departement", required=True, store=True)
    pmr_itms_user = fields.Many2one('pmr.itms.user', string="User", required=True)
    pmr_quantity_product_it = fields.Float(string="Quantity", required=True, default=1)
    pmr_asset = fields.Boolean(string="Asset", default=False)
    pmr_no_asset = fields.Char(string="Nomor Asset")
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    product_category = fields.Many2one('pmr.product.category', string="Category",store=True)
    product_sub_category = fields.Many2one('pmr.product.sub.category', string="Sub Category", store=True)
    state = fields.Selection([
        ('not', 'Not State'),
        ('reject', 'Reject'),
        ('repair', 'Repair'),
        ('good', 'Good'),
    ], string="State", default="not", tracking=True, store=True)

    @api.depends('pmr_create_date')
    def _compute_pmr_umur_product(self):
        """Calculates product age and ensures the result is not negative."""
        today_date = date.today() 
        for record in self:
            if record.pmr_create_date:
                create_date = record.pmr_create_date.date()
                record.pmr_umur_product = max((today_date - create_date).days, 0)
            else:
                record.pmr_umur_product = 0  
    
    @api.depends('pmr_umur_product')
    def _compute_pmr_umur_product_str(self):
        """Change pmr_umur_product to a string with the format 'X days'."""
        for record in self:
            record.pmr_umur_product_str = f"{record.pmr_umur_product} days"
    
    @api.depends('pmr_umur_product')
    def _compute_pmr_umur_product_str_year(self):
        """Convert pmr_umur_product into years format (X years, X months)."""
        for record in self:
            years = record.pmr_umur_product // 365
            months = (record.pmr_umur_product % 365) // 30  
            if years > 0 and months > 0:
                record.pmr_umur_product_str_year = f"{years} years {months} months"
            elif years > 0:
                record.pmr_umur_product_str_year = f"{years} years"
            elif months > 0:
                record.pmr_umur_product_str_year = f"{months} months"
            else:
                record.pmr_umur_product_str_year = "0 days"
    
    def action_reject(self):
        self.state= 'reject'

    def action_repair(self):
        self.state = 'repair'

    def action_good(self):
        self.state= 'good'
    
    def generate_pc_laptop_sequence(self):
        for record in self:
            if record.product_type == 'switch':
                current_date = record.pmr_create_date or datetime.now()
                year_month = current_date.strftime('%y%m')

                last_barcode = self.env['pmr.barcode'].search([
                    ('name', 'like', f"{year_month}%SW")
                ], order='name desc', limit=1)

                if last_barcode:
                    last_sequence = int(last_barcode.name[4:9]) + 1
                else:
                    last_sequence = 1

                sequence_str = str(last_sequence).zfill(5)
                barcode_name = f"{year_month}{sequence_str}SW"

                barcode = self.env['pmr.barcode'].create({
                    'name': barcode_name,
                    'pmr_create_date': current_date,  
                    'pmr_inventory_it': record.name  
                })

                record.pmr_barcode = barcode.id

    def action_generate_barcode(self):
        self.generate_pc_laptop_sequence()

class PmrDeviceModel(models.Model):
    _name = "pmr.device.model"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Device Model"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Device Model", required=True, store=True)

class PmrPowerSupply(models.Model):
    _name = "pmr.power.supply"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Power Supply"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Name", required=True, store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
class PmrMotherboardType(models.Model):
    _name = "pmr.motherboard.type"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Motherboard Type"
    
    name = fields.Char(string="Mother Board Type", required=True, store=True)

class PmrBarcode(models.Model):
    _name = "pmr.barcode"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Barcode"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Barcode", required=True, store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_inventory_it = fields.Char(string="Inventory IT Name")

class PmrMainboard(models.Model):
    _name = "pmr.mainboard"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Mainboard"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Name", required=True, store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)

class PmrFdd(models.Model):
    _name = "pmr.fdd"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr FDD"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Name", required=True, store=True)
    pmr_pci = fields.Boolean(string="External", default=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)

class PmrLanCard(models.Model):
    _name = "pmr.lan.card"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Lan Card"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Name", required=True, store=True)
    pmr_onboard = fields.Boolean(string="On Board", default=True)
    pmr_pci = fields.Boolean(string="External")
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())

class PmrCasing(models.Model):
    _name = "pmr.casing"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Casing"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Name", required=True, store=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
   
class PmrKeyboard(models.Model):
    _name = "pmr.keyboard"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Keyboard"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Name", required=True, store=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    
class PmrMouse(models.Model):
    _name = "pmr.mouse"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Mouse"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Name", required=True, store=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    
class PmrMonitor(models.Model):
    _name = "pmr.monitor"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Monitor"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Name", required=True, store=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())

class PmrPrinter(models.Model):
    _name = "pmr.printer"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Printer"
    
    name = fields.Char(string="Name", required=True, store=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_jenis_printer = fields.Many2one('pmr.jenis.printer',string="Jenis Printer", store=True)
    pmr_kecepatan_cetak = fields.Many2one('pmr.kecepatan.cetak',string="Kecepatan Cetak", store=True)
    pmr_konektivitas_printer = fields.Many2one('pmr.konektivitas',string="Konektivitas", store=True)
    pmr_ukuran_kertas = fields.Many2one('pmr.ukuran.kertas',string="Ukuran Kertas", store=True)
    pmr_fitur_tambahan = fields.Many2one('pmr.fitur.tambahan',string="Fitur Tambahan", store=True)
    pmr_ip_printer = fields.Char(string="IP Printer")
    
    
class PmrPC(models.Model):
    _name = "pmr.pc"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr PC"
    
    name = fields.Char(string="Name", required=True, store=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_mainboard = fields.Many2one('pmr.mainboard',string="Motherboard", store=True)
    pmr_processor = fields.Many2one('pmr.processor', string="Processor", store=True)
    pmr_hardisk_1= fields.Many2one('pmr.hardisk', string="Hardisk 1", store=True)
    pmr_hardisk_2= fields.Many2one('pmr.hardisk', string="Hardisk 2", store=True)
    pmr_hardisk_3= fields.Many2one('pmr.hardisk', string="Hardisk 3", store=True)
    pmr_hardisk_4= fields.Many2one('pmr.hardisk', string="Hardisk 4", store=True)
    pmr_ram_1= fields.Many2one('pmr.ram', string="RAM 1", store=True)
    pmr_ram_2= fields.Many2one('pmr.ram', string="RAM 2", store=True)
    pmr_ram_3= fields.Many2one('pmr.ram', string="RAM 3", store=True)
    pmr_ram_4= fields.Many2one('pmr.ram', string="RAM 4", store=True)
    pmr_vga_1= fields.Many2one('pmr.vga', string="VGA 1", store=True)
    pmr_vga_2= fields.Many2one('pmr.vga', string="VGA 2", store=True)
    pmr_operating_system = fields.Many2one('pmr.os', string="Operating System", store=True)
    pmr_antivirus = fields.Many2one('pmr.antivirus',string="Antivirus", store=True)
    pmr_cad = fields.Many2one('pmr.cad', string="CAD", store=True)
    pmr_cam = fields.Many2one('pmr.cam', string="CAM", store=True)
    pmr_office = fields.Many2one('pmr.office', string="Office", store=True)
    pmr_power_supply = fields.Many2one('pmr.power.supply', string="Power Supply", store=True)
    pmr_fdd = fields.Many2one('pmr.fdd', string="Expansion Slot", store=True)
    pmr_lan_card = fields.Many2one('pmr.lan.card',string="Integrated LAN", store=True)
    pmr_hdmi_boolean = fields.Boolean(string="HDMI")
    pmr_dvd_room_boolean = fields.Boolean(string="CD/DVD Room")
    pmr_ups_boolean = fields.Boolean(string="UPS")
    pmr_usb_2_0_port =fields.Boolean(string="USB 2.0 Port")
    pmr_usb_3_0_port =fields.Boolean(string="USB 3.0 Port")
    pmr_vga_port =fields.Boolean(string="VGA Port")
    pmr_hdmi_port =fields.Boolean(string="HDMI Port")
    pmr_display_port =fields.Boolean(string="Display Port")
    pmr_rj45_port =fields.Boolean(string="RJ45 Port")
    pmr_3_in_1_audio_port =fields.Boolean(string="3-in-1 Audio Port")
    pmr_io_interface = fields.Char(string="I/O Interface", default="I/O Interface")
    pmr_casing = fields.Many2one('pmr.casing', string="Casing", store=True)
    pmr_keyboard = fields.Many2one('pmr.keyboard', string="Keyboard", store=True)
    pmr_monitor = fields.Many2one('pmr.monitor', string="Monitor", store=True)
    pmr_mouse = fields.Many2one('pmr.mouse',string="Mouse", store=True)
    pmr_lan_card_type = fields.Char(string="Type", compute="_compute_lan_card_type", store=True)
    pmr_vga_type_1 = fields.Char(string="Type", compute="_compute_vga_type", store=True)
    pmr_vga_type_2 = fields.Char(string="Type", compute="_compute_vga_type", store=True)
    
    @api.depends('pmr_vga_1', 'pmr_vga_1.pmr_onboard', 'pmr_vga_1.pmr_pci', 'pmr_vga_2', 'pmr_vga_2.pmr_onboard', 'pmr_vga_2.pmr_pci')
    def _compute_vga_type(self):
        for record in self:
            vga_1_types = []
            if record.pmr_vga_1:
                if record.pmr_vga_1.pmr_onboard:
                    vga_1_types.append("Onboard")
                if record.pmr_vga_1.pmr_pci:
                    vga_1_types.append("External")
            record.pmr_vga_type_1 = " dan ".join(vga_1_types) if vga_1_types else ""

            vga_2_types = []
            if record.pmr_vga_2:
                if record.pmr_vga_2.pmr_onboard:
                    vga_2_types.append("Onboard")
                if record.pmr_vga_2.pmr_pci:
                    vga_2_types.append("External")
            record.pmr_vga_type_2 = " dan ".join(vga_2_types) if vga_2_types else ""

    @api.depends('pmr_lan_card', 'pmr_lan_card.pmr_onboard', 'pmr_lan_card.pmr_pci')
    def _compute_lan_card_type(self):
        for record in self:
            lan_card_types = []
            if record.pmr_lan_card:
                if record.pmr_lan_card.pmr_onboard:
                    lan_card_types.append("Onboard")
                if record.pmr_lan_card.pmr_pci:
                    lan_card_types.append("External")
            record.pmr_lan_card_type = " dan ".join(lan_card_types) if lan_card_types else ""

class PmrRouter(models.Model):
    _name = "pmr.router"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Router"
    
    name = fields.Char(string="Name", required=True, store=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_hardware_router = fields.Many2one('pmr.hardware.router',string="Hardware Router", store=True)
    pmr_konektivitas_router = fields.Many2one('pmr.konektivitas.router',string="Konektivitas", store=True)
    pmr_fitur_tambahan_router = fields.Many2one('pmr.fitur.tambahan.router',string="Fitur Tambahan Router", store=True)

class PmrWifi(models.Model):
    _name = "pmr.wifi"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Wifi"
    
    name = fields.Char(string="Name", required=True, store=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_frekuensi_wifi = fields.Many2one('pmr.frekuensi.wifi',string="Frekuensi WIFI", store=True)
    pmr_keamanan = fields.Many2one('pmr.keamanan',string="Keamanan Wifi")

class PmrSwitch(models.Model):
    _name = "pmr.switch"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Switch"
    
    name = fields.Char(string="Name", required=True, store=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_jenis_switch = fields.Many2one('pmr.jenis.switch',string="Jenis Switch", store=True)
    pmr_jumlah_port = fields.Float(string="Jumlah Port")
    pmr_kecepatan_port = fields.Many2one('pmr.kecepatan.port',string="Kecepatan Port", store=True)
    pmr_switching_capacity = fields.Many2one('pmr.switching.capacity',string="Switching Capacity")

class PmrProcessor(models.Model):
    _name = "pmr.processor"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Processor"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Name", required=True, store=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())

class PmrHardisk(models.Model):
    _name = "pmr.hardisk"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Hardisk"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Name", required=True, store=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
   
class PmrRam(models.Model):
    _name = "pmr.ram"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr RAM"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Name", required=True, store=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
   
class PmrVga(models.Model):
    _name = "pmr.vga"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr VGA"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Name", required=True, store=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_onboard = fields.Boolean(string="On Board")
    pmr_pci = fields.Boolean(string="External")

    def name_get(self):
        result = []
        for rec in self:
            display_name = f"{rec.name}"  # Atau f"{rec.brand} - {rec.name}" jika ada brand
            result.append((rec.id, display_name))
        return result

   
class PmrOs(models.Model):
    _name = "pmr.os"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Os"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Name", required=True, store=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    pmr_sn_operating_system = fields.Char(string="Product Key")
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_itms_os  = fields.One2many('pmr.license.os','pmr_itms_license_os', tracking=10)
    type_software = fields.Selection([
        ('freeware', 'freeware'),
        ('licensed', 'licensed'),
        ('lifetime', 'lifetime licensed')
    ], string="Type", default='freeware', tracking=True, store=True)
    
class PmrLicenseOs(models.Model):
    _name = "pmr.license.os"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Os"

    name = fields.Char(string="Name",store=True)
    pmr_itms_license_os = fields.Many2one('pmr.os', string="ID Memo")
    pmr_itms_user = fields.Char(string="User",store=True)

class PmrKeamanan(models.Model):
    _name = "pmr.keamanan"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Keamanan"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Keamanan Wifi", required=True, store=True)

class PmrAntivirus(models.Model):
    _name = "pmr.antivirus"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Antivirus"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Name",store=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    type_software = fields.Selection([
        ('freeware', 'freeware'),
        ('licensed', 'licensed'),
        ('lifetime', 'lifetime licensed')
    ], string="Type", default='freeware', tracking=True, store=True)
    pmr_itms_antivirus  = fields.One2many('pmr.license.antivirus','pmr_itms_license_antivirus', tracking=10)

class PmrLicenseAntivirus(models.Model):
    _name = "pmr.license.antivirus"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Antivirus"

    name = fields.Char(string="Name", store=True)
    pmr_itms_license_antivirus = fields.Many2one('pmr.antivirus', string="ID Memo")
    pmr_itms_user = fields.Char(string="User",store=True)

class PmrOffice(models.Model):
    _name = "pmr.office"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Office"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Name", required=True, store=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    pmr_sn_office = fields.Char(string="Product Key")
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    type_software = fields.Selection([
        ('freeware', 'freeware'),
        ('licensed', 'licensed'),
        ('lifetime', 'lifetime licensed')
    ], string="Type", default='freeware', tracking=True, store=True)
    pmr_itms_office  = fields.One2many('pmr.license.office','pmr_itms_license_office', tracking=10)

class PmrLicenseOffice(models.Model):
    _name = "pmr.license.office"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Office"

    name = fields.Char(string="Name", required=True, store=True)
    pmr_itms_license_office = fields.Many2one('pmr.office', string="ID Memo")
    pmr_itms_user = fields.Char(string="User",store=True)

class PmrCad(models.Model):
    _name = "pmr.cad"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Cad"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Name", required=True, store=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    type_software = fields.Selection([
        ('freeware', 'freeware'),
        ('licensed', 'licensed'),
        ('lifetime', 'lifetime licensed')
    ], string="Type", default='freeware', tracking=True, store=True)
    pmr_itms_cad  = fields.One2many('pmr.license.cad','pmr_itms_license_cad', tracking=10)

class PmrLicenseCad(models.Model):
    _name = "pmr.license.cad"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Cad"

    name = fields.Char(string="Name", store=True)
    pmr_itms_license_cad = fields.Many2one('pmr.cad', string="ID Memo")
    pmr_itms_user = fields.Char(string="User",store=True)

class PmrCam(models.Model):
    _name = "pmr.cam"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Cam"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Name", required=True, store=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    type_software = fields.Selection([
        ('freeware', 'freeware'),
        ('licensed', 'licensed'),
        ('lifetime', 'lifetime licensed')
    ], string="Type", default='freeware', tracking=True, store=True)
    pmr_itms_cam  = fields.One2many('pmr.license.cam','pmr_itms_license_cam', tracking=10)

class PmrLicenseCam(models.Model):
    _name = "pmr.license.cam"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Cam"

    name = fields.Char(string="Name", store=True)
    pmr_itms_license_cam = fields.Many2one('pmr.cam', string="ID Memo")
    pmr_itms_user = fields.Char(string="User",store=True)

class PmrSoftwareLain(models.Model):
    _name = "pmr.software.lain"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Software Lain"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Name", required=True, store=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    pmr_sn_sotfware_lain = fields.Char(string="Product Key")
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    type_software = fields.Selection([
        ('freeware', 'freeware'),
        ('licensed', 'licensed'),
        ('lifetime', 'lifetime licensed')
    ], string="Type", default='freeware', tracking=True, store=True)
    pmr_itms_software_lain  = fields.One2many('pmr.license.software.lain','pmr_itms_license_software_lain', tracking=10)

class PmrLicenseSoftwareLain(models.Model):
    _name = "pmr.license.software.lain"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Software Lain"

    name = fields.Char(string="Name", store=True)
    pmr_itms_license_software_lain = fields.Many2one('pmr.software.lain', string="ID Memo")
    pmr_itms_user = fields.Char(string="User",store=True)

class PmrJenisPrinter(models.Model):
    _name = "pmr.jenis.printer"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Jenis Printer"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="JEnis Printer", required=True, store=True)

class PmrKecepatanCetak(models.Model):
    _name = "pmr.kecepatan.cetak"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Kecepatan Cetak"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Kecepatan Cetak", required=True, store=True)

class PmrKonektivitas(models.Model):
    _name = "pmr.konektivitas"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Konektivitas"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Konektivitas", required=True, store=True)

class PmrUkuranKertas(models.Model):
    _name = "pmr.ukuran.kertas"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Ukuran Kertas"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Ukuran Kertas", required=True, store=True)

class PmrFiturTambahan(models.Model):
    _name = "pmr.fitur.tambahan"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Fitur Tambahan"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Fitur Tambahan", required=True, store=True)

class PmrHardwareRouter(models.Model):
    _name = "pmr.hardware.router"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Hardware Router"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Hardware Router", required=True, store=True)

class PmrKonektivitasRouter(models.Model):
    _name = "pmr.konektivitas.router"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Konektivitas Router"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Konektivitas Router", required=True, store=True)

class PmrFiturTambahanRouter(models.Model):
    _name = "pmr.fitur.tambahan.router"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Fitur Tambahan Router"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Name", required=True, store=True)

class PmrFrekuensiWifi(models.Model):
    _name = "pmr.frekuensi.wifi"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Frekuensi Wifi"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Frequenci Wifi", required=True, store=True)

class PmrJenisSwitch(models.Model):
    _name = "pmr.jenis.switch"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Jenis Switch"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Jenis Switch", required=True, store=True)

class PmrKecepatanPort(models.Model):
    _name = "pmr.kecepatan.port"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Kecepatan Port"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Name", required=True, store=True)

class PmrSwitchingCapacity(models.Model):
    _name = "pmr.switching.capacity"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Switching Capacity"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be Unique.')
    ]
    
    name = fields.Char(string="Switch Capacity", required=True, store=True)
   
class PmrItmsRole(models.Model):
    _name = "pmr.itms.role"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Role"
    
    name = fields.Char(string="Name", required=True, store=True)

class PmrCategoryUnit(models.Model):
    _name = "pmr.category.unit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Category Unit"
    
    name = fields.Char(string="Name", required=True, store=True)

class PmrJenisUnit(models.Model):
    _name = "pmr.jenis.unit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Jenis Unit"
    
    name = fields.Char(string="Name", required=True, store=True)

class PmrLocationInventory(models.Model):
    _name = "pmr.location.unit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Lokasi Unit"
    
    name = fields.Char(string="Name", required=True, store=True)

class AssetNumberIt(models.Model):
    _name = "asset.number.it"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Asset Number IT"
    
    name = fields.Char(string="Name", required=True, store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_itms_panset  = fields.One2many('asset.number.it.line','pmr_itms_panset_line', tracking=10)

class AssetNumberItLine(models.Model):
    _name = "asset.number.it.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Asset Number IT Line"

    pmr_itis_product = fields.Char(string="Item")
    pmr_itis_po_number = fields.Many2one('purchase.order',string="PO Number")
    pmr_quantity_product_it = fields.Float(string="Quantity",required=True)
    product_unit_category = fields.Many2one('uom.uom', string="Uom", required=True, store=True)
    pmr_itms_panset_line = fields.Many2one('asset.number.it', string="ID Memo", store=True)

class PmrItmsInventoryIt(models.Model):
    _name = "pmr.itms.inventory.it"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pmr Itms Product IT"
    _rec_name = "product"

    _sql_constraints = [
        ('name_uniq', 'unique(product)', 'Name must be Unique.')
    ]   
    product = fields.Char(string="Name Product")
    pmr_itms_product = fields.Reference(selection=[
        ('pmr.pc', 'pc'),
        ('pmr.wifi', 'wiFi'),
        ('pmr.switch', 'switch'),
        ('pmr.router', 'router'),
        ('pmr.processor', 'processor'),
        ('pmr.hardisk', 'hardisk'),
        ('pmr.ram', 'ram'),
        ('pmr.vga', 'vga'),
        ('pmr.fdd', 'fdd'),
        ('pmr.casing', 'Casing'),
        ('pmr.keyboard', 'keyboard'),
        ('pmr.monitor', 'monitor'),
        ('pmr.mouse', 'mouse'),
        ('pmr.printer', 'printer'),
        ('pmr.mainboard', 'motherboard'),
        ('pmr.power.supply', 'Power Supply'),
        ('pmr.lan.card', 'Integrated LAN'),
        ('pmr.antivirus', 'Antivirus'),
        ('pmr.cad', 'CAD'),
        ('pmr.cam', 'CAM'),
        ('pmr.os', 'Operating System'),
    ], string="Item Name")
    # asset_code = fields.Many2one('asset.number.it',string='Asset Code', required=True, tracking=True)
    pmr_barcode = fields.Many2one('pmr.barcode', String="Barcode")
    onhand_count = fields.Float(string="On Hand Quantity", compute="_compute_onhand_count", store=True)
    category= fields.Selection([
        ('pc', 'PC'),
        ('laptop', 'Laptop'),
        ('printer', 'Printer'),
        ('hardisk', 'Hardisk'),
        ('monitor', 'Monitor'),
        ('motherboard', 'Motherboard'),
        ('mouse', 'Mouse'),
        ('ram', 'RAM'),
        ('vga', 'VGA'),
        ('power_supply', 'Power Supply'),
        ('switch', 'Switch'),
        ('router', 'Router'),
        ('wifi', 'Wifi'),
        ('processor', 'Processor'),
        ('keyboard', 'Keyboard'),
        ('fdd', 'Expansion Slot'),
        ('casing', 'Casing'),
        ('Integrated_LAN', 'Integrated LAN'),
        ('antivirus', 'Antivirus'),
        ('cad', 'CAD'),
        ('cam', 'CAM'),
        ('operatingsys', 'Operating System'),
        ('other', 'Other'),
    ], string='Category', required=True, tracking=True)
    category_product= fields.Selection([
        ('hardware', 'Hardware'),
        ('software', 'Software'),
    ], required=True, tracking=True)
    pmr_quantity_product_it = fields.Float(string="Quantity", required=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    product_location_unit = fields.Many2one('pmr.location.unit', string="Location", required=True, store=True)
    condition = fields.Selection([
        ('new', 'New'),
        ('good', 'Good'),
        ('repair', 'In Repair'),
        ('damaged', 'Damaged'),
    ], default='good', string='Condition', tracking=True)
    usage_status = fields.Selection([
        ('in_use', 'In Use'),
        ('spare', 'Spare'),
        ('retired', 'Retired'),
    ], default='in_use', string='Usage Status', tracking=True)
    # Printer
    pmr_jenis_printer = fields.Char(string="Jenis Printer", store=True)
    pmr_kecepatan_cetak = fields.Char(string="Kecepatan Cetak", store=True)
    pmr_konektivitas_printer = fields.Char(string="Konektivitas", store=True)
    pmr_ukuran_kertas = fields.Char(string="Ukuran Kertas", store=True)
    pmr_fitur_tambahan = fields.Char(string="Fitur Tambahan", store=True)
    pmr_ip_printer = fields.Char(string="IP Printer")

    # Router
    pmr_hardware_router = fields.Char(string="Hardware Router", store=True)
    pmr_konektivitas_router = fields.Char(string="Konektivitas", store=True)
    pmr_fitur_tambahan_router = fields.Char(string="Fitur Tambahan Router", store=True)

     # Wifi
    pmr_frekuensi_wifi = fields.Char(string="Frekuensi WIFI", store=True)
    pmr_keamanan = fields.Char(string="Keamanan Wifi")

    # Switch
    pmr_jenis_switch = fields.Char(string="Jenis Switch", store=True)
    pmr_jumlah_port = fields.Float(string="Jumlah Port")
    pmr_kecepatan_port = fields.Char(string="Kecepatan Port", store=True)
    pmr_switching_capacity = fields.Char(string="Switching Capacity")

    # CPU/Laptop
    pmr_processor = fields.Char(string="Processor", store=True)
    pmr_mainboard = fields.Char(string="Motherboard", store=True)
    pmr_hardisk_1 = fields.Char(string="Hardisk 1", store=True)
    pmr_hardisk_2 = fields.Char(string="Hardisk 2", store=True)
    pmr_hardisk_3 = fields.Char(string="Hardisk 3", store=True)
    pmr_hardisk_4 = fields.Char(string="Hardisk 4", store=True)
    pmr_ram_1 = fields.Char(string="RAM 1", store=True)
    pmr_ram_2 = fields.Char(string="RAM 2", store=True)
    pmr_ram_3 = fields.Char(string="RAM 3", store=True)
    pmr_ram_4 = fields.Char(string="RAM 4", store=True)
    pmr_vga_1 = fields.Char(string="VGA 1", store=True)
    pmr_vga_2 = fields.Char(string="VGA 2", store=True)
    pmr_dvd_room_boolean = fields.Boolean(string="CD/DVD Room")
    pmr_ups_boolean = fields.Boolean(string="UPS")
    pmr_fdd = fields.Char(string="Expansion Slot", store=True)
    pmr_hdmi_boolean = fields.Boolean(string="HDMI")
    pmr_lan_card = fields.Char(string="Integrated LAN", store=True)
    pmr_casing = fields.Char(string="Casing", store=True)
    pmr_power_supply = fields.Char(string="Power Supply", store=True)
    pmr_keyboard = fields.Char(string="Keyboard", store=True)
    pmr_mouse = fields.Char(string="Mouse", store=True)
    pmr_monitor = fields.Char(string="Monitor", store=True)
    pmr_ups = fields.Many2one('pmr.ups', string="UPS", store=True)
    pmr_printer = fields.Many2one('pmr.printer',string="Printer", store=True)
    pmr_operating_system = fields.Many2one('pmr.os', string="Operating System", store=True)
    pmr_sn_operating_system = fields.Char(string="SN Operating System", store=True)
    pmr_office = fields.Many2one('pmr.office', string="Office", store=True)
    pmr_cad = fields.Many2one('pmr.cad', string="CAD", store=True)
    pmr_cam = fields.Many2one('pmr.cam', string="CAM", store=True)
    pmr_antivirus = fields.Many2one('pmr.antivirus',string="Antivirus", store=True)
    pmr_program_lain = fields.Many2many('pmr.software.lain',string="Software Lain")
    pmr_vga_type_1 = fields.Char(string="Type", store=True)
    pmr_vga_type_2 = fields.Char(string="Type", store=True)
    pmr_lan_card_type = fields.Char(string="Type", store=True)
    # pmr_fdd_type = fields.Char(string="Type", compute="_compute_fdd_type", store=True)
    pmr_usb_2_0_port =fields.Boolean(string="USB 2.0 Port")
    pmr_usb_3_0_port =fields.Boolean(string="USB 3.0 Port")
    pmr_vga_port =fields.Boolean(string="VGA Port")
    pmr_hdmi_port =fields.Boolean(string="HDMI Port")
    pmr_display_port =fields.Boolean(string="Display Port")
    pmr_rj45_port =fields.Boolean(string="RJ45 Port")
    pmr_3_in_1_audio_port =fields.Boolean(string="3-in-1 Audio Port")
    pmr_io_interface = fields.Char(string="I/O Interface", default="I/O Interface")

    total_onhand_quantity = fields.Float(string="Total On Hand Quantity", compute="_compute_total_onhand_quantity", store=False)
    serial_number = fields.Char(string="Serial Number", tracking=True)
    notes = fields.Text(string='Notes')
    
    @api.depends('product', 'pmr_quantity_product_it')
    def _compute_total_onhand_quantity(self):
        for rec in self:
            if rec.product:
                movements = self.env['pmr.itms.inventory.movement'].search([
                    ('name_product', '=', rec.product)
                ])
                rec.total_onhand_quantity = sum(mov.pmr_quantity_product_it for mov in movements)
            else:
                rec.total_onhand_quantity = 0.0



    def action_set_to_retired (self):
        # (Opsional) logika membuat data baru bisa diletakkan di sini
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inventory Movement',
            'view_mode': 'tree,form',
            'res_model': 'pmr.itms.inventory.movement',
            'target': 'current',
            'domain': [('name_product', '=', self.product)],
        }

    @api.model
    def create(self, vals):
        record = super(PmrItmsInventoryIt, self).create(vals)
        if record.pmr_itms_product:
            record.product = record.pmr_itms_product.display_name
        return record

    @api.onchange('pmr_itms_product')
    def _onchange_pmr_itms_product(self):
        """Mengisi field category otomatis dari referensi model."""
        if self.pmr_itms_product:
            model = self.pmr_itms_product._name
            mapping = {
                'pmr.pc': 'pc',
                'pmr.wifi': 'wifi',
                'pmr.switch': 'switch',
                'pmr.router': 'router',
                'pmr.processor': 'processor',
                'pmr.hardisk': 'hardisk',
                'pmr.ram': 'ram',
                'pmr.vga': 'vga',
                'pmr.fdd': 'fdd',
                'pmr.casing': 'casing',
                'pmr.keyboard': 'keyboard',
                'pmr.monitor': 'monitor',
                'pmr.mouse': 'mouse',
                'pmr.printer': 'printer',
                'pmr.mainboard': 'motherboard',
                'pmr.power.supply': 'power_supply',
                'pmr.lan.card': 'Integrated_LAN',
                'pmr.antivirus': 'antivirus',
                'pmr.cad': 'cad',
                'pmr.cam': 'cam',
                'pmr.os': 'operating_system',
            }
            self.category = mapping.get(model, 'other')
            
    @api.onchange('pmr_itms_product')
    def _onchange_pmr_itms_product(self):
        if self.pmr_itms_product:
            model = self.pmr_itms_product._name
            record = self.pmr_itms_product
            # Printer
            if model == 'pmr.printer':
                self.category = 'printer'
                self.pmr_jenis_printer = record.pmr_jenis_printer.name
                self.product_unit_category = record.product_unit_category
                self.pmr_kecepatan_cetak = record.pmr_kecepatan_cetak.name
                self.pmr_konektivitas_printer = record.pmr_konektivitas_printer.name
                self.pmr_ukuran_kertas = record.pmr_ukuran_kertas.name
                self.pmr_fitur_tambahan = record.pmr_fitur_tambahan.name
                self.pmr_ip_printer = record.pmr_ip_printer
            # Router
            elif model == 'pmr.router':
                self.category = 'router'
                self.product_unit_category = record.product_unit_category
                self.pmr_konektivitas_router = record.pmr_konektivitas_router.name
                self.pmr_hardware_router = record.pmr_hardware_router.name
                self.pmr_fitur_tambahan_router = record.pmr_fitur_tambahan_router.name
            # Wifi
            elif model == 'pmr.wifi':
                self.category = 'wifi'
                self.product_unit_category = record.product_unit_category
                self.pmr_frekuensi_wifi = record.pmr_frekuensi_wifi.name
                self.pmr_keamanan = record.pmr_keamanan.name
            # Switch
            elif model == 'pmr.switch':
                self.category = 'switch'
                self.product_unit_category = record.product_unit_category
                self.pmr_jenis_switch = record.pmr_jenis_switch.name
                self.pmr_jumlah_port = record.pmr_jumlah_port
                self.pmr_kecepatan_port = record.pmr_kecepatan_port.name
                self.pmr_switching_capacity = record.pmr_switching_capacity.name
            # CPU/Laptop
            elif model == 'pmr.pc':
                self.category = 'pc'
                self.product_unit_category = record.product_unit_category
                self.pmr_processor = record.pmr_processor.name 
                self.pmr_mainboard = record.pmr_mainboard.name   
                self.pmr_power_supply = record.pmr_power_supply.name   
                self.pmr_mouse = record.pmr_mouse.name   
                self.pmr_casing = record.pmr_casing.name   
                self.pmr_keyboard = record.pmr_keyboard.name   
                self.pmr_monitor = record.pmr_monitor.name   
                self.pmr_lan_card = record.pmr_lan_card.name   
                self.pmr_lan_card_type = record.pmr_lan_card_type  
                self.pmr_fdd = record.pmr_fdd.name   
                self.pmr_dvd_room_boolean = record.pmr_dvd_room_boolean   
                self.pmr_hdmi_boolean = record.pmr_hdmi_boolean   
                self.pmr_ups_boolean = record.pmr_ups_boolean   
                self.pmr_usb_2_0_port = record.pmr_usb_2_0_port   
                self.pmr_usb_3_0_port = record.pmr_usb_3_0_port   
                self.pmr_vga_port = record.pmr_vga_port   
                self.pmr_hdmi_port = record.pmr_hdmi_port   
                self.pmr_display_port = record.pmr_display_port 
                self.pmr_rj45_port = record.pmr_rj45_port 
                self.pmr_3_in_1_audio_port = record.pmr_3_in_1_audio_port 
                self.pmr_ram_1 = record.pmr_ram_1.name 
                self.pmr_ram_2 = record.pmr_ram_2.name 
                self.pmr_ram_3 = record.pmr_ram_3.name 
                self.pmr_ram_4 = record.pmr_ram_4.name 
                self.pmr_hardisk_1 = record.pmr_hardisk_1.name 
                self.pmr_hardisk_2 = record.pmr_hardisk_2.name 
                self.pmr_hardisk_3 = record.pmr_hardisk_3.name 
                self.pmr_hardisk_4 = record.pmr_hardisk_4.name 
                self.pmr_vga_1 = record.pmr_vga_1.name 
                self.pmr_vga_2 = record.pmr_vga_2.name 
                self.pmr_vga_type_1 = record.pmr_vga_type_1
                self.pmr_vga_type_2 = record.pmr_vga_type_2
            # Processor
            elif model == 'pmr.processor':
                self.category = 'processor'
                self.product_unit_category = record.product_unit_category
            # Hardisk
            elif model == 'pmr.hardisk':
                self.category = 'hardisk'
                self.product_unit_category = record.product_unit_category
            # RAM
            elif model == 'pmr.ram':
                self.category = 'ram'
                self.product_unit_category = record.product_unit_category
            # VGA
            elif model == 'pmr.vga':
                self.category = 'vga'
                self.product_unit_category = record.product_unit_category
            # FDD
            elif model == 'pmr.fdd':
                self.category = 'fdd'
                self.product_unit_category = record.product_unit_category
            # Casing
            elif model == 'pmr.casing':
                self.category = 'casing'
                self.product_unit_category = record.product_unit_category
            # Keyboard
            elif model == 'pmr.keyboard':
                self.category = 'keyboard'
                self.product_unit_category = record.product_unit_category
            # Monitor
            elif model == 'pmr.monitor':
                self.category = 'monitor'
                self.product_unit_category = record.product_unit_category
            # Mouse
            elif model == 'pmr.mouse':
                self.category = 'mouse'
                self.product_unit_category = record.product_unit_category
            # Motherboard
            elif model == 'pmr.mainboard':
                self.category = 'mainboard'
                self.product_unit_category = record.product_unit_category
            # Power Supply
            elif model == 'pmr.power.supply':
                self.category = 'power.supply'
                self.product_unit_category = record.product_unit_category
            # Integrated LAN
            elif model == 'pmr.lan.card':
                self.category = 'Integrated_LAN'
                self.product_unit_category = record.product_unit_category
            # Antivirus
            elif model == 'pmr.antivirus':
                self.category = 'antivirus'
                self.product_unit_category = record.product_unit_category
            # CAD
            elif model == 'pmr.cad':
                self.category = 'cad'
                self.product_unit_category = record.product_unit_category
            # CAM
            elif model == 'pmr.cam':
                self.category = 'cam'
                self.product_unit_category = record.product_unit_category
            # OS
            elif model == 'pmr.os':
                self.category = 'operating_system'
                self.product_unit_category = record.product_unit_categorys

            self.product = record.display_name

    @api.onchange('category')
    def _onchange_category(self):
        hardware_categories = [
            'pc', 'laptop', 'printer', 'hardisk', 'monitor', 'motherboard', 'mouse',
            'ram', 'vga', 'power_supply', 'switch', 'router', 'wifi', 'processor',
            'keyboard', 'fdd', 'casing', 'Integrated_LAN'
        ]
        if self.category in hardware_categories:
            self.category_product = 'hardware'
        else:
            self.category_product = 'software'
            
    # def generate_pc_laptop_sequence(self):
    #     suffix_mapping = {
    #         'pc': 'PC',
    #         'laptop': 'LP',
    #         'printer': 'PR',
    #         'hardisk': 'HD',
    #         'monitor': 'MN',
    #         'motherboard': 'MB',
    #         'mouse': 'MS',
    #         'ram': 'RM',
    #         'vga': 'VG',
    #         'power_supply': 'PS',
    #         'switch': 'SW',
    #         'router': 'RT',
    #         'wifi': 'WF',
    #         'processor': 'PRC',
    #         'keyboard': 'KB',
    #         'fdd': 'FD',
    #         'casing': 'CS',
    #         'Integrated_LAN': 'LAN',
    #         'antivirus': 'AV',
    #         'cad': 'CD',
    #         'cam': 'CM',
    #         'operatingsys': 'OS',
    #         'other': 'OT'
    #     }
    #     for record in self:
    #         category = record.category or 'other'
    #         suffix = suffix_mapping.get(category, 'OT')  # default 'OT' if tidak ditemukan
            
    #         current_date = fields.Datetime.now()
    #         year_month = current_date.strftime('%y%m')

    #         # Cari barcode terakhir yang cocok dengan pola tahunbulan + suffix
    #         last_barcode = self.env['pmr.barcode'].search([
    #             ('name', 'like', f"{year_month}%{suffix}")
    #         ], order='name desc', limit=1)

    #         if last_barcode:
    #             last_sequence = int(last_barcode.name[4:9]) + 1
    #         else:
    #             last_sequence = 1

    #         sequence_str = str(last_sequence).zfill(5)
    #         barcode_name = f"{year_month}{sequence_str}{suffix}"

    #         barcode = self.env['pmr.barcode'].create({
    #             'name': barcode_name,
    #             'pmr_create_date': current_date,
    #             'pmr_inventory_it': record.name
    #         })

    #         record.pmr_barcode = barcode.id

    # def action_generate_barcode(self):
    #     self.generate_pc_laptop_sequence()

class PmrMaster(models.Model):
    _name = "pmr.master"
    _description = "Pmr Condtion"

    name = fields.Char(string="Condition", store=True)
    color = fields.Integer(string="Color Index")


class PmrItmsInventoryMovement(models.Model):
    _name = "pmr.itms.inventory.movement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "IT Inventory Movement"
   
    name_product = fields.Char(string="Product", store=True)
    pmr_create_date = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    pmr_itms_departement = fields.Many2one('hr.department', string="Departement", required=True, store=True)
    pmr_itms_user = fields.Many2one('pmr.itms.user', string="User", required=True)
    pmr_quantity_product_it = fields.Float(string="On Hand Quantity", required=True, default=1)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
    product_location_unit = fields.Many2one('pmr.location.unit', string="Location", store=True)