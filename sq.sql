DROP DATABASE IF EXISTS fitness;
CREATE DATABASE fitness;
USE fitness;

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(225),
    email VARCHAR(225),
    password VARCHAR(225)
);
