create table otus.relationship (
  relationship_id integer auto_increment primary key,
  subscriber_id integer,
  follower_subscriber_id integer
);
