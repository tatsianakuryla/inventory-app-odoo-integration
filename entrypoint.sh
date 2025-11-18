#!/bin/bash
set -e

echo "=== Railway Odoo Entrypoint ==="
echo "PORT: ${PORT}"
echo "DB_HOST: ${DB_HOST}"
echo "DB_PORT: ${DB_PORT}"
echo "DB_USER: ${DB_USER}"

# Database configuration with fallback values
DB_HOST="${DB_HOST:-postgres.railway.internal}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-odoo}"
DB_PASSWORD="${DB_PASSWORD:-strong_password_here_123}"
HTTP_PORT="${PORT:-8069}"

echo ""
echo "Using database configuration:"
echo "  Host: ${DB_HOST}"
echo "  Port: ${DB_PORT}"
echo "  User: ${DB_USER}"
echo "  HTTP Port: ${HTTP_PORT}"
echo ""

cat > /tmp/odoo.conf <<EOF
[options]
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
data_dir = /var/lib/odoo
proxy_mode = True
list_db = False
db_name = ${DB_NAME:-railway}
dbfilter = ^${DB_NAME:-railway}\$
without_demo = all
http_interface = 0.0.0.0
http_port = ${HTTP_PORT}
db_host = ${DB_HOST}
db_port = ${DB_PORT}
db_user = ${DB_USER}
db_password = ${DB_PASSWORD}
EOF

echo "Generated /tmp/odoo.conf"
echo ""
echo "Starting Odoo..."

# Initialize database if DB_NAME is set, otherwise Odoo will prompt for DB creation
if [ -n "${DB_NAME}" ]; then
    echo "Initializing database: ${DB_NAME}"
    odoo -c /tmp/odoo.conf -d "${DB_NAME}" -i base --stop-after-init
    echo "Database initialized. Starting Odoo normally..."
    exec odoo -c /tmp/odoo.conf -d "${DB_NAME}"
else
    exec odoo -c /tmp/odoo.conf
fi
