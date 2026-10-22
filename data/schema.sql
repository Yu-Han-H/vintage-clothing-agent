-- ============================================================
-- vintage_shop 数据库建表脚本
-- 用法：mysql -u vintage -p vintage_shop < schema.sql
-- ============================================================

-- 商品主表
CREATE TABLE products (
  sku VARCHAR(32) PRIMARY KEY,
  category VARCHAR(20) NOT NULL COMMENT '品类: top/pants/skirt/jacket',
  gender VARCHAR(10) NULL COMMENT '适用性别: male/female/unisex',
  brand VARCHAR(64) NULL,
  price DECIMAL(10,2) NULL COMMENT '价格允许后补',
  `condition` VARCHAR(20) NULL COMMENT '成色: new/like_new/good',
  source_platform VARCHAR(20) NULL COMMENT '来源平台',
  description TEXT NULL COMMENT '详情页原文/卖点',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 商品尺寸表（一个 sku 一条）
CREATE TABLE measurements (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  sku VARCHAR(32) NOT NULL,
  chest_cm INT NULL COMMENT '胸围',
  shoulder_cm INT NULL COMMENT '肩宽',
  length_cm INT NULL COMMENT '衣长，外套存后衣长',
  sleeve_cm INT NULL COMMENT '袖长',
  waist_cm INT NULL COMMENT '腰围',
  hip_cm INT NULL COMMENT '臀围',
  FOREIGN KEY (sku) REFERENCES products(sku) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 商品图片表（图片文件存 static/images/，库里只存 URL）
CREATE TABLE images (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  sku VARCHAR(32) NOT NULL,
  url VARCHAR(255) NOT NULL,
  sort_order INT DEFAULT 0,
  FOREIGN KEY (sku) REFERENCES products(sku) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 顾客表
CREATE TABLE customers (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  height_cm INT NULL COMMENT '身高',
  weight_kg INT NULL COMMENT '体重',
  gender VARCHAR(10) NULL,
  preference TEXT NULL COMMENT '风格与宽松度偏好',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
