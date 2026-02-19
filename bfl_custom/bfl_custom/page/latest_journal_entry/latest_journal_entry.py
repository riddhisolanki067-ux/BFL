import frappe
from frappe import _

@frappe.whitelist()
def get_latest_journal_entries(account=None, from_date=None):

    conditions = ""
    filters = {}

    if account:
        conditions += " AND jea.account = %(account)s "
        filters["account"] = account

    if from_date:
        conditions += " AND je.posting_date >= %(from_date)s "
        filters["from_date"] = from_date

    data = frappe.db.sql(f"""

        SELECT
            je.name AS voucher,
            je.posting_date,
            je.creation,

            cash_line.account AS cash_account,

            GROUP_CONCAT(
                CONCAT(
                    other_line.account,
                    IF(other_line.party IS NOT NULL,
                        CONCAT(' (', other_line.party, ')'),
                        ''
                    ),
                    ' D:', other_line.debit_in_account_currency,
                    ' C:', other_line.credit_in_account_currency
                ) SEPARATOR '; '
            ) AS counter_details,

            je.remark,

            CASE je.docstatus
                WHEN 0 THEN 'Draft'
                WHEN 1 THEN 'Submitted'
                WHEN 2 THEN 'Cancelled'
            END AS status,

            je.custom_payment_type,

            cash_line.debit_in_account_currency AS debit,
            cash_line.credit_in_account_currency AS credit

        FROM `tabJournal Entry` je

        JOIN `tabJournal Entry Account` cash_line
            ON je.name = cash_line.parent

        LEFT JOIN `tabJournal Entry Account` other_line
            ON je.name = other_line.parent
            AND other_line.name != cash_line.name

        WHERE je.docstatus < 2
        {conditions}

        GROUP BY
            je.name,
            cash_line.name

        ORDER BY je.creation DESC
        LIMIT 10

    """, filters, as_dict=True)

    return data
