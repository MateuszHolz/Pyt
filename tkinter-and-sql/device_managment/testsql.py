import sqlite3 as sql

db = sql.connect(r'\\192.168.64.200\byd-fileserver\MHO\devicestestt.db')
cur = db.cursor()
cur.execute("""
	CREATE TABLE IF NOT EXISTS devices (
	jeden TEXT,
	dwa TEXT,
	trzy TEXT,
	cztery TEXT)
	""")
db.commit()

#cur.execute("INSERT INTO devices VALUES (?, ?, ?, ?)", ('piec', 'szesc', 'siedem', 'osiem'))
db.commit()
cur.execute("SELECT * FROM devices")
print(cur.fetchall())
cur.execute("UPDATE devices SET jeden = dziesiec, dwa = jedenascie, trzy = dwanascie, cztery = trzynascie WHERE jeden = piec")
#, ("jeden = dziesiec, dwa = jedenascie, trzy = dwanascie, cztery = trzynascie",))
db.commit()
cur.execute("SELECT * FROM devices")
print(cur.fetchall())