-- =====================================================================
-- queries.sql : 핵심 쿼리 17개 (schema.sql, data.sql 실행 후 실행)
--   기본 조회 4 / 조인 4 / 집계 4 / 서브쿼리 2 / 인덱스 1 / 수정·삭제 2
--
-- 기준일: 2026-10-12
--   DATE('now') 처럼 "오늘"을 쓰면 실행하는 날마다 결과가 달라지므로,
--   날짜 조건은 고정값으로 작성했다.
--
-- 작성 규칙
--   각 쿼리 위의 [Qnn] 줄이 "무엇을 확인하는 쿼리인지"에 대한 한 줄 설명이다.
--   그 아래 주석은 쿼리에 쓰인 문법과 동작 원리에 대한 설명이다.
--   (run.py 는 [Qnn] 줄을 기준으로 결과를 results/queries/Qnn.txt 로 저장한다.)
--
-- SELECT 문이 실제로 처리되는 순서 (작성 순서와 다르다)
--   FROM / JOIN  ->  WHERE  ->  GROUP BY  ->  HAVING  ->  SELECT  ->  ORDER BY  ->  LIMIT
--   예) WHERE 에서는 SELECT 에서 붙인 별칭을 쓸 수 없지만, ORDER BY 에서는 쓸 수 있다.
-- =====================================================================

-- [SQLite 전용] FK 검사 켜기. 연결마다 실행해야 한다.
PRAGMA foreign_keys = ON;


-- =====================================================================
-- 1. 기본 조회 (WHERE / ORDER BY / LIMIT)
--    하나의 테이블에서 조건에 맞는 행을 골라(WHERE), 정렬하고(ORDER BY), 개수를 자른다(LIMIT).
-- =====================================================================

-- [Q01] 기본 조회 | 판매 중인 메뉴 중 가격이 가장 비싼 상위 5개를 확인한다
--   WHERE is_available = 1 : 판매 종료(0)된 메뉴는 제외
--   ORDER BY price DESC    : 가격 내림차순(비싼 것부터)
--            , id          : 가격이 같으면 id 오름차순 -> 실행할 때마다 순서가 같도록 보장
--   LIMIT 5                : 정렬된 결과에서 앞의 5행만 가져온다 ("TOP N" 패턴)
SELECT id, name, price
FROM menu
WHERE is_available = 1
ORDER BY price DESC, id
LIMIT 5;

-- [Q02] 기본 조회 | GOLD 등급 고객을 오래된 가입 순으로 확인한다
--   문자열 비교는 작은따옴표('GOLD')를 쓴다. (큰따옴표는 컬럼/테이블 이름에 쓰는 것이 표준)
--   joined_at 은 'YYYY-MM-DD' 형식이므로 문자열 정렬 순서 = 날짜 순서이다.
SELECT id, name, phone, joined_at
FROM customer
WHERE grade = 'GOLD'
ORDER BY joined_at;

-- [Q03] 기본 조회 | 기준일(2026-10-12) 최근 7일간 들어온 주문을 최신순으로 확인한다
--   ordered_at 은 'YYYY-MM-DD HH:MM:SS' 문자열로 저장되어 있다.
--   '2026-10-05 09:10:00' >= '2026-10-05' 처럼 앞에서부터 글자를 비교하므로,
--   날짜만 적어도 그 날 0시 이후의 모든 주문이 포함된다.
SELECT id, customer_id, ordered_at, status
FROM orders
WHERE ordered_at >= '2026-10-05'
ORDER BY ordered_at DESC;

-- [Q04] 기본 조회 | 이름에 '라떼'가 들어간 메뉴를 검색해 싼 순으로 확인한다
--   LIKE '%라떼%' : % 는 "0글자 이상의 아무 문자"를 뜻한다. -> 앞뒤에 무엇이 있든 '라떼'를 포함하면 일치
--   (참고: '라떼%' 는 '라떼'로 시작, '%라떼' 는 '라떼'로 끝나는 이름)
--   판매 종료 메뉴(호박라떼)도 검색 결과에는 나오도록 is_available 조건은 걸지 않았다.
SELECT id, name, price, is_available
FROM menu
WHERE name LIKE '%라떼%'
ORDER BY price, id;


-- =====================================================================
-- 2. 조인 (INNER JOIN 3 / LEFT JOIN 1)
--    FK 로 연결된 여러 테이블을 ON 조건(보통 "자식.FK = 부모.PK")으로 이어 붙여 한 번에 조회한다.
--    INNER JOIN : 양쪽 테이블 모두에 짝이 있는 행만 남는다.
--    LEFT JOIN  : 왼쪽 테이블의 행은 짝이 없어도 모두 남고, 오른쪽 값은 NULL 로 채워진다.
-- =====================================================================

-- [Q05] INNER JOIN | 메뉴마다 카테고리 이름을 붙여서 확인한다 (category 1:N menu)
--   menu 테이블에는 category_id(숫자)만 있어서 "커피"라는 이름을 알 수 없다.
--   m.category_id = c.id 로 짝을 지으면 각 메뉴 행 옆에 해당 카테고리 행이 붙는다.
--   m, c 는 테이블 별칭(alias). 컬럼 이름이 겹칠 때(id, name) 어느 테이블 것인지 구분해 준다.
SELECT c.name AS category, m.name AS menu, m.price
FROM menu m
INNER JOIN category c ON c.id = m.category_id
ORDER BY c.id, m.price;

-- [Q06] INNER JOIN | 10월 주문의 상세 내역(누가, 무엇을, 몇 개, 얼마에)을 확인한다 (4개 테이블 조인)
--   orders --(customer_id)--> customer   : 누가 주문했는지
--   orders <--(order_id)--   order_item  : 주문에 담긴 메뉴들 (주문 1건 -> 상세 여러 행)
--   order_item --(menu_id)--> menu       : 메뉴 이름
--   주문 1건에 메뉴가 2개면 결과도 2행이 된다. (1:N 조인을 하면 N 쪽 행 수만큼 늘어난다)
--   quantity * unit_price 처럼 SELECT 절에서 계산한 값에도 별칭(AS line_total)을 붙일 수 있다.
SELECT o.id                         AS order_id,
       o.ordered_at,
       cu.name                      AS customer,
       m.name                       AS menu,
       oi.quantity,
       oi.quantity * oi.unit_price  AS line_total
FROM orders o
INNER JOIN customer   cu ON cu.id      = o.customer_id
INNER JOIN order_item oi ON oi.order_id = o.id
INNER JOIN menu       m  ON m.id       = oi.menu_id
WHERE o.ordered_at >= '2026-10-01'
ORDER BY o.id, oi.id;

-- [Q07] INNER JOIN | 아직 처리되지 않은(ORDERED) 주문과 고객 연락처를 확인한다
--   매장 직원이 "준비해야 할 주문 + 호출할 연락처"를 보는 화면을 가정한 쿼리.
--   JOIN 으로 테이블을 붙인 뒤 WHERE 로 상태를 걸러낸다.
SELECT o.id AS order_id, o.ordered_at, cu.name AS customer, cu.phone
FROM orders o
INNER JOIN customer cu ON cu.id = o.customer_id
WHERE o.status = 'ORDERED'
ORDER BY o.ordered_at;

-- [Q08] LEFT JOIN | 한 번도 주문된 적 없는 메뉴를 확인한다 (판매 이력이 없으면 oi 쪽이 NULL)
--   menu 를 왼쪽에 두고 LEFT JOIN 하면, 주문 상세가 하나도 없는 메뉴도 결과에 남는다.
--   이때 짝이 없는 메뉴는 oi.* 컬럼이 전부 NULL 이 된다.
--   -> WHERE oi.id IS NULL 로 "짝이 없는 행"만 고르면 판매 이력이 없는 메뉴가 된다.
--   주의: NULL 은 '= NULL' 로 비교할 수 없고 반드시 IS NULL / IS NOT NULL 을 써야 한다.
--   (같은 쿼리를 INNER JOIN 으로 바꾸면 짝이 없는 메뉴가 처음부터 빠져서 결과가 0행이 된다.)
SELECT m.id, m.name, m.price
FROM menu m
LEFT JOIN order_item oi ON oi.menu_id = m.id
WHERE oi.id IS NULL
ORDER BY m.id;


-- =====================================================================
-- 3. 집계 (COUNT / SUM / AVG + GROUP BY)
--    GROUP BY 로 같은 값끼리 묶은 뒤, 묶음마다 집계 함수로 하나의 값을 계산한다.
--    규칙: GROUP BY 를 쓰면 SELECT 에는 "묶는 기준 컬럼"이나 "집계 함수"만 올 수 있다.
-- =====================================================================

-- [Q09] 집계 | 카테고리별 메뉴 수와 평균 가격을 확인한다 (COUNT, AVG)
--   GROUP BY c.id, c.name : 카테고리 하나당 결과 1행
--   COUNT(m.id)           : 그 카테고리에 속한 메뉴 수 (NULL 이 아닌 값의 개수)
--   AVG(m.price)          : 평균 가격. ROUND() 로 소수점 반올림
--   (SQLite 의 ROUND 는 실수를 돌려주므로 결과가 5000.0 처럼 표시된다)
SELECT c.name               AS category,
       COUNT(m.id)          AS menu_count,
       ROUND(AVG(m.price))  AS avg_price
FROM category c
INNER JOIN menu m ON m.category_id = c.id
GROUP BY c.id, c.name
ORDER BY menu_count DESC, c.id;

-- [Q10] 집계 | 고객별 주문 횟수와 총 결제 금액 랭킹을 확인한다 (취소 주문 제외, COUNT + SUM)
--   customer - orders - order_item 을 조인하면 "주문 상세 1행 = 결과 1행"이 된다.
--   그래서 COUNT(o.id) 를 그냥 세면 주문 횟수가 아니라 상세 행 수가 나온다.
--   -> COUNT(DISTINCT o.id) 로 중복을 제거해야 실제 주문 횟수가 된다.
--   SUM(quantity * unit_price) : 상세 행마다 금액을 계산해서 고객별로 모두 더한다.
--   WHERE 는 GROUP BY 전에 실행되므로, 취소 주문은 집계하기 전에 미리 빠진다.
SELECT cu.id,
       cu.name,
       COUNT(DISTINCT o.id)                AS order_count,
       SUM(oi.quantity * oi.unit_price)    AS total_amount
FROM customer cu
INNER JOIN orders     o  ON o.customer_id = cu.id
INNER JOIN order_item oi ON oi.order_id   = o.id
WHERE o.status <> 'CANCELED'
GROUP BY cu.id, cu.name
ORDER BY total_amount DESC;

-- [Q11] 집계 | 가장 많이 팔린 메뉴 TOP 5(판매 수량 기준)와 매출을 확인한다 (HAVING으로 2개 이상 팔린 메뉴만)
--   WHERE  : 묶기 "전" 개별 행을 거른다     -> 취소 주문의 상세 행 제외
--   HAVING : 묶은 "후" 그룹을 거른다        -> 총 판매 수량이 2개 이상인 메뉴만
--   (집계 함수 SUM(...) 에 대한 조건은 WHERE 에 쓸 수 없고 HAVING 에 써야 한다)
--   ORDER BY + LIMIT 5 로 판매 수량 순위 상위 5개만 남긴다.
SELECT m.name,
       SUM(oi.quantity)                  AS sold_qty,
       SUM(oi.quantity * oi.unit_price)  AS revenue
FROM order_item oi
INNER JOIN menu   m ON m.id = oi.menu_id
INNER JOIN orders o ON o.id = oi.order_id
WHERE o.status <> 'CANCELED'
GROUP BY m.id, m.name
HAVING SUM(oi.quantity) >= 2
ORDER BY sold_qty DESC, revenue DESC
LIMIT 5;

-- [Q12] 집계 | 월별 주문 건수, 매출, 주문당 평균 금액(객단가)을 확인한다 (취소 제외)
--   두 단계로 집계한다.
--   1단계 (FROM 안의 서브쿼리 t) : 주문 상세를 주문별로 묶어 "주문 1건의 총액(order_total)"을 만든다.
--   2단계 (바깥 쿼리)            : 그 주문들을 월별로 다시 묶어 건수, 합계, 평균을 구한다.
--   한 번에 AVG(quantity * unit_price) 를 구하면 "주문당 평균"이 아니라 "상세 행당 평균"이 되어 틀린다.
--   SUBSTR(ordered_at, 1, 7) : 1번째 글자부터 7글자를 잘라 '2026-10' 형식의 월을 만든다.
--   (MySQL 은 DATE_FORMAT, PostgreSQL 은 TO_CHAR 도 있지만, SUBSTR 은 세 DB 모두에서 동작한다)
SELECT SUBSTR(t.ordered_at, 1, 7)  AS month,
       COUNT(*)                    AS order_count,
       SUM(t.order_total)          AS revenue,
       ROUND(AVG(t.order_total))   AS avg_order_amount
FROM (
    SELECT o.id, o.ordered_at, SUM(oi.quantity * oi.unit_price) AS order_total
    FROM orders o
    INNER JOIN order_item oi ON oi.order_id = o.id
    WHERE o.status <> 'CANCELED'
    GROUP BY o.id, o.ordered_at
) t
GROUP BY SUBSTR(t.ordered_at, 1, 7)
ORDER BY month;


-- =====================================================================
-- 4. 서브쿼리
--    쿼리 안에 괄호로 넣은 또 다른 SELECT. 안쪽 쿼리 결과를 바깥 쿼리의 조건이나 값으로 쓴다.
-- =====================================================================

-- [Q13] 서브쿼리 | 주문 기록이 한 번도 없는 고객을 확인한다 (NOT IN)
--   안쪽 쿼리 : 주문한 적 있는 고객 id 목록       예) (1, 2, 1, 3, 4, ...)
--   바깥 쿼리 : 그 목록에 "없는" 고객만 고른다.
--   Q08 의 LEFT JOIN + IS NULL 과 같은 종류의 문제를 서브쿼리로 푼 것이다.
--   주의: 안쪽 결과에 NULL 이 하나라도 있으면 NOT IN 은 아무 행도 돌려주지 않는다.
--         여기서는 orders.customer_id 가 NOT NULL 이라 안전하다.
SELECT id, name, joined_at
FROM customer
WHERE id NOT IN (SELECT customer_id FROM orders)
ORDER BY id;

-- [Q14] 서브쿼리 | 전체 메뉴 평균 가격보다 비싼 메뉴를 확인한다 (스칼라 서브쿼리)
--   스칼라 서브쿼리 : 결과가 딱 1행 1열(값 하나)인 서브쿼리. 일반 값처럼 비교식이나 SELECT 절에 쓸 수 있다.
--   WHERE price > (SELECT AVG(price) FROM menu) : 평균(약 5,440원)보다 비싼 메뉴만
--   SELECT 절에도 같은 서브쿼리를 넣어 비교 기준이 된 평균값을 함께 보여준다.
--   (WHERE price > AVG(price) 처럼 쓰면 에러: WHERE 에서는 집계 함수를 바로 쓸 수 없다)
SELECT name, price,
       (SELECT ROUND(AVG(price)) FROM menu) AS avg_price
FROM menu
WHERE price > (SELECT AVG(price) FROM menu)
ORDER BY price DESC, id;


-- =====================================================================
-- 5. 인덱스
--    책 뒤의 "찾아보기"처럼, 컬럼 값 -> 행 위치를 정렬해 저장해 두는 별도 자료구조(B-Tree).
--    장점: WHERE / JOIN / ORDER BY 에서 테이블 전체를 훑지(SCAN) 않고 필요한 행만 바로 찾는다(SEARCH).
--    단점: 저장 공간을 더 쓰고, INSERT/UPDATE/DELETE 때 인덱스도 같이 고쳐야 해서 쓰기가 느려진다.
--    -> "자주 검색·조인·정렬하는 컬럼"에만 만든다. (PK, UNIQUE 컬럼은 DB 가 자동으로 인덱스를 만든다)
-- =====================================================================

-- [Q15] 인덱스 | 주문 테이블의 고객 FK·주문일시에 인덱스를 만들고, 조회 시 실제로 사용되는지 확인한다
-- 적용 이유: orders.customer_id 는 고객별 주문 조회/조인에, ordered_at 은 기간 검색·정렬에 자주 쓰이므로
--           인덱스가 없으면 매번 전체 테이블을 훑어야 한다(데이터가 많아질수록 느려짐).
--   FK 컬럼은 PK 와 달리 인덱스가 자동으로 생기지 않으므로 직접 만들어 주는 것이 일반적이다.
CREATE INDEX idx_orders_customer_id ON orders (customer_id);
CREATE INDEX idx_orders_ordered_at  ON orders (ordered_at);

-- [SQLite 전용] EXPLAIN QUERY PLAN: 쿼리를 실제로 실행하지 않고 "어떻게 실행할지" 계획만 보여준다.
--   결과의 detail 이  'SCAN orders'                    -> 전체 테이블 탐색 (인덱스 미사용)
--                    'SEARCH orders USING INDEX ...'  -> 인덱스로 필요한 행만 탐색
EXPLAIN QUERY PLAN
SELECT * FROM orders WHERE customer_id = 1;

EXPLAIN QUERY PLAN
SELECT * FROM orders WHERE ordered_at >= '2026-10-01';


-- =====================================================================
-- 6. 데이터 수정 및 삭제 (UPDATE / DELETE)
--    ※ 데이터가 바뀌므로 맨 마지막에 실행한다. 변경 전/후를 SELECT 로 함께 확인한다.
--    ※ UPDATE / DELETE 에 WHERE 를 빠뜨리면 테이블의 "모든 행"이 바뀌거나 지워지므로 항상 주의한다.
--       실무에서는 같은 WHERE 조건으로 SELECT 를 먼저 실행해 대상 행을 확인한 뒤 실행한다.
-- =====================================================================

-- [Q16] UPDATE | 누적 결제 금액(취소 제외)이 30,000원 이상인 고객을 GOLD 등급으로 승급한다
--   1) 변경 전: GOLD 가 아닌 고객 목록 확인
--   2) UPDATE : 서브쿼리가 "누적 결제액 30,000원 이상인 고객 id 목록"을 만들고,
--               그 목록에 포함되면서 아직 GOLD 가 아닌 고객만 grade 를 'GOLD' 로 바꾼다.
--               (이미 GOLD 인 고객은 grade <> 'GOLD' 조건으로 제외 -> 영향받은 행 수가 실제 승급 인원이 된다)
--   3) 변경 후: GOLD 고객 목록으로 결과 확인
SELECT id, name, grade FROM customer WHERE grade <> 'GOLD' ORDER BY id;

UPDATE customer
SET grade = 'GOLD'
WHERE grade <> 'GOLD'
  AND id IN (
      SELECT o.customer_id
      FROM orders o
      INNER JOIN order_item oi ON oi.order_id = o.id
      WHERE o.status <> 'CANCELED'
      GROUP BY o.customer_id
      HAVING SUM(oi.quantity * oi.unit_price) >= 30000
  );

SELECT id, name, grade FROM customer WHERE grade = 'GOLD' ORDER BY id;

-- [Q17] DELETE | 취소된 주문을 삭제하고, ON DELETE CASCADE로 주문 상세도 함께 지워지는지 확인한다
--   order_item.order_id 에는 ON DELETE CASCADE 가 걸려 있다. (schema.sql 참고)
--   -> 부모(orders) 행을 지우면 그 주문을 참조하던 자식(order_item) 행도 DB 가 자동으로 지운다.
--   CASCADE 가 없었다면 자식 행이 남아 있어서 FK 에러가 났을 것이다. (bonus.sql 의 B04 참고)
--   SELECT 절에 스칼라 서브쿼리 3개를 나란히 써서, 여러 테이블의 행 수를 한 줄로 비교한다.
SELECT (SELECT COUNT(*) FROM orders)                         AS orders_before,
       (SELECT COUNT(*) FROM order_item)                     AS items_before,
       (SELECT COUNT(*) FROM orders WHERE status = 'CANCELED') AS canceled;

DELETE FROM orders
WHERE status = 'CANCELED';

SELECT (SELECT COUNT(*) FROM orders)                         AS orders_after,
       (SELECT COUNT(*) FROM order_item)                     AS items_after,
       (SELECT COUNT(*) FROM orders WHERE status = 'CANCELED') AS canceled;
