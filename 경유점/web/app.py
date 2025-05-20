from flask import Flask, request, jsonify
from navigation.navigation import Navigation
from config.shared_config import SERVER_CONFIG

app = Flask(__name__)
navigator = Navigation()

@app.route('/init', methods=['GET'])
def init_simulation():
    result = navigator.init_simulation()
    return jsonify(result)


@app.route('/info', methods=['POST'])
def update_info():
    """시뮬레이터에서 전송된 LiDAR 및 위치 데이터를 처리."""
    data = request.get_json()
    if not data:
        return jsonify({"status": "ERROR", "message": "데이터 누락"}), 400
    result = navigator.update_info(data)

    print("=== /info 응답 ===")
    print(result)

    if result["status"] == "ERROR":
        return jsonify(result), 400
    return jsonify(result)

@app.route('/update_position', methods=['POST'])
def update_position():
    data = request.get_json()
    if not data or "position" not in data:
        return jsonify({"status": "ERROR", "message": "위치 데이터 누락"}), 400

    if isinstance(data["position"], str):
        result = navigator.position_handler.update_position(data["position"])
    else:
        position_str = f"{data['position']['x']},{data['position']['y']},{data['position']['z']}"
        result = navigator.position_handler.update_position(position_str)
    
    if result["status"] == "ERROR":
        return jsonify(result), 400
    return jsonify(result)

@app.route('/set_destination', methods=['POST'])
def set_destination():
    data = request.get_json()
    if not data or "destination" not in data:
        return jsonify({"status": "ERROR", "message": "목적지 데이터 누락"}), 400

    result = navigator.set_destination(data["destination"])
    if result["status"] == "ERROR":
        return jsonify(result), 400
    return jsonify(result)

@app.route('/get_move', methods=['GET'])
def get_move():
    return jsonify(navigator.get_move())

@app.route('/get_action', methods=['GET'])
def get_action():
    """get_move와 동일한 동작을 수행 (호환성 유지)."""
    return jsonify(navigator.get_move())

@app.route('/update_obstacle', methods=['POST'])
def update_obstacle():
    """정적 장애물 데이터를 Navigation 클래스에 반영."""
    data = request.get_json()
    if not data or "obstacles" not in data:
        return jsonify({"status": "ERROR", "message": "장애물 데이터 누락"}), 400

    result = navigator.update_obstacle(data)
    if result["status"] == "ERROR":
        return jsonify(result), 400
    return jsonify(result), 200

def run_flask():
    app.run(host=SERVER_CONFIG['flask_host'], port=SERVER_CONFIG['flask_port'])