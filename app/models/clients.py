from flask import current_app, render_template, flash

from app import *
from hashlib import sha256
from datetime import datetime

from flask.ext.mail import Mail,Message
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship

import random
import string
import datetime
from hashlib import md5

class Client(db.Model):
    __tablename__ = 'client'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(75))
    major = db.Column(db.String(75))
    email = db.Column(db.String(75), unique=True)
    password = db.Column(db.String(75))
    bio = db.Column(db.TEXT)
    verified = db.Column(db.Boolean, default=False)
    stripe_customer_id = db.Column(db.String(200))



    def __init__(self, name, major, email, password, verified=False, stripe_customer_id=None):

        self.name = name
        self.major = major
        self.email = email
        self.password = sha256(password).hexdigest()

        self.verified = verified

        #self.send_verify_email()
        self.stripe_customer_id = stripe_customer_id



    def send_verify_email(self):
        for tok in self.tokens:
            db.session.delete(tok)

        db.session.commit()

        token = ''.join(random.SystemRandom().choice("ABCDEF0123456789") for _ in range(16))
        valid = False

        tok = None

        print " i am being caleeeeeeeeeeeeeeeeeeed"
        while not valid:
            try:
                tok = VerifyClientToken(token, self)

                db.session.add(tok)
                db.session.commit()

                valid = True
            except IntegrityError:
                pass
        print "passseddddddddddddddddd"
        email = render_template('AUBOOST/emails/verify.html', token=token, prefix=current_app.config.get('URL_PREFIX'))



        print "render email"
        try:


            message=Message("Welcome to AUBOOST",
                            recipients=[self.email]
            )


            message.html=(email)
            current_app.mail.send(message)

        except Exception as e:
            print str(e)
            print "-----------"
            flash(("flash_error", "Error sending verification email"))

    def reset_password(self):
        new_password = ''.join(random.SystemRandom().choice(string.uppercase + string.digits) for _ in xrange(10))

        try:
            new_hashed = sha256(new_password).hexdigest()

            email = render_template('AUBOOST/emails/reset_password.html', password=new_password, name=self.name)


            message=Message("AUBOOST account password reset",
                            recipients=[self.email]
            )


            message.html=(email)
            current_app.mail.send(message)

            self.password = new_hashed

            db.session.commit()
            return True
        except Exception as e:
            print str(e)
            print "-----------"
            flash(("flash_error", "Error sending password reset email"))

            return False

    def __repr__(self):
        return '<Client: %s>' % self.name

    @classmethod
    def is_authenticated(cls):
        return True

    @classmethod
    def is_active(cls):
        return True

    @classmethod
    def is_anonymous(cls):
        return False

    def get_id(self):
        return unicode(self.id)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)

    def numberOfRaters(self):
        return len(self.rated)


    def ratingOfUser(self):
        average=0
        for i in self.rated:
            average+=i.rating


        if len(self.rated)>0:
            return int(average*1.0/len(self.rated))

        return None

    def reviews(self):
        reviews=[]

        for i in self.reviewed:
            reviews.append({'review':i.review,'reviewer': i.reviewer})

        return reviews

    def messages_sent_to_me(self):

        messages={}
        for i in self.receiverMessage:
            try:
                messages[i.sender].append(i.message)
            except KeyError:
                messages[i.sender]=[]
                messages[i.sender].append(i.message)

        return messages

    def messages_sent_by_me(self):
        messages={}
        for i in self.senderMessage:
            try:
                messages[i.receiver].append(i.message)
            except KeyError:
                messages[i.receiver]=[]
                messages[i.receiver].append(i.message)

        return messages

    def getCourses(self):
        courses={}
        for course in self.courses:
            try:

                if str(course.course_number) not in courses[course.course_name]:
                    courses[course.course_name].append(str(course.course_number))
            except KeyError:
                courses[course.course_name]=[]
                courses[course.course_name].append(str(course.course_number))
        return courses
class VerifyClientToken(db.Model):
    __tablename__ = 'client_token'

    token = db.Column(db.String(75), primary_key=True)

    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    client = db.relationship('Client', backref='tokens')

    def __init__(self, token, client):
        self.token = token

        self.client = client
        self.client_id = client.id


class Messages(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.INTEGER, primary_key=True)
    senderID = db.Column(db.INTEGER,db.ForeignKey('client.id'))
    receiverID = db.Column(db.INTEGER,db.ForeignKey('client.id'))
    message = db.Column(db.TEXT)
    #time =db.Column(db.DateTime, default=datetime.datetime.utcnow())
    sender=relationship("Client", foreign_keys=senderID, backref="senderMessage")
    receiver=relationship("Client", foreign_keys=receiverID, backref="receiverMessage")

    #condition for primary key for two
    def __init__(self, receiverID, senderID,message):
        self.senderID=senderID
        self.receiverID=receiverID
        self.message=message

class Rating(db.Model):
    __tablename__ = 'ratings'


    rater_id = db.Column(db.INTEGER,db.ForeignKey('client.id'),primary_key=True)
    rated_id = db.Column(db.INTEGER,db.ForeignKey('client.id'),primary_key=True)
    rating = db.Column(db.INT)


    rater=relationship("Client", foreign_keys=rater_id, backref="rater")
    rated=relationship("Client", foreign_keys=rated_id, backref="rated")

    def __init__(self, rater_id, rated_id,rating):

        if int(rating) not in range(0,5):
            raise ValueError

        #if rated_id == rated_id:
        #    raise Exception

        self.rater_id=rater_id
        self.rated_id=rated_id
        self.rating=rating

class Reviews(db.Model):
    __tablename__ = 'reviews'


    reviewer_id = db.Column(db.INTEGER,db.ForeignKey('client.id'),primary_key=True)
    reviewed_id = db.Column(db.INTEGER,db.ForeignKey('client.id'),primary_key=True)
    review = db.Column(db.TEXT)


    reviewer=relationship("Client", foreign_keys=reviewer_id, backref="reviewer")
    reviewed=relationship("Client", foreign_keys=reviewed_id, backref="reviewed")

    def __init__(self, reviewer_id, reviewed_id,review):

        #if reviewed_id == reviewed_id:
        #    raise Exception

        self.reviewer_id=reviewer_id
        self.reviewed_id=reviewed_id
        self.review=review

class AvailableTimes(db.Model):
    __tablename__ = 'availableTimes'

    #id=db.Column(db.INTEGER,primary_key=True)
    user_id=db.Column(db.INTEGER,db.ForeignKey('client.id'),primary_key=True)
    start_date=db.Column(db.DATETIME,primary_key=True)
    end_date=db.Column(db.DATETIME,primary_key=True)

    client=relationship("Client", foreign_keys=user_id, backref="availableTimes")

    def __init__(self,user_id,start_date,end_date):
        self.user_id=user_id
        self.start_date=start_date
        self.end_date=end_date
'''
class BookedTimes(db.Model):
    __tablename__ = 'bookedTimes'
    #id=db.Column(db.Integer,primary_key=True)
    #tutor id
    user_id=db.Column(db.INTEGER,db.ForeignKey('client.id'),primary_key=True)
    time_id=db.Column(db.INTEGER,db.ForeignKey('availableTimes.id'),primary_key=True)

class Requests(db.Model):
    __tablename__ = 'Requests'

    #id=db.Column(db.Integer,primary_key=True)
    tutor_id=db.Column(db.INTEGER,db.ForeignKey('client.id'),primary_key=True)
    tutored_id=db.Column(db.INTEGER,db.ForeignKey('client.id'),primary_key=True)
    time_id=db.Column(db.INTEGER,db.ForeignKey('availableTimes.id'),primary_key=True)
    accepted=db.Column(db.Boolean)

    sender_request=relationship("Client", foreign_keys=tutored_id, backref="senderRequest")
    receiver_request=relationship("Client", foreign_keys=tutor_id, backref="receiverRequest")'''


class Courses(db.Model):
    __tablename__ = 'courses'

    course_name=db.Column(db.String(75),primary_key=True)
    course_number=db.Column(db.INTEGER,primary_key=True)
    user_id=db.Column(db.INTEGER,db.ForeignKey('client.id'),primary_key=True)

    user=relationship("Client", foreign_keys=user_id, backref="courses")

    def __init__(self, user_id, course_name,course_number):
        #if reviewed_id == reviewed_id:
        #    raise Exception

        self.user_id=user_id
        self.course_name=course_name.upper().strip()
        self.course_number=course_number

    @classmethod
    def getCourses(cls):
        courses={}
        for course in db.session.query(cls).all():
            try:
                if str(course.course_number) not in courses[course.course_name]:
                    courses[course.course_name].append(str(course.course_number))
            except KeyError:
                courses[course.course_name]=[]
                courses[course.course_name].append(str(course.course_number))
        return courses
    @classmethod
    def getTutorsAccordingToCourse(cls,course_name,course_number):
        users=[]
        for i in db.session.query(Courses).filter(Courses.course_name==course_name).filter(Courses.course_number==
                course_number):
            if i.user not in users:
                users.append(i.user)

        return users
class ReportedUsers(db.Model):
    __tablename__ = 'reportedUsers'

    id=db.Column(db.Integer,primary_key=True)
    reported_user_id=db.Column(db.INTEGER,db.ForeignKey('client.id'))
    reporting_user_id=db.Column(db.INTEGER,db.ForeignKey('client.id'))