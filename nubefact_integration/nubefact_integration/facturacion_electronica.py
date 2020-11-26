# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import frappe
from nubefact_integration.nubefact_integration.doctype.autenticacion_nubefact.autenticacion_nubefact import get_autentication, get_url
from nubefact_integration.nubefact_integration.doctype.configuracion_nubefact.configuracion_nubefact import get_cuentas_bancarias, get_doc_serie
from nubefact_integration.nubefact_integration.utils import *
from nubefact_integration.nubefact_integration.doctype.tipos_de_transaccion_sunat.tipos_de_transaccion_sunat import get_tipo_transaccion, get_tipo_transaccion_fee
from erpnext.controllers.taxes_and_totals import get_plastic_bags_information
from frappe import utils

import requests
import json
import datetime

@frappe.whitelist()
def send_document(company, invoice, doctype):
    if doctype == "Fees":
        serie_nota_credito = frappe.get_value("Fees", invoice, "serie_nota_credito")
        if serie_nota_credito:
            numero_nota_credito = generate_fee_numero_comprobante(serie_nota_credito)
            tipo, serie, correlativo = get_serie_correlativo(numero_nota_credito)
            numero_comprobante = frappe.get_value("Fees", invoice, "numero_comprobante")
        else:
            serie_comprobante = frappe.get_value("Fees", invoice, "serie_comprobante")
            numero_comprobante = generate_fee_numero_comprobante(serie_comprobante)
            tipo, serie, correlativo = get_serie_correlativo(numero_comprobante)            
    else:
        tipo, serie, correlativo = get_serie_correlativo(invoice)
    online = get_serie_online(company, tipo + "-" + serie)
    if online:
        url = get_url(company)
        headers = get_autentication(company)
        if url != "" and headers != "":
            return_type = return_serie = return_correlativo = codigo_nota_credito = codigo_nota_debito = party_name = ""
            address = {}
            try:
                if doctype == 'Fees':
                    doc = frappe.get_doc("Fees", invoice)
                    student_email = frappe.get_value("Student", doc.student, "student_email_id")
                    if doc.is_return == 1:
                        tipo, return_serie, return_correlativo = get_serie_correlativo(numero_comprobante)
                        codigo_nota_credito = doc.codigo_nota_credito
                        return_type = "1" if doc.codigo_tipo_documento == "6" else "2"
                    if doc.factura_de_venta == 1:
                        address = get_address_information(doc.direccion)
                        customer = frappe.get_doc("Customer", doc.razon_social)
                    electronic_invoice = get_electronic_invoice(company, str(tipo_de_comprobante(doc.codigo_comprobante)), numero_comprobante)
                    if electronic_invoice.get('codigo_hash'):
                        return electronic_invoice
                    else:
                        content = {
                            "operacion": "generar_comprobante",
                            "tipo_de_comprobante": str(tipo_de_comprobante(doc.codigo_comprobante)),
                            "serie": serie,
                            "numero": correlativo,
                            "sunat_transaction": doc.codigo_transaccion_sunat,
                            "cliente_tipo_de_documento": doc.codigo_tipo_documento,
                            "cliente_numero_de_documento": doc.tax_id.strip(),
                            "cliente_denominacion": customer.customer_name if doc.factura_de_venta else doc.student_name,
                            "cliente_direccion": address.address if address.get('address') else "",
                            "cliente_email": student_email if student_email else "",
                            "cliente_email_1": "",
                            "cliente_email_2": "",
                            "fecha_de_emision": datetime.datetime.now().strftime("%d-%m-%Y"),
                            "fecha_de_vencimiento": datetime.datetime.now().strftime("%d-%m-%Y"),
                            "moneda": str(get_moneda(doc.currency)),
                            "tipo_de_cambio": "",
                            "porcentaje_de_igv": str(18.00),
                            "descuento_global": "",
                            "total_descuento": "",
                            "total_anticipo": "",
                            "total_gravada": "",
                            "total_inafecta": str(round(doc.grand_total, 2)),
                            "total_exonerada": "",
                            "total_igv": "",
                            "total_gratuita": "",
                            "total_otros_cargos": "",
                            "total": str(round(doc.grand_total, 2)),
                            "percepcion_tipo": "",
                            "percepcion_base_imponible": "",
                            "total_percepcion": "",
                            "total_incluido_percepcion": "",
                            "detraccion": "false",
                            "observaciones": "",
                            "documento_que_se_modifica_tipo": return_type,
                            "documento_que_se_modifica_serie": return_serie,
                            "documento_que_se_modifica_numero": return_correlativo,
                            "tipo_de_nota_de_credito": str(codigo_nota_credito),
                            "tipo_de_nota_de_debito": str(codigo_nota_debito),
                            "enviar_automaticamente_a_la_sunat": "true",
                            "enviar_automaticamente_al_cliente": "false",
                            "codigo_unico": "",
                            "condiciones_de_pago": "",
                            "medio_de_pago": "",
                            "placa_vehiculo": "",
                            "orden_compra_servicio": "",
                            "tabla_personalizada_codigo": "",
                            "formato_de_pdf": ""
                        }
                        content['items'] = []
                        for item in doc.components:
                            content['items'].append({
                                "unidad_de_medida": "ZZ",
                                "codigo": item.fees_category,
                                "descripcion": item.description if item.description else item.fees_category,
                                "cantidad": "1",
                                "valor_unitario": str(round(item.amount, 2)),
                                "precio_unitario": str(round(item.amount, 2)),
                                "descuento": "",
                                "subtotal": str(round(item.amount, 2)),
                                "tipo_de_igv": "9",
                                "igv": "0",
                                "total": str(round(item.amount, 2)),
                                "anticipo_regularizacion": "false",
                                "anticipo_documento_serie": "",
                                "anticipo_documento_numero": ""
                            })
                elif doctype == "Sales Invoice":
                    multi  = 1
                    monto_anticipo_neto = igv_anticipo = anticipo_amount = anticipo_total = 0
                    producto_bolsas_plasticas = []
                    doc = frappe.get_doc("Sales Invoice", invoice)
                    party_name = doc.customer_name
                    if doc.total_taxes_and_charges:
                        igv, monto_impuesto, igv_inc = get_igv(company, invoice, doctype)
                        ibp, monto_ibp, ibp_inc = get_impuesto_bolsas_plasticas(company, invoice, doctype)
                        if get_plastic_bags_information(doctype):
                            producto_bolsas_plasticas = get_plastic_bags_information(doctype)["plastic_bags_items"]
                            impuesto_bolsas_plasticas = get_plastic_bags_information(doctype)["plastic_bags_tax"]
                    else:
                        igv = monto_impuesto = igv_inc = 0
                        ibp = monto_ibp = ibp_inc = 0
                    cuenta_bancaria = "/ CUENTA BANCARIA Nº " + get_cuentas_bancarias(company, doc.currency) if get_cuentas_bancarias(company, doc.currency) != "" else ""
                    instrucciones = "Instrucciones: " + doc.instrucciones if doc.instrucciones else ""
                    nota_de_entrega = " / NOTA DE ENTREGA Nº " + doc.nota_entrega_origen if doc.nota_entrega_origen else ""
                    if doc.customer_address:
                        address = get_address_information(doc.customer_address)
                    if doc.codigo_transaccion_sunat == "4":
                        if doc.sales_invoice_advance:
                            advance = frappe.get_doc("Sales Invoice", doc.sales_invoice_advance)
                            monto_anticipo_neto = round(advance.net_total, 2)
                            anticipo_total = round(advance.grand_total)
                            igv_anticipo, anticipo_amount, anticipo_inc = get_igv(company, advance.name, doctype)
                    if doc.is_return == 1:
                        tipo, return_serie, return_correlativo = get_serie_correlativo(doc.return_against)
                        codigo_nota_credito = doc.codigo_nota_credito
                        return_type = "1" if doc.codigo_tipo_documento == "6" else "2"
                        multi = -1
                    elif doc.es_nota_debito == 1:
                        return_type = "1" if doc.codigo_tipo_documento == "6" else "2"
                        codigo_nota_debito = doc.codigo_nota_debito
                        tipo, return_serie, return_correlativo = get_serie_correlativo(doc.nota_de_debito_contra_factura_de_venta)
                    content = {
                            "operacion": "generar_comprobante",
                            "tipo_de_comprobante": str(tipo_de_comprobante(doc.codigo_comprobante)),
                            "serie": serie,
                            "numero": correlativo,
                            "sunat_transaction": doc.codigo_transaccion_sunat,
                            "cliente_tipo_de_documento": doc.codigo_tipo_documento,
                            "cliente_numero_de_documento": doc.tax_id.strip() if doc.tax_id else "",
                            "cliente_denominacion": party_name,
                            "cliente_direccion": address.address if address.get('address') else "",
                            "cliente_email": address.email if address.get('email') else "",
                            "cliente_email_1": "",
                            "cliente_email_2": "",
                            "fecha_de_emision": doc.get_formatted("posting_date"),
                            "fecha_de_vencimiento": doc.get_formatted("due_date"),
                            "moneda": str(get_moneda(doc.currency)),
                            "tipo_de_cambio": str(doc.conversion_rate),
                            "porcentaje_de_igv": str((igv - igv_anticipo)) if doc.total_taxes_and_charges else str(18.00),
                            "descuento_global": "",
                            "total_descuento": "",
                            "total_anticipo": monto_anticipo_neto if not monto_anticipo_neto==0 else "",
                            "total_gravada": str(round(doc.net_total - monto_anticipo_neto, 2) * multi) if doc.total_taxes_and_charges else "",
                            "total_inafecta": str(round(doc.grand_total - anticipo_total, 2) * multi) if not doc.total_taxes_and_charges else "",
                            "total_exonerada": "",
                            "total_igv": str(round(monto_impuesto - anticipo_amount, 2) * multi) if doc.total_taxes_and_charges else "",
                            "total_gratuita": str(doc.total_amount_free),
                            "total_otros_cargos": "",
                            "total": str(round(doc.grand_total - anticipo_total, 2) * multi),
                            "percepcion_tipo": "",
                            "percepcion_base_imponible": "",
                            "total_percepcion": "",
                            "total_incluido_percepcion": "",
                            "detraccion": "false",
                            "observaciones": (instrucciones + nota_de_entrega + cuenta_bancaria) if doc.doctype == "Sales Invoice" else "",
                            "documento_que_se_modifica_tipo": return_type,
                            "documento_que_se_modifica_serie": return_serie,
                            "documento_que_se_modifica_numero": return_correlativo,
                            "tipo_de_nota_de_credito": str(codigo_nota_credito),
                            "tipo_de_nota_de_debito": str(codigo_nota_debito),
                            "enviar_automaticamente_a_la_sunat": "true",
                            "enviar_automaticamente_al_cliente": "false",
                            "codigo_unico": "",
                            "condiciones_de_pago": doc.payment_terms_template,
                            "medio_de_pago": "",
                            "placa_vehiculo": "",
                            "orden_compra_servicio": doc.po_no if doc.doctype == "Sales Invoice" else "",
                            "tabla_personalizada_codigo": "",
                            "formato_de_pdf": "",
                            "total_impuestos_bolsas": str(round(monto_ibp, 2) * multi) if monto_ibp != 0 else ""
                    }
                    content['items'] = []
                    if doc.codigo_transaccion_sunat == "4":
                        if doc.sales_invoice_advance:
                            advance_tipo, advance_serie, advance_correlativo = get_serie_correlativo(doc.sales_invoice_advance)
                            content['items'].append({
                                "unidad_de_medida": "NIU",
                                "codigo": "001",
                                "descripcion": "REGULARIZACIÓN DEL ANTICIPO",
                                "cantidad": "1",
                                "valor_unitario": str(monto_anticipo_neto),
                                "precio_unitario": str(anticipo_total),
                                "descuento": "",
                                "subtotal": str(monto_anticipo_neto),
                                "tipo_de_igv": "1",
                                "igv": str(round(anticipo_amount, 2)),
                                "total": str(anticipo_total),
                                "anticipo_regularizacion": "true",
                                "anticipo_documento_serie": str(advance_serie),
                                "anticipo_documento_numero": str(advance_correlativo)
                            })
                        else:
                            content['items'].append(
                                {
                                    "unidad_de_medida": "NIU",
                                    "codigo": "001",
                                    "descripcion": "PRIMER ANTICIPO",
                                    "cantidad": "1",
                                    "valor_unitario": str(round(doc.net_total, 2)),
                                    "precio_unitario": str(round(doc.grand_total, 2)),
                                    "descuento": "",
                                    "subtotal": str(round(doc.net_total, 2)),
                                    "tipo_de_igv": "1",
                                    "igv": str(round(monto_impuesto, 2)),
                                    "total": str(round(doc.grand_total, 2)),
                                    "anticipo_regularizacion": "false",
                                    "anticipo_documento_serie": "",
                                    "anticipo_documento_numero": ""
                                })
                    else:
                        for item in doc.items:
                            tipo_producto = get_tipo_producto(item.item_code)
                            if item.unit_value > 0:
                                tipo_igv = "6"
                                precio_unitario = round(item.unit_value, 4)
                                total = round(item.free_amount, 2) * multi
                            elif doc.total_taxes_and_charges:
                                tipo_igv = "1"
                                if igv_inc == 1:
                                    precio_unitario = round(item.rate, 4)
                                    total = round(item.amount, 2) * multi
                                elif igv > 0:
                                    precio_unitario = round(item.net_rate, 4) * 1.18
                                    total = round(item.net_amount, 2) * 1.18 * multi
                            elif doc.codigo_transaccion_sunat == "2":
                                tipo_igv = "16"
                                precio_unitario = round(item.unit_value, 4)
                                total = round(item.amount, 2) * multi
                            else:
                                tipo_igv = "9"
                                precio_unitario = round(item.rate, 4)
                                total = round(item.amount, 2) * multi
                            content['items'].append({
                                "unidad_de_medida": tipo_producto,
                                "codigo": item.item_code,
                                "descripcion": item.item_name,
                                "cantidad": str(item.qty * multi),
                                "valor_unitario": str(round(item.unit_value, 4)) if (item.unit_value > 0) else str(round(item.net_rate, 4)),
                                "precio_unitario": str(precio_unitario),
                                "descuento": str(round(item.discount_amount, 2)) if (item.discount_amount > 0) else "",
                                "subtotal": str(round(item.free_amount, 2) * multi) if (item.unit_value > 0) else str(round(item.net_amount, 2) * multi),
                                "tipo_de_igv": tipo_igv,
                                "igv": str(round(item.net_amount * igv / 100, 2) * multi) if doc.total_taxes_and_charges else "0",
                                "total": str(total),
                                "anticipo_regularizacion": "false",
                                "anticipo_documento_serie": "",
                                "anticipo_documento_numero": "",
                                "impuesto_bolsas": str(item.qty * impuesto_bolsas_plasticas.tax_amount * multi) if (item.item_code in producto_bolsas_plasticas) else ""
                        })
                elif doctype == "Delivery Note":
                    doc = frappe.get_doc("Delivery Note", invoice)
                    doc_transportista = get_doc_transportista(doc.transporter)
                    doc_conductor = get_doc_conductor(doc.driver)
                    company_address = customer_address = {}
                    instrucciones = "Instrucciones: " + doc.instructions if doc.instructions else ""
                    pedido_de_compra = " / Pedido de compra No. " + doc.po_no if doc.po_no else ""
                    mtc_no = "/ N° de Inscripcion del MTC. "+ doc.lr_no if doc.lr_no else "" 
                    if doc.customer_address:
                        address = get_address_information(doc.customer_address)
                    if doc.shipping_address_name:
                        customer_address = get_address_information(doc.shipping_address_name)
                    else:
                        customer_address = address
                    if doc.company_address:
                        company_address = get_address_information((doc.company_address))
                    content = {
                        "operacion": "generar_guia",
                        "tipo_de_comprobante": "7",
                        "serie": serie,
                        "numero": correlativo,
                        "cliente_tipo_de_documento": doc.codigo_tipo_documento,
                        "cliente_numero_de_documento": doc.tax_id.strip(),
                        "cliente_denominacion": doc.customer_name,
                        "cliente_direccion": address.getaddress if address.get('address') else "",
                        "cliente_email": address.email if address.get('email') else "",
                        "cliente_email_1": "",
                        "cliente_email_2": "",
                        "fecha_de_emision": doc.get_formatted("posting_date"),
                        "observaciones": instrucciones + pedido_de_compra + mtc_no,
                        "motivo_de_traslado": doc.codigo_motivo_traslado,
                        "peso_bruto_total": doc.total_net_weight,
                        "numero_de_bultos": doc.numero_bultos if doc.numero_bultos else "0",
                        "tipo_de_transporte": doc.codigo_motivo_traslado,
                        "fecha_de_inicio_de_traslado": doc.get_formatted("lr_date"),
                        "transportista_documento_tipo": doc_transportista.codigo_tipo_documento,
                        "transportista_documento_numero": doc_transportista.tax_id,
                        "transportista_denominacion": doc_transportista.supplier_name,
                        "transportista_placa_numero": doc.vehicle_no,
                        "conductor_documento_tipo": doc_conductor.codigo_documento_identidad,
                        "conductor_documento_numero": doc_conductor.tax_id,
                        "conductor_denominacion": doc_conductor.full_name,
                        "punto_de_partida_ubigeo": company_address.ubigeo,
                        "punto_de_partida_direccion": company_address.address,
                        "punto_de_llegada_ubigeo": customer_address.ubigeo,
                        "punto_de_llegada_direccion": customer_address.address,
                        "enviar_automaticamente_a_la_sunat": "true",
                        "enviar_automaticamente_al_cliente": "false",
                        "codigo_unico": "",
                        "formato_de_pdf": "",
                    }
                    content['items'] = []
                    for item in doc.items:
                        tipo_producto = get_tipo_producto(item.item_code)
                        content['items'].append({
                            "unidad_de_medida": tipo_producto,
                            "codigo": item.item_code,
                            "descripcion": item.item_name,
                            "cantidad": str(item.qty)
                    })
                response = requests.post(url, headers=headers, data=json.dumps(content))
                data = json.loads(response.content)
                if doctype == "Fees":
                    data["numero_comprobante"] = numero_comprobante
                    if serie_nota_credito:
                        data["numero_nota_credito"] = numero_nota_credito
                request = frappe.get_doc({
                    "doctype": "Electronic Invoice Request",
                    "document_type": doc.doctype,
                    "document_name": doc.name,
                    "date": doc.get("posting_date"),
                    "request": json.dumps(content),
                    "response": response.content
                })
                request.save(ignore_permissions=True)
            except Exception as e:
                print(e)
                return e
            else:
                return data
        else:
            return ""
    else:
        return ""

def get_electronic_invoice(company, tipo_de_comprobante, numero_comprobante):
    tipo, serie, correlativo = numero_comprobante.split('-')
    url = get_url(company)
    headers = get_autentication(company)
    if url != "" and headers != "":
        content = {
            "operacion": "consultar_comprobante",
            "tipo_de_comprobante": tipo_de_comprobante,
            "serie": serie,
            "numero": correlativo
        }
    response = requests.post(url, headers=headers, data=json.dumps(content))
    data = json.loads(response.content)
    data['numero_comprobante'] = numero_comprobante
    return data

@frappe.whitelist()
def consult_document(company, invoice, doctype):
    if doctype == "Fees":
        serie_nota_credito = frappe.get_value("Fees", invoice, "serie_nota_credito")
        if serie_nota_credito:
            numero_nota_credito = generate_fee_numero_comprobante(serie_nota_credito)
            tipo, serie, correlativo = get_serie_correlativo(numero_nota_credito)
            numero_comprobante = frappe.get_value("Fees", invoice, "numero_comprobante")
        else:
            serie_comprobante = frappe.get_value("Fees", invoice, "serie_comprobante")
            numero_comprobante = generate_fee_numero_comprobante(serie_comprobante)
            tipo, serie, correlativo = get_serie_correlativo(numero_comprobante)            
    else:
        tipo, serie, correlativo = get_serie_correlativo(invoice)
    online = get_serie_online(company, tipo + "-" + serie)
    if online:
        url = get_url(company)
        headers = get_autentication(company)
        if url != "" and headers != "":
            if doctype == "Sales Invoice":
                doc = frappe.get_doc("Sales Invoice", invoice)
            elif doctype == 'Fees':
                doc = frappe.get_doc("Fees", invoice)
            elif doctype == "Delivery Note":
                doc = frappe.get_doc("Delivery Note", invoice)
            content = {
                "operacion": "consultar_comprobante",
                "tipo_de_comprobante": str(tipo_de_comprobante(doc.codigo_tipo_comprobante if doctype == "Delivery Note" else doc.codigo_comprobante)),
                "serie": serie,
                "numero": correlativo
            }
            response = requests.post(url, headers=headers, data=json.dumps(content))
            return json.loads(response.content)
        else:
            return ""
    else:
        return ""

@frappe.whitelist()
def cancel_document(company, invoice, doctype, motivo):
    if doctype == "Fees":
        serie_nota_credito = frappe.get_value("Fees", invoice, "serie_nota_credito")
        if serie_nota_credito:
            numero_nota_credito = generate_fee_numero_comprobante(serie_nota_credito)
            tipo, serie, correlativo = get_serie_correlativo(numero_nota_credito)
            numero_comprobante = frappe.get_value("Fees", invoice, "numero_comprobante")
        else:
            serie_comprobante = frappe.get_value("Fees", invoice, "serie_comprobante")
            numero_comprobante = generate_fee_numero_comprobante(serie_comprobante)
            tipo, serie, correlativo = get_serie_correlativo(numero_comprobante)            
    else:
        tipo, serie, correlativo = get_serie_correlativo(invoice)
    online = get_serie_online(company, tipo + "-" + serie)
    if online:
        url = get_url(company)
        headers = get_autentication(company)
        if url != "" and headers != "":
            data = consult_document(company, invoice, doctype)
            if data.get("aceptada_por_sunat"):
                content = {
                    "operacion": "generar_anulacion",
                    "tipo_de_comprobante": data["tipo_de_comprobante"],
                    "serie": data["serie"],
                    "numero": data["numero"],
                    "motivo": motivo,
                    "codigo_unico": ""
                }
                response = requests.post(url, headers=headers, data=json.dumps(content))
                if doctype == "Sales Invoice":
                    frappe.db.sql(
                        """UPDATE `tabSales Invoice` SET estado_anulacion='En proceso', hora_cancelacion='{0}' WHERE name='{1}' and company='{2}'""".format(
                            datetime.datetime.now(), invoice, company))
                    frappe.db.commit()
                elif doctype == 'Fees':
                    frappe.db.sql(
                        """UPDATE `tabFees` SET estado_anulacion='En proceso', hora_cancelacion='{0}' WHERE name='{1}' and company='{2}'""".format(
                            datetime.datetime.now(), invoice, company))
                    frappe.db.commit()
                elif doctype == 'Delivery Note':
                    frappe.db.sql(
                        """UPDATE `tabDelivery Note` SET estado_anulacion='En proceso', hora_cancelacion='{0}' WHERE name='{1}' and company='{2}'""".format(
                            datetime.datetime.now(), invoice, company))
                    frappe.db.commit()
                return json.loads(response.content)
        else:
            return ""
    else:
        return ""

@frappe.whitelist()
def consult_cancel_document(company, invoice, doctype):
    if doctype == "Fees":
        serie_nota_credito = frappe.get_value("Fees", invoice, "serie_nota_credito")
        if serie_nota_credito:
            numero_nota_credito = generate_fee_numero_comprobante(serie_nota_credito)
            tipo, serie, correlativo = get_serie_correlativo(numero_nota_credito)
            numero_comprobante = frappe.get_value("Fees", invoice, "numero_comprobante")
        else:
            serie_comprobante = frappe.get_value("Fees", invoice, "serie_comprobante")
            numero_comprobante = generate_fee_numero_comprobante(serie_comprobante)
            tipo, serie, correlativo = get_serie_correlativo(numero_comprobante)            
    else:
        tipo, serie, correlativo = get_serie_correlativo(invoice)
    online = get_serie_online(company, tipo + "-" + serie)
    if online:
        url = get_url(company)
        headers = get_autentication(company)
        if url != "" and headers != "":
            data = consult_document(company, invoice, doctype)
            if data.get("aceptada_por_sunat"):
                content = {
                    "operacion": "consultar_anulacion",
                    "tipo_de_comprobante": data["tipo_de_comprobante"],
                    "serie": data["serie"],
                    "numero": data["numero"]
                }
                response = requests.post(url, headers=headers, data=json.dumps(content))
                return json.loads(response.content)
        else:
            return ""
    else:
        return ""

def set_electronic_invoice_fields(doc, method=None):
    if doc.customer and doc.is_autogenerated == 1:
        culqi_settings = frappe.get_doc("Culqi Settings", doc.company)
        enable_electronic_invoice = culqi_settings.get('enable_electronic_invoice')
        doc_serie = get_doc_serie(company=doc.company, doctype=doc.doctype, is_return=doc.is_return, 
            es_nota_debito=doc.es_nota_debito, contingencia=doc.contingencia, codigo_tipo_documento=doc.codigo_tipo_documento,
            online = enable_electronic_invoice)
        tipo_transaccion = get_tipo_transaccion(customer=doc.customer)
        doc.tipo_documento_identidad = frappe.get_value("Customer", doc.customer, 'tipo_documento_identidad')
        doc.codigo_tipo_documento = frappe.get_value("Customer", doc.customer, 'codigo_tipo_documento')
        doc.tipo_comprobante = doc_serie.get('descripcion')
        doc.codigo_comprobante = doc_serie.get('codigo')
        doc.naming_series = doc_serie.get('series')[0]
        doc.tipo_transaccion_sunat = tipo_transaccion.get('descripcion')
        doc.codigo_transaccion_sunat = tipo_transaccion.get('codigo')

def send_electronic_invoice(doc, method=None):
    tipo, serie, correlativo = get_serie_correlativo(doc.name)
    online = get_serie_online(doc.company, tipo + "-" + serie)
    if doc.is_autogenerated == 1 and online:
        if not doc.customer_address and doc.codigo_tipo_documento != "-":
            frappe.throw("Customer Address is missing")
            frappe.validated = False
        if not doc.estado_sunat or doc.is_return == 1:
            document = consult_document(company=doc.company, invoice=doc.name, doctype=doc.doctype)
            if document.get('codigo') == 24:
                invoice = send_document(company=doc.company, invoice=doc.name, doctype=doc.doctype)
                if invoice.get('codigo_hash'):
                    doc.estado_sunat = "Aceptado" if invoice.get('codigo_hash') else "Rechazado"
                    doc.respuesta_sunat = invoice.get('sunat_description')
                    doc.codigo_qr_sunat = invoice.get('cadena_para_codigo_qr')
                    doc.codigo_barras_sunat = invoice.get('codigo_de_barras')
                    doc.codigo_hash_sunat = invoice.get('codigo_hash')
                    doc.enlace_pdf = invoice.get('enlace_del_pdf')
                else:
                    frappe.throw(invoice.get('errors'))
                    frappe.validated = False

def set_fees_fields(doc):
    culqi_settings = frappe.get_doc("Culqi Settings", doc.company)
    enable_electronic_invoice = culqi_settings.get('enable_electronic_invoice')
    if doc.student:
        student = frappe.get_doc("Student", doc.student)
        if student.factura_de_venta == 1:
            doc.factura_de_venta = 1
            doc.razon_social = student.razon_social
            doc.direccion = student.direccion
            tipo_transaccion = get_tipo_transaccion(customer=doc.razon_social)
        else:
            doc.codigo_tipo_documento = student.codigo_tipo_documento
            doc.tipo_documento_identidad = student.tipo_documento_identidad
            tipo_transaccion = get_tipo_transaccion_fee(student=doc.student)
        doc.codigo_tipo_documento = student.codigo_tipo_documento
        doc.tipo_documento_identidad = student.tipo_documento_identidad
        doc.tax_id = student.tax_id
        doc.tipo_transaccion_sunat = tipo_transaccion.get('descripcion')
        doc.codigo_transaccion_sunat = tipo_transaccion.get('codigo')
        doc_serie = get_doc_serie(company=doc.company, doctype=doc.doctype, is_return=doc.is_return, 
            contingencia=doc.contingencia, codigo_tipo_documento=doc.codigo_tipo_documento,
            online = enable_electronic_invoice)
        doc.tipo_comprobante = doc_serie.get('descripcion')
        doc.codigo_comprobante = doc_serie.get('codigo')
        doc.serie_comprobante = doc_serie.get('series')[0]
        doc.save(ignore_permissions=True)

def send_fees_invoice(doc, method=None):
    if doc.get("fee"):
        fee = frappe.get_doc("Fees", doc.fee)
        set_fees_fields(fee)
        serie_comprobante = fee.serie_comprobante
        numero_comprobante = generate_fee_numero_comprobante(serie_comprobante)
        tipo, serie, correlativo = get_serie_correlativo(numero_comprobante)
        online = get_serie_online(fee.company, tipo + "-" + serie)
        if online:
            invoice = send_document(company=fee.company, invoice=fee.name, doctype=fee.doctype)
            if invoice:
                if invoice.get('codigo_hash'):
                    fee.estado_sunat = "Aceptado" if invoice.get('codigo_hash') else "Rechazado"
                    fee.respuesta_sunat = invoice.get("sunat_description")
                    fee.codigo_qr_sunat = invoice.get("cadena_para_codigo_qr")
                    fee.enlace_pdf = invoice.get("enlace_del_pdf")
                    fee.codigo_hash_sunat = invoice.get("codigo_hash")
                    fee.numero_comprobante = numero_comprobante
                    fee.fecha_comprobante = frappe.utils.today()
                    fee.add_course()
                else:
                    revert_fee_numero_comprobante(serie_comprobante=serie_comprobante, numero_comprobante=numero_comprobante)
                    fee.numero_comprobante = ""
                    fee.fecha_comprobante = ""
                    frappe.validated = False
                fee.save(ignore_permissions=True)
            else:
                revert_fee_numero_comprobante(serie_comprobante=serie_comprobante, numero_comprobante=numero_comprobante)
                frappe.validated = False
