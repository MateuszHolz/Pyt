import sqlite3
 
def create_table():
    conn = sqlite3.connect("lite.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS tab (item TEXT, quantity INTEGER, price FLOAT)")
    conn.commit()
    cur.close()
 
def insert(item,quantity,price):
    conn = sqlite3.connect("lite.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO tab VALUES(?,?,?)",(item,quantity,price))
    conn.commit()
    cur.close()
 
def view():
    conn = sqlite3.connect("lite.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM tab")
    rows = cur.fetchall()
    cur.close()
    return rows
 
create_table()
insert('Coffee Cup', 25, 9.5)
print(view())