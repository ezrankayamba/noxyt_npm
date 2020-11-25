create table npm_payments(
    trans_id varchar(40) primary key,
    amount double,
    payer_account varchar(40),
    trans_date datetime,
    balance double,
    channel varchar(40),
    receipt_no varchar(40),
    status varchar(20) default 'Pending',
    recorded_at timestamp default current_timestamp
);

CREATE TABLE npm_customers (
  id int(11) primary key AUTO_INCREMENT,
  name varchar(100) NOT NULL,
  email varchar(100) NOT NULL,
  msisdn varchar(20) NOT NULL,
  UNIQUE KEY name (name),
  UNIQUE KEY email (email)
);

ALTER TABLE npm_payments add column email varchar(100) NOT NULL DEFAULT 'npmnoxyt@gmail.com';
ALTER TABLE npm_payments add column msisdn varchar(20) NOT NULL default '255676100393';

CREATE TABLE npm_aliases (
  id int(11) NOT NULL AUTO_INCREMENT,
  email varchar(100) NOT NULL,
  alias varchar(100) NOT NULL,
  used int(1) DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY email (email,alias)
);

CREATE TABLE npm_messages (
  id int(11) primary key AUTO_INCREMENT,
  status int(2) NOT NULL default 0,
  email varchar(100) NOT NULL,
  message_id varchar(100) NOT NULL,
  body varchar(2000) NOT NULL
);