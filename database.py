import sqlite3


def create_db():
    con = sqlite3.connect(database=r'loyalty_points.db')
    # To write any queries, we need to establish a cursor
    cur = con.cursor()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS category(id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "name text)")
    cur.execute("INSERT INTO category VALUES(1, 'Health')")
    cur.execute("INSERT INTO category VALUES(2, 'Skin Care')")
    cur.execute("INSERT INTO category VALUES(3, 'Mobiles')")
    cur.execute("INSERT INTO category VALUES(4, 'Electronics')")
    cur.execute("INSERT INTO category VALUES(5, 'Clothing')")
    print('category')
    con.commit()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS product(id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "category_id INTEGER, "
        "price REAL, "
        "loyalty_points INTEGER, loyalty_points_applicable INTEGER, "
        "name text, "
        "image_path text)")
    cur.execute("INSERT INTO product VALUES(1, 1, 20, 10, 1, 'Panadol', 'panadol.jpg')")
    cur.execute("INSERT INTO product VALUES(2, 1, 15, 5, 1, 'Disprin', 'disprin.jpg')")
    cur.execute("INSERT INTO product VALUES(3, 1, 40, 20, 1, 'Ponston', 'ponston.jpg')")
    cur.execute("INSERT INTO product VALUES(4, 2, 210, 30, 1, 'Ponds Cream', 'ponds_cream.jpg')")
    cur.execute("INSERT INTO product VALUES(5, 2, 150, 35, 1, 'Fair Menz Cream', 'fair_menz_cream.jpg')")
    cur.execute("INSERT INTO product VALUES(6, 3, 60000, 100, 1, 'Samsung Galaxy S8', 'samsung_galaxy_s8.jpg')")
    cur.execute("INSERT INTO product VALUES(7, 3, 115000, 135, 1, 'iPhone 8', 'iphone_8.jpg')")
    cur.execute("INSERT INTO product VALUES(8, 4, 122000, 0, 0, 'Sony LCD 32 inch', 'sony_lcd_32_inch.jpg')")
    cur.execute("INSERT INTO product VALUES(9, 5, 1500, 0, 1, 'Men T-Shirt', 'men_t-shirt.jpg')")
    print('product')
    con.commit()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "username TEXT, name text, password TEXT, "
        "dob TEXT, gender TEXT, address TEXT, "
        "loyalty_points INTEGER, loyalty_points_expiry TEXT)")
    cur.execute("INSERT INTO user VALUES(1, 'kashif', 'Kashif', '123456', '01/07/1990', 'MALE', 'Lahore', 0)")
    cur.execute("INSERT INTO user VALUES(2, 'zaheer', 'Zaheer', '123456', '02/09/1995', 'MALE', 'Lahore', 0)")
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
