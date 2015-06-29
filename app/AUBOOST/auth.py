"""
AUTHENTICATION
"""
from app import db, app
from app.models.clients import Client, VerifyClientToken

from flask import render_template, redirect, url_for, request, flash, Blueprint, jsonify, abort, current_app
from flask.ext.login import (LoginManager, current_user, login_required,
                             login_user, logout_user, UserMixin,
                             confirm_login, fresh_login_required, #set_login_view)
                             )

from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from hashlib import sha256

import forms

mod = Blueprint('AUBOOST_auth', __name__, url_prefix='/AUBOOST')

login_manager = LoginManager()
login_manager.login_message = ('flash_warning', 'PLEASE LOG IN TO ACCESS THIS PAGE.')
login_manager.login_view = 'AUBOOST_auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(client):
    return Client.query.get(client)


@mod.route('/signup', methods=['POST', 'GET'])
def signup():
    form = forms.Signup()
    
    if request.method == 'POST' and form.validate_on_submit():
        if not form.password.data == form.password_confirmation.data:
            form.password.data = ''
            form.password_confirmation.data = ''
        
            form.errors['password_confirmation'] = ['Passwords Don\'t Match']
            return render_template('AUBOOST/signup.html', form=form)

        if not Client.query.filter(Client.email==form.email.data).first() is None:
            form.errors['email'] = ['Email Already in use']            
            return render_template('AUBOOST/signup.html', form=form)

        client = Client(form.name.data, form.major.data.upper(), form.email.data, form.password.data)

        try:
            db.session.add(client)
            db.session.commit()
            
            login_user(client)
            flash(("flash_notification", "Signed Up."))

            return redirect(url_for('AUBOOST.AUBOOST'))
        except IntegrityError:
            flash(('flash_error', 'Duplicated Email'))
        except Exception as e:
            flash(('flash_error',str(e)))

    return render_template('AUBOOST/signup.html', form=form)


@mod.route('/login', methods=['POST', 'GET'])
def login():
    form = forms.Signin()

    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        password = sha256(password).hexdigest()

        remember_me = form.rememberme.data
        next_url = form.next_url.data
        print next_url

        client = Client.query.filter(and_(Client.email==email, Client.password==password)).first()
        if client and login_user(client, remember=remember_me):
            return redirect(next_url)
        else:
            flash(('flash_error', "Incorrect username or password"))

    form.next_url.data = request.args.get('next', url_for('AUBOOST.AUBOOST'))
    return render_template('AUBOOST/login.html', form=form, next=next)


@mod.route("/reset_password", methods=['POST', 'GET'])
def reset_password():
    form = forms.PasswordRecovery()

    if request.method == 'POST' and form.validate_on_submit():
        client = Client.query.filter(Client.email==form.email.data).first()
        if client is None:
            form.errors['email'] = ['Email Doesn\'t Exist']
            return render_template('AUBOOST/reset_password.html', form=form)

        if client.reset_password():
            flash(('flash_notification', 'Password Reset Email has been sent!'))
            return redirect(url_for('AUBOOST_auth.login'))

    return render_template('AUBOOST/reset_password.html', form=form)

@mod.route("/logout")
@login_required
def logout():
    logout_user()
    flash(("flash_notification", "Logged out."))
    return redirect(url_for("AUBOOST_auth.login"))





