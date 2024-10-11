# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
{
    "name": "Thai Localization - Account Billing Note",
    "version": "17.0.1.0.3",
    "author": "Cybernetics +,Cybernetics plus Co.,Ltd.",
    "license": "AGPL-3",
    "website": "https://cybernetics.plus",
    "category": "Localization / Accounting",
    "depends": [
        "account",
        "account_payment_order",
    ],
    "data": [
        "data/billing_sequence.xml",
        "security/ir.model.access.csv",
        "views/account_billing_note_view.xml",
        'views/account_billing_report.xml',
        'views/report_billing_note.xml',
        'views/account_move_view.xml'
    ],
    "installable": True,
    "development_status": "Alpha",
    "maintainers": ["krittapak.arr"],
}
