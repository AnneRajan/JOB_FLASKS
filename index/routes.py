import os
import secrets
from PIL import Image

from flask import Flask, render_template,flash, url_for, request, session, redirect, jsonify
from index.forms import RegistrationForm, LoginForm, UpdateForm
from index.models import User
from index import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from tensorflow.keras.optimizers import Adam
import numpy as np
import tensorflow as tf
import keras
from keras.models import load_model




model = load_model('Job_Role_model.h5')
graph = tf.get_default_graph()

@app.route("/")
def home():
    return render_template('index.html');
    
 
    
@app.route("/main")
def main():
    return render_template('main.html')

    
@app.route("/resume")
def resume():
    return render_template('resume.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(firstname = form.firstname.data, lastname = form.lastname.data, college = form.college.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        name = form.firstname.data
        s    = 'Account created for ' + name + ' successfully !'
        flash(s,'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password.','danger')
    return render_template('login.html', form=form)

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex   = secrets.token_hex(8)
    _, f_ext     = os.path.splitext(form_picture.filename)
    picture_fn   = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size  = (125,125)
    i            = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateForm()
    if form.validate_on_submit():
        if form.picture.data :
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.firstname = form.firstname.data
        current_user.lastname  = form.lastname.data
        current_user.college   = form.college.data
        current_user.email     = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('jobprofile'))
    elif request.method == 'GET':
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.college.data = current_user.college
        form.email.data = current_user.email
    img_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', img_file=img_file, form=form)

@app.route("/jobprofile")
def jobprofile():
    return render_template('jobprofile.html')

@app.route('/prediction',methods=['POST'])
def prediction():

    os          = request.form["os"]
    aoa         = request.form["aoa"]
    pc          = request.form["pc"]
    se          = request.form["se"]
    cn          = request.form["cn"]
    ma          = request.form["ma"]
    cs          = request.form["cs"]
    hac         = request.form["hac"]
    interest    = request.form["interest"]
    cert        = request.form["cert"]
    personality = request.form["personality"]
    mantech     = request.form["mantech"]
    leadership  = request.form["leadership"]
    team        = request.form["team"]
    selfab      = request.form["selfab"]

    myu = [77.00318789848731, 76.99831228903614, 77.07569696212026, 77.11301412676585, 76.9541817727216, 77.0150018752344, 77.060320040005, 5.002687835979497]
    sig = [10.071578660726848, 10.098653693844197, 10.137528173238477, 10.088164425588161, 10.018397202418788, 10.18533143324003, 10.095941558583263, 2.582645138598079]
    arr = [os,aoa,pc,se,cn,ma,cs,hac]

    for i in range(8):
        arr[i] = float(arr[i])
        arr[i] = (arr[i]- myu[i])/sig[i]

    inti     = [0,0,0,0,0,0,0,0,0,0,0,0,0]
    certi    = [0,0,0,0,0,0,0]

    if interest == "analyst":
        inti[0] = 1
    elif interest == "hadoop":
        inti[1] = 1
    elif interest == "cloud":
        inti[2] = 1
    elif interest == "data":
        inti[3] = 1
    elif interest == "hacking":
        inti[4] = 1
    elif interest == "management":
        inti[5] = 1
    elif interest == "networks":
        inti[6] = 1
    elif interest == "programming":
        inti[7] = 1
    elif interest == "security":
        inti[8] = 1
    elif interest == "software":
        inti[9] = 1
    elif interest == "system":
        inti[10] = 1
    elif interest == "testing":
        inti[11] = 1
    elif interest == "web":
        inti[12] = 1

    if cert == "app":
        certi[0] = 1
    elif cert == "full":
        certi[1] = 1
    elif cert == "hadoop":
        certi[2] = 1
    elif cert == "security":
        certi[3] = 1
    elif cert == "machine":
        certi[4] = 1
    elif cert == "python":
        certi[5] = 1
    elif cert == "shell":
        certi[6] = 1

    for i in certi:
        arr.append(i)

    for i in inti:
        arr.append(i)

    if leadership == "yesl":
        arr.append(0)
        arr.append(1)
    else:
        arr.append(1)
        arr.append(0)

    if team == "yest":
        arr.append(0)
        arr.append(1)
    else:
        arr.append(1)
        arr.append(0)

    if personality == "extrovert":
        arr.append(1)
        arr.append(0)
    else:
        arr.append(0)
        arr.append(1)

    if selfab == "nos":
        arr.append(1)
        arr.append(0)
    else:
        arr.append(0)
        arr.append(1)

    if mantech == "man":
        arr.append(1)
        arr.append(0)
    else:
        arr.append(0)
        arr.append(1)


    print (arr)

    with graph.as_default():
        print("done in loop")
        y      = model.predict(np.array( [arr,]))
        result = np.where(y == np.amax(y))
        print(result[0])

    print("done1")

    if result[1]==[0]:
        print('Business Intelligence Analyst')
        return render_template('jobprofile.html', prediction_text='Business Intelligence')
        
    elif result[1]==[1]:
        print('Database Administrator')
        return render_template('jobprofile.html', prediction_text='Database Administrator')
        
    elif result[1]==[2]:
        print('Project Manager')
        return render_template('jobprofile.html', prediction_text='Project Manager')
        
    elif result[1]==[3]:
        print('Security Administrator')
        return render_template('jobprofile.html', prediction_text='Security Administrator')
        
    elif result[1]==[4]:
        print('Software Developer')
        return render_template('jobprofile.html', prediction_text='Software Developer')
        
    else:
        print('Technical Support')
        return render_template('jobprofile.html', prediction_text='Technical Support')
        

    print("done2")
