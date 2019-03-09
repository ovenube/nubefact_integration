# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import frappe

def tipo_de_comprobante(codigo):
    if codigo == "01":
        tipo_comprobante = 1
    elif codigo == "03":
        tipo_comprobante = 2
    elif codigo == "07":
        tipo_comprobante = 3
    elif codigo == "08":
        tipo_comprobante = 4
    elif codigo == "09":
        tipo_comprobante = 7
    return tipo_comprobante

def get_serie_correlativo(name):
    tipo, serie, correlativo = name.split("-")
    return tipo, serie, correlativo

def get_doc_transportista(name):
    return frappe.get_doc("Supplier", name)

def get_doc_conductor(name):
    return frappe.get_doc("Driver", name)

def get_ubigeo(address):
    doc = frappe.get_doc("Address", address)
    return doc.ubigeo

def get_moneda(currency):
    if currency == "PEN" or currency == "SOL":
        moneda = 1
    elif currency == "USD":
        moneda = 2
    return moneda

def get_address_information(party_address):
    address = frappe.get_doc("Address", party_address)
    return frappe._dict({
        "address": address.address_line1 + "-" + address.city + "-" + address.state + "-" + address.country,
        "email": address.email_id
    })

def get_igv(name, doctype):
    if doctype == "Sales Invoice":
        conf_tax = frappe.db.get_single_value("Configuracion", "igv_ventas")
        account_head = frappe.db.get_value("Sales Taxes and Charges", filters={"parent": conf_tax})
        tax = frappe.get_doc("Sales Taxes and Charges", account_head)
        doc_tax_name = frappe.db.get_value("Sales Taxes and Charges",
                                           filters={"account_head": tax.account_head, "parent": name})
        doc_tax = frappe.get_doc("Sales Taxes and Charges", doc_tax_name)
    elif doctype == "Purchase Invoice":
        conf_tax = frappe.db.get_single_value("Configuracion", "igv_ventas")
        account_head = frappe.db.get_value("Purchase Taxes and Charges", filters={"parent": conf_tax})
        tax = frappe.get_doc("Purchase Taxes and Charges", account_head)
        doc_tax_name = frappe.db.get_value("Purchase Taxes and Charges",
                                           filters={"account_head": tax.account_head, "parent": name})
        doc_tax = frappe.get_doc("Purchase Taxes and Charges", doc_tax_name)
    return doc_tax.rate, doc_tax.tax_amount, doc_tax.included_in_print_rate

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
    #recorre todos los tipos de comprobante y almacena las series online en un diccionario
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
    series = configuracion.serie_guia_remision
    for serie in series:
        if serie.online:
            online_serie.append(serie.serie_guia_remision)
    #devuelve True si el serie es online
    for serie in online_serie:
        if doc_serie in serie:
            online = True
    return online