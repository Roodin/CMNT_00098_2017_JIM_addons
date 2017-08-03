# -*- coding: utf-8 -*-
# Copyright 2017 Omar Castiñeira, Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api,  _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):

    _inherit = "product.template"

    volume = fields.Float(
        'Volume', compute='_compute_volume', inverse='_set_volume',
        help="The volume in m3.", store=True, digits=(10, 6))
    # Avoid translations in those fields because of slow performance when 
    # create a product.product with lang in context.
    name = fields.Char(translate=False)
    description = fields.Text(translate=False)
    description_sale = fields.Text(translate=False)
    description_picking = fields.Text(translate=False)
    description_purchase = fields.Text(translate=False)


class ProductProduct(models.Model):

    _inherit = "product.product"

    volume = fields.Float('Volume', help="The volume in m3.", digits=(10, 6))

    # def apply_package_dimensions(self):


class ProductPackaging(models.Model):

    _inherit = "product.packaging"


    def compute_product_dimensions(self):
        if self.qty == 0:
            raise ValidationError(_("Check quantity !!!!"))
        self.product_tmpl_id.weight = self.max_weight / self.qty
        self.product_tmpl_id.volume = self.height * self.width * \
                self.length / (self.qty )

        for product in self.product_tmpl_id.product_variant_ids:
            product.weight = self.product_tmpl_id.weight
            product.volume = self.product_tmpl_id.volume

        return True


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    legacy_code = fields.Char("Legacy code", size=18)


class ProductTag(models.Model):
    _inherit = "product.tag"

    legacy_code = fields.Char("Legacy code", size=18)
