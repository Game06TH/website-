import os
import psycopg2
from config import db_config
from psycopg2 import extras # นำเข้า extras เพื่อใช้ DictCursor

# ฟังก์ชันตัวช่วยในการสร้างการเชื่อมต่อ
def get_db_connection():
    """สร้างและส่งคืน Object การเชื่อมต่อ PostgreSQL โดยใช้ db_config."""
    conn = None
    try:
        # แปลง Port เป็น int ในกรณีที่ดึงมาจาก Environment Variable (os.environ.get)
        db_config['port'] = int(db_config.get('port', 5432)) 
        
        # เชื่อมต่อ PostgreSQL โดยใช้ค่าจาก db_config
        conn = psycopg2.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            port=db_config['port']
        )
        return conn
    except psycopg2.Error as e:
        print(f"PostgreSQL Connection Error: {e}")
        return None

# --- ฟังก์ชันหลักทั้งหมด ถูกแปลงเป็น PostgreSQL ---

def get_products_by_category():
    conn = get_db_connection()
    if conn is None: return {}
    
    # ใช้ DictCursor เพื่อให้ได้ผลลัพธ์เป็น Dictionary
    cursor = conn.cursor(cursor_factory=extras.DictCursor)
    cursor.execute("SELECT * FROM products")
    products_raw = cursor.fetchall()

    # แปลง DictRow object เป็น dicts ธรรมดา
    products = [dict(row) for row in products_raw]

    # cursor.close() # ปิด cursor
    conn.close() # ปิดการเชื่อมต่อ

    grouped = {}
    for product in products:
        category = product.get('category', 'ไม่ระบุ')
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(product)

    return grouped


def get_product_by_id(product_id):
    conn = get_db_connection()
    if conn is None: return None
    cursor = None
    
    try:
        # ใช้ DictCursor
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product_raw = cursor.fetchone()
        
        if product_raw:
            # แปลง DictRow เป็น dict ธรรมดา
            return dict(product_raw)
        return None
        
    except psycopg2.Error as err:
        print("เกิดข้อผิดพลาด:", err)
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_all_products():
    conn = get_db_connection()
    if conn is None: return []
    
    # ใช้ DictCursor
    cursor = conn.cursor(cursor_factory=extras.DictCursor)
    cursor.execute("SELECT * FROM products")
    products_raw = cursor.fetchall()
    
    products = [dict(row) for row in products_raw]
    conn.close()
    return products

def add_product(name, price, category, image, description):
    conn = get_db_connection()
    if conn is None: return
    
    cursor = conn.cursor()
    # PostgreSQL ใช้ %s สำหรับ placeholder เหมือนกัน
    cursor.execute(
        "INSERT INTO products (name, price, category, image, description) VALUES (%s, %s, %s, %s, %s)",
        (name, price, category, image, description)
    )
    conn.commit()
    conn.close()


def update_product(product_id, name, price, category, image, description):
    conn = get_db_connection()
    if conn is None: return
    
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET name=%s, price=%s, category=%s, image=%s, description=%s WHERE id=%s",
        (name, price, category, image, description, product_id)
    )
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_db_connection()
    if conn is None: return
    
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
    conn.commit()
    conn.close()

def get_product_image(product_id):
    conn = get_db_connection()
    if conn is None: return ''
    
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT image FROM products WHERE id = %s", (product_id,))
        result = cursor.fetchone()
        return result[0] if result else ''
    except psycopg2.Error as err:
        print("เกิดข้อผิดพลาด:", err)
        return ''
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_all_products_1():
    conn = get_db_connection()
    if conn is None: return []
    
    # ใช้ DictCursor
    cursor = conn.cursor(cursor_factory=extras.DictCursor)
    cursor.execute("SELECT * FROM products ORDER BY id DESC")
    result_raw = cursor.fetchall()
    
    result = [dict(row) for row in result_raw]
    conn.close()
    return result