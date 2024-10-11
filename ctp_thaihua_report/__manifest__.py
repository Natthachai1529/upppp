# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybernetics Plus Co., Ltd.
#    Thaihua Autoparts Report
#
#    Copyright (C) 2021-TODAY Cybernetics Plus Technologies (<https://www.cybernetics.plus>).
#    Author: Cybernetics Plus Techno Solutions (<https://www.cybernetics.plus>)
#
###################################################################################

{
    "name": "Thaihua Autoparts Report",
    "version": "17.0.1.0.1",
    "summary": """ 
            Thaihua Autoparts Report
            .""",
    "description": """ 
            Thaihua Autoparts Report
            .""",
    "author": "Cybernetics+",
    "website": "https://www.cybernetics.plus",
    "live_test_url": "https://www.cybernetics.plus",
    "category": "Report",
    "license": "AGPL-3",
    "price": 999999.00,
    "currency": "USD",
    "application": False,
    "auto_install": False,
    "installable": True,
    "contributors": [
        "C+ Developer <dev@cybernetics.plus>",
    ],
    "depends" : [
        "base",
        "account",
        "l10n_th",
        "product",
        "sale",
        "purchase",
    ],
    "data": [
        "reports/billing_note.xml",
        "reports/credit_note.xml",
        "reports/report_purchaseorder_document.xml",
        "reports/report_saleorder_document.xml",
        "reports/tax_invoice_delivery.xml",
        "reports/tax_invoice_receipt.xml",
        "views/paperformat.xml",
    ],
}