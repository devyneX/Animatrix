from datetime import datetime
from flask import (
    render_template,
    redirect,
    url_for,
    request,
    abort,
    flash,
    current_app,
    jsonify,
)
from flask_login import current_user, login_required, login_user, logout_user
from ..models.UserModel import (
    User,
    Recommendation,
    SupportRequest,
    Notification,
    PermanentBan,
)
from ..models.AnimeModel import Anime, Rating
from ..models.PostModel import Post
from ..models.association_tables import follower
from ..extensions import db
from .utils import allowed_file
from werkzeug.utils import secure_filename
import os


class UserController:
    def create_user(self):
        if current_user.is_authenticated:
            return redirect(
                url_for("user.profile.profile", username=current_user.username)
            )

        name = request.form.get("name")
        username = request.form.get("username")
        email = request.form.get("email")
        if PermanentBan.query.get(email):
            flash("You are permanently banned", "error")
            return redirect(url_for("auth.sign_up"))
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if len(name) < 2:
            # name too small
            flash("Enter a valid name", "error")
            return redirect(url_for("auth.sign_up"))
        elif User.query.filter_by(username=username).first() is not None:
            # username already exists
            flash("Username already exists", "error")
            return redirect(url_for("auth.sign_up"))
        elif User.query.filter_by(email=email).first() is not None:
            # email already exists
            flash("Email already exists", "error")
            return redirect(url_for("auth.sign_up"))
        elif len(password1) < 4:  # 8:
            # TODO: change this to 8
            flash("Password too short", "error")
            return redirect(url_for("auth.sign_up"))
        elif password1 != password2:
            # passwords don't match
            flash("Passwords don't match", "error")
            return redirect(url_for("auth.sign_up"))
        else:
            user = User(name=name, username=username, email=email, password=password1)
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            flash("Account created successfully!", "success")
            return redirect(url_for("user.profile.profile", username=user.username))

    def authenticate_user(self):
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user is None:
            flash("Username not found", "error")
            return redirect(url_for("auth.login"))
        elif user.match_password(password):
            login_user(user, remember=True)
            flash("Logged in successfully!", "success")
            return redirect(url_for("user.profile.profile", username=user.username))
        else:
            flash("Wrong Password", "error")
            return redirect(url_for("auth.login"))

    @login_required
    def follow(self, username):
        user = User.query.filter_by(username=username).first()
        if user is None:
            # trying to follow a username that's not in the database
            abort(404)
        elif current_user.id == user.id:
            # trying to follow yourself
            abort(403)
        else:
            if current_user.is_following(user):
                # already following this user
                abort(403)
            else:
                current_user.following.append(user)
                db.session.commit()

                Notification.follow_notification(user, current_user)

                return jsonify({"status": "success"})

    @login_required
    def unfollow(self, username):
        user = current_user.following.filter(User.username == username).first()
        if user is None:
            # trying to unfollow a username that wasn't followed
            abort(404)
        elif current_user.id == user.id:
            # trying to unfollow yourself
            abort(403)
        else:
            current_user.following.remove(user)
            db.session.commit()
            return jsonify({"status": "success"})

    @login_required
    def add_to_favorites(self, id):
        anime = Anime.query.get(id)
        if anime is None:
            abort(404)
        else:
            if current_user.has_favorited(anime):
                # already favorited this anime
                abort(403)
            else:
                if len(current_user.favorites.all()) < 5:
                    current_user.favorites.append(anime)
                    db.session.commit()
                    flash("Added to favorites!", "success")
                    return redirect(url_for("anime.anime_page", id=id))
                else:
                    # can't add more than 5 animes to top 5 favorites
                    flash("You can't add more than 5 animes to your favorites", "error")
                    flash("Remove one of your favorites first", "error")
                    return redirect(url_for("anime.anime_page", id=id))

    @login_required
    def remove_from_favorites(self, id):
        anime = current_user.favorites.filter_by(id=id).first()
        if anime is None:
            abort(404)

        current_user.favorites.remove(anime)
        flash("Removed from favorites!", "success")
        db.session.commit()
        return redirect(url_for("anime.anime_page", id=id))

    @login_required
    def add_to_watchlist(self, id):
        anime = Anime.query.get(id)
        if anime is None:
            # does not exist
            abort(404)
        elif current_user.has_rated(anime):
            # already rated/watched
            abort(403)
        else:
            if current_user.is_watchlisted(anime):
                # already watchlisted this anime
                abort(403)
            else:
                current_user.watchlist_animes.append(anime)
                db.session.commit()
                flash("Added to watchlist!", "success")
                return redirect(url_for("anime.anime_page", id=id))

    def remove_from_watchlist(self, id):
        anime = current_user.watchlist_animes.filter_by(id=id).first()
        if anime is None:
            # trying to remove an anime from watchlist that wasn't watchlisted
            abort(404)

        current_user.watchlist_animes.remove(anime)
        db.session.commit()
        # TODO: flash message
        flash("Removed from watchlist!", "success")
        return redirect(url_for("anime.anime_page", id=id))

    @login_required
    def recommend(self, id):
        if request.method == "POST":
            users = request.form.getlist("users")
            if len(users) == 0:
                # no users selected
                return redirect(url_for("anime.anime_page", id=id))

            for user_id in users:
                if user_id == current_user.id:
                    # trying to recommend yourself
                    continue
                elif current_user.has_recommended(user_id, id):
                    # already recommended this anime to this user
                    continue
                else:
                    recommendation = Recommendation(
                        recommended_by_id=current_user.id,
                        recommended_to_id=user_id,
                        anime_id=id,
                    )
                    db.session.add(recommendation)
            db.session.commit()
            flash("Recommendations sent!", "success")
            return redirect(url_for("anime.anime_page", id=id))
        elif request.method == "GET":
            friends = []
            for friend in current_user.get_friends():
                if current_user.has_recommended(friend.id, id):
                    continue
                friends.append(friend)

            return render_template("recommend.html", list=friends)

    @login_required
    def recommendation_advanced_search(self):
        if request.method == "GET":
            return render_template(
                "recommendation_advanced_search.html",
                friends=current_user.get_friends(),
            )
        elif request.method == "POST":
            title = request.form.get("title")
            recommender = request.form.get("recommender")
            rating = request.form.get("rating")
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date")

            if rating == "":
                rating = 0
            if start_date == "":
                start_date = datetime(1, 1, 1)
            if end_date == "":
                end_date = datetime(9999, 12, 31)

            recommender_user = User.query.filter_by(username=recommender).first()

            ratings = (
                db.select(
                    [Rating.anime_id, db.func.avg(Rating.rate).label("avg_rating")]
                )
                .group_by(Rating.anime_id)
                .alias("ratings")
            )
            if recommender_user is None:
                res = db.session.execute(
                    db.select(Anime, Recommendation, ratings.c.avg_rating)
                    .join(
                        Recommendation,
                        (Anime.id == Recommendation.anime_id),
                    )
                    .join(ratings, Anime.id == ratings.c.anime_id, isouter=True)
                    .filter(
                        Recommendation.recommended_to_id == current_user.id,
                        Anime.title.ilike(f"%{title}%"),
                        ratings.c.avg_rating >= rating,
                        Anime.release_date.between(start_date, end_date),
                    )
                    .order_by(ratings.c.avg_rating)
                ).all()
            else:
                res = db.session.execute(
                    db.select(Anime, Recommendation, ratings.c.avg_rating)
                    .join(
                        Recommendation,
                        (
                            Anime.id == Recommendation.anime_id
                            and Recommendation.recommended_to_id == current_user.id
                        ),
                    )
                    .join(ratings, Anime.id == ratings.c.anime_id, isouter=True)
                    .filter(
                        Recommendation.recommended_to_id == current_user.id,
                        Recommendation.recommended_by_id == recommender_user.id,
                        Anime.title.ilike(f"%{title}%"),
                        ratings.c.avg_rating >= rating,
                        Anime.release_date.between(start_date, end_date),
                    )
                    .order_by(ratings.c.avg_rating)
                ).all()

            return render_template("search_results.html", list=res)

    @login_required
    def post(self):
        if current_user.is_banned():
            # user is banned and cannot post
            flash("You are banned and cannot post!", "error")
            return redirect(
                url_for("user.profile.profile", username=current_user.username)
            )

        text = request.form.get("text")
        if text is None or text == "":
            # no text in post
            return redirect(
                url_for("user.profile.profile", username=current_user.username)
            )

        private = bool(request.form.getlist("private"))

        user_post = Post(text=text, is_private=private)
        current_user.posts.append(user_post)
        db.session.commit()
        return redirect(url_for("user.profile.profile", username=current_user.username))

    @login_required
    def support_requests(self):
        if request.method == "POST":
            text = request.form.get("text")
            if text is None or text == "":
                # no request written
                flash("Write a request to submit", "error")
                return redirect(url_for("user.support_requests"))
            support_request = SupportRequest(text=text)
            current_user.support_requests.append(support_request)
            db.session.commit()
            return redirect(url_for("user.support_requests"))
        elif request.method == "GET":
            return render_template(
                "support_requests.html",
                requests=current_user.support_requests.order_by(
                    SupportRequest.date.desc()
                ).all(),
            )

    @login_required
    def profile_pic(self):
        if request.method == "POST":
            if "profile_pic" not in request.files:
                flash("No file part")
                return redirect(request.url)
            file = request.files["profile_pic"]
            if file.filename == "":
                flash("No selected file")
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)

                file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
                if current_user.profile_pic is not None:
                    os.remove(
                        os.path.join(
                            current_app.config["UPLOAD_FOLDER"],
                            current_user.profile_pic,
                        )
                    )
                current_user.profile_pic = filename
                db.session.commit()
                flash("Profile picture updated successfully", "success")
                return redirect(
                    url_for("user.profile.profile", username=current_user.username)
                )
        elif request.method == "GET":
            return render_template("profile_pic.html")

    @login_required
    def notifications(self):
        notifs = current_user.notifications.filter_by(viewed=False).all()
        for notif in notifs:
            notif.viewed = True

        db.session.commit()
        return render_template("notifications.html", list=notifs)

    @login_required
    def new_notifications(self):
        notifs = current_user.notifications.filter_by(viewed=False).all()
        return jsonify({"notification_count": len(notifs)})
