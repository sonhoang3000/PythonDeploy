from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
import random
import os

app = Flask(__name__)
# Kết nối MongoDB
client = MongoClient('mongodb+srv://vuhoangson3000:123456789Son@cluster0.we2k3.mongodb.net/')
db = client['user_database']
users_collection = db['users']

# Định nghĩa route gốc

@app.route('/test')
def home():
    return "Hello, Flask!"

@app.route('/')
def index():
    return redirect(url_for('login'))  # Điều hướng về trang đăng nhập

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({'username': username, 'password': password})
        if user:
            return redirect(url_for('game'))  # Chuyển đến trang trò chơi sau khi đăng nhập
        else:
            return 'Login failed. Invalid username or password.'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['reg_username']
        password = request.form['reg_password']
        email = request.form['reg_email']
        if users_collection.find_one({'username': username}):
            return 'Username already exists. Please choose another.'
        users_collection.insert_one({'username': username, 'password': password, 'email': email})
        return redirect(url_for('login'))
    return render_template('register.html')

# Danh sách puzzle ban đầu
puzzle = [1, 2, 3, 4, 5, 6, 7, 8, 0]

# Hàm xáo trộn puzzle
def shuffle_puzzle():
    random.shuffle(puzzle)
    return puzzle

def solve_puzzle():
    solution_steps = []  # Chưa thực hiện cụ thể
    return solution_steps

# API cho việc xáo trộn puzzle
@app.route('/shuffle', methods=['POST'])
def shuffle_puzzle_api():
    shuffled_puzzle = shuffle_puzzle()
    return jsonify(shuffled_puzzle)

@app.route('/solve', methods=['POST'])
def solve_puzzle_api():
    solution_steps = solve_puzzle()
    return jsonify(solution_steps)


@app.route('/move', methods=['POST'])
def move_tile_api():
    data = request.json
    index = data['index']

    # Di chuyển tile
    game.move_tile(index)

    # Kiểm tra nếu game đã thắng
    if game.check_win():
        game.game_won = True
        game.win_message = "You win!"

    # Trả về trạng thái mới của puzzle và nếu thắng thì gửi thông báo
    return jsonify({
        'puzzle': game.puzzle,
        'game_won': game.game_won,
        'win_message': game.win_message
    })


# API cho việc tải ảnh
@app.route('/load_image', methods=['POST'])
def load_image():
    # Đây là nơi để xử lý chọn ảnh
    file_path = request.form['image_path']
    if os.path.exists(file_path):
        return jsonify({"status": "success", "file_path": file_path})
    else:
        return jsonify({"status": "error", "message": "File not found"})

# Route cho game
@app.route('/game')
def game():
    return render_template('game.html')  # Hiển thị trang trò chơi trên trình duyệt

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True, port=80)
