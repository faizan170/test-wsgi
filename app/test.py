from flask import Flask, jsonify, request, session
import sqlite3
from sqlite3 import Error
from datetime import datetime
database = "products.db"

try:
    conn = sqlite3.connect(database, check_same_thread=False)
except Error as e:
    print(e)

cur = conn.cursor()
'''
pType = '"%d-%m-%Y"'
for row in cur.execute('select COUNT(product_id) as pid, strftime(' + pType + ', product_date) as month_year from products group by strftime(' + pType + ', product_date)'):
    print(row)
'''

#cur.execute("ALTER TABLE users ADD user_approved INTEGER")
pwd = 'admin447722'
pwd = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())
cur.execute("UPDATE users SET user_name = ?, user_email = ?, user_password=? WHERE user_id = 1", ('Admin', 'admin@ffinder.com', 'admin449922'))
conn.commit()

for row in cur.execute("SELECT * FROM users"):
    print(row)