from odoo import models, fields, api


class InventoryImport(models.Model):
    _name = 'inventory.import'
    _description = 'Imported Inventory Data'
    _order = 'create_date desc'

    name = fields.Char(
        string='Inventory Management System',
        required=True,
        help='Name of the imported inventory'
    )

    inventory_id = fields.Char(
        string='External Inventory ID',
        required=True,
        help='ID from the external system'
    )

    description = fields.Text(
        string='Description',
        help='Inventory description'
    )

    total_items = fields.Integer(
        string='Total Items',
        default=0,
        help='Total number of items in this inventory'
    )

    api_token = fields.Char(
        string='API Token',
        required=True,
        help='Token used to import this inventory'
    )

    field_ids = fields.One2many(
        comodel_name='inventory.field',
        inverse_name='inventory_import_id',
        string='Fields',
        help='Aggregated field data'
    )

    field_count = fields.Integer(
        string='Fields Count',
        compute='_compute_field_count',
        store=True
    )

    import_date = fields.Datetime(
        string='Import Date',
        default=fields.Datetime.now,
        readonly=True,
        help='Date and time when data was imported'
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('imported', 'Imported'),
            ('error', 'Error')
        ],
        string='Status',
        default='draft',
        required=True
    )

    error_message = fields.Text(
        string='Error Message',
        readonly=True
    )

    @api.depends('field_ids')
    def _compute_field_count(self):
        for record in self:
            record.field_count = len(record.field_ids)

    def action_refresh_data(self):
        self.ensure_one()
        wizard = self.env['inventory.import.wizard'].create({
            'api_token': self.api_token,
            'inventory_import_id': self.id,
        })
        return wizard.action_import()

    def unlink(self):
        self.field_ids.unlink()
        return super(InventoryImport, self).unlink()
