import sqlite3


def create_db():
    con = sqlite3.connect(database=r'loyalty_points.db')
    # To write any queries, we need to establish a cursor
    cur = con.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS category(id INTEGER PRIMARY KEY AUTOINCREMENT, name text)")
    cur.execute("INSERT INTO category VALUES(1, 'Health')")
    cur.execute("INSERT INTO category VALUES(2, 'Skin Care')")
    print('category')
    con.commit()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS product(id INTEGER PRIMARY KEY AUTOINCREMENT, category_id INTEGER, price REAL, loyalty_points INTEGER, name text)")
    cur.execute("INSERT INTO product VALUES(1, 1, 20, 10, 'Panadol')")
    cur.execute("INSERT INTO product VALUES(2, 1, 15, 5, 'Disprin')")
    cur.execute("INSERT INTO product VALUES(3, 1, 40, 20, 'Ponston')")
    cur.execute("INSERT INTO product VALUES(4, 2, 210, 30, 'Ponds Cream')")
    cur.execute("INSERT INTO product VALUES(5, 2, 150, 35, 'Fair Menz Cream')")
    print('product')
    con.commit()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY AUTOINCREMENT, name text, password text, loyalty_points INTEGER)")
    cur.execute("INSERT INTO user VALUES(1, 'john', '123456', 0)")
    cur.execute("INSERT INTO user VALUES(2, 'david', '123456', 0)")
    print('user')
    con.commit()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, order_date TIMESTAMP)")
    print('order')
    con.commit()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS order_detail(id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, product_price REAL, quantity INTEGER)")
    print('order_detail')
    con.commit()

    con.commit()
    print('completed')


create_db()
