from flask_login import UserMixin
from main import db, app, login_manager
from datetime import datetime
from wtforms.validators import ValidationError

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(15) ,nullable=False)
    invites_sent = db.relationship('Invite', foreign_keys="Invite.sender_id", backref='author', lazy='dynamic')
    invites_received = db.relationship('Invite', foreign_keys="Invite.recipient_id", backref='recipient', lazy='dynamic')
    last_invite_seen_time = db.Column(db.DateTime)
    notifications_sent = db.relationship('Notification', foreign_keys="Notification.senderId", backref='author', lazy='dynamic')
    notifications_received = db.relationship('Notification', foreign_keys="Notification.receiverId", backref='receiver', lazy='dynamic')
    last_notification_seen_time = db.Column(db.DateTime)
    action = db.relationship('Action', foreign_keys='Action.user_id', backref='user', lazy='dynamic')

    def __repr__(self):
        return "User('{}', '{}')".format(self.name, self.email)

    def new_invites(self):
        last_read_time = self.last_invite_seen_time or datetime(1900,1,1)
        return Invite.query.filter_by(recipient=self).filter(Invite.time > last_read_time).count()
    
    def new_notifications(self):
        last_read_time = self.last_notification_seen_time or datetime(1900,1,1)
        return Notification.query.filter_by(receiver=self).filter(Notification.time > last_read_time).count()
    
    def accept_invite(self, invite):
        accept = Action(user_id=self.id, invite_id=invite.id)
        db.session.add(accept)
    
    def reject_invite(self, invite):
        reject = Action(user_id=self.id, invite_id=invite.id)
        db.session.add(reject)
    
    def has_taken_action(self, invite):
        return Action.query.filter(Action.user_id == self.id, Action.invite_id == invite.id).count() > 0

class Invite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id=db.Column(db.String, db.ForeignKey('user.id'))
    recipient_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    heading=db.Column(db.String())
    date_time=db.Column(db.String())
    deadline=db.Column(db.String())
    host_name=db.Column(db.String())
    paragraph=db.Column(db.String())
    details = db.Column(db.String())
    accepted = db.Column(db.Boolean())
    rejected = db.Column(db.Boolean())
    aor = db.relationship('Action', backref='invite', lazy='dynamic')
    time = db.Column(db.Date, index=True, default=datetime.utcnow())

    def __repr__(self):
        return 'Invite {} {} {} {}'.format(self.date_time, self.host_name, self.paragraph, self.details)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    senderId = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiverId = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String())
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    type = db.Column(db.String)

    def __repr__(self):
        return 'Notification {}'.format(self.message)

class Action(db.Model):
    __tablename__ = 'action'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    invite_id = db.Column(db.Integer, db.ForeignKey('invite.id'))
