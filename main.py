from enum import unique
from operator import add
from flask import Flask
from flask.wrappers import Request
from flask_sqlalchemy import SQLAlchemy
from flask.templating import render_template
from flask import request, redirect, url_for
from flask.helpers import flash
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash #for secure password
from flask_login import login_user, logout_user, login_manager


#to connect to server for db 
local_server = True
app =Flask(__name__)
app.secret_key = 'pradnya_haval'
#only for the first time- 1st it will take username then password then give localhost and db name
#'mysql://username:password@localhost/onlinebookstore'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/onlinebookstore'
db = SQLAlchemy(app)

#db models
class User(UserMixin ,db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    balance = db.Column(db.Float)

class Books(db.Model):
    bookId = db.Column(db.Integer, primary_key=True)
    bookName = db.Column(db.String(100), nullable=False)
    bookAuther = db.Column(db.String(100), nullable=False)
    bookCategory = db.Column(db.String(100), unique=True, nullable=False)
    bookPrice = db.Column(db.Float, nullable=False)
    bookPresent = db.Column(db.String(3), nullable=False)


#functions of each page
@app.route('/')
def base():
    """try:
        Books.query.all()
        return "DB is connected!"
    except:
        return "Database is not connected."""
    return render_template('base.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
        return render_template('login.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        email =  request.form.get('email')
        phone =  request.form.get('phone')
        address = request.form.get('address')
        password = request.form.get('password')
        print(password)
        encript_password = generate_password_hash(password)
        print(password)
        user = User.query.filter_by(email=email).first() #to check if email already present
        phone = User.query.filter_by(phone=phone).first()
        
        if user :
            print("email already exits!")
            flash(f"email already exists!", category="danger") # f for string
            return render_template('/signin.html')
        elif phone:
            print("phone number already exists!")
            flash(f"phone number already exists!", category="danger") # f for string
            return render_template('/signin.html')
        else:
            new_user = db.engine.execute(f"INSERT INTO `user` (`username`, `email`, `phone`, `address`, `password`) VALUES ('{username}', '{email}', '{phone}', '{address}', '{encript_password}')")
            flash(f"Account created successfuly! Please login to explore new books", category="success") 
            return render_template('login.html')
    return render_template('signin.html')

@app.route('/logout')
def logout():
    return render_template('login.html')

@app.route('/purchased_books')
def purchased_books():
    return render_template('purchased_books.html')

if __name__ == '__main__':
    app.run(debug=True)