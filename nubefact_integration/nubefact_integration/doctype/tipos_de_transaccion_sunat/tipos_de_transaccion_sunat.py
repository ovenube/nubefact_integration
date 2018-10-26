# -*- coding: utf-8 -*-
# Copyright (c) 2018, OVENUBE and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class TiposdeTransaccionSunat(Document):
	pass

@frappe.whitelist()
def get_tipo_transaccion(customer):
	cliente = frappe.get_doc("Customer", customer)
	if cliente.codigo_tipo_documento == '-' or cliente.codigo_tipo_documento == '1' or cliente.codigo_tipo_documento == '6':
		transaccion = frappe.get_doc("Tipos de Transaccion Sunat", "VENTA INTERNA")
	resultado = {"codigo": transaccion.codigo_tipo_transaccion, "descripcion": transaccion.name}
	return resultado

