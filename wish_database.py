#creating database "wishlist"

import sqlite3 as sql
conn = sql.connect("wishlist.db")
c = conn.cursor()

#creating users TABLE:
c.execute('''CREATE TABLE IF NOT EXISTS users(
user_id INTEGER PRIMARY KEY AUTOINCREMENT,
login TEXT NOT NULL,
password TEXT NOT NULL,
email TEXT NOT NULL,
name TEXT NOT NULL,
surname TEXT NOT NULL,
adress_id INTEGER NOT NULL)''')

#creating adress TABLE:
c.execute('''CREATE TABLE IF NOT EXISTS adress(
adress_id INTEGER PRIMARY KEY AUTOINCREMENT,
zip_code TEXT NOT NULL,
city TEXT NOT NULL,
street TEXT NOT NULL,
number TEXT NOT NULL
)''')

#creating wishlists TABLE:
c.execute('''CREATE TABLE IF NOT EXISTS wishlists(
wishlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER NOT NULL,
wish TEXT NOT NULL
)''')

#creating groups TABLE:
c.execute('''CREATE TABLE IF NOT EXISTS groups(
group_id INTEGER PRIMARY KEY AUTOINCREMENT,
group_name TEXT NOT NULL
)''')

#creating connections TABLE:
c.execute('''CREATE TABLE IF NOT EXISTS connections(
connection_id INTEGER PRIMARY KEY AUTOINCREMENT,
group_id INTEGER NOT NULL,
wishlist_id INTEGER NOT NULL
)''')

#save
conn.commit()

#connection close
conn.close()
