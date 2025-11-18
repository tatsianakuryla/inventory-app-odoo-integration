from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import requests
import logging

_logger = logging.getLogger(__name__)

class InventoryImportWizard(models.TransientModel):
    _name = 'inventory.import.wizard'
    _description = 'Import Inventory Data Wizard'

    api_token = fields.Char(
        string='API Token',
        required=True,
        help='Enter the API token provided by the inventory system'
    )
    
    api_base_url = fields.Char(
        string='API Base URL',
        default='https://site--inventory-app-server--sm9fnltkyqvh.code.run',
        required=True,
        help='Base URL of the inventory API'
    )
    
    inventory_import_id = fields.Many2one(
        comodel_name='inventory.import',
        string='Update Existing Inventory',
        help='Leave empty to create new, or select to update existing'
    )
    
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('done', 'Done'),
            ('error', 'Error')
        ],
        default='draft',
        string='Status'
    )
    
    error_message = fields.Text(
        string='Error Message',
        readonly=True
    )

    @api.constrains('api_token')
    def _check_api_token(self):
        for record in self:
            if record.api_token and len(record.api_token) < 10:
                raise ValidationError(_('API Token seems invalid. Please check and try again.'))

    def action_import(self):
        self.ensure_one()
        
        try:
            data = self._fetch_inventory_data()
            if not data:
                raise UserError(_('No data received from API'))
            inventory = self._create_or_update_inventory(data)
            self._create_field_aggregations(inventory, data.get('fields', []))

            self.state = 'done'
            return {
                'type': 'ir.actions.act_window',
                'name': _('Imported Inventory'),
                'res_model': 'inventory.import',
                'res_id': inventory.id,
                'view_mode': 'form',
                'target': 'current',
            }
            
        except requests.RequestException as e:
            error_msg = f'API Request failed: {str(e)}'
            _logger.error(error_msg)
            self.state = 'error'
            self.error_message = error_msg
            if self.inventory_import_id:
                self.inventory_import_id.write({
                    'state': 'error',
                    'error_message': error_msg
                })
            raise UserError(_(error_msg))
            
        except Exception as e:
            error_msg = f'Import failed: {str(e)}'
            _logger.error(error_msg, exc_info=True)
            self.state = 'error'
            self.error_message = error_msg
            if self.inventory_import_id:
                self.inventory_import_id.write({
                    'state': 'error',
                    'error_message': error_msg
                })
            raise UserError(_(error_msg))

    def _fetch_inventory_data(self):
        url = f"{self.api_base_url}/api/inventory/odoo/data"
        params = {'token': self.api_token}
        
        _logger.info(f'Fetching inventory data from: {url}')
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            _logger.info(f'Successfully fetched data for inventory: {data.get("inventoryName")}')
            return data
            
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                raise UserError(_('Invalid API token or inventory not found'))
            elif e.response.status_code == 401:
                raise UserError(_('Unauthorized. Please check your API token'))
            else:
                raise UserError(_(f'HTTP Error {e.response.status_code}: {str(e)}'))
        except requests.ConnectionError:
            raise UserError(_(f'Cannot connect to API at {self.api_base_url}. Please check the URL.'))
        except requests.Timeout:
            raise UserError(_('API request timed out. Please try again.'))

    def _create_or_update_inventory(self, data):
        vals = {
            'name': data.get('inventoryName', 'Unnamed Inventory'),
            'inventory_id': data.get('inventoryId', ''),
            'description': data.get('description', ''),
            'total_items': data.get('totalItems', 0),
            'api_token': self.api_token,
            'state': 'imported',
            'import_date': fields.Datetime.now(),
            'error_message': False,
        }
        
        if self.inventory_import_id:
            self.inventory_import_id.write(vals)
            self.inventory_import_id.field_ids.unlink()
            return self.inventory_import_id
        else:
            return self.env['inventory.import'].create(vals)

    def _create_field_aggregations(self, inventory, fields_data):
        InventoryField = self.env['inventory.field']
        
        for idx, field_data in enumerate(fields_data):
            field_vals = {
                'inventory_import_id': inventory.id,
                'sequence': (idx + 1) * 10,
                'field_name': field_data.get('fieldName', 'Unknown'),
                'field_type': field_data.get('fieldType', 'text'),
            }
            
            field = InventoryField.create(field_vals)
            aggregation = field_data.get('aggregation', {})
            if aggregation:
                field.parse_aggregation_data(aggregation)
        
        _logger.info(f'Created {len(fields_data)} field aggregations for inventory {inventory.name}')

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}
