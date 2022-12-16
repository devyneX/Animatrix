from ..extensions import db


follower = db.Table(
    "follower",
    db.Column(
        "followed_id",
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "follower_id",
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


favorite = db.Table(
    "favorite",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id", ondelete="CASCADE")),
    db.Column("anime_id", db.Integer, db.ForeignKey("anime.id", ondelete="CASCADE")),
)

watchlist = db.Table(
    "watchlist",
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "anime_id",
        db.Integer,
        db.ForeignKey("anime.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

prequel = db.Table(
    "prequel",
    db.Column("prequel_id", db.Integer, db.ForeignKey("anime.id"), primary_key=True),
    db.Column("sequel_id", db.Integer, db.ForeignKey("anime.id"), primary_key=True),
)
