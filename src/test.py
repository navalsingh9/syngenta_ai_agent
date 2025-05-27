import sqlite3

# conn = sqlite3.connect("data/transactions.db")
# cursor = conn.execute("PRAGMA table_info(transactions);")
# for row in cursor.fetchall():
#     print(row)

import sqlite3

conn = sqlite3.connect("data/transactions.db")  # adjust path if needed
cursor = conn.cursor()

query = """
SELECT SUM(sales) 
FROM transactions 
WHERE LOWER(order_region) = LOWER('southwest') 
AND date(
    substr(order_date_dateorders_, 7, 4) || '-' || 
    substr(order_date_dateorders_, 1, 2) || '-' || 
    substr(order_date_dateorders_, 4, 2)
) BETWEEN '2017-07-01' AND '2017-09-30';

"""  # Replace with any SQL you want to test

cursor.execute(query)
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
