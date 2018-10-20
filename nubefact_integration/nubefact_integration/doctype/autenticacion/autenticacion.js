// Copyright (c) 2018, OVENUBE and contributors
// For license information, please see license.txt
frappe.provide("nubefact_integration.autenticacion")

frappe.ui.form.on('Autenticacion', {
	refresh: function(frm) {
		nubefact_integration.autenticacion.check_mandatory_to_set_button(frm);
	}
});

frappe.ui.form.on('Autenticacion', 'ruta_nubefact', function(frm) {
	nubefact_integration.autenticacion.check_mandatory_to_set_button(frm);


});

frappe.ui.form.on('Autenticacion', 'token_nubefact', function(frm) {
	nubefact_integration.autenticacion.check_mandatory_to_set_button(frm);


});

nubefact_integration.autenticacion.check_mandatory_to_set_button = function(frm) {
	if (frm.doc.ruta_nubefact && frm.doc.token_nubefact){
		frm.fields_dict.test_connection.$input.addClass("btn-primary");
	}
	else{
		frm.fields_dict.test_connection.$input.removeClass("btn-primary");
	}
};

nubefact_integration.autenticacion.check_mandatory_to_fetch = function(doc) {
	$.each(['ruta_nubefact'], function (i, field) {
		if(!doc[frappe.model.scrub(field)]) frappe.throw(__("Please select {0} first", [field]));
    });
	$.each(['token_nubefact'], function (i, field) {
		if(!doc[frappe.model.scrub(field)]) frappe.throw(__("Please select {0} first", [field]));
    });
}

frappe.ui.form.on('Autenticacion', 'test_connection', function(frm) {
	nubefact_integration.autenticacion.check_mandatory_to_fetch(frm.doc);
	frappe.call({
		method: "nubefact_integration.nubefact_integration.doctype.autenticacion.autenticacion.test_connection",
		args: {
			'url': frm.doc.ruta_nubefact,
			'token': frm.doc.token_nubefact
		},
		callback: function (data) {
			if (data.message.codigo == 10){
				frappe.throw(data.message.errors);
			}
			else{
				msgprint(__("Successful Connection"),__("Success"));
			}
        }
	})
});