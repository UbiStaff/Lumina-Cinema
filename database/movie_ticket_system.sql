-- 电影票选座与影评系统数据库脚本
-- 创建数据库
CREATE DATABASE IF NOT EXISTS movie_ticket_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE movie_ticket_system;

-- 1. 用户信息表 (users)
CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    real_name VARCHAR(50),
    avatar VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
);

-- 2. 电影信息表 (movies)
CREATE TABLE IF NOT EXISTS movies (
    movie_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    director VARCHAR(50),
    actors TEXT,
    genre VARCHAR(50),
    duration INT, -- 分钟
    release_date DATE,
    description TEXT,
    poster VARCHAR(255),
    rating DECIMAL(3,1) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_title (title),
    INDEX idx_genre (genre),
    INDEX idx_release_date (release_date)
);

-- 3. 影院信息表 (cinemas)
CREATE TABLE IF NOT EXISTS cinemas (
    cinema_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_address (address)
);

-- 4. 放映厅表 (halls)
CREATE TABLE IF NOT EXISTS halls (
    hall_id INT PRIMARY KEY AUTO_INCREMENT,
    cinema_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    total_seats INT NOT NULL,
    rows INT NOT NULL,
    cols INT NOT NULL,
    FOREIGN KEY (cinema_id) REFERENCES cinemas(cinema_id) ON DELETE CASCADE,
    INDEX idx_cinema_id (cinema_id)
);

-- 5. 放映场次表 (screenings)
CREATE TABLE IF NOT EXISTS screenings (
    screening_id INT PRIMARY KEY AUTO_INCREMENT,
    movie_id INT NOT NULL,
    hall_id INT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    remaining_seats INT NOT NULL,
    status ENUM('upcoming', 'ongoing', 'ended') DEFAULT 'upcoming',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE,
    FOREIGN KEY (hall_id) REFERENCES halls(hall_id) ON DELETE CASCADE,
    INDEX idx_movie_id (movie_id),
    INDEX idx_hall_id (hall_id),
    INDEX idx_start_time (start_time)
);

-- 6. 座位表 (seats)
CREATE TABLE IF NOT EXISTS seats (
    seat_id INT PRIMARY KEY AUTO_INCREMENT,
    hall_id INT NOT NULL,
    seat_row CHAR(2) NOT NULL, -- A, B, C...
    seat_col INT NOT NULL,     -- 1, 2, 3...
    type ENUM('regular', 'vip', 'disabled') DEFAULT 'regular',
    FOREIGN KEY (hall_id) REFERENCES halls(hall_id) ON DELETE CASCADE,
    UNIQUE KEY uk_hall_row_col (hall_id, seat_row, seat_col),
    INDEX idx_hall_id (hall_id)
);

-- 7. 订单表 (orders)
CREATE TABLE IF NOT EXISTS orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    screening_id INT NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'paid', 'cancelled', 'completed') DEFAULT 'pending',
    payment_method VARCHAR(20),
    transaction_id VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (screening_id) REFERENCES screenings(screening_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_screening_id (screening_id),
    INDEX idx_status (status),
    INDEX idx_order_time (order_time)
);

-- 8. 订单座位表 (order_seats)
CREATE TABLE IF NOT EXISTS order_seats (
    order_seat_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    seat_id INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (seat_id) REFERENCES seats(seat_id) ON DELETE CASCADE,
    UNIQUE KEY uk_order_seat (order_id, seat_id),
    INDEX idx_order_id (order_id),
    INDEX idx_seat_id (seat_id)
);

-- 9. 影评表 (reviews)
CREATE TABLE IF NOT EXISTS reviews (
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    likes INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_movie (user_id, movie_id),
    INDEX idx_user_id (user_id),
    INDEX idx_movie_id (movie_id),
    INDEX idx_rating (rating),
    INDEX idx_created_at (created_at)
);

-- 10. 影评点赞表 (review_likes)
CREATE TABLE IF NOT EXISTS review_likes (
    like_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    review_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (review_id) REFERENCES reviews(review_id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_review (user_id, review_id),
    INDEX idx_user_id (user_id),
    INDEX idx_review_id (review_id)
);

-- 插入示例数据

-- 插入用户数据
INSERT INTO users (username, password, email, phone, real_name) VALUES
('user1', 'password123', 'user1@example.com', '13800138001', '张三'),
('user2', 'password123', 'user2@example.com', '13800138002', '李四'),
('user3', 'password123', 'user3@example.com', '13800138003', '王五');

-- 插入电影数据
INSERT INTO movies (title, director, actors, genre, duration, release_date, description, poster, rating) VALUES
('流浪地球2', '郭帆', '吴京, 刘德华, 李雪健', '科幻, 冒险, 灾难', 173, '2023-01-22', '太阳即将膨胀为红巨星，人类开启“流浪地球计划”，试图带着地球逃离太阳系寻找新家园。', 'https://example.com/poster1.jpg', 9.5),
('满江红', '张艺谋', '沈腾, 易烊千玺, 张译', '喜剧, 悬疑, 历史', 159, '2023-01-22', '南宋绍兴年间，岳飞死后四年，秦桧率兵与金国会谈。会谈前夜，金国使者死在宰相驻地，所携密信也不翼而飞。', 'https://example.com/poster2.jpg', 8.2),
('消失的她', '崔睿, 刘翔', '朱一龙, 倪妮, 文咏珊', '悬疑, 犯罪', 121, '2023-06-22', '何非的妻子李木子在结婚周年旅行中离奇消失，在何非苦寻无果之时妻子突然现身，何非却坚持眼前的陌生女人并非妻子。', 'https://example.com/poster3.jpg', 7.5);

-- 插入影院数据
INSERT INTO cinemas (name, address, phone) VALUES
('万达影城', '北京市朝阳区建国路93号万达广场', '010-85596666'),
('大地影院', '上海市浦东新区张杨路501号第一八佰伴', '021-58368888'),
('CGV影城', '广州市天河区天河路385号太古汇', '020-38682222');

-- 插入放映厅数据
INSERT INTO halls (cinema_id, name, total_seats, rows, cols) VALUES
(1, '1号厅', 100, 10, 10),
(1, '2号厅', 80, 8, 10),
(2, '3号厅', 120, 12, 10),
(3, '4号厅', 90, 9, 10);

-- 插入放映场次数据
INSERT INTO screenings (movie_id, hall_id, start_time, end_time, price, remaining_seats, status) VALUES
(1, 1, '2023-12-20 10:00:00', '2023-12-20 12:53:00', 80.00, 100, 'upcoming'),
(1, 1, '2023-12-20 14:00:00', '2023-12-20 16:53:00', 80.00, 100, 'upcoming'),
(2, 2, '2023-12-20 11:00:00', '2023-12-20 13:39:00', 70.00, 80, 'upcoming'),
(3, 3, '2023-12-20 15:00:00', '2023-12-20 17:01:00', 75.00, 120, 'upcoming');

-- 插入座位数据
DELIMITER //
CREATE PROCEDURE insert_seats()
BEGIN
    DECLARE hall INT DEFAULT 1;
    DECLARE row_char CHAR(2);
    DECLARE col_num INT;
    DECLARE total_halls INT;
    DECLARE total_rows INT;
    DECLARE total_cols INT;
    
    SELECT MAX(hall_id) INTO total_halls FROM halls;
    
    WHILE hall <= total_halls DO
        SELECT rows, cols INTO total_rows, total_cols FROM halls WHERE hall_id = hall;
        SET col_num = 1;
        
        WHILE col_num <= total_cols DO
            SET row_char = CHAR(64 + col_num DIV 26 + IF(col_num % 26 = 0, 0, 1));
            IF col_num % 26 = 0 THEN
                SET row_char = CONCAT(row_char, CHAR(90));
            ELSE
                SET row_char = CONCAT(row_char, CHAR(64 + col_num % 26));
            END IF;
            
            INSERT INTO seats (hall_id, seat_row, seat_col) VALUES (hall, row_char, col_num);
            
            SET col_num = col_num + 1;
        END WHILE;
        
        SET hall = hall + 1;
    END WHILE;
END //
DELIMITER ;

CALL insert_seats();
DROP PROCEDURE insert_seats;

-- 插入影评数据
INSERT INTO reviews (user_id, movie_id, rating, content, likes) VALUES
(1, 1, 5, '非常震撼的科幻大片，特效一流，故事感人！', 15),
(2, 1, 4, '剧情紧凑，演员演技在线，值得一看。', 8),
(3, 2, 5, '张艺谋导演的又一力作，反转不断，结局出乎意料！', 12),
(1, 3, 3, '悬疑氛围营造得不错，但结局有点牵强。', 5);

-- 插入影评点赞数据
INSERT INTO review_likes (user_id, review_id) VALUES
(2, 1),
(3, 1),
(1, 3),
(2, 3);

-- 创建视图：用户订单详情
CREATE VIEW user_order_details AS
SELECT 
    o.order_id,
    u.username,
    m.title AS movie_title,
    c.name AS cinema_name,
    h.name AS hall_name,
    s.start_time,
    o.total_price,
    o.order_time,
    o.status
FROM orders o
JOIN users u ON o.user_id = u.user_id
JOIN screenings s ON o.screening_id = s.screening_id
JOIN movies m ON s.movie_id = m.movie_id
JOIN halls h ON s.hall_id = h.hall_id
JOIN cinemas c ON h.cinema_id = c.cinema_id;

-- 创建视图：电影详情与平均评分
CREATE VIEW movie_details AS
SELECT 
    m.movie_id,
    m.title,
    m.director,
    m.actors,
    m.genre,
    m.duration,
    m.release_date,
    m.description,
    m.poster,
    AVG(r.rating) AS average_rating,
    COUNT(r.review_id) AS review_count
FROM movies m
LEFT JOIN reviews r ON m.movie_id = r.movie_id
GROUP BY m.movie_id;

-- 创建索引：优化常见查询
CREATE INDEX idx_screening_movie_time ON screenings(movie_id, start_time);
CREATE INDEX idx_order_user_time ON orders(user_id, order_time);
CREATE INDEX idx_review_movie_rating ON reviews(movie_id, rating);

-- 创建触发器：更新电影评分
DELIMITER //
CREATE TRIGGER update_movie_rating AFTER INSERT ON reviews
FOR EACH ROW
BEGIN
    UPDATE movies 
    SET rating = (SELECT AVG(rating) FROM reviews WHERE movie_id = NEW.movie_id)
    WHERE movie_id = NEW.movie_id;
END //

CREATE TRIGGER update_movie_rating_after_update AFTER UPDATE ON reviews
FOR EACH ROW
BEGIN
    UPDATE movies 
    SET rating = (SELECT AVG(rating) FROM reviews WHERE movie_id = NEW.movie_id)
    WHERE movie_id = NEW.movie_id;
END //

CREATE TRIGGER update_movie_rating_after_delete AFTER DELETE ON reviews
FOR EACH ROW
BEGIN
    UPDATE movies 
    SET rating = (SELECT AVG(rating) FROM reviews WHERE movie_id = OLD.movie_id)
    WHERE movie_id = OLD.movie_id;
END //
DELIMITER ;

-- 创建触发器：更新放映场次剩余座位
DELIMITER //
CREATE TRIGGER update_remaining_seats AFTER INSERT ON order_seats
FOR EACH ROW
BEGIN
    DECLARE screening_id_val INT;
    
    SELECT o.screening_id INTO screening_id_val
    FROM orders o
    WHERE o.order_id = NEW.order_id;
    
    UPDATE screenings 
    SET remaining_seats = remaining_seats - 1
    WHERE screening_id = screening_id_val;
END //

CREATE TRIGGER update_remaining_seats_after_cancel AFTER DELETE ON order_seats
FOR EACH ROW
BEGIN
    DECLARE screening_id_val INT;
    
    SELECT o.screening_id INTO screening_id_val
    FROM orders o
    WHERE o.order_id = OLD.order_id;
    
    UPDATE screenings 
    SET remaining_seats = remaining_seats + 1
    WHERE screening_id = screening_id_val;
END //
DELIMITER ;

-- 创建存储过程：获取可用座位
DELIMITER //
CREATE PROCEDURE get_available_seats(IN screening_id_param INT)
BEGIN
    SELECT 
        s.seat_id,
        s.seat_row,
        s.seat_col,
        s.type,
        CASE 
            WHEN os.seat_id IS NOT NULL THEN 'unavailable'
            ELSE 'available'
        END AS status
    FROM seats s
    JOIN halls h ON s.hall_id = h.hall_id
    JOIN screenings sc ON h.hall_id = sc.hall_id
    LEFT JOIN (
        SELECT os.seat_id
        FROM order_seats os
        JOIN orders o ON os.order_id = o.order_id
        WHERE o.screening_id = screening_id_param AND o.status IN ('pending', 'paid')
    ) os ON s.seat_id = os.seat_id
    WHERE sc.screening_id = screening_id_param
    ORDER BY s.seat_row, s.seat_col;
END //
DELIMITER ;

-- 创建存储过程：创建订单
DELIMITER //
CREATE PROCEDURE create_order(IN user_id_param INT, IN screening_id_param INT, IN seat_ids TEXT, OUT order_id_out INT)
BEGIN
    DECLARE price_val DECIMAL(10,2);
    DECLARE seat_count INT;
    
    -- 获取票价
    SELECT price INTO price_val FROM screenings WHERE screening_id = screening_id_param;
    
    -- 计算座位数量
    SET seat_count = LENGTH(seat_ids) - LENGTH(REPLACE(seat_ids, ',', '')) + 1;
    
    -- 开始事务
    START TRANSACTION;
    
    -- 创建订单
    INSERT INTO orders (user_id, screening_id, total_price) 
    VALUES (user_id_param, screening_id_param, price_val * seat_count);
    
    SET order_id_out = LAST_INSERT_ID();
    
    -- 插入订单座位
    SET @sql = CONCAT('INSERT INTO order_seats (order_id, seat_id) VALUES ');
    SET @seat_list = REPLACE(seat_ids, ',', CONCAT(',', order_id_out, '), (', order_id_out, ','));
    SET @sql = CONCAT(@sql, '(', order_id_out, ',', @seat_list, ')');
    
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
    
    -- 提交事务
    COMMIT;
END //
DELIMITER ;

-- 结束
SELECT '数据库创建完成！' AS message;