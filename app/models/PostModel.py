from ..extensions import db
from datetime import datetime


class Post(db.Model):
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # picture =
    text = db.Column(db.String(1023))
    is_private = db.Column(db.Boolean, default=False, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_type = db.Column(db.String(15))
    _post_time = db.Column(db.DateTime, default=datetime.utcnow)
    reactions = db.relationship("Reaction", backref="post", lazy="dynamic")
    comments = db.relationship("Comment", backref="post", lazy="dynamic")

    __mapper_args__ = {
        "polymorphic_identity": "general_post",
        "polymorphic_on": "post_type",
    }

    @property
    def post_time(self):
        return self._post_time.strftime("%d %b, %Y")

    def get_reaction(self, user):
        return self.reactions.filter_by(user_id=user.id).first()

    @classmethod
    def delete(cls, user):
        Reaction.query.filter_by(user_id=user.id).delete()
        Comment.query.filter_by(author_id=user.id).delete()
        AnimePost.query.filter_by(author_id=user.id).delete()
        cls.query.filter_by(author_id=user.id).delete()
        db.session.commit()


class AnimePost(Post):
    __tablename__ = "anime_post"
    id = db.Column(db.Integer, db.ForeignKey("post.id"), primary_key=True)
    category = db.Column(db.String(31), nullable=False)
    anime_id = db.Column(db.Integer, db.ForeignKey("anime.id"), nullable=False)

    __mapper_args__ = {"polymorphic_identity": "anime_post"}


class Reaction(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), primary_key=True)
    like = db.Column(db.Boolean, nullable=False)


class Comment(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), primary_key=True)
    text = db.Column(db.String(1023), nullable=False)
    _date = db.Column(db.DateTime, default=datetime.utcnow, primary_key=True)

    @property
    def date(self):
        return self._date.strftime("%d %b, %Y")
