# -*- coding: utf-8 -*-
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

DEFAULT_EXPIRATION = "2099-12-31"


def _get_env(args):
    # Odoo 17+ pasa el env; <=16 pasa (cr, registry).
    if len(args) == 1:
        return args[0]
    return api.Environment(args[0], SUPERUSER_ID, {})


def _warranty_crons(env):
    """Crons del publisher warranty, por modelo o por el código que ejecutan.

    Se buscan así en vez de por xmlid para no depender de un id que puede
    variar entre versiones.
    """
    out = env["ir.cron"].browse()
    for cron in env["ir.cron"].with_context(active_test=False).search([]):
        code = cron.code or ""
        model = cron.model_id.model if cron.model_id else ""
        if "update_notification" in code or model == "publisher_warranty.contract":
            out |= cron
    return out


def post_init_hook(*args):
    env = _get_env(args)
    ICP = env["ir.config_parameter"].sudo()
    ICP.set_param("database.expiration_date", DEFAULT_EXPIRATION)
    ICP.set_param("database.expiration_reason", "renewal")
    ICP.set_param("odoo_license_stealth.enabled", "True")
    ICP.set_param("odoo_license_stealth.disable_cron", "True")
    ICP.set_param("odoo_license_stealth.reported_users", "0")

    for cron in _warranty_crons(env):
        cron.sudo().active = False
        _logger.info("odoo_license_stealth: cron '%s' desactivado", cron.name)


def uninstall_hook(*args):
    env = _get_env(args)
    for cron in _warranty_crons(env):
        cron.sudo().active = True
        _logger.info("odoo_license_stealth: cron '%s' reactivado", cron.name)