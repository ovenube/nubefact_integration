// Copyright (c) 2019, OVENUBE and contributors
// For license information, please see license.txt

frappe.ui.form.on('Configuracion Nubefact', {
	onload: function(frm) {
		frappe.call({
			method: "get_series",
			doc: frm.doc,
			callback: function(r) {
				frappe.meta.get_docfield("Detalle Serie Factura Electronica","serie_factura", frm.doc.name).options = r.message["venta"];
				frm.refresh_field("serie_factura");
				frappe.meta.get_docfield("Detalle Serie Factura Electronica Contingencia","serie_factura_contingencia", frm.doc.name).options = r.message["venta"];
				frm.refresh_field("serie_factura_contingencia");
				frappe.meta.get_docfield("Detalle Serie Boleta Electronica","serie_boleta", frm.doc.name).options = r.message["venta"];
				frm.refresh_field("serie_boleta");
				frappe.meta.get_docfield("Detalle Serie Boleta Electronica Contingencia","serie_boleta_contingencia", frm.doc.name).options = r.message["venta"];
				frm.refresh_field("serie_boleta_contingencia");
				frappe.meta.get_docfield("Detalle Serie Nota de Credito Electronica","serie_nota_credito", frm.doc.name).options = r.message["venta"];
				frm.refresh_field("serie_nota_credito");
				frappe.meta.get_docfield("Detalle Serie Nota de Credito Electronica Contingencia","serie_nota_credito_contingencia", frm.doc.name).options = r.message["venta"];
				frm.refresh_field("serie_nota_credito_contingencia");
				frappe.meta.get_docfield("Detalle Serie Nota de Debito Electronica","serie_nota_debito", frm.doc.name).options = r.message["compra"];
				frm.refresh_field("serie_nota_debito");
				frappe.meta.get_docfield("Detalle Serie Nota de Debito Electronica Contingencia","serie_nota_debito_contingencia", frm.doc.name).options = r.message["compra"];
				frm.refresh_field("serie_nota_debito_contingencia");
				frappe.meta.get_docfield("Detalle Serie Guia de Remision Electronica","serie_guia_remision", frm.doc.name).options = r.message["guia"];
				frm.refresh_field("serie_guia_remision");
			}
		});
	},

	setup: function(frm) {
		frm.set_query("igv_ventas", function() {
			return {
				filters: {
					"company": frm.doc.company
				}
			};
		});

		frm.set_query("igv_compras", function() {
			return {
				filters: {
					"company": frm.doc.company
				}
			};
		});

		frm.set_query("percepcion_ventas", function() {
			return {
				filters: {
					"company": frm.doc.company
				}
			};
		});

		frm.set_query("percepcion_compras", function() {
			return {
				filters: {
					"company": frm.doc.company
				}
			};
		});

		frm.set_query("anticipo", function() {
			return {
				filters: {
					"company": frm.doc.company
				}
			};
		});
	}
});
