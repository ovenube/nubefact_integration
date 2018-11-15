from __future__ import unicode_literals
import frappe
import datetime
from nubefact_integration.facturacion_electronica import consult_cancel_document

def daily():
    canceled_sales = frappe.get_all("Sales Invoice", filters={'estado_anulacion': 'En proceso'},
                                    fields=['name', 'hora_cancelacion'])
    canceled_purchases = frappe.get_all("Purchase Invoice", filters={'estado_anulacion': 'En proceso'},
                                        fields=['name', 'hora_cancelacion'])
    for sales in canceled_sales:
        inv = frappe.get_doc("Sales Invoice", sales['name'])
        wait_time = 0.25 * 3600 if inv.codigo_comprobante == "1" or inv.codigo_comprobante == "7" else 24 * 3600
        if (datetime.datetime.now() - sales['hora_cancelacion']).total_seconds() > wait_time:
            status = consult_cancel_document(inv.name, "Sales Invoice")
            if status["aceptada_por_sunat"]:
                frappe.db.sql(
                    """UPDATE `tabSales Invoice` SET estado_anulacion='Cancelado' WHERE name='{0}'""".format(inv.name))
                frappe.db.commit()
                inv.cancel()
            else:
                frappe.db.sql(
                    """UPDATE `tabSales Invoice` SET estado_anulacion='Rechazado' WHERE name='{0}'""".format(inv.name))
                frappe.db.commit()
    for purchases in canceled_purchases:
        inv = frappe.get_doc("Purchase Invoice", purchases['name'])
        if (datetime.datetime.now() - purchases['hora_cancelacion']).total_seconds() > 0.25 * 3600:
            status = consult_cancel_document(inv.name, "Purchase Invoice")
            if status["aceptada_por_sunat"]:
                frappe.db.sql(
                    """UPDATE `tabPurchases Invoice` SET estado_anulacion='Cancelado' WHERE name='{0}'""".format(
                        inv.name))
                frappe.db.commit()
                inv.cancel()
            else:
                frappe.db.sql(
                    """UPDATE `tabPurchases Invoice` SET estado_anulacion='Rechazado' WHERE name='{0}'""".format(
                        inv.name))
                frappe.db.commit()
