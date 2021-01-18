from project import db


class Relationship(dict):
    fields = (
        "relationship_id",
        "subscriber_id",
        "follow_subscriber_id"
    )

    search_ops = (
        "=",
        "like",
        ">",
        ">=",
        "<",
        "<="
    )

    table = "relationship"

    def __init__(self, **kwargs):
        super().__init__()

        for k, v in kwargs.items():
            if k in Relationship.fields:
                self[k] = v

    @staticmethod
    def add(subscriber_id, follow_subscriber_id):
        fields = ", ".join(Relationship.fields)
        placeholders = ", ".join([f":{field}" for field in Relationship.fields])
        values = {
            "relationship_id": None,
            "subscriber_id": subscriber_id,
            "follow_subscriber_id": follow_subscriber_id
        }

        query = f"""
        insert into {Relationship.table} ({fields})
        values({placeholders})
        """

        db.session.execute(query, values)
        db.session.flush()
        db.session.commit()

        return

    @staticmethod
    def remove(relationship_id):
        query = f"""
        delete from {Relationship.table}
        where relationship_id = :relationship_id
        """

        db.session.execute(query, {"relationship_id": relationship_id})
        db.session.flush()
        db.session.commit()

        return
