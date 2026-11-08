# -*- coding: utf-8 -*-
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

PARAM_ENABLED = "odoo_license_stealth.enabled"


class PublisherWarrantyContract(models.AbstractModel):
    """Corta el 'ping' de licencia sin tocar la red.

    Se intercepta únicamente `_get_sys_logs`, que es el único punto del
    árbol que ejecuta la petición HTTP. `update_notification` se deja tal
    cual (el de Odoo): recibe la respuesta fabricada y persiste el estado
    igual que si viniera del servidor.
    """

    _inherit = "publisher_warranty.contract"

    @api.model
    def _stealth_enabled(self):
        return self.env["ir.config_parameter"].sudo().get_bool(PARAM_ENABLED, True)

    @api.model
    def _stealth_enterprise_info(self):
        ICP = self.env["ir.config_parameter"].sudo()
        return {
            "expiration_date": ICP.get_str("database.expiration_date") or False,
            "expiration_reason": ICP.get_str("database.expiration_reason") or "renewal",
            "enterprise_code": ICP.get_str("database.enterprise_code") or False,
            "database_already_linked_subscription_url":
                ICP.get_str("database.already_linked_subscription_url") or False,
            "database_already_linked_email":
                ICP.get_str("database.already_linked_email") or False,
            "database_already_linked_send_mail_url":
                ICP.get_str("database.already_linked_send_mail_url") or False,
        }

    @api.model
    def _get_sys_logs(self):
        """Devuelve la 'respuesta del servidor' sin salir a la red."""
        if not self._stealth_enabled():
            return super()._get_sys_logs()
        return {
            "messages": [],  # sin mensajes del servidor: nada que inyectar en el canal
            "enterprise_info": self._stealth_enterprise_info(),
            "payload": self._get_message(),  # trazabilidad local de lo que se habría enviado
        }

    @api.model
    def _get_message(self):
        """Permite falsear el conteo de usuarios del payload."""
        msg = super()._get_message()
        n = self.env["ir.config_parameter"].sudo().get_int(
            "odoo_license_stealth.reported_users", 0)
        if n > 0:
            msg["nbr_users"] = n
            msg["nbr_active_users"] = n
            for key in ("nbr_share_users", "nbr_active_share_users",
                        "nbr_light_users", "nbr_active_light_users"):
                if key in msg:
                    msg[key] = 0
        return msg