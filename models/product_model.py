import mysql.connector
from config import db_config

def get_products_by_category():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    print("สินค้าทั้งหมด:", products)  # <-- เพิ่มตรงนี้

    cursor.close()
    conn.close()

    grouped = {}
    for product in products:
        print("สินค้า:", product)  # <-- ตรวจสอบสินค้าแต่ละตัว
        category = product.get('category', 'ไม่ระบุ')
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(product)

    print("Grouped:", grouped)  # <-- ดูโครงสร้างสุดท้าย
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

def add_product(name, price, category, image, description):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, price, category, image, description) VALUES (%s, %s, %s, %s, %s)",
        (name, price, category, image, description)
    )
    conn.commit()
    conn.close()


def update_product(product_id, name, price, category, image, description):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET name=%s, price=%s, category=%s, image=%s, description=%s WHERE id=%s",
        (name, price, category, image, description, product_id)
    )
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
    conn.commit()
    conn.close()

def get_product_image(product_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT image FROM products WHERE id = %s", (product_id,))
        result = cursor.fetchone()
        return result[0] if result else ''
    except mysql.connector.Error as err:
        print("เกิดข้อผิดพลาด:", err)
        return ''
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_all_products_1():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products ORDER BY id DESC")
    result = cursor.fetchall()
    conn.close()
    return result