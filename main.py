import os
from flask import Flask, render_template, redirect, url_for, request, session
from flask_session import Session
import sqlite3
from datetime import date
from dateutil.relativedelta import relativedelta


app = Flask(__name__, static_url_path='/static')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = '/static/images'
app.config['MAX_CONTENT_PATH'] = 1024 * 1024 * 1024

Session(app)


def get_db_connection():
    conn = sqlite3.connect('loyalty_points.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get("username"):
        print('user not logged in')
        return redirect(url_for('login'))
    else:
        print('user logged in: ' + session.get("username"))

    selected_category = None
    if request.method == 'POST':
        print('POST')
        selected_category = request.form.get('select_category', None)
        print(selected_category)
    else:
        print('GET')
        # user = request.args.get('nm')

    if selected_category is None:
        selected_category = "1"

    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM category').fetchall()
    products = conn.execute('SELECT * FROM product WHERE category_id=' + selected_category).fetchall()
    conn.close()

    message = ''
    if session.get("message"):
        message = session.get("message")
        session.pop("message")
    return render_template('index.html',
                           message=message,
                           selected_category=selected_category,
                           categories=categories, products=products)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print('POST')
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        name = request.form.get('name', None)
        dob = request.form.get('dob', None)
        gender = request.form.get('gender', None)
        address = request.form.get('address', None)
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM user WHERE username="{username}"'.format(username=username, )).fetchone()
        if user:
            print('user already exists')
            conn.close()
            return render_template('register.html', message='user already exists')
        else:
            six_months = date.today() + relativedelta(months=+6)
            conn.execute(
                'INSERT INTO user (username, password, name, dob, gender, address, '
                'loyalty_points, loyalty_points_expiry) '
                'VALUES(?,?,?,?,?,?,?,?)',
                (username, password, name, dob, gender, address, 0, six_months))
            conn.commit()
            conn.close()
        return render_template('login.html', message='user registered successfully')
    else:
        print('GET')
    return render_template('register.html', message='')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print('POST')
        username = request.form.get('username', None)
        password = request.form.get('password', None)

        if username == 'admin' and password == 'admin':
            session["username"] = username
            session["user_id"] = 0
            return redirect(url_for('adminpanel'))

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM user WHERE username="{username}" AND password="{password}"'.
                format(username=username, password=password)).fetchone()
        conn.close()
        if user:
            session["username"] = username
            session["user_id"] = user["id"]
            return redirect(url_for('index'))
        else:
            return render_template('login.html')
    else:
        print('GET')
    return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return render_template('login.html')


@app.route('/resetpassword', methods=['GET', 'POST'])
def resetpassword():
    if request.method == 'POST':
        print('POST')
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM user WHERE username="{username}"'.
                format(username=username)).fetchone()
        if user:
            conn.execute('UPDATE user SET password="{password}" WHERE username="{username}"'
                         .format(password=password, username=username))
            conn.commit()
        conn.close()
    else:
        print('GET')
        return render_template('resetpassword.html')
    return render_template('login.html')


@app.route('/add_to_cart', methods=['GET'])
def add_to_cart():
    if not session.get("username"):
        print('user not logged in')
        session["message"] = 'user not logged in'
        return render_template('login.html')
    else:
        print('user logged in: ' + session.get("username"))
        user_id = session["user_id"]
        product_id = request.args.get('product_id')
        quantity = request.args.get('quantity')
        print(product_id)
        print(quantity)
        if not session.get("cart"):
            session["cart"] = []

        cart = session["cart"]
        cart.append([product_id, quantity])
        session["cart"] = cart
    return redirect(url_for('index'))


@app.route('/checkout', methods=['GET'])
def checkout():
    if not session.get("username"):
        print('user not logged in')
        return render_template('login.html')
    else:
        print('user logged in: ' + session.get("username"))
        user_id = session["user_id"]
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM user WHERE id="{user_id}"'.
                format(user_id=user_id)).fetchone()
        if not session.get("cart"):
            session["cart"] = []

        # conn = get_db_connection()
        order = ''
        cart = session["cart"]
        if len(cart) == 0:
            session["message"] = 'cart is empty'
            return redirect(url_for('index'))

        for i in range(len(cart)):
            product_id = cart[i][0]
            quantity = cart[i][1]
            print(product_id, quantity)
            product = conn.execute('SELECT * FROM product WHERE id=' + product_id).fetchone()

            order = order + 'Product: ' + product["name"] + \
                    ', Price: ' + str(product["price"]) + \
                    ', Quantity: ' + str(quantity) + '<br />'

    return render_template('checkout.html', order=order, user=user)


@app.route('/clearcart', methods=['GET'])
def clearcart():
    # clear cart after saving order in database
    session["cart"] = []
    return redirect(url_for('index'))


@app.route('/place_order', methods=['GET'])
def place_order():
    if not session.get("username"):
        print('user not logged in')
        return render_template('login.html')
    else:
        print('user logged in: ' + session.get("username"))
        user_id = session["user_id"]
        if not session.get("cart"):
            session["cart"] = []

        payment_method = request.args.get('payment_method', None)

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM user WHERE id="{user_id}"'.
                format(user_id=user_id)).fetchone()
        existing_points = int(user["loyalty_points"])

        total_loyalty_points = 0
        product_price_quantity = 0
        total_price = 0
        order = ''
        cart = session["cart"]
        for i in range(len(cart)):
            # print(i, cart[i])
            product_id = cart[i][0]
            quantity = cart[i][1]
            print(product_id, quantity)
            product = conn.execute('SELECT * FROM product WHERE id=' + product_id).fetchone()
            points = int(product["loyalty_points"]) * int(quantity)
            total_loyalty_points = total_loyalty_points + points
            product_price_quantity = (int(product["price"]) * int(quantity))
            total_price = total_price + product_price_quantity

            order = order + 'Product: ' + product["name"] + \
                    ', Price: ' + str(product["price"]) + \
                    ', Quantity: ' + str(quantity) + \
                    ', Sub Total: ' + str(product_price_quantity) + \
                    ', Loyalty Points: ' + str(points) + '<br />'

        order = order + 'Total Before Discount: ' + str(total_price) + '<br />'
        discount = int((existing_points / 100) * 10)
        total_price = total_price - discount
        order = order + 'Total After Discount: ' + str(total_price) + '<br />'

        conn.execute('UPDATE user set loyalty_points=loyalty_points + ? WHERE id=' + str(user_id),
                     (total_loyalty_points,))
        conn.commit()
        conn.close()
        # clear cart after saving order in database
        session["cart"] = []

    return render_template('place_order.html',
                           order=order,
                           total_loyalty_points=total_loyalty_points)


@app.route('/profile', methods=['GET'])
def profile():
    if not session.get("username"):
        print('user not logged in')
        return render_template('login.html')
    else:
        print('user logged in: ' + session.get("username"))
        user_id = session["user_id"]
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM user WHERE id="{user_id}"'.
                format(user_id=user_id)).fetchone()
        conn.close()
        print('user["loyalty_points"]: ', user["loyalty_points"])
        return render_template('profile.html',
                               username=user["username"],
                               name=user["name"],
                               dob=user["dob"],
                               gender=user["gender"],
                               address=user["address"],
                               total_loyalty_points=user["loyalty_points"],
                               loyalty_points_expiry=user["loyalty_points_expiry"])


@app.route('/adminpanel', methods=['GET'])
def adminpanel():
    print('adminpanel')
    conn = get_db_connection()
    products = conn.execute('SELECT c.name cname, p.id pid, p.name pname, p.price, p.loyalty_points, p.image_path '
                            'FROM product p INNER JOIN category c '
                            'ON p.category_id=c.id '
                            'ORDER BY c.id').fetchall()
    conn.close()
    return render_template('adminpanel.html', products=products)


@app.route('/add_new_product', methods=['GET', 'POST'])
def add_new_product():
    print('add_new_product')
    if not session.get("username"):
        print('user not logged in')
        return redirect(url_for('login'))
    else:
        print('user logged in: ' + session.get("username"))

    if request.method == 'POST':
        print('POST')
        selected_category = request.form.get('select_category', None)
        product_name = request.form.get('name', None)
        price = request.form.get('price', None)
        loyalty_points = request.form.get('loyalty_points', None)
        loyalty_points_applicable = request.form.get('loyalty_points_applicable', None)
        product_image = request.files['product_image']
        product_image.save(os.path.join('static/images', product_image.filename))

        if loyalty_points_applicable is None:
            loyalty_points_applicable = 0
        else:
            loyalty_points_applicable = 1

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO product (category_id, price, loyalty_points, loyalty_points_applicable, name, image_path) '
            'VALUES(?,?,?,?,?,?)',
            (selected_category, price, loyalty_points, loyalty_points_applicable, product_name, product_image.filename))
        conn.commit()
        conn.close()
        return redirect(url_for('adminpanel'))

    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM category').fetchall()
    conn.close()
    return render_template('addnewproduct.html', categories=categories)


@app.route('/delete_product', methods=['GET'])
def delete_product():
    print('delete_product')
    pid = request.args.get('id')
    conn = get_db_connection()
    conn.execute('DELETE FROM product WHERE id=' + pid)
    conn.commit()
    return redirect(url_for('adminpanel'))


if __name__ == '__main__':
    app.run(debug=True)
