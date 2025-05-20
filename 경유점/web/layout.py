from dash import dcc, html
from config.shared_config import SHARED

def create_card(title, icon, children, header_extra=None):
    return html.Div([
        html.Div([
            html.Div([
                html.I(className=f'fas {icon} mr-2 text-red-600'),
                html.Span(title, className='text-white font-bold text-base')
            ], className='card-title'),
            header_extra if header_extra else html.Div()
        ], className='card-header flex justify-between items-center p-3 bg-gray-800 border-b border-gray-700'),
        html.Div(children, className='card-body p-4')
    ], className='card bg-gray-800 rounded border border-gray-700 mb-5')

def create_form_group(label, input_component, display_id=None):
    return html.Div([
        html.Label(label, className='form-label block mb-1 text-gray-400 text-xs'),
        input_component,
        html.Div(f'현재: {input_component.value}', id=display_id, className='slider-value text-gray-400 text-xs mt-1 text-right') if display_id else html.Div()
    ], className='form-group mb-4')

def create_layout():
    config_params = SHARED.get('CONFIG_PARAMS', {})
    return html.Div([
        html.Header([
            html.Div([
                html.Div([
                    html.I(className='fas fa-shield-alt text-white text-xl'),
                ], className='logo w-10 h-10 bg-red-600 rounded-full flex items-center justify-center mr-4'),
                html.H1('전차 제어 시스템', className='text-white text-2xl uppercase tracking-wide')
            ], className='header-title flex items-center'),
            html.Div([
                html.Div([
                    html.Div(className='status-dot status-online w-2.5 h-2.5 rounded-full mr-1 bg-green-600'),
                    html.Span('시스템 온라인', className='text-xs text-gray-300')
                ], className='status-indicator flex items-center'),
                html.Div([
                    html.Div(className='status-dot status-online blink w-2.5 h-2.5 rounded-full mr-1 bg-green-600'),
                    html.Span('데이터 수신중', className='text-xs text-gray-300')
                ], className='status-indicator flex items-center'),
                html.Div([
                    html.Div(id='warning-indicator', className='status-dot status-warning w-2.5 h-2.5 rounded-full mr-1 bg-yellow-600'),
                    html.Span('경고 0개', id='warning-count', className='text-xs text-gray-300')
                ], className='status-indicator flex items-center'),
            ], className='status-bar flex gap-5 items-center')
        ], className='bg-gray-900 p-4 border-b-2 border-red-600 flex justify-between items-center'),

        html.Div([
            html.Div([
                create_card('실시간 데이터 모니터링', 'fa-chart-line', [
                    html.Div([
                        html.Div('실시간 속도 (km/h)', className='graph-title text-gray-300 text-sm mb-2'),
                        dcc.Graph(id='speed-chart', className='h-64')
                    ], className='graph-container bg-gray-800 border border-gray-700 rounded mb-4 overflow-hidden'),
                    html.Div([
                        html.Div('위치 변화량 (ΔX, ΔZ)', className='graph-title text-gray-300 text-sm mb-2'),
                        dcc.Graph(id='delta-chart', className='h-64')
                    ], className='graph-container bg-gray-800 border border-gray-700 rounded mb-4 overflow-hidden'),
                    html.Div([
                        html.Div(className='map-grid absolute w-full h-full', style={
                            'backgroundImage': 'linear-gradient(rgba(38, 49, 71, 0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(38, 49, 71, 0.5) 1px, transparent 1px)',
                            'backgroundSize': '50px 50px'
                        }),
                        html.Div(id='tank-position', className='tank-position absolute w-5 h-5 bg-green-600 rounded-full', style={'transform': 'translate(-50%, -50%)'}),
                        html.Div(id='obstacles-container', className='obstacles-container absolute w-full h-full'),
                        dcc.Graph(id='position-chart', className='h-full', style={'background': 'transparent'}),
                        html.Div('X: 0.00, Z: 0.00', id='coordinate-display', className='coordinate-display absolute bottom-2 right-2 bg-black bg-opacity-70 p-1 rounded text-xs text-white')
                    ], className='map-container h-96 border border-gray-700 rounded relative bg-gray-800 overflow-hidden'),
                    html.Div([
                        html.Div([
                            html.Div(id='obstacle-count', className='stat-value text-white text-2xl my-1'),
                            html.Div('장애물 개수', className='stat-label text-gray-400 text-xs')
                        ], className='stat-card bg-gray-800 border border-gray-700 rounded p-2.5 text-center'),
                        html.Div([
                            html.Div(id='obstacle-distance', className='stat-value text-white text-2xl my-1'),
                            html.Div('평균 거리 (m)', className='stat-label text-gray-400 text-xs')
                        ], className='stat-card bg-gray-800 border border-gray-700 rounded p-2.5 text-center'),
                    ], className='stats-panel grid grid-cols-2 gap-4 mt-4'),
                    html.Div(id='terminal-log', className='terminal bg-black p-2.5 font-mono h-36 overflow-auto border border-gray-700 text-green-600 text-sm')
                ], html.Div([
                    html.Div(className='status-dot status-online blink w-2.5 h-2.5 rounded-full mr-1 bg-green-600'),
                    html.Span('실시간', id='update-status', className='text-xs text-gray-300')
                ], className='status-indicator flex items-center'))
            ], className='main-content'),

            html.Div([
                create_card('속도 제어', 'fa-tachometer-alt', [
                    html.Div([
                        html.Div([
                            html.Div('0', id='current-speed', className='stat-value text-white text-2xl my-1'),
                            html.Div('현재 속도 (km/h)', className='stat-label text-gray-400 text-xs')
                        ], className='stat-card bg-gray-800 border border-gray-700 rounded p-2.5 text-center'),
                        html.Div([
                            html.Div('0', id='target-speed', className='stat-value text-white text-2xl my-1'),
                            html.Div('목표 속도 (km/h)', className='stat-label text-gray-400 text-xs')
                        ], className='stat-card bg-gray-800 border border-gray-700 rounded p-2.5 text-center'),
                        html.Div([
                            html.Div('0°', id='steering-angle', className='stat-value text-white text-2xl my-1'),
                            html.Div('조향각', className='stat-label text-gray-400 text-xs')
                        ], className='stat-card bg-gray-800 border border-gray-700 rounded p-2.5 text-center'),
                    ], className='stats-panel grid grid-cols-3 gap-4'),
                    create_form_group(
                        '타겟 속도 설정 (-30~70 km/h)',
                        dcc.Slider(id='target-speed-slider', min=-30, max=70, step=1, value=SHARED.get('tank_tar_val_kh', 0.0), marks={i: str(i) for i in range(-30, 71, 10)}, className='w-full'),
                        'target-speed-display'
                    ),
                    html.Div('PID 파라미터 조정', className='section-title text-gray-400 text-sm font-bold mt-5 mb-2.5 pb-1 border-b border-gray-700'),
                    create_form_group(
                        'Kp (비례 게인)',
                        dcc.Input(id='input-kp', type='number', value=SHARED.get('pid', {}).get('kp', 0.5), step=0.0001, min=0, className='form-control w-full p-2 bg-gray-800 border border-gray-700 text-white rounded')
                    ),
                    create_form_group(
                        'Ki (적분 게인)',
                        dcc.Input(id='input-ki', type='number', value=SHARED.get('pid', {}).get('ki', 0.0), step=0.0001, min=0, className='form-control w-full p-2 bg-gray-800 border border-gray-700 text-white rounded')
                    ),
                    create_form_group(
                        'Kd (미분 게인)',
                        dcc.Input(id='input-kd', type='number', value=SHARED.get('pid', {}).get('kd', 0.0), step=0.0001, min=0, className='form-control w-full p-2 bg-gray-800 border border-gray-700 text-white rounded')
                    ),
                    html.Div([
                        html.Button('PID 업데이트', id='update-pid', className='btn btn-primary p-2 bg-blue-800 border-blue-800 rounded font-bold text-white hover:opacity-90')
                    ], className='control-buttons flex gap-2.5 mt-4'),
                    html.Div('시뮬레이션 파라미터', className='section-title text-gray-400 text-sm font-bold mt-5 mb-2.5 pb-1 border-b border-gray-700'),
                    create_form_group(
                        'MOVE_STEP (이동 거리, m)',
                        dcc.Slider(id='input-move-step', min=0.01, max=1.0, step=0.01, value=config_params.get('MOVE_STEP', 0.1), marks={i/10: str(i/10) for i in range(1, 11, 2)}, className='w-full'),
                        'move-step-display'
                    ),
                    create_form_group(
                        'TOLERANCE (도달/탐지 반경, m)',
                        dcc.Slider(id='input-tolerance', min=0.1, max=2.0, step=0.1, value=config_params.get('TOLERANCE', 1.0), marks={i/10: str(i/10) for i in range(1, 21, 5)}, className='w-full'),
                        'tolerance-display'
                    ),
                    create_form_group(
                        'OBSTACLE_RADIUS (장애물 탐지 반경, m)',
                        dcc.Slider(id='input-obstacle-radius', min=0.1, max=2.0, step=0.1, value=config_params.get('OBSTACLE_RADIUS', 1.0), marks={i/10: str(i/10) for i in range(1, 21, 5)}, className='w-full'),
                        'obstacle-radius-display'
                    ),
                    html.Div('장애물 인식 설정', className='section-title text-gray-400 text-sm font-bold mt-5 mb-2.5 pb-1 border-b border-gray-700'),
                    create_form_group(
                        'DBSCAN EPS (클러스터링 거리, m)',
                        dcc.Slider(id='input-dbscan-eps', min=0.1, max=2.0, step=0.1, value=config_params.get('DBSCAN_EPS', 1.0), marks={i/10: str(i/10) for i in range(1, 21, 5)}, className='w-full'),
                        'dbscan-eps-display'
                    ),
                    create_form_group(
                        'DBSCAN MIN SAMPLES (최소 포인트 수)',
                        dcc.Slider(id='input-dbscan-min-samples', min=1, max=10, step=1, value=config_params.get('DBSCAN_MIN_SAMPLES', 3), marks={i: str(i) for i in range(1, 11, 2)}, className='w-full'),
                        'dbscan-min-samples-display'
                    ),
                    html.Div('고급 설정', className='section-title text-gray-400 text-sm font-bold mt-5 mb-2.5 pb-1 border-b border-gray-700'),
                    create_form_group(
                        'LOOKAHEAD_MIN (최소 주시 거리, m)',
                        dcc.Input(id='input-lookahead-min', type='number', value=config_params.get('LOOKAHEAD_MIN', 2.0), step=0.1, min=0.1, className='form-control w-full p-2 bg-gray-800 border border-gray-700 text-white rounded')
                    ),
                    create_form_group(
                        'LOOKAHEAD_MAX (최대 주시 거리, m)',
                        dcc.Input(id='input-lookahead-max', type='number', value=config_params.get('LOOKAHEAD_MAX', 10.0), step=0.1, min=1.0, className='form-control w-full p-2 bg-gray-800 border border-gray-700 text-white rounded')
                    ),
                    create_form_group(
                        'GOAL_WEIGHT (목표 방향 가중치)',
                        dcc.Input(id='input-goal-weight', type='number', value=config_params.get('GOAL_WEIGHT', 1.0), step=0.1, min=0.0, className='form-control w-full p-2 bg-gray-800 border border-gray-700 text-white rounded')
                    ),
                    create_form_group(
                        'SPEED_FACTOR (속도 감소 비율)',
                        dcc.Input(id='input-speed-factor', type='number', value=config_params.get('SPEED_FACTOR', 0.5), step=0.1, min=0.0, max=1.0, className='form-control w-full p-2 bg-gray-800 border border-gray-700 text-white rounded')
                    ),
                    create_form_group(
                        'STEERING_SMOOTHING (조향 평활화, 0~1)',
                        dcc.Input(id='input-steering-smoothing', type='number', value=config_params.get('STEERING_SMOOTHING', 0.7), step=0.1, min=0.0, max=1.0, className='form-control w-full p-2 bg-gray-800 border border-gray-700 text-white rounded')
                    ),
                    create_form_group(
                        'HEADING_SMOOTHING (방향 평활화, 0~1)',
                        dcc.Input(id='input-heading-smoothing', type='number', value=config_params.get('HEADING_SMOOTHING', 0.7), step=0.1, min=0.0, max=1.0, className='form-control w-full p-2 bg-gray-800 border border-gray-700 text-white rounded')
                    ),
                    create_form_group(
                        'WEIGHT_D (오른쪽 가중치)',
                        dcc.Input(id='input-weight-d', type='number', value=config_params.get('WEIGHT_FACTORS', {}).get('D', 1.0), step=0.1, min=0.0, className='form-control w-full p-2 bg-gray-800 border border-gray-700 text-white rounded')
                    ),
                    create_form_group(
                        'WEIGHT_A (왼쪽 가중치)',
                        dcc.Input(id='input-weight-a', type='number', value=config_params.get('WEIGHT_FACTORS', {}).get('A', 1.0), step=0.1, min=0.0, className='form-control w-full p-2 bg-gray-800 border border-gray-700 text-white rounded')
                    ),
                    create_form_group(
                        'WEIGHT_W (전진 가중치)',
                        dcc.Input(id='input-weight-w', type='number', value=config_params.get('WEIGHT_FACTORS', {}).get('W', 1.0), step=0.1, min=0.0, className='form-control w-full p-2 bg-gray-800 border border-gray-700 text-white rounded')
                    ),
                    create_form_group(
                        'WEIGHT_S (후진 가중치)',
                        dcc.Input(id='input-weight-s', type='number', value=config_params.get('WEIGHT_FACTORS', {}).get('S', 1.0), step=0.1, min=0.0, className='form-control w-full p-2 bg-gray-800 border border-gray-700 text-white rounded')
                    ),
                    html.Div([
                        html.Button('설정 업데이트', id='update-config', className='btn btn-primary p-2 bg-blue-800 border-blue-800 rounded font-bold text-white hover:opacity-90'),
                        html.Button('초기화', id='reset-config', className='btn p-2 bg-gray-800 border-gray-700 rounded font-bold text-white hover:opacity-90')
                    ], className='control-buttons flex gap-2.5 mt-4'),
                    html.Div(id='config-display', className='parameters-list list-none mt-2.5 text-gray-300')
                ])
            ], className='sidebar')
        ], className='grid grid-cols-1 md:grid-cols-[2fr_1fr] gap-5 mt-5 max-w-7xl mx-auto'),

        dcc.Interval(id='interval', interval=500, n_intervals=0)
    ], className='min-h-screen bg-gray-950 text-gray-300 text-sm')