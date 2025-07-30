import mysql.connector
from config import db_config

def get_products_by_category():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()

    grouped = {}
    for product in products:
        category = product['category']  # เช่น 'CPU', 'RAM'
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(product)

    return grouped

