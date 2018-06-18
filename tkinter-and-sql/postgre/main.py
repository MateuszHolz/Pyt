import psycopg2


def createTable():
	conn = psycopg2.connect("dbname='database1' user='postgres' password='postgres123' host='localhost' port='5432'")
	cursor = conn.cursor()
	cursor.execute("CREATE TABLE IF NOT EXISTS STORE (item TEXT, quantity INTEGER, price REAL)")
	conn.commit()
	conn.close()

def insert(item, quantity, price):
	conn = psycopg2.connect("dbname='database1' user='postgres' password='postgres123' host='localhost' port='5432'")
	cursor = conn.cursor()
	cursor.execute("INSERT INTO store VALUES (%s, %s, %s)", (item, quantity, price))
	conn.commit()
	conn.close()

def view():
	conn = psycopg2.connect("dbname='database1' user='postgres' password='postgres123' host='localhost' port='5432'")
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM store")
	rows = cursor.fetchall()
	conn.close()
	return rows

def delete(item):
	conn = psycopg2.connect("dbname='database1' user='postgres' password='postgres123' host='localhost' port='5432'")
	cursor = conn.cursor()
	cursor.execute("DELETE FROM store WHERE item=%s", (item,))
	conn.commit()
	conn.close()

createTable()
insert('yellow', 33, 444)
print(view())
delete('blue')
print(view())