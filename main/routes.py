from main import app, db, bcrypt, mail
from flask import redirect, render_template, url_for, request, flash, session
from main.models import User, Invite, Notification
from main.forms import LoginForm, RegistrationForm, BirthdayForm, WeddingForm, OtherForm, UpdateAccount
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime, date
from flask_mail import Message

@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    bform = BirthdayForm(request.form)
    wform = WeddingForm(request.form)
    oform = OtherForm(request.form)
    users = User.query.filter(User.name != current_user.name).all()
    accounts = db.session.execute('select count(id) as c from user').scalar()
    if bform.validate_on_submit() and request.method == 'POST':
        recipient = request.form.get('user')
        paragraph = "{}\'s {}th Birthday".format(bform.name.data, bform.birthday_no.data)
        heading = "Birthday Party"
        send_invite(recipient, bform, paragraph, heading)
        return redirect(url_for('dashboard'))
    elif wform.validate_on_submit() and request.method == 'POST':
        recipient = request.form.get('user')
        paragraph = "{} & {}\'s Wedding".format(wform.bride.data, wform.groom.data)
        heading = "Wedding Ceremony"
        send_invite(recipient, wform ,paragraph, heading)
        return redirect(url_for('dashboard'))
    elif oform.validate_on_submit() and request.method == 'POST':
        recipient = request.form.get('user')
        paragraph = None
        heading = oform.event_name.data
        send_invite(recipient, oform, paragraph, heading)
        return redirect(url_for('dashboard'))
    return render_template('home.html', title="Home", bform=bform, wform=wform, oform=oform, users=users, accounts=accounts-1)

def send_invite(recipient, form, paragraph, heading):
    user = User.query.filter_by(name=recipient).first_or_404()
    date_time = str(form.date1.data) + " " +str(form.time.data) 
    deadline = str(form.date2.data)
    invite = Invite(author=current_user,recipient=user,details=form.details.data, paragraph=paragraph, date_time=date_time, host_name=form.host_name.data, heading=heading, deadline=str(deadline))
    msg = Message('{} from {}'.format(heading, current_user),
        sender='noreply@google.com',
        recipients=[user.email])
    msg.body = "You have received a invitation from {}.The details of the event: {}.The event is hosted by {}. Please do join us. Thanks.".format(current_user.name, form.details.data, form.host_name.data)
    mail.send(msg)
    db.session.add(invite)
    db.session.commit()
    flash('Invite sent succesfully')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm(request.form)
    if form.validate_on_submit() and request.method == 'POST':
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page=request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        else:
            flash('Please check your login credentials.')
    return render_template('login.html', title="Login", form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pwd=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data, password=hashed_pwd)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!')
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    page1 = request.args.get('page1', 1, type=int)
    page2 = request.args.get('page2', 1, type=int)
    current_user.last_invite_seen_time = datetime.utcnow()
    current_user.last_notification_seen_time = datetime.utcnow()
    db.session.commit()
    invites_sent = current_user.invites_sent.order_by(Invite.time.desc()).paginate(page=page1, per_page=3)
    invites_received = current_user.invites_received.order_by(Invite.time.desc()).paginate(page=page2, per_page=3)
    notification_received = current_user.notifications_received.order_by(Notification.time.desc())

    return render_template('dashboard.html', title="Dashboard", invites_sent=invites_sent, invites_received=invites_received, notification_received=notification_received, date=str(date.today()))

@app.route('/action/<int:invite_id>/<action>', methods=['POST', 'GET'])
@login_required
def action(invite_id, action):
    invite = Invite.query.filter_by(id=invite_id).first_or_404()
    user = User.query.filter_by(id=invite.sender_id).first_or_404()
    if request.method == 'POST' and action == 'userResponse':
        response = request.form.get('userResponse')
        message = "{} has sent you a message regarding your invite \"{}\". Message: \"{}\" ".format(current_user.name, invite.heading, response)
        notification = Notification(author=current_user, receiver = user, message=message, type="userResponse")
        db.session.add(notification)
        db.session.commit()
        flash('Your response has been sent successfully.')
    if request.method == 'POST' and action == 'authorResponse':
        notif = Notification.query.filter_by(id=invite_id).first_or_404()
        usern = User.query.filter_by(id=notif.senderId).first_or_404()
        response = request.form.get('authorResponse')
        message = "{} has sent you a message regarding your response. Message: \"{}\" ".format(current_user.name, response)
        notification = Notification(author=current_user, receiver = usern, message=message, type="authorResponse")
        db.session.add(notification)
        db.session.commit()
    if action == 'accept':
        message = "{} has accepted your invitation\n Heading:{}.  \n Details:{}".format(current_user.name, invite.heading, invite.details)
        invite.accepted=True
        notification = Notification(author=current_user, receiver = user, message=message, type="accept")
        db.session.add(notification)
        current_user.accept_invite(invite)
        db.session.commit()
    if action == 'reject':
        message = "{} has rejected your invitation. Heading:{} Details:{}".format(current_user.name, invite.heading, invite.details)
        invite.rejected=True
        notification = Notification(author=current_user, receiver = user, message=message, type="reject")
        db.session.add(notification)
        current_user.reject_invite(invite)
        db.session.commit()
    return redirect(request.referrer)

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccount()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        if form.password.data is not None and bcrypt.check_password_hash(current_user.password,form.password.data):
            pwd_hash = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            current_user.password = pwd_hash
        db.session.commit()
        flash('Your account credentials has been updated')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)
