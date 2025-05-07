from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError

class HandoverFromGrn(models.Model):
    _name = "handover.from.grn"
    _description = "Transfer Location Pe"

    no_handover = fields.Many2one('pmr.itms.handover.it', string='Nomor Handover',store=True)
    handover_line_ids = fields.One2many('handover.from.grn.line', 'handover_id', string='Handover Lines')
    picking_id = fields.Many2one('stock.picking', string='Picking Reference', default=lambda self: self.env.context.get('default_picking_id'))

    @api.model
    def _get_default_move_lines(self, picking_id):
        move_lines = self.env['stock.move'].search([
            ('picking_id', '=', picking_id),
        ])
        
        default_lines = []
        for move in move_lines:
            default_lines.append({
                'pmr_jenis_perangkat': move.description_picking,
                'product_unit_category': move.product_uom.id,
                'pmr_quantity_product_it' : move.quantity_done,
            })
        return default_lines
    
    @api.model
    def default_get(self, fields):
        res = super(HandoverFromGrn, self).default_get(fields)
        
        picking_id = self.env.context.get('default_picking_id')
        
        if picking_id:
            default_lines = self._get_default_move_lines(picking_id)
            
            res['handover_line_ids'] = [(0, 0, line) for line in default_lines]
        
        return res
    
class HandoverFromGrnLine(models.Model):
    _name = "handover.from.grn.line"
    _description = "Handover From GRN Line"

    handover_id = fields.Many2one('handover.from.grn', string="ID Memo")
    pmr_jenis_perangkat = fields.Text(string="Item")
    pmr_merk_type = fields.Char(string="Merk/Type")
    pmr_quantity_product_it = fields.Float(string="Quantity",required=True)
    product_unit_category = fields.Many2one('uom.uom', string="Unit Category", required=True, store=True)
