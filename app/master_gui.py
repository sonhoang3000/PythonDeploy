import sys
import numpy as np
from eightpuzzle import EightPuzzleGame
from fifteenpuzzle import FifteenPuzzleGame
from datetime import datetime

if sys.platform not in ("emscripten", "wasi"):
    from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, session
    from pymongo import MongoClient
    import os

    app = Flask(__name__)
    app.secret_key = 'your_secret_key_here'

    # Kết nối MongoDB
    client = MongoClient("mongodb+srv://vuhoangson3000:123456789Son@cluster0.we2k3.mongodb.net/")
    db = client["user_database"]
    users_collection = db["users"]
    game_history_collection = db["game_history"]

    eight_puzzle_game = EightPuzzleGame()
    fifteen_puzzle_game = FifteenPuzzleGame()

    @app.route("/")
    def index():
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user = users_collection.find_one({"username": username, "password": password})
            if user:
                session['username'] = username
                return redirect(url_for("game"))
            else:
                return "Login failed. Invalid username or password."
        return render_template("login.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form["reg_username"]
            password = request.form["reg_password"]
            email = request.form["reg_email"]
            if users_collection.find_one({"username": username}):
                return "Username already exists. Please choose another."
            users_collection.insert_one({"username": username, "password": password, "email": email})
            return redirect(url_for("login"))
        return render_template("register.html")

    BUILD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build/web")

    @app.route("/game")
    def game():
        if 'username' not in session:
            return redirect(url_for('login'))
        return render_template("game.html", username=session['username'])

    @app.route("/logout")
    def logout():
        session.pop('username', None)
        return redirect(url_for('login'))

    @app.route('/api/move', methods=['POST'])
    def make_move():
        data = request.get_json()
        # TODO: Xử lý logic di chuyển
        return jsonify({'success': True})

    @app.route('/api/solve', methods=['POST'])
    def solve_puzzle():
        try:
            data = request.get_json()
            puzzle_type = data.get('type', '3x3')
            current_state = data.get('currentState', [])

            if puzzle_type == '3x3':
                eight_puzzle_game.puzzle = np.array(current_state)
                solution = eight_puzzle_game.solve_puzzle()
            else:
                fifteen_puzzle_game.puzzle = np.array(current_state)
                solution = fifteen_puzzle_game.solve_puzzle()

            return jsonify({'solution': [state.tolist() for state in solution]})
        except Exception as e:
            print(f"Error solving puzzle: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/upload-image', methods=['POST'])  
    def upload_image():
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        # TODO: Xử lý upload ảnh
        return jsonify({'success': True})

    @app.route('/api/save-score', methods=['POST'])
    def save_score():
        try:
            if 'username' not in session:
                return jsonify({'error': 'Chưa đăng nhập'}), 401
            
            data = request.get_json()
            score = data.get('score')
            puzzle_type = data.get('type', '3x3')
            
            game_record = {
                'username': session['username'],
                'score': score,
                'puzzle_type': puzzle_type,
                'timestamp': datetime.now(),
            }
            
            game_history_collection.insert_one(game_record)
            
            return jsonify({'success': True, 'message': 'Đã lưu điểm số thành công'})
        except Exception as e:
            print(f"Lỗi khi lưu điểm số: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/get-history', methods=['GET'])
    def get_history():
        try:
            if 'username' not in session:
                return jsonify({'error': 'Chưa đăng nhập'}), 401
            
            # Lấy 10 kết quả mới nhất
            history = game_history_collection.find(
                {'username': session['username']},
                {'_id': 0}
            ).sort('timestamp', -1).limit(10)
            
            # Chuyển đổi timestamp thành chuỗi ISO để JSON có thể xử lý
            history_list = []
            for record in history:
                record['timestamp'] = record['timestamp'].isoformat()
                history_list.append(record)
            
            return jsonify({'history': history_list})
        except Exception as e:
            print(f"Lỗi khi lấy lịch sử: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/delete-history', methods=['DELETE'])
    def delete_history():
        try:
            if 'username' not in session:
                return jsonify({'error': 'Chưa đăng nhập'}), 401
            
            # Xóa tất cả lịch sử của người dùng hiện tại
            result = game_history_collection.delete_many({'username': session['username']})
            
            if result.deleted_count > 0:
                return jsonify({
                    'success': True, 
                    'message': f'Đã xóa {result.deleted_count} bản ghi lịch sử'
                })
            else:
                return jsonify({
                    'success': True, 
                    'message': 'Không có lịch sử để xóa'
                })
            
        except Exception as e:
            print(f"Lỗi khi xóa lịch sử: {str(e)}")
            return jsonify({'error': str(e)}), 500

    # Thêm các route để phục vụ static files
    @app.route('/static/<path:path>')
    def serve_static(path):
        return send_from_directory('static', path)

    if __name__ == "__main__":
        app.run(host="0.0.0.0", debug=True, port=4000)
