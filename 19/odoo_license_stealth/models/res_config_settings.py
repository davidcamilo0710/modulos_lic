# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    license_stealth_enabled = fields.Boolean(
        string="Neutralizar la verificación de licencia",
        config_parameter="odoo_license_stealth.enabled",
        default=True,
    )
    license_stealth_expiration_date = fields.Datetime(
        string="Fecha de expiración simulada",
        config_parameter="database.expiration_date",
        default="2099-12-31 00:00:00",
    )
    license_stealth_expiration_reason = fields.Selection(
        selection=[
            ("renewal", "Renovación (suscripción activa)"),
            ("trial", "Trial"),
            ("demo", "Demo"),
        ],
        string="Motivo de expiración",
        config_parameter="database.expiration_reason",
        default="renewal",
    )
    license_stealth_enterprise_code = fields.Char(
        string="Código Enterprise simulado",
        config_parameter="database.enterprise_code",
    )
    license_stealth_reported_users = fields.Integer(
        string="Usuarios reportados (0 = reales)",
        config_parameter="odoo_license_stealth.reported_users",
        default=0,
    )
    license_stealth_disable_cron = fields.Boolean(
        string="Desactivar el cron 'Publisher: Update Notification'",
        config_parameter="odoo_license_stealth.disable_cron",
        default=True,
    )
    def set_values(self):
            super().set_values()
            for cron in self.env["ir.cron"].with_context(active_test=False).search([]):
                code = cron.code or ""
                model = cron.model_id.model if cron.model_id else ""
                if "update_notification" in code or model == "publisher_warranty.contract":
                    cron.sudo().active = not self.license_stealth_disable_cron