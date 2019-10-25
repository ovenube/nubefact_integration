from __future__ import unicode_literals
import frappe
import datetime
from nubefact_integration.facturacion_electronica import consult_cancel_document

def daily():
    canceled_sales = frappe.get_all("Sales Invoice", filters={'estado_anulacion': 'En proceso'},
                                    fields=['name', 'hora_cancelacion'])
    canceled_purchases = frappe.get_all("Purchase Invoice", filters={'estado_anulacion': 'En proceso'},
                                        fields=['name', 'hora_cancelacion'])
    canceled_fees = frappe.get_all("Fees", filters={'estado_anulacion': 'En proceso'},
                                        fields=['name', 'hora_cancelacion'])
    canceled_delivery_notes = frappe.get_all("Delivery Note", filters={'estado_anulacion': 'En proceso'},
                                   fields=['name', 'hora_cancelacion'])
    for sales in canceled_sales:
        inv = frappe.get_doc("Sales Invoice", sales['name'])
        wait_time = 0.25 * 3600 if inv.codigo_comprobante == "1" or inv.codigo_comprobante == "7" else 24 * 3600
        if (datetime.datetime.now() - sales['hora_cancelacion']).total_seconds() > wait_time:
            status = consult_cancel_document(inv.company, inv.name, "Sales Invoice")
            if status["aceptada_por_sunat"]:
                frappe.db.sql(
                    """UPDATE `tabSales Invoice` SET estado_anulacion='Aceptado' WHERE name='{0}'""".format(inv.name))
                frappe.db.commit()
                inv.cancel()
            else:
                frappe.db.sql(
                    """UPDATE `tabSales Invoice` SET estado_anulacion='Rechazado' WHERE name='{0}'""".format(inv.name))
                frappe.db.commit()
    for purchases in canceled_purchases:
        inv = frappe.get_doc("Purchase Invoice", purchases['name'])
        if (datetime.datetime.now() - purchases['hora_cancelacion']).total_seconds() > 0.25 * 3600:
            status = consult_cancel_document(inv.company, inv.name, "Purchase Invoice")
            if status["aceptada_por_sunat"]:
                frappe.db.sql(
                    """UPDATE `tabPurchases Invoice` SET estado_anulacion='Aceptado' WHERE name='{0}'""".format(
                        inv.name))
                frappe.db.commit()
                inv.cancel()
            else:
                frappe.db.sql(
                    """UPDATE `tabPurchases Invoice` SET estado_anulacion='Rechazado' WHERE name='{0}'""".format(
                        inv.name))
                frappe.db.commit()
    for fees in canceled_fees:
        fee = frappe.get_doc("Fees", fees['name'])
        if (datetime.datetime.now() - fees['hora_cancelacion']).total_seconds() > 0.25 * 3600:
            status = consult_cancel_document(inv.company, fee.name, "Fees")
            if status["aceptada_por_sunat"]:
                frappe.db.sql(
                    """UPDATE `tabFees` SET estado_anulacion='Aceptado' WHERE name='{0}'""".format(
                        fee.name))
                frappe.db.commit()
                fee.cancel()
            else:
                frappe.db.sql(
                    """UPDATE `tabFees` SET estado_anulacion='Rechazado' WHERE name='{0}'""".format(
                        fee.name))
                frappe.db.commit()
    for delivery_notes in canceled_delivery_notes:
        delivery_note = frappe.get_doc("Delivery Note", delivery_notes['name'])
        if (datetime.datetime.now() - delivery_notes['hora_cancelacion']).total_seconds() > 0.25 * 3600:
            status = consult_cancel_document(inv.company, delivery_note.name, "Fees")
            if status["aceptada_por_sunat"]:
                frappe.db.sql(
                    """UPDATE `tabDelivery Note` SET estado_anulacion='Aceptado' WHERE name='{0}'""".format(
                        delivery_note.name))
                frappe.db.commit()
                delivery_note.cancel()
            else:
                frappe.db.sql(
                    """UPDATE `tabDelivery Note` SET estado_anulacion='Rechazado' WHERE name='{0}'""".format(
                        delivery_note.name))
                frappe.db.commit()