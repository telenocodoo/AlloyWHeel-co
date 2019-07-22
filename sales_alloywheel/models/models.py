# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools


# class SaleReport(models.Model):
#     _inherit = 'sale.report'
#     project_id = fields.Many2one('project.project', store=True)
#
#     # @api.depends('order_id')
#     # def get_project_sales(self):
#     #     self.project_id = self.order_id.id
#
#     @api.model_cr
#     def init(self):
#         rec = super(SaleReport, self).init()
#         tools.drop_view_if_exists(self._cr, 'sale_report')
#         x = self._cr.execute("""
#                     create or replace view sale_order as (
#                         select
#                             s.name from sale_order s
#                     )""")
#         print("::::::::,", x)
#         return rec


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    minimum_qtys = fields.Float(string="Minimum Quantity")

    @api.multi
    def server_do_action(self):
        product_template_ids = self.search([])
        for record in product_template_ids:
            if record.qty_available <= record.minimum_qtys:
                groups = self.env['res.groups'].search([('name', '=', 'ceo')])
                recipient_partners = []
                for group in groups:
                    for recipient in group.users:
                        if recipient.partner_id.id not in recipient_partners:
                            recipient_partners.append(recipient.partner_id.id)
                if len(recipient_partners):
                    record.message_post(body='There is No enough QTY',
                                        subtype='mt_comment',
                                        subject='Minimum Qty',
                                        partner_ids=recipient_partners,
                                        message_type='notification')

    @api.model
    def cron_do_task(self):
        self.server_do_action()


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    current_user_id = fields.Many2one('res.users', default=lambda self: self.env.user)

    @api.onchange('current_user_id')
    def get_current_access_partner(self):
        """"get current access partner related to current user"""
        self.partner_id = self.current_user_id.partner_id
