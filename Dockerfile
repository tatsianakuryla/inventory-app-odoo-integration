FROM odoo:17.0

USER root

# Copy custom module and entrypoint
COPY ./inventory_integration /mnt/extra-addons/inventory_integration
COPY ./entrypoint.sh /entrypoint.sh

# Set permissions
RUN chown -R odoo:odoo /mnt/extra-addons && \
    chmod +x /entrypoint.sh

USER odoo

# Expose port
EXPOSE 8069

# Use custom entrypoint
ENTRYPOINT ["/entrypoint.sh"]
