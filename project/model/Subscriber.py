from flask_login import UserMixin

from .Relationship import Relationship
from project import db


class Subscriber(dict, UserMixin):
    fields = (
        "subscriber_id",
        "email",
        "password_hash",
        "first_name",
        "last_name",
        "birth_dt",
        "sex",
        "interests",
        "city"
    )

    search_ops = (
        "=",
        "like",
        ">",
        ">=",
        "<",
        "<="
    )

    sex_map = {
        "m": "male",
        "f": "female"
    }

    table = "subscriber"

    def __init__(self, **kwargs):
        super().__init__()

        for k, v in kwargs.items():
            self[k] = v

    def get_id(self):
        return self["subscriber_id"]

    def save(self):
        fields = ", ".join(Subscriber.fields)
        placeholders = ", ".join([f":{field}" for field in Subscriber.fields])
        values = dict([(field, self.get(field)) for field in Subscriber.fields])

        query = f"""
        insert into {Subscriber.table} ({fields})
        values({placeholders})
        """

        db.session.execute(query, values)
        db.session.flush()
        db.session.commit()

        return

    def friends(self, fields=None, limit=10):
        if fields is None or not fields:
            fields = ", ".join([f"s.{f}" for f in Subscriber.fields])
        else:
            fields = ", ".join([f"s.{f}" for f in fields if f in Subscriber.fields])

        if fields == "":
            raise ValueError("no fields selected")

        query = f"""
        select
          r.relationship_id, {fields}
        from {Relationship.table} r
        inner join {Subscriber.table} s
          on s.subscriber_id = r.follow_subscriber_id
        where r.subscriber_id = :subscriber_id
        limit {limit}
        """

        rs = db.session.execute(query, {"subscriber_id": self["subscriber_id"]})
        res = [{column: value for column, value in rowproxy.items()} for rowproxy in rs]

        subs = list([Subscriber(**row) for row in res])

        return subs

    @staticmethod
    def load(search_conditions, fields=None, limit=10):
        for condition in search_conditions:
            if condition["field"] not in Subscriber.fields:
                raise ValueError(f"Unknown search field: {condition['field']}")

            if condition["op"] not in Subscriber.search_ops:
                raise ValueError(f"Unknown search operator: {condition['op']}")

        if fields is None or not fields:
            fields = ", ".join(Subscriber.fields)
        else:
            fields = ", ".join([f for f in fields if f in Subscriber.fields])

        if fields == "":
            raise ValueError("no fields selected")

        placeholders = "1 = 1"
        values = {}

        if search_conditions:
            filters = []
            cc = 0

            for condition in search_conditions:
                cc = cc + 1
                placeholder = f"ph{cc}"
                filter = f"{condition['field']} {condition['op']} :{placeholder}"

                values[placeholder] = condition["value"]
                filters.append(filter)

            placeholders = "(" + ") and (".join(filters) + ")"

        query = f"""
        select
          {fields}
        from {Subscriber.table}
        where {placeholders}
        limit {limit}
        """

        rs = db.session.execute(query, values)
        res = [{column: value for column, value in rowproxy.items()} for rowproxy in rs]

        subs = list([Subscriber(**row) for row in res])

        return subs
