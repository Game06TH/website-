from flask import Flask, render_template
from models.product_model import get_products_by_category

app = Flask(__name__)

@app.route('/')
def index():
    grouped_products = get_products_by_category()
    return render_template('index.html', grouped_products=grouped_products)

if __name__ == '__main__':
    app.run(debug=True)


