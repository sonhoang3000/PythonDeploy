import sys
import numpy as np
import random


# Bổ sung lớp FifteenPuzzleGame để trả về dữ liệu JSON cho giao diện web
class FifteenPuzzleGame:
    def __init__(self):
        self.puzzle = np.array(range(16))
        self.goal = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0])
        self.solution_path = []

    def shuffle_puzzle(self):
        while True:
            random.shuffle(self.puzzle)
            if self.is_solvable(self.puzzle):
                break

    def is_solvable(self, puzzle):
        inversions = 0
        blank_row = 0
        for i in range(16):
            if puzzle[i] == 0:
                blank_row = i // 4 + 1
                continue
            for j in range(i + 1, 16):
                if puzzle[j] != 0 and puzzle[i] > puzzle[j]:
                    inversions += 1
        return (inversions % 2 == 0) if (blank_row % 2 == 1) else (inversions % 2 == 1)

    def move_tile(self, index):
        blank_index = np.where(self.puzzle == 0)[0].item()
        if index in (blank_index - 1, blank_index + 1, blank_index - 4, blank_index + 4):
            self.puzzle[blank_index], self.puzzle[index] = self.puzzle[index], self.puzzle[blank_index]

    def get_puzzle(self):
        return self.puzzle.tolist()


game = FifteenPuzzleGame()

if sys.platform not in ("emscripten", "wasi"):
    from flask import Flask, jsonify, request

    app = Flask(__name__)

    @app.route("/shuffle", methods=["GET"])
    def shuffle():
        game.shuffle_puzzle()
        return jsonify({"puzzle": game.get_puzzle()})

    @app.route("/move", methods=["POST"])
    def move():
        data = request.json
        game.move_tile(data["index"])
        return jsonify({"puzzle": game.get_puzzle()})

    if __name__ == "__main__":
        app.run(debug=True)
