from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .association_tables import follower, watchlist, favorite
from ..extensions import db


class BaseUser(db.Model, UserMixin):
    __tablename__ = "base_user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    _password = db.Column(db.String(511), nullable=False)
    user_type = db.Column(db.String(15))

    __mapper_args__ = {
        "polymorphic_identity": "base_user",
        "polymorphic_on": "user_type",
    }

    @property
    def password(self):
        return AttributeError("Write-Only Field")

    @password.setter
    def password(self, passwrd):
        self._password = generate_password_hash(passwrd)

    def match_password(self, passwrd):
        return check_password_hash(self._password, passwrd)


class User(BaseUser):
    __tablename__ = "user"
    id = db.Column(db.Integer, db.ForeignKey("base_user.id"), primary_key=True)

    profile_pic = db.Column(db.String())

    _joindate = db.Column(db.DateTime, default=datetime.utcnow)

    following = db.relationship(
        "User",
        secondary=follower,
        backref=db.backref("followers", lazy="dynamic"),
        primaryjoin=lambda: User.id == follower.c.follower_id,
        secondaryjoin=lambda: User.id == follower.c.followed_id,
        lazy="dynamic",
    )

    favorites = db.relationship(
        "Anime",
        secondary=favorite,
        backref="favorited_by",
        lazy="dynamic",
    )

    watchlist_animes = db.relationship(
        "Anime",
        secondary=watchlist,
        backref="watchlisted_by",
        lazy="dynamic",
    )

    recommendations_made = db.relationship(
        "Recommendation",
        backref="recommended_by",
        primaryjoin=lambda: User.id == Recommendation.recommended_by_id,
        lazy="dynamic",
    )

    recommendations_received = db.relationship(
        "Recommendation",
        backref="recommended_to",
        primaryjoin=lambda: User.id == Recommendation.recommended_to_id,
        lazy="dynamic",
    )

    ratings = db.relationship("Rating", backref="user", lazy="dynamic")

    posts = db.relationship("Post", backref="author", lazy="dynamic")

    reactions = db.relationship("Reaction", backref="user")

    comments = db.relationship("Comment", backref="author")

    bans = db.relationship("Ban", backref="user", lazy="dynamic")

    support_requests = db.relationship("SupportRequest", backref="user", lazy="dynamic")

    notifications = db.relationship("Notification", backref="user", lazy="dynamic")

    __mapper_args__ = {"polymorphic_identity": "user"}

    @property
    def joindate(self):
        return self._joindate.strftime("%d %b, %Y")

    def get_friends(self):
        return list(set(self.followers.all()) & set(self.following.all()))

    def is_following(self, user):
        return bool(self.following.filter(User.id == user.id).first())

    def is_follower(self, user):
        return bool(self.followers.filter(User.id == user.id).first())

    def get_relationship(self, user):
        if self.is_following(user):
            if self.is_follower(user):
                return "friends"
            else:
                return "following"
        elif self.id == user.id:
            return "self"
        else:
            return None

    def has_favorited(self, anime):
        return bool(self.favorites.filter_by(id=anime.id).first())

    def is_watchlisted(self, anime):
        return bool(self.watchlist_animes.filter_by(id=anime.id).first())

    def has_recommended(self, user_id, anime_id):
        return bool(
            self.recommendations_made.filter_by(
                recommended_to_id=user_id, anime_id=anime_id
            ).first()
        )

    def has_rated(self, anime):
        return bool(self.ratings.filter_by(anime_id=anime.id).first())

    def is_banned(self):
        return bool(self.bans.filter(Ban._ban_end > datetime.utcnow()).first())


class Recommendation(db.Model):
    __tablename__ = "recommendation"
    recommended_to_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), primary_key=True
    )
    recommended_by_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), primary_key=True
    )
    anime_id = db.Column(db.Integer, db.ForeignKey("anime.id"), primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class Admin(BaseUser):
    __tablename__ = "admin"

    id = db.Column(db.Integer, db.ForeignKey("base_user.id"), primary_key=True)

    bans = db.relationship("Ban", backref="admin")

    responses = db.relationship("SupportResponse", backref="admin")

    permanent_bans = db.relationship("PermanentBan", backref="admin")

    __mapper_args__ = {"polymorphic_identity": "admin"}


class Ban(db.Model):
    __tablename__ = "ban"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"), primary_key=True)
    reason = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255), nullable=False)
    ban_start = db.Column(db.DateTime, default=datetime.utcnow, primary_key=True)
    _ban_end = db.Column(db.DateTime, nullable=False)

    @property
    def ban_end(self):
        return self._ban_end.strftime("%d %b, %Y")


class PermanentBan(db.Model):
    __tablename__ = "permanent_ban"
    email = db.Column(db.String(255), primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))

    @classmethod
    def add(cls, user):
        user.following = []
        user.followers = []
        user.favorites = []
        user.watchlist_animes = []
        user.recommendations_made = []
        user.recommendations_received = []
        user.ratings = []
        user.posts = []
        user.reactions = []
        user.comments = []
        user.bans = []
        user.support_requests = []
        user.notifications = []
        ban = cls(email=user.email)
        db.session.delete(user)
        db.session.commit()

        return ban


class SupportRequest(db.Model):
    __tablename__ = "support_request"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    response = db.relationship(
        "SupportResponse", backref="support_request", uselist=False
    )


class SupportResponse(db.Model):
    __tablename__ = "support_response"
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"), primary_key=True)
    support_request_id = db.Column(
        db.Integer, db.ForeignKey("support_request.id"), primary_key=True
    )
    text = db.Column(db.String(255), nullable=False)


class Notification(db.Model):
    __tablename__ = "notification"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    text = db.Column(db.String(255), nullable=False)
    viewed = db.Column(db.Boolean, default=False)

    @classmethod
    def follow_notification(cls, user, follower):
        notification = cls(text=f"{follower.username} has followed you")
        user.notifications.append(notification)
        db.session.commit()

    @classmethod
    def ban_notification(cls, user, ban):
        notification = cls(
            text=f"You have been banned upto {ban.ban_end} because of {ban.reason}\n{ban.link}"
        )
        user.notifications.append(notification)
        db.session.commit()

    @classmethod
    def support_notification(cls, user, support_request):
        support_text = (
            support_request.text
            if len(support_request.text) <= 20
            else support_request.text[:20] + "..."
        )
        notification = cls(
            text=f"You have a response to your support request '{support_text}'\nCheck it out"
        )
        user.notifications.append(notification)
        db.session.commit()
