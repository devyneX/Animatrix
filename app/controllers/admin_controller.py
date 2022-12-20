from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, request, abort, flash, current_app
from flask_login import current_user, login_user, logout_user
from ..extensions import db
from ..models.UserModel import (
    User,
    Admin,
    Ban,
    PermanentBan,
    SupportRequest,
    SupportResponse,
    Notification,
)
from ..models.AnimeModel import Anime
from .utils import allowed_file
from werkzeug.utils import secure_filename
import os
from .utils import admin_decorator


class AdminController:
    def login(self):
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            admin = Admin.query.filter_by(username=username).first()
            if admin and admin.match_password(password):
                login_user(admin)
                return redirect(url_for("admin.users"))
            return render_template(
                "admin_login.html", error="Wrong username or password"
            )
        elif request.method == "GET":
            return render_template("admin_login.html")

    @admin_decorator
    def logout(self):
        logout_user()
        return redirect(url_for("admin.login"))

    @admin_decorator
    def users(self):
        users = User.query.all()

        return render_template("admin_users.html", list=users)

    @admin_decorator
    def permanent_ban(self, username):
        user = User.query.filter_by(username=username).first()
        if not user:
            abort(404)

        current_user.permanent_bans.append(PermanentBan.add(user))
        db.session.commit()
        return redirect(url_for("admin.users"))

    @admin_decorator
    def animes(self):
        animes = Anime.query.order_by(Anime.id).all()

        return render_template("admin_anime.html", list=animes)

    @admin_decorator
    def ban_form(self, username):
        user = User.query.filter_by(username=username).first()
        if not user:
            abort(404)
        return render_template("admin_ban.html", username=username)

    @admin_decorator
    def ban(self):
        username = request.form.get("username")
        user = User.query.filter_by(username=username).first()
        reason = request.form.get("reason")
        link = request.form.get("link")
        duration = request.form.get("duration")
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=int(duration))
        ban = Ban(
            user_id=user.id,
            admin_id=current_user.id,
            reason=reason,
            link=link,
            ban_start=start_date,
            ban_end=end_date,
        )

        db.session.add(ban)
        db.session.commit()

        Notification.ban_notification(user, ban)
        flash(f"Banned {user.username} successfully", "success")
        return redirect(url_for("admin.users"))

    @admin_decorator
    def add_anime(self):
        if request.method == "GET":
            return render_template("admin_anime_add.html")
        elif request.method == "POST":
            title = request.form.get("title")
            synopsis = request.form.get("synopsis")
            release_date = request.form.get("release_date")
            prequel_id = request.form.get("prequel_id")
            teaser_link = request.form.get("teaser_link")
            trailer_link = request.form.get("trailer_link")

            if release_date == "":
                release_date = None

            anime = Anime(
                title=title,
                synopsis=synopsis,
                release_date=release_date,
                teaser_link=teaser_link,
                trailer_link=trailer_link,
            )

            if "profile_pic" not in request.files:
                flash("No file part")
                return redirect(request.url)
            file = request.files["profile_pic"]

            if file and file.filename != "" and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
                if anime.picture is not None:
                    os.remove(
                        os.path.join(
                            current_app.config["UPLOAD_FOLDER"],
                            current_user.profile_pic,
                        )
                    )
                anime.picture = filename

            db.session.add(anime)

            if prequel_id != "":
                prequel = Anime.query.get(prequel_id)
                if prequel:
                    anime.prequel_anime = prequel

            db.session.commit()
            flash("Anime added successfully", "success")
            return redirect(url_for("admin.animes"))

    @admin_decorator
    def edit_anime(self, id):
        if request.method == "GET":
            anime = Anime.query.get(id)
            if not anime:
                abort(404)
            return render_template("admin_anime_edit.html", anime=anime)
        elif request.method == "POST":
            anime = Anime.query.get(id)
            if not anime:
                abort(404)
            title = request.form.get("title")
            synopsis = request.form.get("synopsis")
            release_date = request.form.get("release_date")
            prequel_id = request.form.get("prequel_id")
            teaser_link = request.form.get("teaser_link")
            trailer_link = request.form.get("trailer_link")

            if release_date == "":
                release_date = None

            anime.title = title
            anime.synopsis = synopsis
            anime.release_date = release_date
            anime.teaser_link = teaser_link
            anime.trailer_link = trailer_link

            if "profile_pic" not in request.files:
                flash("No file part")
                return redirect(request.url)
            file = request.files["profile_pic"]

            if file and file.filename != "" and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
                if anime.picture is not None:
                    os.remove(
                        os.path.join(
                            current_app.config["UPLOAD_FOLDER"],
                            current_user.profile_pic,
                        )
                    )
                anime.picture = filename

            if prequel_id != "":
                prequel = Anime.query.get(prequel_id)
                if prequel:
                    anime.prequel_anime = prequel

            db.session.commit()

            flash("Changes saved", "success")
            return redirect(url_for("admin.animes"))

    @admin_decorator
    def support_requests(self):
        unresponded = (
            SupportRequest.query.filter_by(response=None)
            .order_by(SupportRequest.date.asc())
            .all()
        )
        responded = (
            SupportRequest.query.filter(SupportRequest.response != None)
            .order_by(SupportRequest.date.desc())
            .all()
        )
        return render_template(
            "admin_support_requests.html", list=unresponded + responded
        )

    @admin_decorator
    def support_response_form(self, id):
        support_req = SupportRequest.query.get(id)
        if support_req is None:
            abort(404)
        elif support_req.response:
            abort(403)
        else:
            return render_template("admin_support_response.html", req_id=id)

    @admin_decorator
    def support_respond(self):
        support_id = request.form.get("id")
        support_req = SupportRequest.query.get(support_id)
        if support_req is None:
            abort(404)
        elif support_req.response:
            abort(403)
        else:
            response = request.form.get("text")
            support_resp = SupportResponse(
                admin_id=current_user.id, support_request_id=support_id, text=response
            )
            db.session.add(support_resp)
            db.session.commit()

            Notification.support_notification(support_req.user, support_req)

            flash("Response sent", "success")

            return redirect(url_for("admin.support_requests"))
