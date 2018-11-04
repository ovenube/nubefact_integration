# -*- coding: utf-8 -*-
# Copyright (c) 2018, OVENUBE and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.setup.doctype.naming_series.naming_series import NamingSeries

class Configuracion(NamingSeries):
	def get_series(self):
		serie_ventas = self.get_options("Sales Invoice")
		serie_ventas.replace("\n\n", "\n")
		serie_ventas = serie_ventas.split("\n")
		serie_compras = self.get_options("Purchase Invoice")
		serie_compras.replace("\n\n", "\n")
		serie_compras = serie_compras.split("\n")
		series_dict = {}
		series_dict["venta"] = []
		series_dict["compra"] = []
		for serie in serie_ventas:
			series_dict["venta"].append(serie)
		for serie in serie_compras:
			series_dict["compra"].append(serie)
		return series_dict

@frappe.whitelist()
def get_doc_serie(doctype, is_return, contingencia, codigo_tipo_documento):
	doc_series = []
	configuracion = frappe.get_doc("Configuracion", "Configuracion")
	if doctype == "Sales Invoice":
		if is_return == "1":
			comprobante = frappe.get_doc("Tipos de Comprobante", "Nota de Crédito")
			if contingencia == "1":
				series = configuracion.serie_nota_credito_contingencia
				if codigo_tipo_documento == "6":
					for serie in series:
						if serie.comprobante == "Factura":
							doc_series.append(serie.serie_nota_credito_contingencia)
				elif codigo_tipo_documento == "1" or codigo_tipo_documento == "-":
					for serie in series:
						if serie.comprobante == "Boleta":
							doc_series.append(serie.serie_nota_credito_contingencia)
			else:
				series = configuracion.serie_nota_credito
				if codigo_tipo_documento == "6":
					for serie in series:
						if serie.comprobante == "Factura":
							doc_series.append(serie.serie_nota_credito)
				elif codigo_tipo_documento == "1" or codigo_tipo_documento == "-":
					for serie in series:
						if serie.comprobante == "Boleta":
							doc_series.append(serie.serie_nota_credito)
		else:
			if codigo_tipo_documento == "6":
				comprobante = frappe.get_doc("Tipos de Comprobante", "Factura")
				if contingencia == "1":
					series = configuracion.serie_factura_contingencia
					for serie in series:
						doc_series.append(serie.serie_factura_contingencia)
				else:
					series = configuracion.serie_factura
					for serie in series:
						doc_series.append(serie.serie_factura)
			elif codigo_tipo_documento == "1" or codigo_tipo_documento == "-":
				comprobante = frappe.get_doc("Tipos de Comprobante", "Boleta de Venta")
				if contingencia == "1":
					series = configuracion.serie_boleta_contingencia
					for serie in series:
						doc_series.append(serie.serie_boleta_contingencia)
				else:
					series = configuracion.serie_boleta
					for serie in series:
						doc_series.append(serie.serie_boleta)
	elif doctype == "Purchase Invoice":
		if is_return == "1":
			comprobante = frappe.get_doc("Tipos de Comprobante", "Nota de Débito")
			if contingencia == "1":
				series = configuracion.serie_nota_debito_contingencia
				if codigo_tipo_documento == "6":
					for serie in series:
						if serie.comprobante == "Factura":
							doc_series.append(serie.serie_nota_debito_contingencia)
				elif codigo_tipo_documento == "1" or codigo_tipo_documento == "-":
					for serie in series:
						if serie.comprobante == "Boleta":
							doc_series.append(serie.serie_nota_debito_contingencia)
			else:
				series = configuracion.serie_nota_debito
				if codigo_tipo_documento == "6":
					for serie in series:
						if serie.comprobante == "Factura":
							doc_series.append(serie.serie_nota_debito)
				elif codigo_tipo_documento == "1" or codigo_tipo_documento == "-":
					for serie in series:
						if serie.comprobante == "Boleta":
							doc_series.append(serie.serie_nota_debito)
	resultado = {"codigo": comprobante.codigo_tipo_comprobante, "descripcion": comprobante.name, "series": doc_series}
	return resultado