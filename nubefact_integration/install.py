# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import csv
import frappe
import os.path

def after_install():
    my_path = os.path.abspath(os.path.dirname(__file__))
    my_path = os.path.join(my_path, "imports/")

    path = os.path.join(my_path, "tipos_de_transaccion.csv")
    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=str(','))
        for idx, val in enumerate(reader):
            if idx == 0:
                continue  # If csv have first row with headers

            # Do something with your data
            doc = frappe.new_doc('Tipos de Transaccion Sunat')
            doc.codigo_tipo_transaccion = val[0]
            doc.nombre_tipo_transaccion = val[1].decode('utf-8')
            doc.insert()

    path = os.path.join(my_path, "tipos_notas_credito.csv")
    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=str(','))
        for idx, val in enumerate(reader):
            if idx == 0:
                continue  # If csv have first row with headers

            # Do something with your data
            doc = frappe.new_doc('Tipos de Notas de Credito')
            doc.codigo_notas_credito = val[0]
            doc.nombre_notas_credito = val[1].decode('utf-8')
            doc.insert()

    path = os.path.join(my_path, "tipos_notas_debito.csv")
    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=str(','))
        for idx, val in enumerate(reader):
            if idx == 0:
                continue  # If csv have first row with headers

            # Do something with your data
            doc = frappe.new_doc('Tipos de Notas de Debito')
            doc.codigo_notas_debito = val[0]
            doc.nombre_notas_debito = val[1].decode('utf-8')
            doc.insert()

    path = os.path.join(my_path, "motivo_traslado.csv")
    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=str(','))
        for idx, val in enumerate(reader):
            if idx == 0:
                continue  # If csv have first row with headers

            # Do something with your data
            doc = frappe.new_doc('Motivos de Traslado')
            doc.codigo_motivo_traslado = val[0]
            doc.nombre_motivo_traslado = val[1].decode('utf-8')
            doc.insert()

    path = os.path.join(my_path, "tipos_transporte.csv")
    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=str(','))
        for idx, val in enumerate(reader):
            if idx == 0:
                continue  # If csv have first row with headers

            # Do something with your data
            doc = frappe.new_doc('Tipos de Transporte')
            doc.codigo_tipo_transporte = val[0]
            doc.nombre_tipo_transporte = val[1].decode('utf-8')
            doc.insert()
