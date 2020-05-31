from main import app, db, bcrypt
from flask import redirect, render_template, url_for, request, flash, session
from main.models import User, Invite, Notification
from main.forms import LoginForm, RegistrationForm, BirthdayForm, WeddingForm, OtherForm, UpdateAccount, AcceptForm, RejectForm
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

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
    date_time = str(form.date.data) + " " +str(form.time.data) 
    invite = Invite(author=current_user,recipient=user,details=form.details.data, paragraph=paragraph, date_time=date_time, host_name=form.host_name.data, heading=heading)
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
    aform = AcceptForm(request.form)
    rform = RejectForm(request.form)
    page1 = request.args.get('page1', 1, type=int)
    page2 = request.args.get('page2', 1, type=int)
    current_user.last_invite_seen_time = datetime.utcnow()
    current_user.last_notification_seen_time = datetime.utcnow()
    db.session.commit()
    invites_sent = current_user.invites_sent.order_by(Invite.time.desc()).paginate(page=page1, per_page=3)
    invites_received = current_user.invites_received.order_by(Invite.time.desc()).paginate(page=page2, per_page=3)
    notification_sent = current_user.notifications_sent.order_by(Notification.time.desc())
    notification_received = current_user.notifications_received.order_by(Notification.time.desc())

    if rform.validate_on_submit() and request.method == 'POST':
        recipient = current_user.invites_received.order_by(Invite.time.desc())[0].sender_id
        id1 = current_user.invites_received.order_by(Invite.time.desc())[0].id
        message = "{} rejected your Invitation.".format(current_user.name)
        rejected = False
        send_notification(recipient, message, rejected, id1)

    if aform.validate_on_submit() and request.method == 'POST':
        recipient = current_user.invites_received.order_by(Invite.time.desc())[0].sender_id
        id1 = current_user.invites_received.order_by(Invite.time.desc())[0].id
        message = "{} accepted your Invitation.".format(current_user.name)
        accepted = True
        send_notification(recipient, message, accepted, id1)

    return render_template('dashboard.html', title="Dashboard", invites_sent=invites_sent, invites_received=invites_received, notification_sent=notification_sent, notification_received=notification_received, aform=aform, rform=rform)

def send_notification(recipient, message, bool1, id1):
    user = User.query.filter_by(id=recipient).first_or_404()
    invite = Invite.query.filter_by(id=id1).first()
    if bool1:
        invite.accepted=True
    else:
        invite.rejected=True
    notification = Notification(author=current_user, receiver=user, message=message)
    db.session.add(notification)
    db.session.commit()
    return redirect(url_for('home'))

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
