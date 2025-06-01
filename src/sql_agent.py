# from langchain.prompts import PromptTemplate
# from langchain_core.runnables import RunnableSequence
# import sqlite3
# import pandas as pd
# import re

# column_aliases = {
# "type": "type",  # Defines the nature of the transaction, such as Sale, Return, or Exchange. Helps segment datasets when analyzing returns policy effectiveness.
#     "days_for_shipping_real": "days_for_shipping_real_",  # Captures the actual number of days it took to ship an item. Useful in evaluating on-time performance and measuring SLA adherence.
#     "days_for_shipment_scheduled": "days_for_shipment_scheduled_",  # Planned shipment timeline in days. Useful for benchmarking against actual shipment time to detect inefficiencies or late deliveries.
#     "benefit_per_order": "benefit_per_order",  # Additional benefit (e.g., coupon, rebate) tied to each order. Helps evaluate impact of loyalty programs or promotions on sales.
#     "sales_per_customer": "sales_per_customer",  # Cumulative revenue per customer. Useful in customer segmentation and identifying high-value clients.
#     "delivery_status": "delivery_status",  # Reflects if an order has been delivered, cancelled, or returned. Critical for reverse logistics or claim investigations.
#     "late_delivery_risk": "late_delivery_risk",  # Predictive indicator flagging likelihood of a late delivery. Important for supply chain risk assessments.
#     "category_id": "category_id",  # Numeric key to group items into product categories. Helps in filtering by category when performing inventory aging or sales breakdown.
#     "category_name": "category_name",  # Textual representation of category. Used in generating human-readable reports by product classification.
#     "customer_city": "customer_city",  # City associated with a customer. Useful in heatmapping demand or targeting regional offers.
#     "customer_country": "customer_country",  # Country of the customer, enabling queries related to international shipments and compliance.
#     "customer_email": "customer_email",  # Email address linked to customer. Useful when investigating top buyers or complaints.
#     "customer_fname": "customer_fname",  # Customer’s first name. Not commonly queried directly, but useful for personalizing analytics.
#     "customer_id": "customer_id",  # Unique ID assigned to each customer. Key for linking multiple orders or returns to the same entity.
#     "customer_lname": "customer_lname",  # Customer’s last name. Supplementary to customer_fname for full identification.
#     "customer_password": "customer_password",  # Placeholder field not used in analytics. Ensure exclusion in reporting and compliance outputs.
#     "customer_segment": "customer_segment",  # Classification such as Consumer, Corporate, or Home Office. Supports behavioral segmentation and targeted campaigns.
#     "customer_state": "customer_state",  # State-level location of the customer. Used for comparing regional demand patterns.
#     "customer_street": "customer_street",  # Detailed street address. Useful in planning last-mile logistics or resolving disputed deliveries.
#     "customer_zipcode": "customer_zipcode",  # Postal code of customer address. Critical for geographic distribution analysis and service zone planning.
#     "department_id": "department_id",  # Unique identifier for internal department responsible for the transaction. Useful in tracking performance by business unit.
#     "department_name": "department_name",  # Human-readable name of the department. Ideal for KPI dashboards showing departmental contribution.
#     "latitude": "latitude",  # Latitude coordinate of transaction point. Used in GIS tools for logistics network optimization.
#     "longitude": "longitude",  # Longitude coordinate to be paired with latitude for complete spatial plotting.
#     "market": "market",  # Regional or global market (e.g., APAC, EU). Important for analyzing cross-border performance or localized policy compliance.
#     "order_city": "order_city",  # City where the order was placed. Helps in analyzing origin points for logistics or fraud detection.
#     "order_country": "order_country",  # Country from which the order originated. Essential for calculating domestic vs. international shipping efficiency.
#     "order_customer_id": "order_customer_id",  # Connects the order to the customer placing it. Mirrors customer_id for matching purposes.
#     "order_date": "order_date_dateorders_",  # The date the order was created. Central for calculating lead times, aging inventory, and quarterly performance.
#     "order_id": "order_id",  # Unique transaction identifier. Core to all order tracking, auditing, and customer service cases.
#     "order_item_cardprod_id": "order_item_cardprod_id",  # Code for the product ordered. Used in inventory tracking and matching with catalog metadata.
#     "order_item_discount": "order_item_discount",  # Monetary discount applied to the item. Analyzed in discount effectiveness or promotional ROI studies.
#     "order_item_discount_rate": "order_item_discount_rate",  # Percentage-based discount. Important for comparing discount strategies across items or timeframes.
#     "order_item_id": "order_item_id",  # Unique ID for each item in an order. Enables line-item level granularity in sales analysis.
#     "order_item_product_price": "order_item_product_price",  # Base price per item before any discounts. Useful in MSRP vs. billed price comparisons.
#     "order_item_profit_ratio": "order_item_profit_ratio",  # Profit margin as a ratio. Key for identifying most profitable products and categories.
#     "order_item_quantity": "order_item_quantity",  # Number of units in a given line item. Crucial for inventory turnover and reorder planning.
#     "sales": "sales",  # Final total revenue from a sale after discounts. Central metric in all sales performance analysis.
#     "order_item_total": "order_item_total",  # Calculated total amount billed for a line item. Used in invoice-level audits and validation.
#     "order_profit_per_order": "order_profit_per_order",  # Net profit made from each order. Used in profitability dashboards and margin optimization.
#     "order_region": "order_region",  # Named region (e.g., Southwest) for the order. Common filter for regional analysis and policy deployment.
#     "order_state": "order_state",  # State in which the order was fulfilled. Useful in state-level compliance reporting or shipping delays.
#     "order_status": "order_status",  # Indicates whether the order was delivered, returned, or cancelled. Required for reverse logistics reporting.
#     "order_zipcode": "order_zipcode",  # Zip code of shipping destination. Important in service coverage and delivery SLAs.
#     "product_card_id": "product_card_id",  # Primary key for product reference. Used in joins with master product list.
#     "product_category_id": "product_category_id",  # Category key for classification. Used in trend analysis and compliance with category policies.
#     "product_description": "product_description",  # Textual detail of the product. Supports QA and returns diagnostics.
#     "product_image": "product_image",  # URL or path to product image. Generally excluded from data analysis but helpful for UI tools.
#     "product_name": "product_name",  # Name of the product. Needed for report readability and top product lists.
#     "product_price": "product_price",  # Listed price of the product. Core to profitability and pricing strategy insights.
#     "product_status": "product_status",  # Current lifecycle status (e.g., Active, Obsolete). Crucial for obsolete inventory write-off policies.
#     "shipping_date": "shipping_date_dateorders_",  # Date when the order was shipped. Used for calculating lead time and compliance with dispatch SLAs.
#     "shipping_mode": "shipping_mode"  # Describes shipping method like First Class or Express. Used in cost-benefit analyses for transportation policies.
# }

# def detect_date_format(db_path="data/transactions.db", column="order_date_dateorders_"):
#     try:
#         conn = sqlite3.connect(db_path)
#         df = pd.read_sql(f"SELECT {column} FROM transactions WHERE {column} IS NOT NULL LIMIT 100;", conn)
#         conn.close()

#         sample = df[column].dropna().astype(str).iloc[0]
#         if re.match(r"\d{4}-\d{2}-\d{2}", sample):
#             return "ISO"
#         elif re.match(r"\d{1,2}/\d{1,2}/\d{4}", sample):
#             return "US"
#         elif re.match(r"\d{4}/\d{2}/\d{2}", sample):
#             return "YMD"
#         else:
#             return "UNKNOWN"
#     except Exception as e:
#         print(f"[DEBUG] Could not detect date format: {str(e)}")
#         return "UNKNOWN"

# def get_dataset_context(db_path="data/transactions.db"):
#     try:
#         conn = sqlite3.connect(db_path)
#         cursor = conn.cursor()
#         cursor.execute("PRAGMA table_info(transactions);")
#         schema_rows = cursor.fetchall()
#         cursor.execute("SELECT MIN(order_date_dateorders_), MAX(order_date_dateorders_) FROM transactions")
#         min_date, max_date = cursor.fetchone()
#         conn.close()

#         schema_text = "\n".join([f"- {col[1].strip()}: {col[2].strip()}" for col in schema_rows])
#         return schema_text, min_date, max_date
#     except:
#         return "", "", ""

# def get_prompt(llm):
#     is_claude = "ClaudeBedrockLLM" in str(type(llm))
#     schema_text, min_date, max_date = get_dataset_context()
#     date_format = detect_date_format()

#     if date_format == "US":
#         date_sql = "date(substr(order_date_dateorders_, 7, 4) || '-' || substr(order_date_dateorders_, 1, 2) || '-' || substr(order_date_dateorders_, 4, 2))"
#     elif date_format == "ISO":
#         date_sql = "order_date_dateorders_"
#     elif date_format == "YMD":
#         date_sql = "date(order_date_dateorders_)"
#     else:
#         date_sql = "date(order_date_dateorders_)"

#     return PromptTemplate.from_template(f'''
# You are a helpful assistant that writes SQLite SQL queries for a table called `transactions`.

# Schema:
# {schema_text}

# Date column `order_date_dateorders_` has format: {date_format}.
# Use this transformation for date filtering:
#   {date_sql}

# Only return a valid SQL query, no explanation.

# Question: {{question}}
# ''')

# def extract_sql_from_markdown(response: str) -> str:
#     match = re.search(r"```sql\s*(.*?)```", response, re.DOTALL | re.IGNORECASE)
#     if match:
#         return match.group(1).strip()
#     return response.strip()

# def replace_column_aliases(query: str, alias_map: dict) -> str:
#     for alias, actual in alias_map.items():
#         query = re.sub(rf"\b{alias}\b", actual, query, flags=re.IGNORECASE)
#     return query

# def normalize_region_case(query: str) -> str:
#     return re.sub(r"(order_region\s*=\s*)'([^']+)'",
#                   lambda m: f"LOWER(order_region) = LOWER('{m.group(2)}')", query)

# def patch_malformed_date_usage(sql: str) -> str:
#     corrected = (
#         "date("
#         "substr(order_date_dateorders_, 7, 4) || '-' || "
#         "substr(order_date_dateorders_, 1, 2) || '-' || "
#         "substr(order_date_dateorders_, 4, 2)"
#         ")"
#     )
#     sql = re.sub(r"order_date_dateorders_\([^)]*\)", "order_date_dateorders_", sql)
#     sql = re.sub(r"date\s*\([^)]*\)", corrected, sql, flags=re.IGNORECASE)
#     return sql

# def ask_data_question(question: str, llm):
#     is_claude = llm.__class__.__name__.lower().startswith("claude")
#     prompt = get_prompt(llm)
#     chain = prompt | llm

#     try:
#         response = chain.invoke({"question": question})
#         sql_query = extract_sql_from_markdown(response)

#         if is_claude:
#             match = re.search(r"(?i)(SELECT\s.*?);?$", sql_query, re.DOTALL)
#             if match:
#                 sql_query = match.group(1).strip()
#     except Exception as e:
#         return None, f"❌ LLM failed to generate SQL: {str(e)}"

#     if not is_claude:
#         sql_query = replace_column_aliases(sql_query, column_aliases)
#         sql_query = patch_malformed_date_usage(sql_query)
#         sql_query = normalize_region_case(sql_query)

#     if any(ref in sql_query for ref in ["last_date", "last_quarter_start"]) and "WITH" not in sql_query.upper():
#         return sql_query, "⚠️ Detected use of `last_date` or `last_quarter_start` without a `WITH` clause. Please include the full CTE block."

#     try:
#         conn = sqlite3.connect("data/transactions.db")
#         cursor = conn.execute(sql_query)
#         result = cursor.fetchall()
#         desc = cursor.description
#         conn.close()

#         if desc is None:
#             return sql_query, "⚠️ Query executed but returned no data or columns."

#         df_result = pd.DataFrame(result, columns=[col[0] for col in desc])
#         return sql_query, df_result

#     except Exception as e:
#         return sql_query, f"❌ Error executing SQL: {str(e)}"

# def get_ground_truth(nl_query: str) -> str | None:
#     import json, os
#     path = os.path.join(os.path.dirname(__file__), "test_cases.jsonl")
#     if not os.path.exists(path):
#         return None

#     with open(path, "r", encoding="utf-8") as f:
#         for line in f:
#             case = json.loads(line)
#             if case["nl_query"].strip().lower() == nl_query.strip().lower():
#                 return case["expected_sql"]
#     return None

from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
import sqlite3
import pandas as pd
import re

column_aliases = {
    "type": "type",
    "days_for_shipping_real": "days_for_shipping_real_",
    "days_for_shipment_scheduled": "days_for_shipment_scheduled_",
    "benefit_per_order": "benefit_per_order",
    "sales_per_customer": "sales_per_customer",
    "delivery_status": "delivery_status",
    "late_delivery_risk": "late_delivery_risk",
    "category_id": "category_id",
    "category_name": "category_name",
    "customer_city": "customer_city",
    "customer_country": "customer_country",
    "customer_email": "customer_email",
    "customer_fname": "customer_fname",
    "customer_id": "customer_id",
    "customer_lname": "customer_lname",
    "customer_password": "customer_password",
    "customer_segment": "customer_segment",
    "customer_state": "customer_state",
    "customer_street": "customer_street",
    "customer_zipcode": "customer_zipcode",
    "department_id": "department_id",
    "department_name": "department_name",
    "latitude": "latitude",
    "longitude": "longitude",
    "market": "market",
    "order_city": "order_city",
    "order_country": "order_country",
    "order_customer_id": "order_customer_id",
    "order_date": "order_date_dateorders_",
    "order_id": "order_id",
    "order_item_cardprod_id": "order_item_cardprod_id",
    "order_item_discount": "order_item_discount",
    "order_item_discount_rate": "order_item_discount_rate",
    "order_item_id": "order_item_id",
    "order_item_product_price": "order_item_product_price",
    "order_item_profit_ratio": "order_item_profit_ratio",
    "order_item_quantity": "order_item_quantity",
    "sales": "sales",
    "order_item_total": "order_item_total",
    "order_profit_per_order": "order_profit_per_order",
    "order_region": "order_region",
    "order_state": "order_state",
    "order_status": "order_status",
    "order_zipcode": "order_zipcode",
    "product_card_id": "product_card_id",
    "product_category_id": "product_category_id",
    "product_description": "product_description",
    "product_image": "product_image",
    "product_name": "product_name",
    "product_price": "product_price",
    "product_status": "product_status",
    "shipping_date": "shipping_date_dateorders_",
    "shipping_mode": "shipping_mode"
}

def detect_date_format(db_path="data/transactions.db", column="order_date_dateorders_"):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql(f"SELECT {column} FROM transactions WHERE {column} IS NOT NULL LIMIT 100;", conn)
        conn.close()

        sample = df[column].dropna().astype(str).iloc[0]
        if re.match(r"\d{4}-\d{2}-\d{2}", sample):
            return "ISO"
        elif re.match(r"\d{1,2}/\d{1,2}/\d{4}", sample):
            return "US"
        elif re.match(r"\d{4}/\d{2}/\d{2}", sample):
            return "YMD"
        else:
            return "UNKNOWN"
    except Exception as e:
        print(f"[DEBUG] Could not detect date format: {str(e)}")
        return "UNKNOWN"

def get_dataset_context(db_path="data/transactions.db"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(transactions);")
        schema_rows = cursor.fetchall()
        cursor.execute("SELECT MIN(order_date_dateorders_), MAX(order_date_dateorders_) FROM transactions")
        min_date, max_date = cursor.fetchone()
        conn.close()

        schema_text = "\n".join([f"- {col[1].strip()} ({col[2].strip()})" for col in schema_rows])
        return schema_text, min_date, max_date
    except:
        return "", "", ""

def get_prompt(llm):
    schema_text, min_date, max_date = get_dataset_context()
    date_format = detect_date_format()

    if date_format == "US":
        date_sql = "date(substr(order_date_dateorders_, 7, 4) || '-' || substr(order_date_dateorders_, 1, 2) || '-' || substr(order_date_dateorders_, 4, 2))"
    elif date_format == "ISO":
        date_sql = "order_date_dateorders_"
    elif date_format == "YMD":
        date_sql = "date(order_date_dateorders_)"
    else:
        date_sql = "date(order_date_dateorders_)"

    return PromptTemplate.from_template(f'''
You are an expert data assistant. You write **accurate SQLite SQL queries** for the table `transactions` using the correct column names and types.

## Table schema
{schema_text}

## Notes
- Dates are stored as TEXT. Convert them using `DATE(...)` or `STRFTIME(...)` for comparisons.
- Use real column names. Do not invent new ones.

## Examples:
Q: Total sales in the Southwest region in March 2024  
A:
```sql
SELECT SUM(sales) 
FROM transactions 
WHERE order_region = 'Southwest' 
AND DATE(order_date_dateorders_) BETWEEN '2024-03-01' AND '2024-03-31';
```

Q: Count of late deliveries in India  
A:
```sql
SELECT COUNT(*) 
FROM transactions 
WHERE delivery_status = 'Late' 
AND customer_country = 'India';
```

Now generate a SQL query for:

Q: {{question}}
A:
''')

def extract_sql_from_markdown(response: str) -> str:
    match = re.search(r"```sql\s*(.*?)```", response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return response.strip()

def replace_column_aliases(query: str, alias_map: dict) -> str:
    for alias, actual in alias_map.items():
        query = re.sub(rf"\b{alias}\b", actual, query, flags=re.IGNORECASE)
    return query

def normalize_region_case(query: str) -> str:
    return re.sub(r"(order_region\s*=\s*)'([^']+)'", lambda m: f"LOWER(order_region) = LOWER('{m.group(2)}')", query)

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

def ask_data_question(question: str, llm):
    is_claude = llm.__class__.__name__.lower().startswith("claude")
    prompt = get_prompt(llm)
    chain = prompt | llm

    try:
        response = chain.invoke({"question": question})
        sql_query = extract_sql_from_markdown(response)

        if is_claude:
            match = re.search(r"(?i)(SELECT\s.*?);?$", sql_query, re.DOTALL)
            if match:
                sql_query = match.group(1).strip()
    except Exception as e:
        return None, f"❌ LLM failed to generate SQL: {str(e)}"

    if not is_claude:
        sql_query = replace_column_aliases(sql_query, column_aliases)
        sql_query = patch_malformed_date_usage(sql_query)
        sql_query = normalize_region_case(sql_query)

    if any(ref in sql_query for ref in ["last_date", "last_quarter_start"]) and "WITH" not in sql_query.upper():
        return sql_query, "⚠️ Detected use of `last_date` or `last_quarter_start` without a `WITH` clause. Please include the full CTE block."

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

def get_ground_truth(nl_query: str) -> str | None:
    import json, os
    path = os.path.join(os.path.dirname(__file__), "test_cases.jsonl")
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            case = json.loads(line)
            if case["nl_query"].strip().lower() == nl_query.strip().lower():
                return case["expected_sql"]
    return None
