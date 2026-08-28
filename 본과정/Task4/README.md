# Mini Redis

Redis의 핵심 동작을 학습용으로 직접 구현한 CLI 기반 Mini Redis입니다. 실제 Redis 서버에 연결하지 않고, Python 메모리 안에서 `SET`, `GET`, `DEL`, `EXPIRE`, `TTL`, LRU 제거, 메모리 사용량 계산을 직접 처리합니다.

## 실행 방법

Task4 폴더에서 실행합니다.

```powershell
cd C:\Codyssey26\본과정\Task4
python -m mini_redis
```

실행하면 아래 프롬프트가 나타납니다.

```text
mini-redis>
```

종료는 `exit` 또는 `quit`을 입력합니다.

## 명령어

### 문자열 기본 명령

```text
SET key value
GET key
DEL key
EXISTS key
DBSIZE
KEYS
```

값에 공백이 있으면 큰따옴표로 감쌀 수 있습니다.

```text
SET user:1 "Alice Kim"
GET user:1
```

### 메모리 관리

```text
CONFIG SET maxmemory 30
INFO memory
```

`maxmemory`는 바이트 단위입니다. `0`은 무제한입니다. 메모리 계산은 과제 조건대로 아래 공식만 사용합니다.

```text
used_memory = len(utf8(key)) + len(utf8(value)) 의 합
```

메모리가 초과되면 가장 오래 사용하지 않은 키부터 LRU 방식으로 삭제합니다.

### TTL 관리

```text
EXPIRE key seconds
TTL key
```

`EXPIRE`는 키의 만료 시간을 설정합니다. `TTL`은 남은 시간을 초 단위로 보여줍니다.

## 실행 예시

```text
mini-redis> CONFIG SET maxmemory 30
OK
mini-redis> SET user:1 "Alice"
OK
mini-redis> SET user:2 "Bob"
OK
mini-redis> SET user:3 "Charlie"
OK
mini-redis> GET user:1
(nil)
mini-redis> INFO memory
used_memory:22
maxmemory:30
evicted_keys:1
mini-redis> KEYS
1. "user:2"
2. "user:3"
mini-redis> EXPIRE user:2 3
(integer) 1
mini-redis> TTL user:2
(integer) 2
```

## 프로젝트 구조

```text
mini_redis/
├── __init__.py       패키지 표시
├── __main__.py       python -m mini_redis 실행 진입점
├── cli.py            REPL, 명령어 파싱, Redis 스타일 출력
├── store.py          SET/GET/TTL/LRU/메모리 제한 업무 로직
├── hashmap.py        직접 구현한 체이닝 방식 해시맵
├── linked_list.py    직접 구현한 이중 연결 리스트
└── min_heap.py       직접 구현한 최소 힙
```

## 모듈별 책임

| 모듈 | 책임 |
| --- | --- |
| `cli.py` | 사용자가 입력한 문자열 명령을 파싱하고 결과를 출력합니다 |
| `store.py` | Redis 명령의 실제 동작, LRU, TTL, 메모리 제한을 조합합니다 |
| `hashmap.py` | `dict` 대신 사용할 해시맵을 직접 구현합니다 |
| `linked_list.py` | 최근 사용 순서를 관리하기 위한 이중 연결 리스트를 구현합니다 |
| `min_heap.py` | 가장 빨리 만료될 TTL을 찾기 위한 최소 힙을 구현합니다 |
| `__main__.py` | `python -m mini_redis` 실행 시 `cli.main()`을 호출합니다 |

## 왜 이렇게 나누었나

Redis가 빠른 이유를 이해하려면 기능별로 어떤 자료구조가 쓰이는지 분리해서 보는 것이 좋습니다. 그래서 해시맵, 이중 연결 리스트, 힙을 각각 독립 모듈로 나누었습니다.

`HashMap`은 키로 값을 빠르게 찾는 역할을 합니다. `DoublyLinkedList`는 가장 최근 사용한 키를 앞에 두고, 가장 오래 사용하지 않은 키를 뒤에 두어 LRU 제거를 쉽게 만듭니다. `MinHeap`은 가장 먼저 만료될 키를 빠르게 확인하기 위해 사용합니다.

`store.py`는 이 자료구조들을 조합합니다. 예를 들어 `GET`에 성공하면 LRU 순서를 갱신하고, `SET`은 메모리 사용량을 계산한 뒤 초과하면 오래된 키를 제거합니다. `EXPIRE`는 만료 시간을 해시맵과 힙에 함께 기록하고, 만료된 키는 명령 실행 전에 삭제합니다.

## 구현 제약

학습 목적에 맞춰 `dict`, `set`, `collections`로 해시맵이나 캐시를 대체하지 않았습니다. 버킷 배열, 체이닝 노드, 리스트 노드, 힙 배열을 직접 다룹니다.

데이터 영속성은 구현하지 않습니다. 프로그램을 종료하면 저장된 키는 사라집니다.

