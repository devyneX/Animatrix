from datetime import datetime
from flask import render_template, redirect, url_for, request
from flask_login import current_user, login_required
from ..models.AnimeModel import Anime, Rating
from ..models.UserModel import User, Recommendation
from ..models.association_tables import favorite, watchlist
from ..extensions import db


class BrowseController:
    def home(self):
        return render_template("home.html")

    def top_anime(self):
        ratings = (
            db.select(
                [
                    Rating.anime_id,
                    db.func.round(db.func.avg(Rating.rate), 2).label("avg_rating"),
                ]
            )
            .group_by(Rating.anime_id)
            .alias("ratings")
        )
        animes = db.session.execute(
            db.select([Anime, ratings.c.avg_rating])
            .join(ratings, Anime.id == ratings.c.anime_id, isouter=True)
            .order_by(db.nullslast(ratings.c.avg_rating.desc()))
            .limit(50)
        ).all()
        r = render_template("search_results.html", list=animes, top_anime=True)

        print(r)

        return r

    def most_popular_anime(self):
        # TODO: implement
        favorites = (
            db.select(
                [
                    favorite.c.anime_id,
                    db.func.count(favorite.c.anime_id).label("favorites_count"),
                ]
            )
            .group_by(favorite.c.anime_id)
            .alias("favorites")
        )
        recommendations = (
            db.select(
                [
                    Recommendation.anime_id,
                    db.func.count(Recommendation.anime_id).label(
                        "recommendation_count"
                    ),
                ]
            )
            .group_by(Recommendation.anime_id)
            .alias("recommendations")
        )
        watchlists = (
            db.select(
                [
                    watchlist.c.anime_id,
                    db.func.count(watchlist.c.anime_id).label("watchlist_count"),
                ]
            )
            .group_by(watchlist.c.anime_id)
            .alias("watchlist")
        )
        animes = db.session.execute(
            db.select(
                [
                    Anime,
                    favorites.c.favorites_count,
                    recommendations.c.recommendation_count,
                    watchlists.c.watchlist_count,
                ]
            )
            .join(favorites, Anime.id == favorites.c.anime_id, isouter=True)
            .join(recommendations, Anime.id == recommendations.c.anime_id, isouter=True)
            .join(watchlists, Anime.id == watchlists.c.anime_id, isouter=True)
            .order_by(
                db.nullslast(favorites.c.favorites_count.desc()),
                db.nullslast(recommendations.c.recommendation_count.desc()),
                db.nullslast(watchlists.c.watchlist_count.desc()),
            )
            .limit(50)
        ).all()
        return render_template("most_popular_anime.html", list=animes)

    def anime_search(self, search_term):
        ratings = (
            db.select([Rating.anime_id, db.func.avg(Rating.rate).label("avg_rating")])
            .group_by(Rating.anime_id)
            .alias("ratings")
        )
        res = db.session.execute(
            db.select(Anime, ratings.c.avg_rating)
            .join(ratings, Anime.id == ratings.c.anime_id, isouter=True)
            .filter(Anime.title.ilike(f"%{search_term}%"))
            .order_by(db.nullslast(ratings.c.avg_rating.desc()))
        ).all()
        return render_template("search_results.html", list=res)

    @login_required
    def user_search(self, search_term):
        users = User.query.filter(User.name.ilike(f"%{search_term}%")).all()
        relationships = []
        for user in users:
            relationships.append(current_user.get_relationship(user))

        lst = list(zip(users, relationships))
        return render_template("user_search_results.html", list=lst)

    def search(self):
        option = request.form.get("search_option")
        search_term = request.form.get("search_term")

        if search_term == "":
            return redirect(url_for("browse.home"))

        if option == "anime":
            return redirect(url_for("browse.anime_search", search_term=search_term))
        elif option == "user":
            return redirect(url_for("browse.user_search", search_term=search_term))

    def advanced_search(self):
        if request.method == "GET":
            return render_template("find_anime.html")
        elif request.method == "POST":
            title = request.form.get("title")
            rating = request.form.get("rating")
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date")

            if rating == "":
                rating = 0
            if start_date == "":
                start_date = datetime(1, 1, 1)
            if end_date == "":
                end_date = datetime(9999, 12, 31)

            ratings = (
                db.select(
                    [Rating.anime_id, db.func.avg(Rating.rate).label("avg_rating")]
                )
                .group_by(Rating.anime_id)
                .alias("ratings")
            )
            res = db.session.execute(
                db.select(Anime, ratings.c.avg_rating)
                .join(ratings, Anime.id == ratings.c.anime_id, isouter=True)
                .filter(
                    Anime.title.ilike(f"%{title}%"),
                    ratings.c.avg_rating >= rating,
                    Anime._release_date.between(start_date, end_date),
                )
                .order_by(db.nullslast(ratings.c.avg_rating.desc()))
            ).all()

            return render_template("search_results.html", list=res)
