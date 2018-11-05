# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr
from nubefact_integration.nubefact_integration.doctype.autenticacion.autenticacion import get_autentication, get_url
from utils import tipo_de_comprobante, get_serie_correlativo, get_moneda, get_igv, get_tipo_producto, get_serie_online
import requests
import json

@frappe.whitelist()
def send_document(invoice, doctype):
    tipo, serie, correlativo = get_serie_correlativo(invoice)
    online = get_serie_online(tipo + "-" + serie)
    if online:
        url = get_url()
        headers = get_autentication()
        if doctype == "Sales Invoice":
            return_type = ""
            return_serie = ""
            return_correlativo = ""
            codigo_nota_credito = ""
            mult = 1
            doc = frappe.get_doc("Sales Invoice", invoice)
            igv, monto_impuesto = get_igv(invoice, doctype)
            if doc.is_return == 1:
                return_type, return_serie, return_correlativo = get_serie_correlativo(doc.return_against)
                codigo_nota_credito = doc.codigo_nota_credito
                mult = -1
            return_type = "1" if doc.codigo_tipo_documento == "6" else "2"
            content = {
                    "operacion": "generar_comprobante",
                    "tipo_de_comprobante": str(tipo_de_comprobante(doc.codigo_comprobante)),
                    "serie": serie,
                    "numero": correlativo,
                    "sunat_transaction": doc.codigo_transaccion_sunat,
                    "cliente_tipo_de_documento": doc.codigo_tipo_documento,
                    "cliente_numero_de_documento": doc.tax_id,
                    "cliente_denominacion": doc.customer_name,
                    "cliente_direccion": doc.address_display if doc.address_display else "",
                    "cliente_email": doc.contact_email if doc.contact_email else "",
                    "cliente_email_1": "",
                    "cliente_email_2": "",
                    "fecha_de_emision": doc.get_formatted("posting_date"),
                    "fecha_de_vencimiento": doc.get_formatted("due_date"),
                    "moneda": str(get_moneda(doc.currency)),
                    "tipo_de_cambio": str(doc.conversion_rate),
                    "porcentaje_de_igv": str(igv * mult),
                    "descuento_global": "",
                    "total_descuento": "",
                    "total_anticipo": "",
                    "total_gravada": str(round(doc.net_total, 2) * mult),
                    "total_inafecta": "",
                    "total_exonerada": "",
                    "total_igv": str(round(monto_impuesto, 2) * mult),
                    "total_gratuita": "",
                    "total_otros_cargos": "",
                    "total": str(round(doc.grand_total, 2) * mult),
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
                    "tipo_de_nota_de_debito": "",
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
            for item in doc.items:
                tipo_producto = get_tipo_producto(item.item_name)
                content['items'].append({
                    "unidad_de_medida": tipo_producto,
                    "codigo": item.item_code,
                    "descripcion": item.item_name,
                    "cantidad": str(item.qty * mult),
                    "valor_unitario": str(round(item.net_rate, 2)),
                    "precio_unitario": str(round(item.rate, 2)),
                    "descuento": str(round(item.discount_amount, 2)),
                    "subtotal": str(round(item.base_net_amount, 2) * mult),
                    "tipo_de_igv": "1",
                    "igv": str(round(item.amount - item.net_amount, 2) * mult),
                    "total": str(round(item.amount, 2) * mult),
                    "anticipo_regularizacion": "false",
                    "anticipo_documento_serie": "",
                    "anticipo_documento_numero": ""
                })
            print content
        response = requests.post(url, headers=headers, data=json.dumps(content))
        return json.loads(response.content)
    else:
        return ""