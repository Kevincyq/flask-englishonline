DROP TABLE IF EXISTS cousession;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS course;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS role;

CREATE TABLE role(
  role_id INT unsigned PRIMARY KEY,
  role_name varchar(15) unique not null
  );
CREATE TABLE user(
  id INT unsigned  PRIMARY KEY AUTO_INCREMENT,
  username varchar(40) unique not null,
  password varchar(100) not null,
  user_email varchar(50) not null,
  role_id int unsigned not null,
  FOREIGN KEY (role_id) REFERENCES role (role_id)
  );
CREATE TABLE post (
  id INT unsigned PRIMARY KEY AUTO_INCREMENT,
  author_id INT unsigned  NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title varchar(100) NOT NULL,
  body varchar(400) NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
  );
CREATE TABLE course(
  id int unsigned primary key auto_increment,
  teacher_id INT unsigned not null,
  course_type varchar(5) not null default '10',
  course_name varchar(20) not null,
  course_day varchar(10) not null,
  course_start_at TIME NOT NULL,
  course_duration varchar(10) not null,
  isBooked tinyint not null default 0,
  FOREIGN KEY (teacher_id) REFERENCES user(id)
  );
CREATE TABLE cousession(
  id int unsigned primary key auto_increment,
  student_id int unsigned not null,
  course_id int unsigned not null,
  session_date date not null,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status varchar(10) not null default 'Not Start',
  isPaid varchar(1) not null default 'N',
  teacher_id int unsigned not null,
  cancel_sign tinyint default 0,
  renew_sign tinyint default 1,
  recurred_sign tinyint default 1,
  FOREIGN KEY (student_id) REFERENCES user (id),
  FOREIGN KEY (course_id) REFERENCES course (id)
  );