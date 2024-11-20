import sys
import numpy as np
import random
from collections import deque
import heapq
from typing import List, Tuple, Set
import asyncio


# Bổ sung lớp FifteenPuzzleGame để trả về dữ liệu JSON cho giao diện web
class FifteenPuzzleGame:
    def __init__(self):
        self.puzzle = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0])
        self.goal = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0])

    def get_manhattan_distance(self, state) -> int:
        distance = 0
        size = 4
        for i in range(len(state)):
            if state[i] != 0:  # Bỏ qua ô trống
                current_row = i // size
                current_col = i % size
                target_row = (state[i] - 1) // size
                target_col = (state[i] - 1) % size
                distance += abs(current_row - target_row) + abs(current_col - target_col)
        return distance

    def get_neighbors(self, state: Tuple[int, ...]) -> List[Tuple[int, ...]]:
        neighbors = []
        state_list = list(state)
        empty = state_list.index(0)
        size = 4

        # Các hướng di chuyển có thể: trái, phải, lên, xuống
        moves = []
        # Kiểm tra có thể di chuyển sang trái
        if empty % size > 0:
            moves.append(-1)
        # Kiểm tra có thể di chuyển sang phải
        if empty % size < size - 1:
            moves.append(1)
        # Kiểm tra có thể di chuyển lên
        if empty >= size:
            moves.append(-size)
        # Kiểm tra có thể di chuyển xuống
        if empty < len(state) - size:
            moves.append(size)

        # Tạo các trạng thái mới
        for move in moves:
            new_pos = empty + move
            if 0 <= new_pos < len(state):
                new_state = state_list.copy()
                new_state[empty], new_state[new_pos] = new_state[new_pos], new_state[empty]
                neighbors.append(tuple(new_state))

        return neighbors

    def solve_puzzle(self):
        def a_star():
            start = tuple(self.puzzle)
            goal = tuple(self.goal)
            
            if start == goal:
                return [np.array(start)]
            
            frontier = [(self.get_manhattan_distance(start), 0, start, [start])]
            heapq.heapify(frontier)
            visited = {start}
            
            while frontier:
                _, cost, current, path = heapq.heappop(frontier)
                
                if current == goal:
                    return [np.array(p) for p in path]
                
                for neighbor in self.get_neighbors(current):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        new_cost = cost + 1
                        priority = new_cost + self.get_manhattan_distance(neighbor)
                        new_path = list(path)
                        new_path.append(neighbor)
                        heapq.heappush(frontier, (priority, new_cost, neighbor, new_path))
                        
                        # Giới hạn độ sâu tìm kiếm để tránh tràn bộ nhớ
                        if len(path) > 100:  
                            continue
            
            return [self.puzzle]  # Trả về trạng thái hiện tại nếu không tìm thấy giải pháp

        return a_star()

    async def solve_puzzle_async(self):
        return self.solve_puzzle()

    def shuffle_puzzle(self, moves=100):
        for _ in range(moves):
            empty = np.where(self.puzzle == 0)[0][0]
            possible_moves = []
            
            # Kiểm tra các nước đi hợp lệ
            if empty % 4 > 0:  # Có thể di chuyển sang trái
                possible_moves.append(empty - 1)
            if empty % 4 < 3:  # Có thể di chuyển sang phải
                possible_moves.append(empty + 1)
            if empty >= 4:    # Có thể di chuyển lên
                possible_moves.append(empty - 4)
            if empty < 12:    # Có thể di chuyển xuống
                possible_moves.append(empty + 4)
            
            # Chọn một nước đi ngẫu nhiên
            if possible_moves:
                move = np.random.choice(possible_moves)
                self.puzzle[empty], self.puzzle[move] = self.puzzle[move], self.puzzle[empty]

    def move_tile(self, index):
        """Di chuyển một ô nếu nó nằm cạnh ô trống"""
        empty_index = np.where(self.puzzle == 0)[0][0]
        if index in (empty_index - 1, empty_index + 1, empty_index - 4, empty_index + 4):
            if abs(empty_index - index) == 1 and min(empty_index, index) // 4 != max(empty_index, index) // 4:
                return False
            self.puzzle[empty_index], self.puzzle[index] = self.puzzle[index], self.puzzle[empty_index]
            return True
        return False


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
