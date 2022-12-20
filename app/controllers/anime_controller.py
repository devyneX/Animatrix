from flask import render_template, redirect, request, url_for, abort
from flask_login import current_user, login_required
from ..models.AnimeModel import Anime, Rating
from ..models.PostModel import AnimePost
from ..extensions import db


class AnimeController:
    def gather_anime_info(self, id):
        self.anime = Anime.query.get(id)

        if self.anime is None:
            abort(404)

        if current_user.is_authenticated:
            self.is_watchlisted = current_user.is_watchlisted(self.anime)
            self.is_favorited = current_user.has_favorited(self.anime)
            self.is_rated = current_user.has_rated(self.anime)
        else:
            self.is_watchlisted = False
            self.is_favorited = False
            self.is_rated = False

        self.avg_rating = self.anime.get_avg_rating()
        self.num_rating = len(self.anime.ratings.all())
        self.num_recommendation = len(self.anime.recommendations)
        self.num_watchlist = len(self.anime.watchlisted_by)
        self.num_favorited = len(self.anime.favorited_by)

    def anime_page(self, id):
        self.gather_anime_info(id)
        posts = (
            self.anime.posts.filter_by(is_private=False)
            .order_by(AnimePost._post_time.desc())
            .all()
        )
        if current_user.is_authenticated:
            user_reactions = []

            for post in posts:
                user_reactions.append(post.get_reaction(current_user))
        else:
            user_reactions = [None] * len(posts)

        posts = zip(posts, user_reactions)

        return render_template(
            "anime.html",
            anime=self.anime,
            avg_rating=self.avg_rating,
            num_ratings=self.num_rating,
            num_favorites=self.num_favorited,
            num_recommendations=self.num_recommendation,
            num_watchlist=self.num_watchlist,
            is_favorited=self.is_favorited,
            is_watchlisted=self.is_watchlisted,
            is_rated=self.is_rated,
            posts=posts,
        )

    def teaser(self, id):
        self.gather_anime_info(id)

        return render_template(
            "teaser_trailer.html",
            anime=self.anime,
            avg_rating=self.avg_rating,
            num_ratings=self.num_rating,
            num_favorites=self.num_favorited,
            num_recommendations=self.num_recommendation,
            num_watchlist=self.num_watchlist,
            is_favorited=self.is_favorited,
            is_watchlisted=self.is_watchlisted,
            is_rated=self.is_rated,
            link=self.anime.teaser_link,
            content="Teaser",
        )

    def trailer(self, id):
        self.gather_anime_info(id)

        return render_template(
            "teaser_trailer.html",
            anime=self.anime,
            avg_rating=self.avg_rating,
            num_ratings=self.num_rating,
            num_favorites=self.num_favorited,
            num_recommendations=self.num_recommendation,
            num_watchlist=self.num_watchlist,
            is_favorited=self.is_favorited,
            is_watchlisted=self.is_watchlisted,
            is_rated=self.is_rated,
            link=self.anime.trailer_link,
            content="Trailer",
        )

    @login_required
    def rate(self, id):
        rating = int(request.form.get("star"))
        user_rating = current_user.ratings.filter_by(anime_id=id).first()
        if user_rating is not None:
            user_rating.rate = rating
            db.session.commit()
            return redirect(url_for("anime.anime_page", id=id))

        rating_obj = Rating(anime_id=id, user_id=current_user.id, rate=rating)
        db.session.add(rating_obj)
        db.session.commit()
        anime = current_user.watchlist_animes.filter_by(id=id).first()
        if anime is None:
            abort(404)

        current_user.watchlist_animes.remove(anime)
        db.session.commit()
        return redirect(url_for("anime.anime_page", id=id))

    @login_required
    def post(self, id):
        if current_user.is_banned():
            # user is banned and cannot post
            abort(403)
        anime = Anime.query.get(id)
        text = request.form.get("text")
        if text is None or text == "":
            # no text in post
            return redirect(
                url_for("user.profile.profile", username=current_user.username)
            )

        private = bool(request.form.getlist("private"))
        category = request.form.get("category")

        anime_post = AnimePost(
            text=text, is_private=private, author_id=current_user.id, category=category
        )
        anime.posts.append(anime_post)
        db.session.commit()
        return redirect(url_for("anime.anime_page", id=id))
