from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from models.product_model import get_all_products, add_product, update_product, delete_product, get_products_by_category, get_product_by_id , get_product_image
from config import db_config
import os
import mysql.connector
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash



app = Flask(__name__)
app.secret_key = 'myshop123456'

# ----------- ตั้งค่าอัปโหลดรูป -----------
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------- USER ROUTES -----------
@app.route('/')
def index():
    grouped_products = get_products_by_category()
    print(grouped_products)  # ตรวจสอบข้อมูลว่ามาถึง template ไหม
    return render_template('index.html', grouped_products=grouped_products)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if product:
        return render_template('product_detail.html', product=product)
    else:
        abort(404)

@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart = session.get('cart')
    if not isinstance(cart, dict):
        cart = {}
    str_id = str(product_id)
    if str_id in cart:
        cart[str_id]['quantity'] += 1
    else:
        cart[str_id] = {'quantity': 1}
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    products = []
    total = 0
    for str_id, item in cart.items():
        product = get_product_by_id(int(str_id))
        if product:
            product['quantity'] = item['quantity']
            product['subtotal'] = product['quantity'] * product['price']
            total += product['subtotal']
            products.append(product)
    return render_template('cart.html', products=products, total=total)

@app.route('/cart/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    cart = session.get('cart', {})
    str_id = str(product_id)
    if str_id in cart:
        if quantity <= 0:
            del cart[str_id]
        else:
            cart[str_id]['quantity'] = quantity
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/cart/clear')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('cart'))

@app.route('/reset_session')
def reset_session():
    session.clear()
    return 'Session ถูกล้างแล้ว'

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('cart'))
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        products = []
        total = 0
        for str_id, item in cart.items():
            product = get_product_by_id(int(str_id))
            if product:
                quantity = item['quantity']
                subtotal = product['price'] * quantity
                total += subtotal
                products.append({
                    'id': product['id'],
                    'price': product['price'],
                    'quantity': quantity
                })
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO orders (customer_name, customer_address, customer_phone, total_price) VALUES (%s, %s, %s, %s)",
                (name, address, phone, total)
            )
            order_id = cursor.lastrowid
            for item in products:
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                    (order_id, item['id'], item['quantity'], item['price'])
                )
            conn.commit()
        except Exception as e:
            print("❌ Error saving order:", e)
            return "เกิดข้อผิดพลาดระหว่างบันทึกคำสั่งซื้อ", 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        session.pop('cart', None)
        return redirect(url_for('order_success'))
    return render_template('checkout.html')

@app.route('/order_success', endpoint='order_success')
def show_order_success():
    return render_template('order_success.html')

# ----------- ADMIN ROUTES -----------
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            # ดึงผู้ใช้จากฐานข้อมูล
            cursor.execute("SELECT * FROM admins WHERE username = %s AND password = %s", (username, password))
            admin = cursor.fetchone()

            if admin:
                session['admin_logged_in'] = True
                return redirect(url_for('admin_dashboard'))
            else:
                flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง', 'danger')
        except Exception as e:
            flash('เกิดข้อผิดพลาดในการเชื่อมต่อฐานข้อมูล', 'danger')
            print(e)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('admin/login.html')



@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin/dashboard.html')

@app.route('/admin/manage-products')
def manage_products():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    products = get_all_products()
    return render_template('admin/manage_products.html', products=products)

@app.route('/admin/product/add', methods=['POST'])
def admin_add_product():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    name = request.form['name']
    description = request.form.get('description', '')
    price = float(request.form['price'])
    category = request.form['category']
    file = request.files['image']
    image_filename = ''

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        image_path = os.path.join('static/images', filename)  # เปลี่ยน path จาก uploads ➜ static/images
        file.save(image_path)
        image_filename = filename

    add_product(name, price, category, image_filename, description)
    return redirect(url_for('manage_products'))

@app.route('/admin/product/update/<int:product_id>', methods=['POST'])
def admin_update_product(product_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    name = request.form['name']
    description = request.form.get('description', '')  # เพิ่มอ่าน description
    price = float(request.form['price'])
    category = request.form['category']
    image_filename = request.form.get('old_image')  # ใช้ชื่อภาพเดิมเป็นค่า default

    # รับไฟล์ใหม่ (ถ้ามีการแนบไฟล์)
    file = request.files.get('image')
    if file and file.filename != '' and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        image_path = os.path.join('static/images', filename)
        file.save(image_path)
        image_filename = filename  # ใช้ชื่อใหม่แทนที่ชื่อเดิม

    # อัปเดตสินค้าพร้อม description
    update_product(product_id, name, price, category, image_filename, description)
    return redirect(url_for('manage_products'))




@app.route('/admin/product/delete/<int:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    try:
        # ดึงชื่อไฟล์ภาพก่อนลบ (สมมติคุณมีฟังก์ชันนี้)
        image_filename = get_product_image(product_id)
        delete_product(product_id)

        # ลบไฟล์ภาพจากโฟลเดอร์ static/images/
        if image_filename:
            image_path = os.path.join('static/images', image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)

    except Exception as e:
        flash('เกิดข้อผิดพลาดในการลบสินค้า', 'danger')
        print(e)

    return redirect(url_for('manage_products'))




# ✅ หน้าแสดงคำสั่งซื้อทั้งหมด
@app.route('/admin/orders')
def admin_orders():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM orders ORDER BY id DESC")
        orders = cursor.fetchall()
    except Exception as e:
        flash('เกิดข้อผิดพลาดในการโหลดข้อมูลคำสั่งซื้อ', 'danger')
        orders = []
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    return render_template('admin/orders.html', orders=orders)

# ✅ ลบคำสั่งซื้อ
@app.route('/admin/order/delete/<int:order_id>', methods=['POST'])
def admin_delete_order(order_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # ลบรายการสินค้าก่อน
        cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))
        # ลบคำสั่งซื้อหลัก
        cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
        
        conn.commit()
        flash('ลบคำสั่งซื้อเรียบร้อย', 'success')
    except Exception as e:
        flash('เกิดข้อผิดพลาดในการลบคำสั่งซื้อ', 'danger')
        print(e)
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    return redirect(url_for('admin_orders'))


if __name__ == '__main__':
    app.run(debug=True)
