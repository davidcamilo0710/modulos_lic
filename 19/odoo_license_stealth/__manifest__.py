# -*- coding: utf-8 -*-
{
    "name": "Odoo Enterprise License Stealth",
    "summary": "Neutraliza la verificación de licencia sin contactar a Odoo",
    "version": "19.0.1.0.0",
    "author": "DCMG",
    "license": "LGPL-3",
    "category": "Hidden/Technical",
    "depends": ["base_setup", "mail"],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}