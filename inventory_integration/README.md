# Inventory Integration Module for Odoo

This Odoo module allows you to import and view aggregated inventory data from external inventory management systems via API.

## Features

- 🔗 **API Integration**: Connect using secure API tokens
- 📊 **Data Aggregation**: View min/max/avg for numbers, popular values for text
- 📋 **Read-only Viewer**: Browse inventories and field-level statistics
- 🔄 **Refresh Data**: Update inventory data with latest aggregations
- 🎯 **Multiple Field Types**: Support for text, number, boolean, link fields

## Installation

### Prerequisites

- Odoo 15.0 or later (compatible with 16.0, 17.0)
- Python 3.8+
- `requests` Python library

### Install Python Dependencies

```bash
pip install requests
```

### Install the Module

1. **Copy module to Odoo addons directory:**
   ```bash
   cp -r inventory_integration /path/to/odoo/addons/
   ```

2. **Update Odoo addons list:**
   - Restart Odoo server with `--update=all` flag, or
   - Go to Apps → Update Apps List (developer mode)

3. **Install the module:**
   - Go to Apps
   - Search for "Inventory Integration"
   - Click "Install"

## Configuration

### 1. Configure API Base URL

By default, the module uses `http://localhost:3000` as the API base URL.

To change it:
- Open the import wizard
- Modify the "API Base URL" field
- Or set a default in the wizard model

### 2. Obtain API Token

From your inventory application:
1. Navigate to inventory Settings tab
2. Click "Generate API Token"
3. Copy the generated token

## Usage

### Import Inventory Data

1. **Navigate to**: Inventory Integration → Import from API
2. **Enter**:
   - API Token (from your inventory system)
   - API Base URL (default: http://localhost:3000)
   - (Optional) Select existing inventory to update
3. **Click**: "Import"
4. **Result**: View imported inventory with aggregated statistics

### View Imported Inventories

1. **Navigate to**: Inventory Integration → Imported Inventories
2. **Click** on any inventory to view:
   - Basic info (name, total items, import date)
   - Field aggregations with statistics
   - Top values for text fields
   - Min/max/avg for numeric fields

### Refresh Inventory Data

1. Open an imported inventory
2. Click "Refresh Data" button
3. Data will be re-fetched from API with latest statistics

## API Specification

The module expects the following API endpoint:

**Endpoint**: `GET /api/inventory/odoo/data?token=<api_token>`

**Response Format**:
```json
{
  "inventoryId": "abc123",
  "inventoryName": "My Inventory",
  "description": "Description text",
  "totalItems": 150,
  "fields": [
    {
      "fieldName": "Price",
      "fieldType": "number",
      "aggregation": {
        "min": 10.5,
        "max": 999.99,
        "average": 250.75,
        "count": 150
      }
    },
    {
      "fieldName": "Category",
      "fieldType": "text",
      "aggregation": {
        "topValues": [
          {"value": "Electronics", "count": 45},
          {"value": "Books", "count": 30}
        ],
        "uniqueCount": 10,
        "totalCount": 150
      }
    },
    {
      "fieldName": "In Stock",
      "fieldType": "boolean",
      "aggregation": {
        "trueCount": 120,
        "falseCount": 25,
        "nullCount": 5
      }
    }
  ]
}
```

## Module Structure

```
inventory_integration/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── inventory_import.py      # Main inventory model
│   └── inventory_field.py       # Field aggregation model
├── wizard/
│   ├── __init__.py
│   ├── import_wizard.py         # Import wizard logic
│   └── import_wizard_views.xml
├── views/
│   ├── inventory_import_views.xml
│   ├── inventory_field_views.xml
│   └── menu_views.xml
├── security/
│   └── ir.model.access.csv
└── static/
    └── description/
        ├── icon.png
        └── index.html
```

## Models

### inventory.import
Main model storing imported inventory data:
- `name`: Inventory name
- `inventory_id`: External inventory ID
- `description`: Inventory description
- `total_items`: Number of items
- `api_token`: API access token
- `field_ids`: Related field aggregations
- `state`: Import status (draft/imported/error)

### inventory.field
Field aggregation data:
- `field_name`: Name of the field
- `field_type`: Type (text/number/boolean/link/long)
- `aggregation_json`: Raw JSON data
- Number fields: min, max, average, count
- Text fields: unique_count, total_count, top_values
- Boolean fields: true_count, false_count, null_count

## Troubleshooting

### Connection Errors

**Problem**: Cannot connect to API

**Solutions**:
- Verify API base URL is correct
- Check if backend server is running
- Ensure firewall allows connection
- Check Odoo server logs for detailed error

### Invalid Token

**Problem**: "Invalid API token" error

**Solutions**:
- Generate new token from inventory system
- Verify token is copied completely
- Check token hasn't expired

### Import Fails

**Problem**: Import fails with error

**Solutions**:
- Check error message in form
- Verify API response format matches specification
- Check Odoo server logs: `odoo-bin --log-level=debug`

## Development

### Enable Developer Mode

1. Settings → Activate Developer Mode
2. Access technical menus and debug info

### View Logs

```bash
tail -f /var/log/odoo/odoo-server.log
```

### Debug Import

Add logging in `import_wizard.py`:
```python
import logging
_logger = logging.getLogger(__name__)
_logger.info('Debug message here')
```

## Security

- API tokens stored encrypted in database
- User access controlled via Odoo security groups
- Read-only access for public users
- Full CRUD for authenticated users

## License

LGPL-3

## Support

For issues or questions:
- Check Odoo logs
- Verify API endpoint accessibility
- Review module documentation

## Changelog

### Version 1.0.0
- Initial release
- API token-based import
- Field aggregation display
- Refresh functionality
- Multi-field type support
