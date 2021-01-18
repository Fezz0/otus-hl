create table otus.subscriber (
  subscriber_id integer auto_increment primary key,
  email varchar(256),
  password_hash varchar(80),
  first_name varchar(256),
  last_name varchar(256),
  birth_dt date,
  sex ENUM('m', 'f'),
  interests text,
  city varchar(256)
);