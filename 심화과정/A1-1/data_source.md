# 데이터셋 출처 및 전처리 기록

## 1. 데이터셋 기본 정보

- **데이터셋 이름:** Brazilian E-Commerce Public Dataset by Olist
- **제공 기관:** Olist
- **원본 URL:** https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- **다운로드 날짜:** 실제 다운로드한 날짜 기입
- **데이터 형식:** CSV
- **라이선스:** CC BY-NC-SA 4.0
- **이용 조건:** 저작자 표시, 비상업적 이용, 동일조건변경허락 조건 준수
- **데이터 기간:** 2016년~2018년

## 2. 사용한 파일명

1. `olist_orders_dataset.csv`
2. `olist_customers_dataset.csv`
3. `olist_order_items_dataset.csv`
4. `olist_order_payments_dataset.csv`
5. `olist_order_reviews_dataset.csv`
6. `olist_products_dataset.csv`
7. `olist_sellers_dataset.csv`
8. `olist_geolocation_dataset.csv`
9. `product_category_name_translation.csv`

## 3. 데이터에서 제외하거나 변경한 항목

- 원본 데이터는 별도로 보존한다.
- 날짜형 컬럼은 날짜 분석에 적합한 자료형으로 변환한다.
- 가격 및 결제 금액 컬럼은 숫자형으로 변환한다.
- 결측치와 중복 데이터는 실제 현황을 확인한 후 처리하고 처리 건수를 기록한다.
- 고객 재구매 분석에는 `customer_unique_id`를 사용한다.
- 취소·미배송 주문은 분석 목적에 따라 포함 여부를 결정하고 근거를 기록한다.
- 이상치는 탐지 결과를 먼저 확인하고, 제거가 필요한 경우에만 제거한다.
- 원본 데이터의 컬럼이나 행을 제거·변경한 경우 파일명, 대상, 건수 및 사유를 기록한다.
- 기본 데이터에는 실제 상품 이미지가 포함되어 있지 않으므로 이미지 배열 분석은 별도 데이터가 필요하다.

## 4. 라이선스 및 이용 시 주의사항

이 데이터셋은 CC BY-NC-SA 4.0 조건으로 공개되어 있다. 출처를 표시하고 비상업적 이용 및 변경 데이터의 동일조건변경허락 의무를 확인한다. 상업적 이용이 필요한 경우 원 제공처에 별도 허가 필요 여부를 확인한다.

## 5. 실제 전처리 내역

- 처리 일자: 2026-11-24
- 처리한 파일: `olist_order_items_dataset.csv`(주 분석 대상, 112,650행 × 7컬럼), `olist_products_dataset.csv`, `product_category_name_translation.csv`(상품 정보 조회용)
- 제외한 행 및 컬럼: 원본 파일과 `df`에서 제외한 행·컬럼 없음. 이상치(price가 IQR 상한 277.4 초과인 8,427행, 약 7.5%)는 처리 전후 비교를 위해 별도 Series(`after`)에서만 제외했고 원본 `df`에는 그대로 남겼다.
- 변경한 자료형 및 컬럼: 추가 컬럼 3개 — `product_category_name_english`(카테고리 영문명), `name_word_count`(카테고리명 단어 수), `name_length`(상품명 글자 수). `df`에 `product_id` 기준으로 값을 붙였고 행 수는 112,650으로 변함없다. `shipping_limit_date`의 날짜형 변환: [기입]
- 결측치 처리 내역: `order_items`의 7개 컬럼 모두 결측 0건이라 처리하지 않았다. 추가한 `name_length`에는 결측 1,603행이 있다(상품 정보가 없는 610개 상품에 해당). 처리 방식: [기입]
- 중복 데이터 처리 내역: `order_items` 전체 컬럼 기준 중복 행 0건, `products`의 중복 행 0건, `product_id` 중복 0건. 제거한 행 없음.
- 기타 변경 사항 및 사유: 과제 8-1은 상품명(`product_name`)의 단어 수 계산을 요구하나, Olist 데이터에는 상품명 텍스트 컬럼이 없다(`products`에는 `product_category_name`과 상품명 글자 수 `product_name_lenght`만 존재). 따라서 (1) 카테고리명(영문 번역)의 단어 수를 `name_word_count`로, (2) 상품명 글자 수를 `name_length`로 대체해 파생 변수를 만들었다. 카테고리가 비어 있는 상품은 `name_word_count`를 0으로 처리했다.
