import frappe

@frappe.whitelist()
def get_latest_journal_entries(account):

    # ⭐ Get latest 10 JE names first (by creation)
    latest_vouchers = frappe.db.sql("""
        SELECT je.name
        FROM `tabJournal Entry` je
        JOIN `tabJournal Entry Account` jea
            ON je.name = jea.parent
        WHERE jea.account = %(account)s
        ORDER BY je.creation DESC
        LIMIT 10
    """, {"account": account}, pluck=True)

    if not latest_vouchers:
        return {"rows": [], "total_debit": 0, "total_credit": 0}

    # ⭐ Opening Balance (before these 10)
    opening_balance = frappe.db.sql("""
        SELECT
            COALESCE(
                SUM(jea.debit_in_account_currency
                  - jea.credit_in_account_currency), 0
            )
        FROM `tabJournal Entry Account` jea
        JOIN `tabJournal Entry` je
            ON je.name = jea.parent
        WHERE
            jea.account = %(account)s
            AND je.name NOT IN %(vouchers)s
    """, {
        "account": account,
        "vouchers": tuple(latest_vouchers)
    })[0][0]

    # ⭐ Main Data
    data = frappe.db.sql("""

        SELECT
            je.name AS voucher,
            je.posting_date,
            je.creation,

            cash_line.account AS cash_account,

            GROUP_CONCAT(
                CONCAT(
                    other_line.account,
                    IF(other_line.party IS NOT NULL,
                        CONCAT(' (', other_line.party, ')'), ''
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

        WHERE
            cash_line.account = %(account)s
            AND je.name IN %(vouchers)s

        GROUP BY
            je.name,
            cash_line.name

        ORDER BY je.creation DESC

    """, {
        "account": account,
        "vouchers": tuple(latest_vouchers)
    }, as_dict=True)

    # ⭐ Running Balance add manually
    running = opening_balance
    for d in data:
        running += (d.debit or 0) - (d.credit or 0)
        d["running_balance"] = running

    # ⭐ Add Opening Row
    opening_row = {
        "voucher": "Opening",
        "posting_date": "",
        "cash_account": account,
        "counter_details": "",
        "remark": "Opening Balance",
        "status": "",
        "custom_payment_type": "",
        "debit": 0,
        "credit": 0,
        "running_balance": opening_balance
    }

    data.insert(0, opening_row)

    # ⭐ Totals
    total_debit = sum(d["debit"] for d in data)
    total_credit = sum(d["credit"] for d in data)

    return {
        "rows": data,
        "total_debit": total_debit,
        "total_credit": total_credit
    }
