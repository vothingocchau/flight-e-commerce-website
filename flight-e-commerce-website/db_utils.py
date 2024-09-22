import mysql.connector
from flask import Flask
import hashlib
app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="bomehuytai1",
    database="quan_ly_chuyen_bay"
)
cursor = db.cursor()
def authenticate_user(username, password):
    query = "SELECT * FROM nguoi_dung WHERE ma_nguoi_dung = %s AND mat_khau = %s"
    cursor.execute(query, (username, hashlib.md5(password.encode()).hexdigest()))
    user = cursor.fetchone()
    return user