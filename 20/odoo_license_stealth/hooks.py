# -*- coding: utf-8 -*-
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

CRON_XMLID = "mail.ir_cron_module_update_notification"
DEFAULT_EXPIRATION = "2099-12-31 00:00:00"


def _get_env(args):
    if len(args) == 1:
        return args[0]
    return api.Environment(args[0], SUPERUSER_ID, {})


def post_init_hook(*args):
    env = _get_env(args)
    ICP = env["ir.config_parameter"].sudo()
    ICP.set_str("database.expiration_date", DEFAULT_EXPIRATION)
    ICP.set_str("database.expiration_reason", "renewal")
    ICP.set_bool("odoo_license_stealth.enabled", True)
    ICP.set_bool("odoo_license_stealth.disable_cron", True)
    ICP.set_int("odoo_license_stealth.reported_users", 0)

    cron = env.ref(CRON_XMLID, raise_if_not_found=False)
    if cron:
        cron.sudo().active = False
        _logger.info("odoo_license_stealth: cron '%s' desactivado", cron.name)


def uninstall_hook(*args):
    env = _get_env(args)
    cron = env.ref(CRON_XMLID, raise_if_not_found=False)
    if cron:
        cron.sudo().active = True
        _logger.info("odoo_license_stealth: cron '%s' reactivado", cron.name)