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

def get_serie_correlativo(name):
    tipo, serie, correlativo = name.split("-")
    return tipo, serie, correlativo

def get_moneda(currency):
    if currency == "PEN":
        moneda = 1
    elif currency == "USD":
        moneda = 2
    return moneda

def get_igv(name, doctype):
    if doctype == "Sales Invoice":
        tax = frappe.db.get_single_value("Configuracion", "igv_ventas")
        tax_name = frappe.db.get_value("Sales Taxes and Charges", filters={"parent": name, "account_head": tax})
        doc_tax = frappe.get_doc("Sales Taxes and Charges", tax_name)
    elif doctype == "Purchase Invoice":
        tax = frappe.db.get_single_value("Configuracion", "igv_compras")
        tax_name = frappe.db.get_value("Purchase Taxes and Charges", filters={"parent": name, "account_head": tax})
        doc_tax = frappe.get_doc("Purchase Taxes and Charges", tax_name)
    return doc_tax.rate, doc_tax.tax_amount

def get_tipo_producto(item_name):
    producto = frappe.get_doc("Item", item_name)
    if producto.item_group == "Servicios":
        tipo_producto = "ZZ"
    else:
        tipo_producto = "NIU"
    return tipo_producto

def get_serie_online(doc_serie):
    online_serie =[]
    online = False
    configuracion = frappe.get_doc("Configuracion", "Configuracion")
    series = configuracion.serie_factura
    for serie in series:
        if serie.online:
            online_serie.append(serie.serie_factura)
    series = configuracion.serie_factura_contingencia
    for serie in series:
        if serie.online:
            online_serie.append(serie.serie_factura_contingencia)
    series = configuracion.serie_boleta
    for serie in series:
        if serie.online:
            online_serie.append(serie.serie_boleta)
    series = configuracion.serie_boleta_contingencia
    for serie in series:
        if serie.online:
            online_serie.append(serie.serie_boleta_contingencia)
    series = configuracion.serie_nota_credito
    for serie in series:
        if serie.online:
            online_serie.append(serie.serie_nota_credito)
    series = configuracion.serie_nota_credito_contingencia
    for serie in series:
        if serie.online:
            online_serie.append(serie.serie_nota_credito_contingencia)
    series = configuracion.serie_nota_debito
    for serie in series:
        if serie.online:
            online_serie.append(serie.serie_nota_debito)
    series = configuracion.serie_nota_debito_contingencia
    for serie in series:
        if serie.online:
            online_serie.append(serie.serie_nota_debito_contingencia)
    for serie in online_serie:
        if doc_serie in serie:
            online = True
    return online