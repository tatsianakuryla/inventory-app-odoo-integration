FROM odoo:17.0

USER root

# Copy custom module
COPY ./inventory_integration /mnt/extra-addons/inventory_integration

# Set permissions
RUN chown -R odoo:odoo /mnt/extra-addons

USER odoo

# Default command
CMD ["odoo", "--addons-path=/mnt/extra-addons"]
