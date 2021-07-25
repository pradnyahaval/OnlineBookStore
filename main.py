from enum import unique
from operator import add
from flask import Flask
from flask.wrappers import Request
from flask_sqlalchemy import SQLAlchemy
from flask.templating import render_template
from flask import request, redirect, url_for
from flask.helpers import flash
from werkzeug.security import generate_password_hash, check_password_hash #for password security
from flask_login import UserMixin, login_user, logout_user, login_manager, LoginManager, login_required, current_user


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
    if not User.is_authenticated:
        return render_template('login.html')
    else:
        return render_template('home.html', username=current_user.username)
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
            return redirect(url_for('home'))
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
        print(user, check_phone)
        
        if user:
            print("email already exits!")
            flash(f"email already exists!", category="warning") # f for string
            return render_template('login.html')
        if check_phone:
            print("phone number already exists!")
            flash(f"phone number already exists!", category="warning")
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

#purchased books
@app.route('/purchased_books')
def purchased_books():
    return render_template('purchased_books.html')

if __name__ == '__main__':
    app.run(debug=True)
