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

def get_product_by_id(product_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        return product
    except mysql.connector.Error as err:
        print("เกิดข้อผิดพลาด:", err)
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_all_products():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

def add_product(name, price, category, image_filename):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, price, category, image) VALUES (%s, %s, %s, %s)",
        (name, price, category, image_filename)
    )
    conn.commit()
    conn.close()


def update_product(product_id, name, price, category, image):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET name=%s, price=%s, category=%s, image=%s WHERE id=%s", (name, price, category, image, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
    conn.commit()
    conn.close()

