// Copyright (c) 2019, OVENUBE and contributors
// For license information, please see license.txt

frappe.provide("nubefact_integration.autenticacion_nubefact");

frappe.ui.form.on('Autenticacion Nubefact', {
	onload_post_render: function(frm) {
		nubefact_integration.autenticacion_nubefact.check_mandatory_to_set_button(frm);	
	},

	ruta_nubefact: function(frm) {
		nubefact_integration.autenticacion_nubefact.check_mandatory_to_set_button(frm);	
	},

	token_nubefact: function(frm) {
		nubefact_integration.autenticacion_nubefact.check_mandatory_to_set_button(frm);	
	}
});

nubefact_integration.autenticacion_nubefact.check_mandatory_to_set_button = function(frm) {
	if (frm.doc.ruta_nubefact != "" && frm.doc.token_nubefact != ""){
		frm.fields_dict.test_connection.$input.addClass("btn-primary");
	}
	else{
		frm.fields_dict.test_connection.$input.removeClass("btn-primary");
	}
};

nubefact_integration.autenticacion_nubefact.check_mandatory_to_fetch = function(doc) {
	$.each(["ruta_nubefact"], function(i, field) {
		if(!doc[frappe.model.scrub(field)]) frappe.throw(__("Please select {0} first", [field]));
	});
	$.each(["token_nubefact"], function(i, field) {
		if(!doc[frappe.model.scrub(field)]) frappe.throw(__("Please select {0} first", [field]));
	});
};

frappe.ui.form.on('Autenticacion Nubefact', 'test_connection', function(frm) {
	nubefact_integration.autenticacion_nubefact.check_mandatory_to_fetch(frm.doc);
	frappe.call({
		method: "nubefact_integration.nubefact_integration.doctype.autenticacion_nubefact.autenticacion_nubefact.test_connection",
		args: {
			'url': frm.doc.ruta_nubefact,
			'token': frm.doc.token_nubefact
		},
		callback: function (data) {
			if (data.message.codigo === 10){
				frappe.throw(data.message.errors);
			}
			else{
				msgprint(__("Successful Connection"),__("Success"));
			}
        }
	});
});
