from flask import render_template, redirect, url_for, request, abort
from flask_login import current_user, login_required, login_user, logout_user
from ..models.UserModel import User, Recommendation
from ..models.PostModel import Post
from ..extensions import db


class ProfileController:
    def gather_profile_info(self, username):
        self.user = User.query.filter_by(username=username).first()

        if self.user is None:
            abort(404)

        self.relationship = current_user.get_relationship(self.user)

        self.friends = self.user.get_friends()
        self.followers = self.user.followers.all()
        self.following = self.user.following.all()

        self.num_friends = len(self.friends)
        self.num_followers = len(self.followers)
        self.num_following = len(self.following)

    @login_required
    def profile(self, username):
        self.gather_profile_info(username)

        posts = []
        user_reactions = []
        if self.relationship == "self" or self.relationship == "friends":
            posts = self.user.posts.order_by(Post._post_time.desc()).all()
        else:
            posts = (
                self.user.posts.filter_by(is_private=False)
                .order_by(Post._post_time.desc())
                .all()
            )

        for post in posts:
            user_reactions.append(post.get_reaction(current_user))

        posts = zip(posts, user_reactions)

        return render_template(
            "profile.html",
            user=self.user,
            relationship=self.relationship,
            num_friends=self.num_friends,
            num_followers=self.num_followers,
            num_following=self.num_following,
            posts=posts,
        )

    @login_required
    def followers(self, username):
        self.gather_profile_info(username)

        relationships = list(
            map(lambda x: current_user.get_relationship(x), self.followers)
        )

        lst = zip(self.followers, relationships)

        return render_template(
            "connections.html",
            user=self.user,
            relationship=self.relationship,
            num_friends=self.num_friends,
            num_followers=self.num_followers,
            num_following=self.num_following,
            content="Followers",
            list=lst,
            num_connections=self.num_followers,
        )

    @login_required
    def following(self, username):
        self.gather_profile_info(username)

        relationships = list(
            map(lambda x: current_user.get_relationship(x), self.following)
        )

        lst = zip(self.following, relationships)

        return render_template(
            "connections.html",
            user=self.user,
            relationship=self.relationship,
            num_friends=self.num_friends,
            num_followers=self.num_followers,
            num_following=self.num_following,
            content="Following",
            list=lst,
            num_connections=self.num_following,
        )

    @login_required
    def friends(self, username):
        self.gather_profile_info(username)

        relationships = list(
            map(lambda x: current_user.get_relationship(x), self.friends)
        )

        lst = zip(self.friends, relationships)

        return render_template(
            "connections.html",
            user=self.user,
            relationship=self.relationship,
            num_friends=self.num_friends,
            num_followers=self.num_followers,
            num_following=self.num_following,
            content="Friends",
            list=lst,
            num_connections=self.num_friends,
        )

    @login_required
    def favorites(self, username):
        self.gather_profile_info(username)

        lst = self.user.favorites.all()

        return render_template(
            "watchlist.html",
            user=self.user,
            relationship=self.relationship,
            num_friends=self.num_friends,
            num_followers=self.num_followers,
            num_following=self.num_following,
            content="Favorites",
            watchlist=lst,
            num_items=len(lst),
        )

    @login_required
    def watchlist(self):
        self.gather_profile_info(current_user.username)

        lst = current_user.watchlist_animes.all()

        return render_template(
            "watchlist.html",
            user=self.user,
            relationship=self.relationship,
            num_friends=self.num_friends,
            num_followers=self.num_followers,
            num_following=self.num_following,
            content="Watchlist",
            watchlist=lst,
            num_items=len(lst),
        )

    @login_required
    def recommendations(self):
        self.gather_profile_info(current_user.username)

        lst = current_user.recommendations_received.order_by(
            Recommendation.date.desc()
        ).all()

        return render_template(
            "recommendation.html",
            user=self.user,
            relationship=self.relationship,
            num_friends=self.num_friends,
            num_followers=self.num_followers,
            num_following=self.num_following,
            content="Recommendations",
            recommendations=lst,
            num_items=len(lst),
        )
