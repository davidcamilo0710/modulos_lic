# -*- coding: utf-8 -*-
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

PARAM_ENABLED = "odoo_license_stealth.enabled"


class PublisherWarrantyContract(models.AbstractModel):
    """Odoo 19: corta el 'publisher warranty' sin salir a la red.

    Se intercepta únicamente `_get_sys_logs`, que es el único punto del
    árbol que ejecuta la petición HTTP. `update_notification` se deja tal
    cual (el de Odoo 19): recibe la respuesta fabricada y persiste el
    estado igual que si viniera del servidor.
    """

    _inherit = "publisher_warranty.contract"

    @api.model
    def _stealth_enabled(self):
        # En 19 get_param sigue existiendo (la 20 lo quitó).
        val = self.env["ir.config_parameter"].sudo().get_param(PARAM_ENABLED, "True")
        return str(val).lower() in ("1", "true", "yes", "on")

    @api.model
    def _stealth_enterprise_info(self):
        ICP = self.env["ir.config_parameter"].sudo()

        def g(key):
            return ICP.get_param(key) or False

        return {
            "expiration_date": g("database.expiration_date"),
            "expiration_reason": g("database.expiration_reason") or "renewal",
            "enterprise_code": g("database.enterprise_code"),
            "database_already_linked_subscription_url":
                g("database.already_linked_subscription_url"),
            "database_already_linked_email": g("database.already_linked_email"),
            "database_already_linked_send_mail_url":
                g("database.already_linked_send_mail_url"),
        }

    @api.model
    def _get_sys_logs(self):
        """Devuelve la 'respuesta del servidor' sin salir a la red.

        En Odoo 19 el esquema es el mismo anidado en `enterprise_info`
        (existe desde la 16), así que no hace falta compatibilidad extra.
        """
        if not self._stealth_enabled():
            return super()._get_sys_logs()
        return {
            "messages": [],  # sin avisos del servidor: ni el de exceso de usuarios
            "enterprise_info": self._stealth_enterprise_info(),
        }

    @api.model
    def _get_message(self):
        # En 19 NO existen los 'light users' (son de la 20): se omiten.
        msg = super()._get_message()
        try:
            n = int(self.env["ir.config_parameter"].sudo().get_param(
                "odoo_license_stealth.reported_users", 0) or 0)
        except (TypeError, ValueError):
            n = 0
        if n > 0:
            msg["nbr_users"] = n
            msg["nbr_active_users"] = n
            for key in ("nbr_share_users", "nbr_active_share_users"):
                if key in msg:
                    msg[key] = 0
        return msg