-- =====================================================================
-- bonus.sql : 보너스 과제 (schema.sql, data.sql 실행 직후 새 DB에서 실행)
--
--   보너스 1. 같은 요구를 JOIN / 서브쿼리 두 방식으로 풀고 비교하기   (B01, B02)
--   보너스 2. FK 에러를 일부러 내 보고, 왜 막히는지와 해결 방법 기록 (B03 ~ B06)
--   보너스 3. 미니 리포트 - 핵심 지표 3개를 구하는 SQL               (B07 ~ B09)
--
--   queries.sql 의 UPDATE/DELETE 가 적용되지 않은 초기 데이터 기준이다.
--   (run.py 는 bonus.sql 을 별도의 깨끗한 DB 에서 실행한다)
-- =====================================================================

PRAGMA foreign_keys = ON;  -- [SQLite 전용]


-- =====================================================================
-- 보너스 1. 같은 요구를 JOIN / 서브쿼리 두 방식으로 풀기
-- 요구: "케이크 카테고리 메뉴를 한 번이라도 주문한 고객 목록"
-- =====================================================================

-- [B01] JOIN 방식 | 4개 테이블을 이어 붙인 뒤, 한 고객이 여러 번 나올 수 있어 DISTINCT로 중복 제거
--   customer -> orders -> order_item -> menu -> category 를 FK 를 따라 차례로 이어 붙인다.
--   조인 결과는 "주문 상세 1행 = 1행"이므로, 케이크를 2번 주문한 고객은 2행으로 나온다.
--   DISTINCT 는 SELECT 결과에서 완전히 같은 행을 하나만 남긴다.
--   장점: 필요하면 SELECT 에 o.ordered_at, m.name 등을 추가해 "언제 무엇을" 샀는지도 바로 보여줄 수 있다.
SELECT DISTINCT cu.id, cu.name
FROM customer cu
INNER JOIN orders     o  ON o.customer_id = cu.id
INNER JOIN order_item oi ON oi.order_id   = o.id
INNER JOIN menu       m  ON m.id          = oi.menu_id
INNER JOIN category   c  ON c.id          = m.category_id
WHERE c.name = '케이크'
ORDER BY cu.id;

-- [B02] 서브쿼리 방식 | 안쪽부터 "케이크 메뉴 -> 그 메뉴가 담긴 주문 -> 그 주문의 고객" 순으로 좁혀 나감
--   가장 안쪽부터 읽는다.
--     (1) category 에서 '케이크'의 id               -> 7
--     (2) 그 카테고리에 속한 menu.id 목록           -> (15, 16)
--     (3) 그 메뉴가 담긴 order_item.order_id 목록   -> (2, 5, 10, 14, 17)
--     (4) 그 주문을 한 orders.customer_id 목록      -> (2, 4, 7, 4, 6)
--     (5) 바깥 쿼리: 그 목록에 포함된 고객
--   IN 은 "목록에 들어 있는지"만 보기 때문에 고객 4번이 목록에 두 번 있어도 결과에는 한 번만 나온다.
--   -> DISTINCT 없이도 중복이 생기지 않는다. 대신 결과에는 customer 의 컬럼만 쓸 수 있다.
--   (1) 처럼 = (SELECT ...) 로 비교하려면 서브쿼리 결과가 반드시 1행이어야 한다. (category.name 이 UNIQUE 라서 보장됨)
SELECT cu.id, cu.name
FROM customer cu
WHERE cu.id IN (
    SELECT o.customer_id
    FROM orders o
    WHERE o.id IN (
        SELECT oi.order_id
        FROM order_item oi
        WHERE oi.menu_id IN (
            SELECT m.id
            FROM menu m
            WHERE m.category_id = (SELECT id FROM category WHERE name = '케이크')
        )
    )
)
ORDER BY cu.id;


-- =====================================================================
-- 보너스 2. 데이터 정합성 깨뜨려 보기 (FK 에러)
-- =====================================================================

-- [B03] FK 위반 (자식 INSERT) | 존재하지 않는 고객(999번)의 주문을 넣으면 거부된다
--   orders.customer_id 는 customer.id 를 참조한다.
--   customer 에 id = 999 인 행이 없으므로 "누구의 주문인지 알 수 없는" 데이터가 된다.
--   -> 기대 결과: ERROR: FOREIGN KEY constraint failed
INSERT INTO orders (id, customer_id, ordered_at, status)
VALUES (100, 999, '2026-10-12 11:00:00', 'ORDERED');

-- [B04] FK 위반 (부모 DELETE) | 주문 이력이 있는 고객(1번)을 삭제하면 자식(orders)이 고아가 되므로 거부된다
--   FK 는 자식을 넣을 때뿐 아니라 부모를 지울 때도 검사한다.
--   1번 고객을 지우면 그 고객의 주문 4건이 존재하지 않는 고객을 가리키게 된다(고아 데이터).
--   orders.customer_id FK 에 ON DELETE 옵션이 없으므로(기본값: 삭제 금지) 에러가 난다.
--   해결 방법:
--     (a) 자식(주문 -> 주문 상세)을 먼저 지운 뒤 부모를 지운다.
--     (b) 스키마에서 ON DELETE CASCADE(같이 삭제) 또는 ON DELETE SET NULL(연결만 끊기)을 지정한다.
--     (c) 실무에서는 아예 지우지 않고 탈퇴 여부 컬럼을 두는 방식(소프트 삭제)을 많이 쓴다.
DELETE FROM customer WHERE id = 1;

-- [B05] FK 위반 (자식 UPDATE) | 주문 상세의 메뉴를 없는 메뉴(999번)로 바꾸는 것도 거부된다
--   INSERT 때만이 아니라, 이미 있는 행의 FK 값을 UPDATE 로 바꿀 때도 검사한다.
UPDATE order_item SET menu_id = 999 WHERE id = 1;

-- [B06] 올바른 해결 | 부모(고객)를 먼저 만들고, 그 id로 자식(주문)을 넣으면 성공한다
--   B03 이 실패한 이유는 부모가 없었기 때문이므로, 순서를 "부모 INSERT -> 자식 INSERT" 로 바꾼다.
--   마지막 SELECT 에서 JOIN 이 성공하는 것으로 두 행이 올바르게 연결되었음을 확인한다.
INSERT INTO customer (id, name, phone, grade, joined_at)
VALUES (13, '신규고객', '010-1111-0013', 'BASIC', '2026-10-12');

INSERT INTO orders (id, customer_id, ordered_at, status)
VALUES (100, 13, '2026-10-12 11:00:00', 'ORDERED');

SELECT o.id AS order_id, o.customer_id, cu.name, o.status
FROM orders o
INNER JOIN customer cu ON cu.id = o.customer_id
WHERE o.id = 100;

-- 실습용 데이터 정리 (아래 미니 리포트에 영향을 주지 않도록).
--   지울 때는 넣을 때와 반대로 자식 -> 부모 순서. (부모를 먼저 지우면 B04 와 같은 FK 에러가 난다)
DELETE FROM orders   WHERE id = 100;
DELETE FROM customer WHERE id = 13;


-- =====================================================================
-- 보너스 3. 미니 리포트 - 이 DB로 뽑을 수 있는 핵심 지표 3개
-- =====================================================================

-- [B07] 지표 1: 월별 매출 추이와 전월 대비 증감 | 매출이 늘고 있는지 줄고 있는지 확인한다
--       (윈도우 함수 LAG 사용 - SQLite 3.25+, MySQL 8+, PostgreSQL 지원)
--   안쪽 쿼리(monthly) : 월별 매출 합계 (queries.sql Q12 와 같은 방식)
--   LAG(revenue) OVER (ORDER BY month) : 월 순서로 정렬했을 때 "바로 앞 행"의 revenue 값
--     -> 이번 달 - 지난달 = 전월 대비 증감. 첫 달은 앞 행이 없으므로 NULL 이 나온다.
--   윈도우 함수는 GROUP BY 처럼 행을 합치지 않고, 각 행을 그대로 둔 채 주변 행의 값을 참고해 계산한다.
SELECT month,
       revenue,
       revenue - LAG(revenue) OVER (ORDER BY month) AS diff_from_prev_month
FROM (
    SELECT SUBSTR(o.ordered_at, 1, 7)        AS month,
           SUM(oi.quantity * oi.unit_price)  AS revenue
    FROM orders o
    INNER JOIN order_item oi ON oi.order_id = o.id
    WHERE o.status <> 'CANCELED'
    GROUP BY SUBSTR(o.ordered_at, 1, 7)
) monthly
ORDER BY month;

-- [B08] 지표 2: 카테고리별 매출과 매출 비중(%) | 어떤 카테고리가 매출을 견인하는지 확인한다
--   비중(%) = 카테고리 매출 / 전체 매출 * 100
--   전체 매출은 스칼라 서브쿼리로 한 번 구해서 모든 행의 분모로 쓴다.
--   100.0 처럼 실수를 곱하는 이유: 정수끼리 나누면 소수점이 버려진다. (예: 68500 / 224400 = 0)
SELECT c.name                                   AS category,
       SUM(oi.quantity * oi.unit_price)         AS revenue,
       ROUND(100.0 * SUM(oi.quantity * oi.unit_price) /
             (SELECT SUM(oi2.quantity * oi2.unit_price)
              FROM order_item oi2
              INNER JOIN orders o2 ON o2.id = oi2.order_id
              WHERE o2.status <> 'CANCELED'), 1) AS share_pct
FROM category c
INNER JOIN menu       m  ON m.category_id = c.id
INNER JOIN order_item oi ON oi.menu_id    = m.id
INNER JOIN orders     o  ON o.id          = oi.order_id
WHERE o.status <> 'CANCELED'
GROUP BY c.id, c.name
ORDER BY revenue DESC;

-- [B09] 지표 3: 재방문율 | 주문한 고객 중 2회 이상 주문한 고객의 비율(취소 제외)
--   안쪽 쿼리(per_customer) : 고객별 주문 횟수 (주문한 고객 1명당 1행)
--   COUNT(*)                : 주문한 적 있는 고객 수 (분모)
--   SUM(CASE WHEN ... THEN 1 ELSE 0 END) : 조건에 맞는 행만 1로 세는 "조건부 개수" 패턴 (분자)
SELECT COUNT(*)                                             AS ordered_customers,
       SUM(CASE WHEN order_count >= 2 THEN 1 ELSE 0 END)    AS returning_customers,
       ROUND(100.0 * SUM(CASE WHEN order_count >= 2 THEN 1 ELSE 0 END) / COUNT(*), 1) AS return_rate_pct
FROM (
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    WHERE status <> 'CANCELED'
    GROUP BY customer_id
) per_customer;
