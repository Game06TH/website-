from flask import Flask, render_template, abort, request, redirect, url_for, session
from models.product_model import get_products_by_category, get_product_by_id

app = Flask(__name__)
app.secret_key = 'myshop123456'  # จำเป็นสำหรับ session

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
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append(product_id)
    return redirect(url_for('product_detail', product_id=product_id))

if __name__ == '__main__':
    app.run(debug=True)
