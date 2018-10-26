# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import frappe

def tipo_de_comprobante(codigo):
    if codigo == "1":
        tipo_comprobante = 1
    elif codigo == "3":
        tipo_comprobante = 2
    elif codigo == "7":
        tipo_comprobante = 3
    elif codigo == "8":
        tipo_comprobante = 4
    return tipo_comprobante

def get_serie_correlativo(name, contingencia):
    if contingencia:
        tipo, serie, correlativo = name.split("-")
    else:
        serie, correlativo = name.split("-")
    return serie, correlativo

def get_moneda(currency):
    if currency == "PEN":
        moneda = 1
    elif currency == "USD":
        moneda = 2
    return moneda

def get_igv(name):
    tax_name = frappe.db.get_value("Sales Taxes and Charges", filters={"parent": name})
    tax = frappe.get_doc("Sales Taxes and Charges", tax_name)
    if tax.description == "IGV":
        return tax.rate, tax.tax_amount

def get_tipo_producto(item_name):
    producto = frappe.get_doc("Item", item_name)
    if producto.item_group == "Servicios":
        tipo_producto = "ZZ"
    else:
        tipo_producto = "NIU"
    return tipo_producto
