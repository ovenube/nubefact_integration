# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
        {
            "label": _("Configuracion"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Autenticacion Nubefact",
                    "description": _("Configura la conexión con Nubefact"),
					"onboard": 1,
                },
				 {
                    "type": "doctype",
                    "name": "Configuracion Nubefact",
                    "description": _("Configura los numeros de serie y productos para el uso de la facturacion electronica"),
					"onboard": 1,
                }
            ]
        }
    ]
