# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class ReportSaleLineJim(models.Model):
    _name = "report.sale.line.jim"
    _description = "Sales Lines Orders Statistics"
    _auto = False
    _rec_name = 'order_line_id'
    _order = 'order_line_id'

    order_line_id = fields.Many2one('sale.order.line', readonly=True)
    product_id = fields.Many2one('product.product', string ="Articulo", readonly=True)
    product_code = fields.Char(string="Referencia", readonly=True)
    template_code = fields.Char(string="Ref (patrón)", readonly=True)
    qty_delivered = fields.Float(related="order_line_id.qty_delivered", string="Entregada", readonly=True)
    qty_invoiced = fields.Float(related="order_line_id.qty_invoiced", string="Facturada", readonly=True)
    product_uom_qty = fields.Float(related="order_line_id.product_uom_qty", string="Pedida", readonly=True)
    partner_id = fields.Many2one('res.partner', string="Cliente", readonly=True)
    user_id = fields.Many2one('res.user', string="Comercial", readonly=True)
    order_id = fields.Many2one('sale.order', string="Order", readonly=True)

    #picking_id = fields.Many2one('stock.picking', readonly=True)
    line_delivered_state = fields.Selection([('E','Entregado'), ('NE','No entregado')], "Entrega", readonly=True)
    line_invoice_state = fields.Selection([('NF1','No fact 100%'), ('F','Facturado'), ('NF','No facturado')], "Factura", readonly=True)
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('proforma', 'Proforma'),
        ('lqdr', 'Pending LQDR'),
        ('progress_lqdr', 'Progress LQDR'),
        ('pending', 'Revision Pending'),
        ('progress', 'Confirm in Progress'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ])
    date = fields.Datetime(string="Fecha", readonly=True)


    def _select(self):
        select_str = """            
             SELECT l.id as id,
                    l.id as order_line_id, 
                    l.product_id as product_id,
                    pp.default_code as product_code,
                    pt.default_code as template_code,
                    so.partner_id as partner_id,
                    so.state as state,
                    so.user_id as user_id,
                    so.date_order as date,
                    so.id as order_id,
                    
                    CASE WHEN l.qty_delivered > 0 
                        THEN 'E'
                        ELSE 'NE'
                    END as line_delivered_state,
                    CASE 
                        WHEN l.qty_invoiced = 0 THEN 'NF'
                        WHEN l.qty_to_invoice = qty_delivered THEN 'F'
                        ELSE 'NF1'
                    END as line_invoice_state                                       
        """
        return select_str

    def _from(self):
        from_str = """sale_order_line l
                        left join sale_order so on l.order_id = so.id 
                        left join product_product pp on pp.id = l.product_id
                        left join product_template pt on pp.product_tmpl_id = pt.id"""
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY 
                    l.id,
                    l.product_id,
                    pp.default_code,
                    pt.default_code,
                    so.partner_id,
                    so.state,
                    so.user_id,
                    so.date_order,
                    so.id
                    
                    
        """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM %s
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))