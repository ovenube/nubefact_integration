# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "Nubefact Integration",
			"category": "Modules",
			"label": _("Nubefact Integration"),
			"color": "#3498db",
			"icon": "octicon octicon-repo",
			"type": "module",
			"description": "Configuracion del modulo Nubefact para facturacion electronica"
		}
	]
