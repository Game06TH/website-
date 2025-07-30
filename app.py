from flask import Flask, render_template, request, redirect, url_for, session, abort
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


if __name__ == '__main__':
    app.run(debug=True)
