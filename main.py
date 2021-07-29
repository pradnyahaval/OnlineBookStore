from enum import unique
from operator import add
from flask import Flask
from flask.wrappers import Request
from flask_sqlalchemy import SQLAlchemy
from flask.templating import render_template, render_template_string
from flask import request, redirect, url_for
from flask.helpers import flash
from werkzeug.security import generate_password_hash, check_password_hash #for password security
from flask_login import UserMixin, login_user, logout_user, login_manager, LoginManager, login_required, current_user
from datetime import datetime

date = datetime.now()

#to connect to server for db 
local_server = True
app =Flask(__name__)
app.secret_key = 'pradnya_haval'
#only for the first time- 1st it will take username then password then give localhost and db name
#'mysql://username:password@localhost/onlinebookstore'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/onlinebookstore'
db = SQLAlchemy(app)

#for user access
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#db models
class User(UserMixin ,db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    balance = db.Column(db.Float)

    #to solve the error of login
    @property
    def id(self):
        return self.userid  

class Purchased_books(db.Model):
    purchased_id = db.Column(db.Integer, primary_key=True)
    book_name = db.Column(db.String(100), nullable=False)
    bookPrice = db.Column(db.Float, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)

class Books(db.Model):
    bookId = db.Column(db.Integer, primary_key=True)
    bookName = db.Column(db.String(100), nullable=False)
    bookAuther = db.Column(db.String(100), nullable=False)
    bookCategory = db.Column(db.String(100), unique=True, nullable=False)
    bookPrice = db.Column(db.Float, nullable=False)
    bookCount = db.Column(db.Integer, nullable=False)

class Pending_balance(db.Model):
    pid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    balance =  db.Column(db.Float, nullable=False)
    bank_ref_no =  db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(50), nullable=False)


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

#login
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email =  request.form.get('email')
        password = request.form.get('password')
        print(email, password)
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f"Logged in successfully!", category="success")
            return redirect(url_for('books'))
        else:
            flash(f"email or password is invalid!", category="danger")
            return render_template('login.html')
        
    return render_template('login.html')

#signin
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        email =  request.form.get('email')
        phone =  request.form.get('phone')
        address = request.form.get('address')
        password = request.form.get('password')
        print(username, email, phone, address, password)
        
        user = User.query.filter_by(email=email).first() #to check if email already present
        check_phone = User.query.filter_by(phone=phone).first()
        
        if user:
            print("email already exits!")
            flash(f"email already exists!", category="danger") # f for string
            return render_template('login.html')
        if check_phone:
            print("phone number already exists!")
            flash(f"phone number already exists!", category="danger")
            return render_template('login.html')

        hashed_password = generate_password_hash(password)
        
        new_user = db.engine.execute(f"INSERT INTO `user` (`username`, `email`, `phone`, `address`, `password`) VALUES ('{username}', '{email}', '{phone}', '{address}', '{hashed_password}')")
        flash(f"Account created successfuly! Please login to explore new books", category="success") 
        return render_template('login.html')

    return render_template('signin.html')

#logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(f"You are logged out.", category="success")
    return redirect(url_for('login'))

#books list
@app.route('/books', methods=['GET', 'POST'])
@login_required
def books():
    if not User.is_authenticated:
        return render_template('login.html')
    else:
        query = db.engine.execute(f"SELECT * FROM `books`")
        return render_template('books.html', books=query)
        """if request.method == 'POST':
            flash(f"Books have been purchased!", category="success")            
        return render_template('purchased_books.html')"""
    #return render_template('home.html')

#add new books => for admin
@app.route('/add_books', methods=['GET', 'POST'])
@login_required
def add_books():
    if request.method == 'POST':
        bookname= request.form.get("bookname")
        auther = request.form.get("auther")
        category = request.form.get ("category")
        price = request.form.get("price")
        copies = request.form.get("copies")
        new_book = db.engine.execute(f"INSERT INTO `books` (`bookName`, `bookAuther`, `bookCategory`, `bookPrice`, `bookCount`) VALUES ('{bookname}', '{auther}', '{category}', '{price}', '{copies}')")
        flash(f"book details are added.", category="success")
        return render_template('add_books.html')
    return render_template('add_books.html')

#purchased books
@app.route('/purchased_books')
@login_required
def purchased_books():
    user_email = current_user.email
    query = db.engine.execute(f"SELECT * FROM `purchased_books` WHERE email='{user_email}'")
    if query:
        return render_template('purchased_books.html', purchased_books=query)
    
    return render_template('purchased_book.html')

#user balance => for user
@app.route('/user_balance')
@login_required
def user_balance():
    return render_template('user_balance.html')

#add balance =>for admin
@app.route('/add_balance')
@login_required
def add_balance():
    pending_balance = db.engine.execute(f"SELECT * FROM `pending_request`")
    return render_template('add_balance.html', pending_balance=pending_balance)

#pending_balance
@app.route('/pending_balance', methods=['GET', 'POST'])
def pending_balance():
    user_balance = current_user.balance
    if request.method == 'POST':
        new_balance = request.form.get('new_balance')
        bank_ref_no = request.form.get('bank_ref_no')
       
        update_balance = db.engine.execute(f"INSERT INTO `pending_request` (`username`, `email`, `balance`, `bank_ref_no`, `date`) VALUES ('{current_user.username}', '{current_user.email}', '{new_balance}', '{bank_ref_no}', '{str(date)}')")
        flash(f"Your balance will be updated shortly.", category="success")
    return render_template('user_balance.html', user_balance=user_balance)

#profile
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


if __name__ == '__main__':
    app.run(debug=True)
