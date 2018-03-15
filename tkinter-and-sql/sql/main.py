import sqlite3 as sql

def createTable():
    conn = sql.connect("lite.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS store (item TEXT, quantity INTEGER, price REAL)")
    conn.commit()
    conn.close()

def insert(item, quantity, price):
    conn = sql.connect("lite.db")
    cur = conn.cursor()
    cur.execute(r"INSERT INTO store VALUES ('{}', {}, {})".format(item, quantity, price))
    conn.commit()
    conn.close()

def view():
    conn = sql.connect("lite.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM store")
    rows = cur.fetchall()
    conn.close()
    return rows

def delete(item):
    conn = sql.connect("lite.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM store WHERE item='{}'".format(item))
    conn.commit()
    conn.close()

def update(quantity, price, item):
    conn = sql.connect("lite.db")
    cur = conn.cursor()
    cur.execute("UPDATE store SET quantity={}, price={} WHERE item='{}'".format(quantity, price, item))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    createTable()
    #insert('Wine Glass', 50, 10.2)
    #delete('Water Glass')
    print(view())
    update(44, 15.8, 'Wine Glass')
