# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def assign_picking(self):
        """ Try to assign the moves to an existing picking that has not been
        reserved yet and has the same procurement group, locations and picking
        type (moves should already have them identical). Otherwise, create a new
        picking to assign them to. """
        Picking = self.env['stock.picking']

        # If this method is called in batch by a write on a one2many and
        # at some point had to create a picking, some next iterations could
        # try to find back the created picking. As we look for it by searching
        # on some computed fields, we have to force a recompute, else the
        # record won't be found.
        self.recompute()

        for move in self:
            picking = Picking.search([
                ('group_id', '=', move.group_id.id),
                ('location_id', '=', move.location_id.id),
                ('location_dest_id', '=', move.location_dest_id.id),
                ('picking_type_id', '=', move.picking_type_id.id),
                ('printed', '=', False),
                ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])], limit=1)

            push_picking = Picking.search([
                ('group_id', '=', move.group_id.id),
                ('location_id', '=', move.location_id.id),
                ('location_dest_id', '=', move.location_dest_id.id),
                ('picking_type_id', '=', move.picking_type_id.id),
                ('origin', '=', move.origin),
                ('printed', '=', False),
                ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])], limit=1)
            if not picking or not push_picking:
                picking = Picking.create(move._get_new_picking_values())
            if push_picking:
                picking = push_picking
            move.write({'picking_id': picking.id})
        return True
    _picking_assign = assign_picking