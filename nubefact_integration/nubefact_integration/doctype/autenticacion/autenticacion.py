# -*- coding: utf-8 -*-
# Copyright (c) 2018, OVENUBE and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests
import json

class Autenticacion(Document):
	pass

@frappe.whitelist()
def test_connection(url, token):
	headers = {
			"Authorization": token,
			"Content-Type":  "application/json"
	}
	response = requests.post(url, headers=headers)
	return json.loads(response.content)

def get_autentication():
	token = frappe.db.get_single_value("Autenticacion", "token_nubefact")
	headers = {
		"Authorization": token,
		"Content-Type": "application/json"
	}
	return headers

def get_url():
	url = frappe.db.get_single_value("Autenticacion", "ruta_nubefact")
	return url
