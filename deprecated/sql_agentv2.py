from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
import sqlite3
import pandas as pd
import re

column_aliases = {
    "amount": "sales",
    "sales_amount": "sales",
    "region": "order_region",
    "date": "order_date_dateorders_",
    "timestamp": "order_date_dateorders_",
    "shipping_time": "days_for_shipping_real_",
    "shipping_days": "days_for_shipping_real_",
    "real_shipping_days": "days_for_shipping_real_",
    "scheduled_shipping": "days_for_shipment_scheduled_",
    "late_delivery": "late_delivery_risk",
    "order_date": "order_date_dateorders_",
    "shipping_date": "shipping_date_dateorders_",
    "quantity": "order_item_quantity",
    "profit": "order_profit_per_order",
    "order_region": "order_region",
    "order_country": "order_country"
}

sql_prompt = PromptTemplate(
    input_variables=["question"],
    template="""
You are an expert SQLite assistant.

Use the `transactions` table only.

Note:
- Dates are in MM/DD/YYYY format in `order_date_dateorders_`.
- Convert to YYYY-MM-DD using this:
  date(substr(order_date_dateorders_, 7, 4) || '-' || substr(order_date_dateorders_, 1, 2) || '-' || substr(order_date_dateorders_, 4, 2))

Return only the SQL query. No explanations.

Question: {question}
"""
)

def replace_column_aliases(query: str, alias_map: dict) -> str:
    for alias, actual in alias_map.items():
        query = re.sub(rf"\b{alias}\b", actual, query, flags=re.IGNORECASE)
    return query

def normalize_region_case(query: str) -> str:
    return re.sub(
        r"(order_region\s*=\s*)'([^']+)'",
        lambda m: f"LOWER({m.group(1).strip()[:-1]}) = LOWER('{m.group(2)}')",
        query
    )

def patch_malformed_date_usage(sql: str) -> str:
    corrected = (
        "date("
        "substr(order_date_dateorders_, 7, 4) || '-' || "
        "substr(order_date_dateorders_, 1, 2) || '-' || "
        "substr(order_date_dateorders_, 4, 2)"
        ")"
    )
    sql = re.sub(r"order_date_dateorders_\([^)]*\)", "order_date_dateorders_", sql)
    sql = re.sub(r"date\s*\([^)]*\)", corrected, sql, flags=re.IGNORECASE)
    return sql

def expand_quarter_dates(question: str) -> str:
    if "last quarter" in question.lower():
        return re.sub(r"last quarter", "between 2017-07-01 and 2017-09-30", question, flags=re.IGNORECASE)
    return question

def ask_data_question(question: str, llm):
    question = expand_quarter_dates(question)
    chain = sql_prompt | llm
    sql_query = chain.invoke({"question": question}).strip().strip("```sql").strip("```").strip()
    sql_query = replace_column_aliases(sql_query, column_aliases)
    sql_query = patch_malformed_date_usage(sql_query)
    sql_query = normalize_region_case(sql_query)

    try:
        conn = sqlite3.connect("data/transactions.db")
        cursor = conn.execute(sql_query)
        result = cursor.fetchall()
        desc = cursor.description
        conn.close()

        if desc is None:
            return sql_query, "⚠️ Query executed but returned no data or columns."
        df_result = pd.DataFrame(result, columns=[col[0] for col in desc])
        return sql_query, df_result

    except Exception as e:
        return sql_query, f"❌ Error executing SQL: {str(e)}"