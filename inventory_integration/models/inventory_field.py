from odoo import models, fields, api
import json


class InventoryField(models.Model):
    _name = 'inventory.field'
    _description = 'Inventory Field Aggregation'
    _order = 'sequence, field_name'

    inventory_import_id = fields.Many2one(
        comodel_name='inventory.import',
        string='Inventory Management System',
        required=True,
        ondelete='cascade'
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10
    )

    field_name = fields.Char(
        string='Field Name',
        required=True
    )

    field_type = fields.Selection(
        [
            ('text', 'Text'),
            ('long', 'Long Text'),
            ('number', 'Number'),
            ('link', 'Link'),
            ('boolean', 'Boolean')
        ],
        string='Field Type',
        required=True
    )

    aggregation_json = fields.Text(
        string='Aggregation Data (JSON)',
        help='Raw JSON aggregation data'
    )

    number_min = fields.Float(
        string='Minimum',
        digits=(16, 2)
    )

    number_max = fields.Float(
        string='Maximum',
        digits=(16, 2)
    )

    number_average = fields.Float(
        string='Average',
        digits=(16, 2)
    )

    number_count = fields.Integer(
        string='Count'
    )

    text_unique_count = fields.Integer(
        string='Unique Values'
    )

    text_total_count = fields.Integer(
        string='Total Values'
    )

    text_top_values = fields.Text(
        string='Top Values',
        help='Most popular values with counts'
    )

    boolean_true_count = fields.Integer(
        string='True Count'
    )

    boolean_false_count = fields.Integer(
        string='False Count'
    )

    boolean_null_count = fields.Integer(
        string='Null Count'
    )

    aggregation_summary = fields.Text(
        string='Summary',
        compute='_compute_aggregation_summary',
        store=False
    )

    @api.depends('field_type', 'number_min', 'number_max', 'number_average',
                 'text_unique_count', 'boolean_true_count', 'boolean_false_count')
    def _compute_aggregation_summary(self):
        for record in self:
            if record.field_type == 'number':
                record.aggregation_summary = (
                    f"Min: {record.number_min or 0:.2f}, "
                    f"Max: {record.number_max or 0:.2f}, "
                    f"Avg: {record.number_average or 0:.2f}, "
                    f"Count: {record.number_count or 0}"
                )
            elif record.field_type in ['text', 'long', 'link']:
                record.aggregation_summary = (
                    f"Unique: {record.text_unique_count or 0}, "
                    f"Total: {record.text_total_count or 0}"
                )
            elif record.field_type == 'boolean':
                record.aggregation_summary = (
                    f"True: {record.boolean_true_count or 0}, "
                    f"False: {record.boolean_false_count or 0}, "
                    f"Null: {record.boolean_null_count or 0}"
                )
            else:
                record.aggregation_summary = 'N/A'

    def parse_aggregation_data(self, aggregation_dict):
        self.aggregation_json = json.dumps(aggregation_dict, indent=2)

        if self.field_type == 'number':
            self.number_min = aggregation_dict.get('min')
            self.number_max = aggregation_dict.get('max')
            self.number_average = aggregation_dict.get('average')
            self.number_count = aggregation_dict.get('count', 0)

        elif self.field_type in ['text', 'long', 'link']:
            self.text_unique_count = aggregation_dict.get('uniqueCount', 0)
            self.text_total_count = aggregation_dict.get('totalCount', 0)
            top_values = aggregation_dict.get('topValues', [])
            if top_values:
                formatted_values = '\n'.join([
                    f"{item['value']} ({item['count']})"
                    for item in top_values[:10]
                ])
                self.text_top_values = formatted_values

        elif self.field_type == 'boolean':
            self.boolean_true_count = aggregation_dict.get('trueCount', 0)
            self.boolean_false_count = aggregation_dict.get('falseCount', 0)
            self.boolean_null_count = aggregation_dict.get('nullCount', 0)
