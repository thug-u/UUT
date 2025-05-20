from dash.dependencies import Input, Output, State
from dash import Dash, html, dash
import plotly.graph_objs as go
import numpy as np
from config.shared_config import SHARED, SHARED_LOCK, GRAPH_CONFIG
from web.layout import html as html_layout

def register_callbacks(app: Dash):
    """Dash 앱에 콜백 등록."""
    @app.callback(
        Output('speed-chart', 'figure'),
        Input('interval', 'n_intervals')
    )
    def update_speed_chart(n):
        with SHARED_LOCK:
            data = SHARED['speed_data'][-GRAPH_CONFIG['max_points']:]
        return {
            'data': [go.Scatter(
                y=data,
                mode='lines+markers',
                line=dict(color='#e74c3c'),
                marker=dict(size=6)
            )],
            'layout': go.Layout(
                xaxis=dict(
                    range=[max(0, len(data) - GRAPH_CONFIG['max_points']), len(data)],
                    dtick=10,
                    title='시간 (포인트)',
                    gridcolor='rgba(255,255,255,0.1)',
                    zerolinecolor='rgba(255,255,255,0.1)',
                    titlefont=dict(color='#8d97ad'),
                    tickfont=dict(color='#8d97ad')
                ),
                yaxis=dict(
                    range=[-40, 80],
                    dtick=10,
                    title='속도 (km/h)',
                    gridcolor='rgba(255,255,255,0.1)',
                    zerolinecolor='rgba(255,255,255,0.1)',
                    titlefont=dict(color='#8d97ad'),
                    tickfont=dict(color='#8d97ad')
                ),
                title='',
                template='plotly_dark',
                paper_bgcolor='rgba(28,35,49,1)',
                plot_bgcolor='rgba(28,35,49,1)',
                font=dict(color='#8d97ad'),
                margin=dict(l=50, r=50, t=30, b=50),
                transition={'duration': 500}
            )
        }

    @app.callback(
        Output('delta-chart', 'figure'),
        Input('interval', 'n_intervals')
    )
    def update_delta_chart(n):
        with SHARED_LOCK:
            del_x_data = SHARED['del_playerPos_x'][-GRAPH_CONFIG['max_points']:]
            del_z_data = SHARED['del_playerPos_z'][-GRAPH_CONFIG['max_points']:]
        return {
            'data': [
                go.Scatter(
                    y=del_x_data,
                    mode='lines',
                    name='ΔX',
                    line=dict(color='#e74c3c', dash='dot')
                ),
                go.Scatter(
                    y=del_z_data,
                    mode='lines',
                    name='ΔZ',
                    line=dict(color='#27ae60', dash='dash')
                )
            ],
            'layout': go.Layout(
                xaxis=dict(
                    title='시간 (포인트)',
                    dtick=10,
                    range=[max(0, len(del_x_data) - GRAPH_CONFIG['max_points']), len(del_x_data)],
                    gridcolor='rgba(255,255,255,0.1)',
                    zerolinecolor='rgba(255,255,255,0.1)',
                    titlefont=dict(color='#8d97ad'),
                    tickfont=dict(color='#8d97ad')
                ),
                yaxis=dict(
                    title='좌표 변화량',
                    dtick=1,
                    gridcolor='rgba(255,255,255,0.1)',
                    zerolinecolor='rgba(255,255,255,0.1)',
                    titlefont=dict(color='#8d97ad'),
                    tickfont=dict(color='#8d97ad')
                ),
                title='',
                legend=dict(orientation='h', y=-0.2, font=dict(color='#8d97ad')),
                template='plotly_dark',
                paper_bgcolor='rgba(28,35,49,1)',
                plot_bgcolor='rgba(28,35,49,1)',
                font=dict(color='#8d97ad'),
                margin=dict(l=50, r=50, t=30, b=50),
                transition={'duration': 500}
            )
        }

    @app.callback(
        [Output('position-chart', 'figure'),
         Output('tank-position', 'style'),
         Output('obstacles-container', 'children'),
         Output('coordinate-display', 'children'),
         Output('obstacle-count', 'children'),
         Output('obstacle-distance', 'children')],
        Input('interval', 'n_intervals')
    )
    def update_position_chart(n):
        with SHARED_LOCK:
            pos_data = SHARED['player_pos'][-GRAPH_CONFIG['max_points']:] if SHARED.get('player_pos') else [[0, 0]]
            clusters = SHARED.get('obstacle_clusters', [])
            obstacle_radius = SHARED['CONFIG_PARAMS'].get('OBSTACLE_RADIUS', 1.0)

        # 전차 경로
        x_data = [pos[0] for pos in pos_data]
        z_data = [pos[1] for pos in pos_data]
        latest_pos = pos_data[-1] if pos_data else [0, 0]
        x, z = latest_pos

        # 전차 스타일
        tank_style = {
            'transform': 'translate(-50%, -50%)',
            'left': f'{((x + 10) / 20) * 100}%',
            'top': f'{((10 - z) / 20) * 100}%'
        }

        # 장애물 데이터
        data = [
            go.Scatter(
                x=x_data,
                y=z_data,
                mode='lines+markers',
                name='전차 경로',
                marker=dict(size=8, color='#27ae60'),
                line=dict(width=2, color='rgba(39,174,96,0.5)')
            )
        ]
        obstacle_elements = []
        for i, cluster in enumerate(clusters):
            if not isinstance(cluster, (list, np.ndarray)) or len(cluster) == 0:
                continue
            centroid = np.mean(np.array(cluster), axis=0)
            ox, oz = centroid
            # 장애물 중심점
            data.append(
                go.Scatter(
                    x=[ox],
                    y=[oz],
                    mode='markers',
                    name=f'장애물 {i+1}',
                    marker=dict(size=10, color='#e74c3c', symbol='x')
                )
            )
            # 장애물 원
            theta = np.linspace(0, 2 * np.pi, 100)
            x_circle = ox + obstacle_radius * np.cos(theta)
            z_circle = oz + obstacle_radius * np.sin(theta)
            data.append(
                go.Scatter(
                    x=x_circle,
                    y=z_circle,
                    mode='lines',
                    line=dict(width=1, color='#e74c3c', dash='dot'),
                    showlegend=False
                )
            )
            # HTML 장애물 요소
            obstacle_elements.append(
                html_layout.Div(
                    className='obstacle absolute w-5 h-5 bg-red-600 rounded-full opacity-50',
                    style={
                        'left': f'{((ox + 10) / 20) * 100}%',
                        'top': f'{((10 - oz) / 20) * 100}%',
                        'transform': 'translate(-50%, -50%)',
                        'width': f'{obstacle_radius * 10}px',
                        'height': f'{obstacle_radius * 10}px'
                    }
                )
            )

        # 장애물 통계
        num_obstacles = len(clusters)
        avg_distance = 0.0
        if clusters:
            distances = [
                np.linalg.norm(np.mean(np.array(cluster), axis=0) - np.array([x, z]))
                for cluster in clusters if isinstance(cluster, (list, np.ndarray)) and len(cluster) > 0
            ]
            avg_distance = np.mean(distances) if distances else 0.0

        return (
            {
                'data': data,
                'layout': go.Layout(
                    xaxis=dict(
                        title='X 좌표',
                        range=[x - 10, x + 10],
                        gridcolor='rgba(255,255,255,0.1)',
                        zerolinecolor='rgba(255,255,255,0.1)',
                        titlefont=dict(color='#8d97ad'),
                        tickfont=dict(color='#8d97ad'),
                        showgrid=False
                    ),
                    yaxis=dict(
                        title='Z 좌표',
                        range=[z - 10, z + 10],
                        gridcolor='rgba(255,255,255,0.1)',
                        zerolinecolor='rgba(255,255,255,0.1)',
                        titlefont=dict(color='#8d97ad'),
                        tickfont=dict(color='#8d97ad'),
                        showgrid=False
                    ),
                    title='',
                    showlegend=True,
                    template='plotly_dark',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#8d97ad'),
                    margin=dict(l=50, r=50, t=30, b=50),
                    transition={'duration': 500}
                )
            },
            tank_style,
            obstacle_elements,
            f'X: {x:.2f}, Z: {z:.2f}',
            str(num_obstacles),
            f'{avg_distance:.2f}'
        )

    @app.callback(
        [Output('target-speed-display', 'children'),
         Output('target-speed', 'children')],
        Input('target-speed-slider', 'value')
    )
    def update_target_speed(val):
        with SHARED_LOCK:
            SHARED['tank_tar_val_kh'] = val
        return f'현재: {val} km/h', str(val)

    @app.callback(
        Output('terminal-log', 'children'),
        [Input('input-kp', 'value'),
         Input('input-ki', 'value'),
         Input('input-kd', 'value'),
         Input('update-pid', 'n_clicks')],
        prevent_initial_call=True
    )
    def update_pid_values(kp, ki, kd, n_clicks):
        if n_clicks is None:
            return dash.no_update
        with SHARED_LOCK:
            SHARED['pid']['kp'] = max(0, float(kp)) if kp is not None else SHARED['pid']['kp']
            SHARED['pid']['ki'] = max(0, float(ki)) if ki is not None else SHARED['pid']['ki']
            SHARED['pid']['kd'] = max(0, float(kd)) if kd is not None else SHARED['pid']['kd']
        return html_layout.Div([
            html_layout.Div(f'[INFO] PID Updated: Kp={SHARED["pid"]["kp"]:.4f}, Ki={SHARED["pid"]["ki"]:.4f}, Kd={SHARED["pid"]["kd"]:.4f}', className='terminal-line')
        ])

    @app.callback(
        [Output('config-display', 'children'),
         Output('terminal-log', 'children', allow_duplicate=True),
         Output('move-step-display', 'children'),
         Output('tolerance-display', 'children'),
         Output('obstacle-radius-display', 'children')],
        [Input('input-move-step', 'value'),
         Input('input-tolerance', 'value'),
         Input('input-obstacle-radius', 'value'),
         Input('input-lookahead-min', 'value'),
         Input('input-lookahead-max', 'value'),
         Input('input-goal-weight', 'value'),
         Input('input-speed-factor', 'value'),
         Input('input-steering-smoothing', 'value'),
         Input('input-heading-smoothing', 'value'),
         Input('input-weight-d', 'value'),
         Input('input-weight-a', 'value'),
         Input('input-weight-w', 'value'),
         Input('input-weight-s', 'value'),
         Input('update-config', 'n_clicks'),
         Input('input-dbscan-eps', 'value'),
         Input('input-dbscan-min-samples', 'value'),
         Input('reset-config', 'n_clicks')],
        prevent_initial_call=True
    )
    def update_config_values(move_step, tolerance, obstacle_radius, lookahead_min, lookahead_max, goal_weight,
                            speed_factor, steering_smoothing, heading_smoothing, weight_d, weight_a, weight_w,
                            weight_s, update_n, dbscan_eps, dbscan_min_samples, reset_n):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if triggered_id == 'reset-config':
            with SHARED_LOCK:
                SHARED['CONFIG_PARAMS'] = {
                    'MOVE_STEP': 0.1,
                    'TOLERANCE': 1.0,
                    'OBSTACLE_RADIUS': 1.0,
                    'LOOKAHEAD_MIN': 2.0,
                    'LOOKAHEAD_MAX': 10.0,
                    'GOAL_WEIGHT': 1.0,
                    'SPEED_FACTOR': 0.5,
                    'STEERING_SMOOTHING': 0.7,
                    'HEADING_SMOOTHING': 0.7,
                    'DBSCAN_EPS': 2.0,
                    'DBSCAN_MIN_SAMPLES': 2,
                    'WEIGHT_FACTORS': {'D': 1.0, 'A': 1.0, 'W': 1.0, 'S': 1.0}
                }
            return (
                html_layout.Ul([
                    html_layout.Li(f"MOVE_STEP: {SHARED['CONFIG_PARAMS']['MOVE_STEP']:.2f} m", className='py-1 border-b border-gray-800 flex justify-between'),
                    html_layout.Li(f"TOLERANCE: {SHARED['CONFIG_PARAMS']['TOLERANCE']:.2f} m", className='py-1 border-b border-gray-800 flex justify-between'),
                    html_layout.Li(f"OBSTACLE_RADIUS: {SHARED['CONFIG_PARAMS']['OBSTACLE_RADIUS']:.2f} m", className='py-1 border-b border-gray-800 flex justify-between'),
                    html_layout.Li(f"LOOKAHEAD_MIN: {SHARED['CONFIG_PARAMS']['LOOKAHEAD_MIN']:.2f} m", className='py-1 border-b border-gray-800 flex justify-between'),
                    html_layout.Li(f"LOOKAHEAD_MAX: {SHARED['CONFIG_PARAMS']['LOOKAHEAD_MAX']:.2f} m", className='py-1 border-b border-gray-800 flex justify-between'),
                    html_layout.Li(f"GOAL_WEIGHT: {SHARED['CONFIG_PARAMS']['GOAL_WEIGHT']:.2f}", className='py-1 border-b border-gray-800 flex justify-between'),
                    html_layout.Li(f"SPEED_FACTOR: {SHARED['CONFIG_PARAMS']['SPEED_FACTOR']:.2f}", className='py-1 border-b border-gray-800 flex justify-between'),
                    html_layout.Li(f"STEERING_SMOOTHING: {SHARED['CONFIG_PARAMS']['STEERING_SMOOTHING']:.2f}", className='py-1 border-b border-gray-800 flex justify-between'),
                    html_layout.Li(f"HEADING_SMOOTHING: {SHARED['CONFIG_PARAMS']['HEADING_SMOOTHING']:.2f}", className='py-1 border-b border-gray-800 flex justify-between'),
                    html_layout.Li(f"DBSCAN_EPS: {SHARED['CONFIG_PARAMS']['DBSCAN_EPS']:.2f} m", className='py-1 border-b border-gray-800 flex justify-between'),
                    html_layout.Li(f"DBSCAN_MIN_SAMPLES: {SHARED['CONFIG_PARAMS']['DBSCAN_MIN_SAMPLES']}", className='py-1 border-b border-gray-800 flex justify-between'),
                    html_layout.Li(f"WEIGHT_FACTORS: D={SHARED['CONFIG_PARAMS']['WEIGHT_FACTORS']['D']:.2f}, "
                                   f"A={SHARED['CONFIG_PARAMS']['WEIGHT_FACTORS']['A']:.2f}, "
                                   f"W={SHARED['CONFIG_PARAMS']['WEIGHT_FACTORS']['W']:.2f}, "
                                   f"S={SHARED['CONFIG_PARAMS']['WEIGHT_FACTORS']['S']:.2f}", className='py-1 border-b border-gray-800 flex justify-between')
                ], className='list-none'),
                html_layout.Div([html_layout.Div('[INFO] Configuration Reset', className='terminal-line')]),
                f'현재: {SHARED["CONFIG_PARAMS"]["MOVE_STEP"]} m',
                f'현재: {SHARED["CONFIG_PARAMS"]["TOLERANCE"]} m',
                f'현재: {SHARED["CONFIG_PARAMS"]["OBSTACLE_RADIUS"]} m'
            )

        if triggered_id == 'update-config' and update_n is None:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

        with SHARED_LOCK:
            SHARED['CONFIG_PARAMS']['MOVE_STEP'] = max(0.01, float(move_step)) if move_step is not None else SHARED['CONFIG_PARAMS']['MOVE_STEP']
            SHARED['CONFIG_PARAMS']['TOLERANCE'] = max(0.1, float(tolerance)) if tolerance is not None else SHARED['CONFIG_PARAMS']['TOLERANCE']
            SHARED['CONFIG_PARAMS']['OBSTACLE_RADIUS'] = max(0.1, float(obstacle_radius)) if obstacle_radius is not None else SHARED['CONFIG_PARAMS']['OBSTACLE_RADIUS']
            SHARED['CONFIG_PARAMS']['LOOKAHEAD_MIN'] = max(0.1, float(lookahead_min)) if lookahead_min is not None else SHARED['CONFIG_PARAMS']['LOOKAHEAD_MIN']
            SHARED['CONFIG_PARAMS']['LOOKAHEAD_MAX'] = max(1.0, float(lookahead_max)) if lookahead_max is not None else SHARED['CONFIG_PARAMS']['LOOKAHEAD_MAX']
            SHARED['CONFIG_PARAMS']['GOAL_WEIGHT'] = max(0.0, float(goal_weight)) if goal_weight is not None else SHARED['CONFIG_PARAMS']['GOAL_WEIGHT']
            SHARED['CONFIG_PARAMS']['SPEED_FACTOR'] = max(0.0, float(speed_factor)) if speed_factor is not None else SHARED['CONFIG_PARAMS']['SPEED_FACTOR']
            SHARED['CONFIG_PARAMS']['STEERING_SMOOTHING'] = min(max(0.0, float(steering_smoothing)), 1.0) if steering_smoothing is not None else SHARED['CONFIG_PARAMS']['STEERING_SMOOTHING']
            SHARED['CONFIG_PARAMS']['HEADING_SMOOTHING'] = min(max(0.0, float(heading_smoothing)), 1.0) if heading_smoothing is not None else SHARED['CONFIG_PARAMS']['HEADING_SMOOTHING']
            SHARED['CONFIG_PARAMS']['DBSCAN_EPS'] = max(0.1, float(dbscan_eps)) if dbscan_eps is not None else SHARED['CONFIG_PARAMS']['DBSCAN_EPS']
            SHARED['CONFIG_PARAMS']['DBSCAN_MIN_SAMPLES'] = max(1, int(dbscan_min_samples)) if dbscan_min_samples is not None else SHARED['CONFIG_PARAMS']['DBSCAN_MIN_SAMPLES']
            SHARED['CONFIG_PARAMS']['WEIGHT_FACTORS']['D'] = max(0.0, float(weight_d)) if weight_d is not None else SHARED['CONFIG_PARAMS']['WEIGHT_FACTORS']['D']
            SHARED['CONFIG_PARAMS']['WEIGHT_FACTORS']['A'] = max(0.0, float(weight_a)) if weight_a is not None else SHARED['CONFIG_PARAMS']['WEIGHT_FACTORS']['A']
            SHARED['CONFIG_PARAMS']['WEIGHT_FACTORS']['W'] = max(0.0, float(weight_w)) if weight_w is not None else SHARED['CONFIG_PARAMS']['WEIGHT_FACTORS']['W']
            SHARED['CONFIG_PARAMS']['WEIGHT_FACTORS']['S'] = max(0.0, float(weight_s)) if weight_s is not None else SHARED['CONFIG_PARAMS']['WEIGHT_FACTORS']['S']

        return (
            html_layout.Ul([
                html_layout.Li(f"MOVE_STEP: {SHARED['CONFIG_PARAMS']['MOVE_STEP']:.2f} m", className='py-1 border-b border-gray-800 flex justify-between'),
                html_layout.Li(f"TOLERANCE: {SHARED['CONFIG_PARAMS']['TOLERANCE']:.2f} m", className='py-1 border-b border-gray-800 flex justify-between'),
                html_layout.Li(f"OBSTACLE_RADIUS: {SHARED['CONFIG_PARAMS']['OBSTACLE_RADIUS']:.2f} m", className='py-1 border-b border-gray-800 flex justify-between'),
                html_layout.Li(f"LOOKAHEAD_MIN: {SHARED['CONFIG_PARAMS']['LOOKAHEAD_MIN']:.2f} m", className='py-1 border-b border-gray-800 flex justify-between'),
                html_layout.Li(f"LOOKAHEAD_MAX: {SHARED['CONFIG_PARAMS']['LOOKAHEAD_MAX']:.2f} m", className='py-1 border-b border-gray-800 flex justify-between'),
                html_layout.Li(f"GOAL_WEIGHT: {SHARED['CONFIG_PARAMS']['GOAL_WEIGHT']:.2f}", className='py-1 border-b border-gray-800 flex justify-between'),
                html_layout.Li(f"SPEED_FACTOR: {SHARED['CONFIG_PARAMS']['SPEED_FACTOR']:.2f}", className='py-1 border-b border-gray-800 flex justify-between'),
                html_layout.Li(f"STEERING_SMOOTHING: {SHARED['CONFIG_PARAMS']['STEERING_SMOOTHING']:.2f}", className='py-1 border-b border-gray-800 flex justify-between'),
                html_layout.Li(f"HEADING_SMOOTHING: {SHARED['CONFIG_PARAMS']['HEADING_SMOOTHING']:.2f}", className='py-1 border-b border-gray-800 flex justify-between'),
                html_layout.Li(f"DBSCAN_EPS: {SHARED['CONFIG_PARAMS']['DBSCAN_EPS']:.2f} m", className='py-1 border-b border-gray-800 flex justify-between'),
                html_layout.Li(f"DBSCAN_MIN_SAMPLES: {SHARED['CONFIG_PARAMS']['DBSCAN_MIN_SAMPLES']}", className='py-1 border-b border-gray-800 flex justify-between'),
                html_layout.Li(f"WEIGHT_FACTORS: D={SHARED['CONFIG_PARAMS']['WEIGHT_FACTORS']['D']:.2f}, "
                               f"A={SHARED['CONFIG_PARAMS']['WEIGHT_FACTORS']['A']:.2f}, "
                               f"W={SHARED['CONFIG_PARAMS']['WEIGHT_FACTORS']['W']:.2f}, "
                               f"S={SHARED['CONFIG_PARAMS']['WEIGHT_FACTORS']['S']:.2f}", className='py-1 border-b border-gray-800 flex justify-between')
            ], className='list-none'),
            html_layout.Div([html_layout.Div('[INFO] Configuration Updated', className='terminal-line')]),
            f'현재: {SHARED["CONFIG_PARAMS"]["MOVE_STEP"]:.2f} m',
            f'현재: {SHARED["CONFIG_PARAMS"]["TOLERANCE"]:.2f} m',
            f'현재: {SHARED["CONFIG_PARAMS"]["OBSTACLE_RADIUS"]:.2f} m'
        )

    @app.callback(
        Output('current-speed', 'children'),
        Input('interval', 'n_intervals')
    )
    def update_current_speed(n):
        with SHARED_LOCK:
            return str(SHARED['speed_data'][-1] if SHARED['speed_data'] else 0)