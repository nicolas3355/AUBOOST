from flask import current_app, url_for
from flask.ext.wtf import Form
from flask import url_for
from wtforms.fields import StringField, HiddenField, SelectField, FieldList, IntegerField, FormField, PasswordField, BooleanField,TextAreaField
from wtforms import validators, ValidationError


import collections
import json



class Signin(Form):
    email = StringField('Email', [validators.Required(message="Email is required"), validators.Email(message="Enter a valid email")])
    password = PasswordField('Password', [validators.Required(message="Password is required"), validators.Length(min=6, message="Password is too short")])
    rememberme = BooleanField('Remember Me')
    next_url = HiddenField('next_url')

def valid_aub_email(form,field):
    if(field.data.strip()[-12:]=="mail.aub.edu"):
        pass
    else:
        raise ValidationError("not an aub email")
class Signup(Form):
    name = StringField('Name', [validators.Required(message="Name is required")])
    major = StringField('Major', [validators.Required(message="Major is required")])
    email = StringField('Email',[ validators.Required(message="Email is required"), validators.Email(message="Enter a valid email")])
    password = PasswordField('Password', [validators.Required(message="Password is required"), validators.Length(min=6, message="Password is too short")])
    password_confirmation = PasswordField('Confirm Password', [validators.Required(message="Password is required"), validators.Length(min=6, message="Password is too short")])
    
class Payment(Form):
    payment = StringField('Payment Method', [validators.Required(message="Name is required")])

class EditAccount(Form):
    name = StringField('Name', [validators.Required(message="Name is required")])
    major = StringField('Major', [validators.Required(message="Major is required")])
    email = StringField('Email', [validators.Required(message="Email is required"), validators.Email(message="Enter a valid email")])
    bio =  TextAreaField('Bio')

class AddCourses(Form):
    course_name = StringField('Course Name',[validators.Required(message="Course Name is required"),validators.Length(min=3,max=8,message="use the shortcut for courses like cmps..")])
    course_number= IntegerField('Course Number',[validators.Required(message="can't be empty")])

class DelCourse(Form):
    course_name_del = HiddenField('Course Name',[validators.Required(message="Course Name is required"),validators.Length(min=3,max=8,message="use the shortcut for courses like cmps..")])
    course_number_del= HiddenField('Course Number',[validators.Required(message="can't be empty")])

def validRating(form,field):

    if int(field.data) not in range(1,5):
        raise ValidationError("rating not in range")

class PasswordForm(Form):
    password = PasswordField('Password', [validators.Required(message="Password is required"), validators.Length(min=6, message="Password is too short")])
    password_confirmation = PasswordField('Confirm Password', [validators.Required(message="Password is required"), validators.Length(min=6, message="Password is too short")])

class submitRating(Form):
    rating=HiddenField(u'rate',[validRating])


class submitReview(Form):
    review=StringField(u'reviewLabel')

class ReportEmailForm(Form):
    email = StringField('Email', [validators.Required(message="Email is required"), validators.Email(message="Enter a valid email")])

class CouponsForm(Form):
    coupon = StringField('Coupon Code', [validators.Required(message="Coupon is required")])

class PasswordRecovery(Form):
    email = StringField('Email', [validators.Required(message="Email is required"), validators.Email(message="Enter a valid email")])

