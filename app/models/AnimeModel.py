from ..extensions import db
from .association_tables import prequel


class Anime(db.Model):
    __tablename__ = "anime"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    picture = db.Column(db.String())
    synopsis = db.Column(db.String(1023))
    prequel_anime = db.relationship(
        "Anime",
        secondary=prequel,
        backref=db.backref("sequel_anime", uselist=False),
        uselist=False,
        primaryjoin=lambda: Anime.id == prequel.c.sequel_id,
        secondaryjoin=lambda: Anime.id == prequel.c.prequel_id,
    )
    _release_date = db.Column(db.DateTime)
    # links
    teaser_link = db.Column(db.String(255))
    trailer_link = db.Column(db.String(255))
    recommendations = db.relationship("Recommendation", backref="anime")
    ratings = db.relationship("Rating", backref="anime", lazy="dynamic")
    posts = db.relationship("AnimePost", backref="anime", lazy="dynamic")

    @property
    def release_date(self):
        if self._release_date:
            return self._release_date.strftime("%d %b, %Y")
        else:
            return "Coming Soon"

    @release_date.setter
    def release_date(self, value):
        self._release_date = value

    def release_date_raw(self):
        return self._release_date.strftime("%Y-%m-%d")

    def get_avg_rating(self):
        res = db.session.execute(
            db.select(db.func.avg(Rating.rate)).filter_by(anime_id=self.id)
        ).first()[0]
        return round(res, 2) if res else 0.00


class Rating(db.Model):
    __tablename__ = "rating"
    anime_id = db.Column(db.Integer, db.ForeignKey("anime.id"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    rate = db.Column(db.Integer, nullable=False)
