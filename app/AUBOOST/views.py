from app import db
from flask import render_template, redirect, url_for, request, flash, Blueprint, current_app
from flask.ext.login import login_required, current_user
from hashlib import sha256
from sqlalchemy import exc
from app.models.clients import Client, VerifyClientToken, Rating,Reviews,Courses,AvailableTimes

import datetime

import stripe

import forms


mod = Blueprint('AUBOOST', __name__, url_prefix='/AUBOOST')

@mod.before_request
@login_required
def restrict_to_users():
    pass

def check_verify_user():
    client = current_user
    if not client.verified:
        flash(('flash_warning', '__VERIFY__'))

@mod.route('/', methods=['POST', 'GET'])
def AUBOOST():
    check_verify_user()
    client = current_user

    courses=Courses.getCourses()
    if(courses==None):
        courses=[]

    users=[]



    return render_template('AUBOOST/AUBOOST.html', loggedIn=True, home_page=True,email=client.email,courses=courses,
                           users=users)
@mod.route('/<string:course>/<string:number>', methods=['POST', 'GET'])
def AUBOOST_tutors(course,number):
    check_verify_user()
    client = current_user

    print Courses.getCourses()
    print Courses.getCourses()

    courses=Courses.getCourses()
    if(courses==None):
        courses=[]
    print courses
    users=Courses.getTutorsAccordingToCourse(course,number)



    return render_template('AUBOOST/AUBOOST.html', loggedIn=True, home_page=True,email=client.email,courses=courses,
                           users=users)

@mod.route("/verify/<string:token>", methods=['POST', 'GET'])
def verify(token):
    tok = VerifyClientToken.query.get_or_404(token)

    if tok.client.id == current_user.id:
        tok.client.verified = True

        db.session.delete(tok)
        db.session.commit()
        
        flash(("flash_notification", 'Account has been verified'))

    return redirect(url_for('AUBOOST.AUBOOST'))


@mod.route("/send_verify", methods=['POST', 'GET'])
def send_verify():
    client = current_user
    client.send_verify_email()
    return redirect(url_for('AUBOOST.AUBOOST'))

@mod.route('/account/', methods=['POST', 'GET'])
def account():
    #stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    form = forms.EditAccount()
    password_form = forms.PasswordForm()
    payment_form = forms.Payment()
    courses_form = forms.AddCourses()
    delCourse_form=forms.DelCourse()
    client = current_user
    
    flag = True

    if request.method == 'POST' and form.validate_on_submit():
        client.name = form.name.data
        client.major = form.major.data.upper()
        client.bio=form.bio.data
        if not client.email == form.email.data:        
            client.email = form.email.data
            client.verified = False
            check_verify_user()
            flag = False

        try:
            db.session.commit()
            
            flash(("flash_notification", "Success."))

            client.send_verify_email()
        except exc.IntegrityError:
            db.session.rollback()
            db.session.flush()
            flash(("flash_error", 'Duplicated Email'))
        except Exception as e:
            flash(("flash_error", str(e)))

    if flag:
        check_verify_user()

    form.name.data = client.name
    form.email.data = client.email
    form.major.data = client.major.upper()
    form.bio.data = client.bio
    payment = 'Not Set Yet'
    if not client.stripe_customer_id is None:
        customer = stripe.Customer.retrieve(client.stripe_customer_id)

        card = customer['sources']['data'][0]
        payment = card['brand']+' - **** **** **** '+card['last4']

    payment_form.payment.data = payment

    #invoices = getInvoices(client)
    invoices=[]

    return render_template('AUBOOST/account.html', loggedIn=True, form=form, password_form=password_form,
        payment_form=payment_form, invoices=invoices, email=client.email,bio=client.bio,courses_form=courses_form,
        delCourse_form=delCourse_form,account_page=True ,courses=client.courses)

@mod.route('/account_courses', methods=['POST'])
def account_courses():
    form = forms.EditAccount()
    payment_form = forms.Payment()
    delCourse_form=forms.DelCourse()
    password_form = forms.PasswordForm()
    courses_form = forms.AddCourses()


    print courses_form.validate_on_submit()
    if request.method == 'POST' and courses_form.validate_on_submit():
        try:
            course=Courses(current_user.id,courses_form.course_name.data,courses_form.course_number.data)
            db.session.add(course)
        except Exception as e:
            flash(("flash_error", str(e)))
        try:
            db.session.add(course)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            db.session.flush()
            flash(("flash_error", 'You already added this course'))
        except Exception as e:
            flash(("flash_error", str(e)))


    client = current_user
    check_verify_user()




    form.name.data = client.name
    form.email.data = client.email
    form.major.data = client.major.upper()

    payment = 'Not Set Yet'
    if not client.stripe_customer_id is None:
        customer = stripe.Customer.retrieve(client.stripe_customer_id)

        card = customer['sources']['data'][0]
        payment = card['brand']+' - **** **** **** '+card['last4']

    payment_form.payment.data = payment

    #invoices = getInvoices(client)
    invoices=[]
    return render_template('AUBOOST/account.html', loggedIn=True, form=form, password_form=password_form,
        payment_form=payment_form, invoices=invoices, email=client.email,bio=client.bio,courses_form=courses_form,
        delCourse_form=delCourse_form,account_page=True ,courses=client.courses)

@mod.route('/account_password', methods=['POST'])
def account_password():
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    form = forms.EditAccount()
    payment_form = forms.Payment()
    password_form = forms.PasswordForm()
    courses_form = forms.AddCourses()
    delCourse_form=forms.DelCourse()

    client = current_user
    check_verify_user()
    if request.method == 'POST' and password_form.validate_on_submit():
        if not password_form.password.data == password_form.password_confirmation.data:
            password_form.errors['password_confirmation'] = ['Passwords Don\'t Match']

        else:
            client.password = sha256(password_form.password.data).hexdigest()
            try:
                db.session.commit()
                
                flash(("flash_notification", "Success."))
            except Exception as e:
                flash(("flash_error", str(e)))



    form.name.data = client.name
    form.email.data = client.email
    form.major.data = client.major.upper()

    payment = 'Not Set Yet'
    if not client.stripe_customer_id is None:
        customer = stripe.Customer.retrieve(client.stripe_customer_id)

        card = customer['sources']['data'][0]
        payment = card['brand']+' - **** **** **** '+card['last4']

    payment_form.payment.data = payment

    #invoices = getInvoices(client)
    invoices=[]

    return render_template('AUBOOST/account.html', loggedIn=True, form=form, password_form=password_form,
        payment_form=payment_form, invoices=invoices, email=client.email,bio=client.bio,courses_form=courses_form,
        delCourse_form=delCourse_form,account_page=True ,courses=client.courses)


@mod.route("/profile/<string:user_email>",methods=['POST','GET'])
def profile(user_email):


    form_rating=forms.submitRating()
    form_review=forms.submitReview()
    user=db.session.query(Client).filter(Client.email==user_email).one()

    owner=False
    if user==current_user:
        owner=True

    return render_template('AUBOOST/profile.html',user=user,email=user_email,loggedIn=True,profile_page=True,owner=owner
                           ,form_rating=form_rating,form_review=form_review,courses=user.getCourses())

@mod.route("/delCourse/",methods=['POST'])
def delCourse():
    client=current_user
    delCourse_form=forms.DelCourse()
    noException=True
    if request.method == 'POST' and delCourse_form.validate_on_submit():
        course_name=delCourse_form.course_name_del.data
        course_number=delCourse_form.course_number_del.data
        try:
            course=db.session.query(Courses).filter(Courses.course_name==course_name,
                                                    Courses.course_number==course_number,
                                                    Courses.user_id==client.id).delete()
            db.session.commit()
        except Exception as e:
            noException=False
            db.session.rollback()
            db.session.flush()
            print str(e)
            flash(("flash_error","error deleting course"))
    if noException:
        flash(("flash_notification","deleted the course successfully"))
    return redirect(url_for('AUBOOST.account'))
@mod.route("/rate/<string:user_email>",methods=['POST'])
def rate(user_email):
        form =forms.submitRating()
        person_being_rated=db.session.query(Client).filter(Client.email==user_email).one()

        rating = form.rating.data
        print form.validate_on_submit()
        flag=False
        rating_himself=False
        if request.method == 'POST' and form.validate_on_submit():
            flag=True
            id_of_rater=current_user.id
            id_person_being_rated=person_being_rated.id
            #db.session.query(Rating).filter_by(reviewer_id=1,reviewed_id=1).one()
            if id_of_rater==id_person_being_rated:
                rating_himself=True
                flash(("flash_error", "Are you rating yourself?"))
            try:
                if(not rating_himself):
                    rate=Rating(id_of_rater,id_person_being_rated,rating)
                    db.session.add(rate)
                    db.session.commit()
            except Exception as e:

                flash(("flash_error", "Didn't you rate before?"))
                print str(e)
                return redirect(url_for('AUBOOST.profile',user_email=user_email))
        if flag and not rating_himself:
            flash(("flash_notification", "Successfully added rating."))
        else:
            flash(("flash_error", "Error Setting rating. you probably already rated"))

        return redirect(url_for('AUBOOST.profile',user_email=user_email))


@mod.route("/review/<string:user_email>",methods=['POST','GET'])
def review(user_email):
    person_being_reviewed=db.session.query(Client).filter(Client.email==user_email).one()
    form =forms.submitReview()
    review = form.review.data
    if(person_being_reviewed!= None and review!=None):
        id_of_reviewer=current_user.id
        id_person_being_rated=person_being_reviewed.id
        #db.session.query(Rating).filter_by(reviewer_id=1,reviewed_id=1).one()

        review_person=Reviews(id_of_reviewer,id_person_being_rated,review)
        try:
            db.session.add(review_person)
            db.session.commit()
        except Exception as e:
            flash(("flash_error", "Error Submiting review, you are allowed with one review"))
            print str(e)
            return redirect(url_for('AUBOOST.profile',user_email=user_email))

    flash(("flash_notification", "Successfully submited review."))
    return redirect(url_for('AUBOOST.profile',user_email=user_email))

@mod.route("/conversations",methods=['POST','GET'])
def conversations():
    user=current_user
    return render_template('AUBOOST/conversations.html',loggedIn=True,email=user.email,conversations_page=True,
                           messages_to_me=user.messages_sent_to_me(),messages_by_me=user.messages_sent_by_me())

@mod.route("/schedule",methods=['POST','GET'])
def schedule():

    #add time slot
    if request.method == 'POST':

        try:
            startDate = request.form.getlist('start')[0][4:24]
            endDate = request.form.getlist('end')[0][4:24]
            print startDate
            print endDate
            startDate_datetime=datetime.datetime.strptime(startDate,"%b %d %Y %H:%M:%S")
            endDate_datetime=datetime.datetime.strptime(endDate,"%b %d %Y %H:%M:%S")
            db.session.add(AvailableTimes(current_user.id,startDate_datetime,endDate_datetime))
            db.session.commit()

        except Exception as e:
            flash(("flash_error","error adding time slot"))
            db.session.rollback()
            db.session.flush()
            print str(e)


    flash(("flash_warning", "We don't support mobile at the time."))
    return render_template('AUBOOST/schedule.html',loggedIn=True,schedule_page=True,email=current_user.email)
'''
@mod.route("/account_payment", methods=['POST'])
def account_payment():
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

    client = current_user
    token = request.form.get('stripeToken', None)

    if token is None:
        return abort(404)

    customer_id = client.stripe_customer_id
    if customer_id is None:
        try:
            token = request.form['stripeToken']

            customer = stripe.Customer.create(
                source=token,
                email=client.email
            )

            client.stripe_customer_id = customer['id']
            db.session.commit()
        except stripe.error.CardError as e:
            flash(("flash_error", "Error Updating your card."))
            print str(e)

        except DatabaseError as e:
            flash(("flash_error", "Error Updating your details in database."))
            print str(e)

    else:
        try:
            customer = stripe.Customer.retrieve(customer_id)

            old_card = customer['sources']['data'][0]['id']
            customer.sources.create(source=token)

            customer.sources.retrieve(old_card).delete()
        except stripe.error.CardError as e:
            flash(("flash_error", "Error Updating your card<br> Old Card will be used."))
            print str(e)

    return redirect(url_for('AUBOOST.account'))





@mod.route("/manage_subscription/<int:report_id>", methods=["POST", "GET"])
def charge_client(report_id):
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    api.init(current_app)

    client = current_user

    subscription = None
    for sub in client.subscriptions:
        if sub.report_id == report_id:
            subscription = sub

    if not subscription:
        return abort(404)

    if subscription.status == 'active':
        customer = stripe.Customer.retrieve(client.stripe_customer_id)
        customer.subscriptions.retrieve(subscription.stripe_subscription_id).delete()

        subscription.status = 'cancelled'
        today = datetime.date.today()
        if today.month == 12:
            today = datetime.date(day=1, month=1, year=today.year+1)
        else:
            today = datetime.date(day=1, month=today.month+1, year=today.year)

        subscription.end_date = datetime.datetime.combine(today, datetime.datetime.min.time())

        api.report_active(report_id, False)
        try:
            db.session.commit()
            subscription.send_unsubscribe_email()
        except Exception as e:
            flash(('flash_error', 'We failed to register changes in the database, please contact adminstrator.'))
            error_message = render_template('AUBOOST/emails/unsubscribe_error.html', dt=str(datetime.datetime.now()), client=client, report_id=report_id, subscription=subscription)
            log_error(error_message)

    else:
        customer_id = client.stripe_customer_id

        try:
            if customer_id is None:
                token = request.form['stripeToken']

                customer = stripe.Customer.create(
                    source=token,
                    email=client.email
                )

                customer_id = customer['id']

            plan_id=str(current_app.config['STRIPE_PLAN_ID'])

            trial_end = None
            if subscription.status == 'created':
                trial_days = current_app.config['STRIP_TRIAL_PERIOD']
                today = datetime.date.today()
                today = today + datetime.timedelta(days=trial_days)
                trial_end = calendar.timegm(today.timetuple())

            customer = stripe.Customer.retrieve(customer_id)
            sub = customer.subscriptions.create(
                    plan=plan_id,
                    trial_end=trial_end
                    )

            client.stripe_customer_id = customer_id

            subscription.status = 'active'
            subscription.stripe_subscription_id = sub['id']
            subscription.stripe_old_ids = subscription.stripe_old_ids + [sub['id']]

            now_date = datetime.datetime.now()
            subscription.start_date = now_date
            subscription.end_date = increment_by_month(now_date)

            api.report_active(report_id, True)
            try:
                db.session.commit()
                subscription.send_subscription_email(trial=current_app.config['STRIP_TRIAL_PERIOD'])
            except Exception as e:
                flash(('flash_error', 'You are subscribed. We failed to register changes in the database, please contact adminstrator.'))
                error_message = render_template('AUBOOST/emails/subscribe_error.html', dt=str(datetime.datetime.now()), client=client, report_id=report_id, subscription=subscription)
                log_error(error_message)

        except stripe.error.CardError as e:
            flash(("flash_error", "Error Subscribing Card got Rejected"))


    return redirect(url_for('AUBOOST.report', report_id=report_id))




@mod.route("/subscribe_email/<int:report_id>", methods=['POST'])
def subscribe_email(report_id):
    client = current_user

    subscription = None
    for sub in client.subscriptions:
        if sub.report_id == report_id:
            subscription = sub

    if not subscription:
        return abort(404)

    email = request.form.get('email', '').strip()
    REGEX = re.compile('[^@]+@[^@]+\.[^@]+')

    if REGEX.match(email) and (not email in subscription.delivery_addresses):
        subscription.delivery_addresses = subscription.delivery_addresses + [email]

        db.session.commit()

        return "done"

    else:
        return "fail"

@mod.route("/delete_email/<int:report_id>", methods=['POST'])
def delete_email(report_id):
    client = current_user

    subscription = None
    for sub in client.subscriptions:
        if sub.report_id == report_id:
            subscription = sub

    if not subscription:
        return abort(404)

    email = request.form.get('email', '').strip()

    if email in subscription.delivery_addresses:
        if len(subscription.delivery_addresses) == 1:
            return "LAST EMAIL"

        subscription.delivery_addresses = [e for e in subscription.delivery_addresses if e != email]

        db.session.commit()

    return ""

@mod.route("/coupon/<int:report_id>", methods=['POST'])
def coupon(report_id):
    client = current_user

    subscription = None
    for sub in client.subscriptions:
        if sub.report_id == report_id:
            subscription = sub

    if not subscription:
        return abort(404)

    couponsForm = forms.CouponsForm()
    if couponsForm.validate_on_submit():
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

        try:
            coupon_code = couponsForm.coupon

            if client.stripe_customer_id is None:
                flash(("flash_error", "Please set payment method first"))

            elif subscription.status != 'active':
                flash(("flash_error", "Please subscribe to the report first"))

            else:
                customer = stripe.Customer.retrieve(client.stripe_customer_id)
                sub = customer.subscriptions.retrieve(subscription.stripe_subscription_id)
                sub.coupon = coupon_code.data
                sub.save()

                flash(("flash_notification", "Coupon Applied."))
        except Exception as e:
            flash(("flash_error", "Invalid Coupon."))

    return redirect(url_for('AUBOOST.report', report_id=report_id))



def increment_by_month(sourcedate):
    month = sourcedate.month
    year = sourcedate.year + month / 12
    month = month % 12 + 1

    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    new_date = datetime.date(year, month, day)

    return datetime.datetime.combine(new_date, datetime.datetime.min.time())

def getInvoices(client):
    if client.stripe_customer_id is None:
        return []

    try :
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

        invoices = stripe.Invoice.all(customer=client.stripe_customer_id)['data']
        return_invoices = []

        count = 0
        for invoice in invoices:
            invoice = invoice['lines']['data'][0]

            if count == 10:
                break

            sub_id = invoice['id']
            amount = invoice['amount'] / 100.0
            currency = invoice['currency']
            time_start = invoice['period']['start']
            time_start = datetime.datetime.fromtimestamp(time_start).strftime('%Y-%m-%d')

            sub_name = ""
            for sub in client.subscriptions:
                if sub_id in sub.stripe_old_ids:
                    sub_name = sub.report_name
                    break

            count += 1

            trial = ''
            if amount == 0:
                trial = '(trial period)'
            return_invoices.append({'name': sub_name, 'amount':amount, 'date':time_start, 'trial': trial})

        return return_invoices
    except Exception as e:
        flash(("flash_error", str(e)))
        return []
'''
