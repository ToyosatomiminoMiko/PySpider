-- 电影信息表 MySQL
CREATE TABLE IF NOT EXISTS `movie`(
   `movie_id` INT UNSIGNED , #
   `movie_title` VARCHAR(64) NOT NULL, --标题
   `director` VARCHAR(128) NOT NULL, --导演
   `author` VARCHAR(128) NOT NULL, --编剧
   `actor` VARCHAR(4096) NOT NULL, --演员
   `submission_date` DATE,
   PRIMARY KEY ( `movie_id` )
)ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4;
