# 전차 내비게이션 시스템 (Tank Navigation System)


전차의 실시간 내비게이션, 장애물 회피, 속도 제어를 위한 시뮬레이션 플랫폼입니다. Flask 기반 백엔드와 Dash 기반 프론트엔드를 통합하여 데이터를 처리하고 대화형 대시보드를 제공합니다. LiDAR 데이터를 활용해 Pure Pursuit 경로 추적, PID 제어, DBSCAN 클러스터링을 통해 강력한 내비게이션과 장애물 처리를 구현합니다.

## 목차

- [기능](#기능)
- [아키텍처](#아키텍처)
- [모듈 다이어그램](#모듈-다이어그램)
- [프로젝트 구조](#프로젝트-구조)
- [모듈 및 함수 설명](#모듈-및-함수-설명)
- [기술 스택](#기술-스택)

## 기능

* **실시간 내비게이션**:
    * Pure Pursuit 알고리즘으로 목적지까지 경로 추적.
    * API를 통한 동적 목적지 설정.
* **장애물 회피**:
    * DBSCAN 클러스터링으로 LiDAR 데이터 처리 및 장애물 감지.
    * 정지, 감속, 좌/우 회전 등 회피 동작 수행.
    * KDTree로 장애물 우회 경로 생성.
* **속도 제어**:
    * PID 제어로 목표 속도(-30~70 km/h) 유지.
    * 대시보드를 통해 속도 및 PID 파라미터 조정.
* **대화형 대시보드**:
    * Dash/Plotly로 실시간 시각화: 전차 위치, 경로, 속도, 위치 변화 그래프.
    * 장애물 클러스터 및 통계(개수, 평균 거리).
    * PID 게인, 내비게이션 파라미터, DBSCAN 설정 동적 조정.
* **RESTful API**:
    * Flask로 시뮬레이터와 통신(초기화, 위치/장애물 업데이트).
* **스레드 안전 데이터 공유**:
    * 공유 데이터(`SHARED`)와 스레드 락으로 Flask/Dash 간 안전한 데이터 접근.

## 아키텍처

시스템은 두 가지 주요 구성 요소로 나뉩니다:

* **백엔드 (Flask)**: RESTful API로 시뮬레이터 데이터(LiDAR, 위치) 처리. Navigation 및 하위 모듈로 내비게이션 로직 수행. 스레드 안전 공유 데이터(`SHARED`)에 상태 저장.
* **프론트엔드 (Dash)**: 웹 기반 대시보드로 실시간 모니터링 및 제어. Plotly로 데이터 시각화, 사용자 입력 처리.

**데이터 흐름**:

시뮬레이터가 Flask API로 데이터 전송 -> Navigation이 데이터를 처리, 이동 명령 생성 -> 상태를 `SHARED`에 저장, Dash가 이를 시각화 -> Dash 사용자 입력이 `SHARED`를 통해 시스템에 반영.

## 모듈 다이어그램

아래는 시스템 모듈 간 관계를 나타내는 Mermaid 다이어그램입니다.

```mermaid
flowchart TD
    A[main.py: Multithreading]
    B[Simulator: LiDAR, Position]
    C[Flask: RESTful API]
    D[Navigation: Orchestrates]
    E[Dash: Dashboard]
    F[PositionHandler: Position Update]
    G[PIDController: Speed Control]
    H[PurePursuit: Path Tracking]
    I[ObstacleHandler: Obstacle Avoidance]
    J[SHARED: Shared Data]

    A <--> B
    A --> C
    A --> E
    C <--> D
    E --> J
    D --> F
    D --> G
    D --> H
    D --> I
    F --> J
    G --> J
    H --> J
    I --> J
```
## 프로젝트 구조
```
/
├── assets/                    # 정적 자산 (CSS, JS 등)
├── config/
│   ├── config.py              # 내비게이션 파라미터 (MOVE_STEP, TOLERANCE 등)
│   └── shared_config.py       # 공유 데이터 (SHARED, SERVER_CONFIG 등)
├── navigation/
│   ├── navigation.py          # 핵심 내비게이션 로직
│   ├── position_handler.py    # 위치, 방향, 속도 관리
│   ├── pid_controller.py      # PID 속도 제어
│   ├── pure_pursuit.py        # Pure Pursuit 경로 추적
│   └── obstacle_handler.py    # 장애물 감지 및 회피
├── web/
│   ├── app.py                 # Flask API
│   ├── dash_app.py            # Dash 애플리케이션 설정
│   ├── callbacks.py           # Dash 콜백
│   ├── layout.py              # Dash UI 레이아웃
│   └── styles.py              # 스타일 상수 정의(필요 시 사용)
└── main.py                    # 실행 진입점
```
## 모듈 및 함수 설명

* **실시간 내비게이션**:
    * Pure Pursuit 알고리즘으로 목적지까지 경로 추적.
    * API를 통한 동적 목적지 설정.
* **장애물 회피**:
    * DBSCAN 클러스터링으로 LiDAR 데이터 처리 및 장애물 감지. -> 이부분 수정 필요, 현재 주석처리
    * 정지, 감속, 좌/우 회전 등 회피 동작 수행.
    * KDTree로 장애물 우회 경로 생성.
* **속도 제어**:
    * PID 제어로 목표 속도(-30~70 km/h) 유지.
    * 대시보드를 통해 속도 및 PID 파라미터 조정.
* **대화형 대시보드**:
    * Dash/Plotly로 실시간 시각화: 전차 위치, 경로, 속도, 위치 변화 그래프.
    * 장애물 클러스터 및 통계(개수, 평균 거리).
    * PID 게인, 내비게이션 파라미터, DBSCAN 설정 동적 조정.
* **RESTful API**:
    * Flask리
    * `/update_position (POST)`: 전차 위치 업데이트, `PositionHandler.update_position` 호출.
    * `/set_destination (POST)`: 목적지 설정, `Navigation.set_destination` 호출.
    * `/get_move (GET)`: 다음 이동 명령 반환, `Navigation.get_move` 호출.
    * `/update_obstacle (POST)`: 장애물 데이터 업데이트, `ObstacleHandler.update_obstacle` 호출.
    * `run_flask()`: Flask 서버를 지정된 호스트/포트에서 실행.

### Dash (`web/dash_app.py`, `callbacks.py`, `layout.py`)

* **기능**: 실시간 대시보드 제공, 데이터 시각화, 사용자 입력 처리.
* **주요 구성**:
    * `dash_app.py`:
        * `create_dash_app()`: Dash 앱 생성, 레이아웃 및 콜백 설정.
        * `run_dash()`: Dash 서버 실행.
    * `callbacks.py`:
        * `register_callbacks(app)`: 대시보드 인터랙션을 위한 콜백 등록.
        * `update_speed_chart`: 속도 그래프 업데이트.
        * `update_delta_chart`: 위치 변화량(X, Z) 그래프 업데이트.
        * `update_position_chart`: 전차 위치 및 장애물 맵 업데이트.
        * `update_target_speed`: 목표 속도 설정.
        * `update_pid_values`: PID 게인(`Kp`, `Ki`, `Kd`) 업데이트.
        * `update_config_values`: 내비게이션 파라미터(`MOVE_STEP`, `TOLERANCE` 등) 및 DBSCAN 설정 업데이트.
        * `update_current_speed`: 현재 속도 표시.
    * `layout.py`:
        * `create_layout()`: 대시보드 UI 구성(헤더, 그래프, 설정 패널 등).
        * `create_card(title, icon, children)`: 재사용 가능한 UI 카드 컴포넌트.
        * `create_form_group(label, input_component)`: 입력 폼 그룹 생성.

### Navigation (`navigation/navigation.py`)

* **기능**: 내비게이션 로직을 조정, 하위 모듈 통합.
* **주요 함수**:
    * `__init__()`: `PositionHandler`, `PIDController`, `PurePursuit`, `ObstacleHandler` 초기화.
    * `init_simulation()`: 시뮬레이션 상태 및 모듈 초기화.
    * `set_destination(destination_str)`: 목적지 설정, 초기 거리 계산.
    * `update_info(data)`: LiDAR 데이터 처리, 장애물 업데이트.
    * `get_move()`: 장애물 회피 우선 판단 후 Pure Pursuit로 이동 명령 생성.

### PositionHandler (`navigation/position_handler.py`)

* **기능**: 전차의 위치, 방향, 속도 관리 및 업데이트.
* **주요 함수**:
    * `__init__()`: 위치, 방향, 속도 상태 초기화.
    * `update_position(position_str)`: 새 위치 데이터를 기반으로 위치, 방향, 속도 업데이트. 공유 데이터(`SHARED`)에 저장.

### PIDController (`navigation/pid_controller.py`)

* **기능**: PID 제어로 목표 속도 유지.
* **주요 함수**:
    * `__init__()`: PID 상태(적분 오류, 이전 오류) 초기화.
    * `reset_integral()`: 적분 오류 초기화.
    * `compute_speed(current_speed_kh)`: PID 공식으로 속도 계산, 평활화 적용.

### PurePursuit (`navigation/pure_pursuit.py`)

* **기능**: Pure Pursuit 알고리즘으로 경로 추적 및 이동 명령 생성.
* **주요 함수**:
    * `__init__()`: 명령 및 조향 상태 초기화.
    * `compute_move(current_position, current_heading, current_speed_kh, destination, controller, obstacle_handler)`: 주시점 계산, 장애물 확인, 조향각 및 속도 계산. 동적 가중치로 이동 명령(D, A, W, S) 선택. 새 위치 계산 및 반환.

### ObstacleHandler (`navigation/obstacle_handler.py`)

* **기능**: LiDAR 데이터로 장애물 클러스터링 및 회피 명령 생성.
* **주요 함수**:
    * `__init__()`: DBSCAN 파라미터 및 타겟 상태 초기화.
    * `update_obstacle(obstacle_data)`: LiDAR 데이터 필터링, DBSCAN 클러스터링.
    * `_filter_points(points)`: 유효 LiDAR 포인트 필터링.
    * `_adjust_eps(points)`: 동적 DBSCAN eps 조정.
    * `_cluster_obstacles(points)`: DBSCAN으로 장애물 클러스터링.
    * `get_avoidance_command(current_position, current_heading)`: 장애물 회피 명령 생성(`STOP`, `SLOW_DOWN`, `TURN_LEFT`/`RIGHT`).
    * `is_obstacle_in_path(curr_x, curr_z, lookahead_x, lookahead_z)`: 경로 상 장애물 확인.
    * `find_alternative_path(curr_x, curr_z, goal_x, goal_z)`: 장애물 우회 경로 생성.
    * `get_obstacle_stats()`: 장애물 통계(개수, 평균 거리) 제공.

### SHARED (`config/shared_config.py`)

* **기능**: 스레드 안전 공유 데이터 저장소, 시스템 설정 관리.
* **주요 구성**:
    * `SHARED`: 속도, 위치, LiDAR, 장애물 클러스터, PID 설정, 내비게이션 파라미터 저장.
    * `SHARED_LOCK`: 스레드 안전 데이터 접근 보장.
    * `SERVER_CONFIG`: Flask/Dash 서버 호스트 및 포트 설정.
    * `GRAPH_CONFIG`: 그래프 데이터 제한 설정.

## 기술 스택

* **백엔드**: Flask, Python, NumPy, SciPy, scikit-learn
* **프론트엔드**: Dash, Plotly, Tailwind CSS (사용 시), Font Awesome (사용 시)
* **알고리즘**: Pure Pursuit, PID 제어, DBSCAN, KDTree
* **동시성**: Threading, Threading Lock
