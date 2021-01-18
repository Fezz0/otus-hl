from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user

from model import Subscriber, Relationship

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    search = [{"field": "subscriber_id", "op": "=", "value": current_user["subscriber_id"]}]
    sub = Subscriber.load(search)[0]

    unknown_value = " - "

    page_data = {
        "full_name": f"""{sub["first_name"]} {sub["last_name"]}""",
        "birth_dt": sub.get("birth_dt", unknown_value),
        "sex": Subscriber.sex_map.get(sub["sex"], unknown_value),
        "city": sub.get("city", unknown_value),
        "interests": sub.get("interests", unknown_value)
    }

    return render_template('profile.html', **page_data)


@main.route('/friends')
@login_required
def friends():
    friends = current_user.friends(fields=["subscriber_id", "first_name", "last_name"])
    friend_ids = set([row["subscriber_id"] for row in friends])
    people = Subscriber.load([], fields=["subscriber_id", "first_name", "last_name"])

    page_data = {}
    page_data["friends"] = list([
        {
            "id": f"""{row["relationship_id"]}""",
            "name": f"""{row["last_name"]} {row["first_name"]}"""
        }
        for row in friends
    ])
    page_data["people"] = list([
        {
            "id": f"""{row["subscriber_id"]}""",
            "name": f"""{row["last_name"]} {row["first_name"]}"""
        }
        for row in people
        if row["subscriber_id"] not in friend_ids
    ])

    return render_template('friends.html', **page_data)


@main.route('/friends', methods=['POST'])
@login_required
def friends_post():
    action_id = request.form.get("id")

    action_add = request.form.get("add")
    if action_add is not None:
        Relationship.add(current_user["subscriber_id"], int(action_id))

    action_remove = request.form.get("remove")
    if action_remove is not None:
        Relationship.remove(action_id)

    return redirect(url_for('main.friends'))