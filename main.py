from flask import Flask, render_template, redirect, url_for, request, session
from flask_session import Session
import sqlite3

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
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

    return render_template('index.html',
                           selected_category=selected_category,
                           categories=categories, products=products)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print('POST')
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        conn = get_db_connection()
        conn.execute('INSERT INTO user (name, password, loyalty_points) VALUES(?,?,?)',
                     (username, password, 0))
        conn.commit()
        conn.close()
        return render_template('login.html')
    else:
        print('GET')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print('POST')
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM user WHERE name="{username}" AND password="{password}"'.
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
            'SELECT * FROM user WHERE name="{username}"'.
                format(username=username)).fetchone()
        if user:
            conn.execute('UPDATE user SET password="{password}" WHERE name="{username}"'
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

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM user WHERE id="{user_id}"'.
                format(user_id=user_id)).fetchone()
        existing_points = int(user["loyalty_points"])

        total_loyalty_points = 0
        product_price_quantity = 0
        total_price = 0
        order = '';
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
                               username=user["name"],
                               total_loyalty_points=user["loyalty_points"])


if __name__ == '__main__':
    app.run(debug=True)
