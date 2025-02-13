﻿CREATE DATABASE IF NOT EXISTS todolist;
USE todolist;

DROP TABLE IF EXISTS todolistitem;
CREATE TABLE todolistitem
(
  id SERIAL PRIMARY KEY,
  user_id INT,
  title VARCHAR(64),
  content VARCHAR(1024),
  deadline DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS todolistuser;
CREATE TABLE todolistuser
(
  id SERIAL PRIMARY KEY,
  name VARCHAR(64),
  password VARCHAR(64),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO todolistuser (name, password) VALUES ('test', '66a9bdb327596cc20d47ff20841f8eb66c989e82d36a6b37068a3bdd1891fff4');
INSERT INTO todolistitem (user_id, content, deadline) VALUES (0, 'read the book XXX', '2024-12-31');