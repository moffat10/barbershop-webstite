from flask import Flask,render_template,request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,login_required,logout_user,login_user,UserMixin,current_user
import os

app=Flask(__name__)
app.config['SECRET_KEY']='saystheking'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['UPLOAD_FOLDER']='static/files'
db=SQLAlchemy(app)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50),unique=True,nullable=False)
    phone_number=db.Column(db.Integer,unique=True,nullable=False)
    password=db.Column(db.String(50),nullable=False)
    appointments=db.relationship('Appointments')
    
    def is_active(self):
        return True

class Appointments(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    style=db.Column(db.String(50),nullable=False)
    customer_name=db.Column(db.String(50),unique=True,nullable=False)
    customer_phone=db.Column(db.String(50),unique=True,nullable=False)
    date=db.Column(db.String(50),nullable=False)
    time=db.Column(db.String(50),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))


@app.route("/")
def home():
    return render_template('home.html')

@app.route('/templates/create_account',methods=['GET','POST'])
def create_account():
    if request.method=='POST':
        username=request.form['username']
        phone_number=request.form['phone_number']
        password=request.form['password']
        hashed_password=generate_password_hash(password)
        new_user=User(username=username,password=hashed_password,phone_number=phone_number)
        existing_username=User.query.filter_by(username=username).first()
        existing_phone=User.query.filter_by(phone_number=phone_number).first()
        if existing_username:
            flash('username already exists','danger')
            return redirect(url_for('create_account'))
        elif existing_phone:
            flash('phone number already in use','danger')
            return redirect(url_for('create_account'))
        else:
            db.session.add(new_user)
            db.session.commit()
            flash('account created sucessfully','success')
            return redirect(url_for('login'))
    return render_template('create_account.html')
@app.route('/templates/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        user=User.query.filter_by(username=username).first()

        if user:
           if check_password_hash(user.password,password):
                login_user(user)
                return redirect(url_for('dashboard')) 
        else:
            flash('Wrong username or password, please check and try again!','danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('logged out')
    return redirect(url_for('login'))

@app.route('/templates/booking',methods=['GET','POST'])
@login_required
def booking():
    if request.method=='POST':
        date=request.form['date']
        time=request.form['time']
        style=request.form['style']
        user_id=current_user.id
        customer_name=current_user.username
        customer_phone=current_user.phone_number
        new_appointment=Appointments(date=date,time=time,style=style,user_id=user_id,customer_name=customer_name,customer_phone=customer_phone)
        db.session.add(new_appointment)
        db.session.commit()
        flash('booked sucessfully','success')
        return redirect(url_for('dashboard'))
    return render_template('booking.html')


@app.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
    my_appointments=Appointments.query.filter_by(user_id=current_user.id)
    return render_template('dashboard.html',my_appointments=my_appointments)

@app.route('/templates/cut_style')
def cut_style():
    return render_template('cut_style.html')
@app.route('/templates/cut_style')
def cat_return():
    return render_template('cut_style.html')
@app.route('/templates/admin')
def admin():
    all_appointments=Appointments.query.all()
    return render_template('admin.html',all_appointments=all_appointments)
if __name__=='__main__': 
    with app.app_context():
        db.create_all()   
    app.run(host='0.0.0.0',debug=True)