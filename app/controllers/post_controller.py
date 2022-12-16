import json
from flask import render_template, redirect, url_for, request, jsonify, abort
from flask_login import current_user, login_required
from ..extensions import db
from ..models.PostModel import Post, Reaction, Comment


class PostController:
    def post(self, id):
        post = Post.query.get(id)
        # FIXME
        reaction = post.get_reaction(current_user)
        # like_count = post.reactions.query.filter_by(like=True).all()
        # dislike_count = post.reactions.query.filter_by(like=False).all()
        # comments = post.comments.query.order_by()
        return render_template("post.html", post=post, user_reaction=reaction)

    @login_required
    def react(self):
        reaction_json = json.loads(request.data)
        post = Post.query.get(reaction_json["post_id"])
        reaction = post.get_reaction(current_user)
        if reaction is not None:
            # previously reacted
            # prev  cur   res
            # true  true  delete
            # false true  true
            # true  false false
            # false false delete
            if reaction_json["like"] == reaction.like:
                db.session.delete(reaction)
                db.session.commit()
                return jsonify({"reaction": None})
            else:
                reaction.like = reaction_json["like"]
                db.session.commit()
                return jsonify({"reaction": reaction.like})
        else:
            reaction = Reaction(
                user_id=current_user.id, post_id=post.id, like=reaction_json["like"]
            )
            db.session.add(reaction)
            db.session.commit()
            return jsonify({"reaction": reaction.like})

    @login_required
    def comment(self, id):
        if current_user.is_banned():
            # user is banned and cannot comment
            abort(403)
        post = Post.query.get(id)
        comment = Comment(
            user_id=current_user.id, post_id=post.id, text=request.form.get("comment")
        )
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for("post.post", id=id))
