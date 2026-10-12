-- =====================================================================
-- schema.sql : 카페 주문 관리 DB 스키마 (DBMS: SQLite 3)
-- 실행 순서: schema.sql -> data.sql -> queries.sql
--
-- [도메인]
--   카페에서 고객이 메뉴를 주문한다. 주문 한 건에는 여러 메뉴가 담길 수 있다.
--
-- [테이블 관계 (1:N)]
--   category 1 : N menu        (menu.category_id    -> category.id)   한 카테고리에 여러 메뉴
--   customer 1 : N orders      (orders.customer_id  -> customer.id)   한 고객이 여러 번 주문
--   orders   1 : N order_item  (order_item.order_id -> orders.id)     한 주문에 여러 메뉴
--   menu     1 : N order_item  (order_item.menu_id  -> menu.id)       한 메뉴가 여러 주문에 등장
--
--   orders 와 menu 는 서로 N:M 관계(주문 하나에 메뉴 여러 개, 메뉴 하나가 여러 주문에)이다.
--   관계형 DB 는 N:M 을 직접 표현할 수 없어서, 중간 테이블 order_item 을 두고
--   1:N 관계 두 개로 나누어 표현한다.
--
-- [용어]
--   PK (Primary Key) : 행을 하나로 구별하는 값. NULL 불가, 중복 불가.
--   FK (Foreign Key) : 다른 테이블의 PK 를 가리키는 값. 가리키는 행이 실제로 있어야 한다.
--   N 쪽(자식) 테이블이 FK 를 가진다. 예) 주문(N)이 고객(1)의 id 를 customer_id 로 가진다.
--
-- [자료형 참고 - SQLite]
--   SQLite 는 VARCHAR(30), DATE, DATETIME 같은 타입 이름을 받아 주지만, 내부적으로는
--   TEXT / INTEGER 등으로 저장하고 길이 제한도 검사하지 않는다.
--   그래도 의미가 드러나도록, 그리고 다른 DB 로 옮기기 쉽도록 표준 타입 이름을 사용했다.
-- =====================================================================

-- [SQLite 전용] SQLite 는 기본적으로 FK 검사가 꺼져 있으므로, 접속(연결)마다 켜 주어야 한다.
--   이 설정이 없으면 FOREIGN KEY 를 선언해도 없는 값을 참조하는 INSERT 가 그대로 통과한다.
PRAGMA foreign_keys = ON;

-- 재실행을 위해 기존 테이블을 지운다.
--   자식 테이블부터 지워야 한다. 부모를 먼저 지우면 자식이 참조할 대상이 사라지기 때문이다.
--   IF EXISTS : 테이블이 없을 때(첫 실행) 에러 없이 넘어간다.
DROP TABLE IF EXISTS order_item;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS menu;
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS category;

-- ---------------------------------------------------------------------
-- category : 메뉴 분류 (커피, 티, 베이커리 ...)
--   다른 테이블을 참조하지 않는 부모 테이블이므로 가장 먼저 만든다.
-- ---------------------------------------------------------------------
CREATE TABLE category (
    id   INTEGER     PRIMARY KEY,           -- [SQLite] INTEGER PRIMARY KEY 는 값을 생략하면 자동으로 번호가 매겨진다
    name VARCHAR(30) NOT NULL UNIQUE        -- 같은 이름의 카테고리가 두 개 생기지 않도록 UNIQUE
);

-- ---------------------------------------------------------------------
-- customer : 고객(회원)
-- ---------------------------------------------------------------------
CREATE TABLE customer (
    id        INTEGER     PRIMARY KEY,
    name      VARCHAR(30) NOT NULL,                     -- 이름은 동명이인이 있을 수 있으므로 UNIQUE 를 걸지 않는다
    phone     VARCHAR(20) NOT NULL UNIQUE,              -- 같은 번호로 중복 가입 불가 (고객을 찾는 실질적인 키)
    grade     VARCHAR(10) NOT NULL DEFAULT 'BASIC'      -- 값을 생략하고 INSERT 하면 'BASIC' 이 들어간다
              CHECK (grade IN ('BASIC', 'SILVER', 'GOLD')),  -- 정해진 세 값 이외에는 저장 불가 (오타 방지)
    joined_at DATE        NOT NULL                      -- 'YYYY-MM-DD'
);

-- ---------------------------------------------------------------------
-- menu : 판매 메뉴 (category 1 : N menu)
-- ---------------------------------------------------------------------
CREATE TABLE menu (
    id           INTEGER     PRIMARY KEY,
    category_id  INTEGER     NOT NULL,                    -- 모든 메뉴는 반드시 하나의 카테고리에 속한다
    name         VARCHAR(50) NOT NULL UNIQUE,
    price        INTEGER     NOT NULL CHECK (price > 0),  -- 원 단위 정수. 0원/음수 가격은 막는다
    is_available INTEGER     NOT NULL DEFAULT 1           -- 1: 판매 중, 0: 판매 종료 (SQLite 에는 BOOLEAN 타입이 없음)
                 CHECK (is_available IN (0, 1)),
    -- category_id 에는 category 테이블에 실제로 존재하는 id 만 들어갈 수 있다.
    FOREIGN KEY (category_id) REFERENCES category (id)
);

-- ---------------------------------------------------------------------
-- orders : 주문 (customer 1 : N orders)
--   ORDER 는 SQL 예약어(ORDER BY)이므로 테이블 이름을 orders 로 했다.
--   주문 "한 건"의 정보(누가, 언제, 상태)만 담고, 무엇을 몇 개 샀는지는 order_item 에 담는다.
-- ---------------------------------------------------------------------
CREATE TABLE orders (
    id          INTEGER     PRIMARY KEY,
    customer_id INTEGER     NOT NULL,                     -- 비회원 주문은 받지 않는다는 가정
    ordered_at  DATETIME    NOT NULL,                     -- 'YYYY-MM-DD HH:MM:SS' (문자열 정렬 = 시간 순서)
    status      VARCHAR(10) NOT NULL DEFAULT 'ORDERED'    -- ORDERED: 접수, COMPLETED: 완료, CANCELED: 취소
                CHECK (status IN ('ORDERED', 'COMPLETED', 'CANCELED')),
    -- ON DELETE 옵션을 지정하지 않았으므로, 주문이 남아 있는 고객은 삭제할 수 없다. (bonus.sql B04 참고)
    FOREIGN KEY (customer_id) REFERENCES customer (id)
);

-- ---------------------------------------------------------------------
-- order_item : 주문 상세 (orders 1 : N order_item, menu 1 : N order_item)
--   한 주문에 담긴 메뉴 하나당 한 행. orders 와 menu 의 N:M 관계를 풀어 주는 중간 테이블이다.
-- ---------------------------------------------------------------------
CREATE TABLE order_item (
    id         INTEGER PRIMARY KEY,
    order_id   INTEGER NOT NULL,
    menu_id    INTEGER NOT NULL,
    quantity   INTEGER NOT NULL CHECK (quantity > 0),     -- 0개 이하 주문 불가
    unit_price INTEGER NOT NULL CHECK (unit_price > 0),   -- 주문 시점 가격
        -- menu.price 를 조인해서 쓰지 않고 따로 저장하는 이유:
        -- 나중에 메뉴 가격이 오르면 과거 주문 금액까지 바뀌어 버리기 때문이다. (영수증은 바뀌면 안 된다)

    -- ON DELETE CASCADE : 부모 주문이 삭제되면 그 주문의 상세 행들도 자동으로 함께 삭제된다.
    --   주문 상세는 주문 없이 의미가 없는 데이터이므로 같이 지우는 것이 자연스럽다. (queries.sql Q17 참고)
    FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
    -- 메뉴는 CASCADE 하지 않는다. 메뉴를 지운다고 과거 판매 기록까지 사라지면 안 되기 때문이다.
    -- (판매를 멈출 때는 삭제 대신 menu.is_available = 0 으로 바꾼다)
    FOREIGN KEY (menu_id)  REFERENCES menu (id),

    -- 복합 UNIQUE : 같은 주문에 같은 메뉴가 두 줄로 들어가지 않게 한다. (2잔이면 quantity = 2 로 표현)
    UNIQUE (order_id, menu_id)
);
