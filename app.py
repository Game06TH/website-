from flask import Flask, render_template, request, redirect, url_for, session, abort
from config import db_config
from models.product_model import get_products_by_category, get_product_by_id

app = Flask(__name__)
app.secret_key = 'myshop123456'

@app.route('/')
def index():
    grouped_products = get_products_by_category()
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
        cart = {}  # Reset หากมันเป็น list หรืออย่างอื่น

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

        # ✅ แก้ตรงนี้
        conn = None
        cursor = None

        try:
            import mysql.connector
            conn = mysql.connector.connect(**db_config)  # ใช้ **db_config (ไม่ใช่ db_config ธรรมดา)
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



if __name__ == '__main__':
    app.run(debug=True)
