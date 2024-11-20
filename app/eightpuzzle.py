import sys
import numpy as np
import heapq
import random
from collections import deque
import asyncio


class PuzzleState:
    def __init__(self, puzzle, parent=None):
        self.puzzle = puzzle
        self.parent = parent
        self.blank_index = np.where(self.puzzle == 0)[0].item()
        self.g = 0
        self.h = self.heuristic()
        self.f = self.g + self.h

    def heuristic(self):
        distance = 0
        goal = np.array([1, 2, 3, 4, 5, 6, 7, 8, 0])
        for i in range(1, 9):
            x1, y1 = divmod(np.where(self.puzzle == i)[0].item(), 3)
            x2, y2 = divmod(np.where(goal == i)[0].item(), 3)
            distance += abs(x1 - x2) + abs(y1 - y2)
        return distance

    def generate_children(self):
        children = []
        steps = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for step in steps:
            new_blank_index = self.blank_index + step[0] * 3 + step[1]
            if (
                new_blank_index in range(9)
                and not (self.blank_index % 3 == 0 and step[1] == -1)
                and not (self.blank_index % 3 == 2 and step[1] == 1)
            ):
                new_puzzle = self.puzzle.copy()
                new_puzzle[self.blank_index], new_puzzle[new_blank_index] = (
                    new_puzzle[new_blank_index],
                    new_puzzle[self.blank_index],
                )
                child_state = PuzzleState(new_puzzle, self)
                child_state.g = self.g + 1
                child_state.h = child_state.heuristic()
                child_state.f = child_state.g + child_state.h
                children.append(child_state)
        return children

    def __lt__(self, other):
        return self.f < other.f


class EightPuzzleSolver:
    def __init__(self, initial_puzzle):
        self.initial_state = PuzzleState(initial_puzzle)

    def solve(self):
        open_set = []
        closed_set = set()
        heapq.heappush(open_set, (self.initial_state.f, self.initial_state))

        while open_set:
            current_f, current_state = heapq.heappop(open_set)
            if np.array_equal(current_state.puzzle, np.array([1, 2, 3, 4, 5, 6, 7, 8, 0])):
                return self.get_solution_path(current_state)
            closed_set.add(tuple(current_state.puzzle.flatten()))
            for child in current_state.generate_children():
                if tuple(child.puzzle.flatten()) in closed_set:
                    continue
                heapq.heappush(open_set, (child.f, child))
        return []

    def get_solution_path(self, state):
        path = []
        while state:
            path.append(state.puzzle)
            state = state.parent
        return path[::-1]


class EightPuzzleGame:
    def __init__(self):
        self.puzzle = np.array([1, 2, 3, 4, 5, 6, 7, 8, 0])
        self.goal = np.array([1, 2, 3, 4, 5, 6, 7, 8, 0])
        self.solution_path = []

    def shuffle_puzzle(self):
        while True:
            random.shuffle(self.puzzle)
            if self.is_solvable(self.puzzle):
                break

    def is_solvable(self, puzzle):
        inversions = 0
        blank_row = 0
        for i in range(9):
            if puzzle[i] == 0:
                blank_row = i // 3 + 1
                continue
            for j in range(i + 1, 9):
                if puzzle[j] != 0 and puzzle[i] > puzzle[j]:
                    inversions += 1
        return (inversions % 2 == 0) if (blank_row % 2 == 1) else (inversions % 2 == 1)

    def solve_puzzle(self):
        def get_manhattan_distance(state):
            distance = 0
            size = 3
            for i in range(len(state)):
                if state[i] != 0:  # Bỏ qua ô trống
                    current_row = i // size
                    current_col = i % size
                    target_row = (state[i] - 1) // size
                    target_col = (state[i] - 1) % size
                    distance += abs(current_row - target_row) + abs(current_col - target_col)
            return distance

        def get_neighbors(state):
            neighbors = []
            state_list = list(state)
            try:
                empty = state_list.index(0)  # Tìm vị trí ô trống
            except ValueError:
                return neighbors  # Trả về list rỗng nếu không tìm thấy ô trống
            
            size = 3
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
            if empty < size * (size - 1):
                moves.append(size)

            # Tạo các trạng thái mới
            for move in moves:
                new_pos = empty + move
                if 0 <= new_pos < len(state):
                    new_state = state_list.copy()
                    new_state[empty], new_state[new_pos] = new_state[new_pos], new_state[empty]
                    neighbors.append(tuple(new_state))

            return neighbors

        def a_star():
            start = tuple(self.puzzle)
            goal = tuple(self.goal)
            
            if start == goal:
                return [np.array(start)]
            
            frontier = [(get_manhattan_distance(start), 0, start, [start])]
            heapq.heapify(frontier)
            visited = {start}
            
            while frontier:
                _, cost, current, path = heapq.heappop(frontier)
                
                if current == goal:
                    return [np.array(p) for p in path]
                
                for neighbor in get_neighbors(current):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        new_cost = cost + 1
                        priority = new_cost + get_manhattan_distance(neighbor)
                        new_path = list(path)
                        new_path.append(neighbor)
                        heapq.heappush(frontier, (priority, new_cost, neighbor, new_path))
            
            return [self.puzzle]  # Trả về trạng thái hiện tại nếu không tìm thấy giải pháp

        return a_star()

    def move_tile(self, index):
        blank_index = np.where(self.puzzle == 0)[0].item()
        if index in (blank_index - 1, blank_index + 1, blank_index - 3, blank_index + 3):
            self.puzzle[blank_index], self.puzzle[index] = self.puzzle[index], self.puzzle[blank_index]

    def get_puzzle(self):
        return self.puzzle.tolist()

    async def solve_puzzle_async(self):
        """Phiên bản không đồng bộ của solve_puzzle"""
        from collections import deque
        
        if np.array_equal(self.puzzle, self.goal):
            return [self.puzzle.copy()]

        visited = set()
        queue = deque([(self.puzzle.copy(), [])])
        moves_count = 0

        while queue and moves_count < 181440:  # Giới hạn số bước tìm kiếm
            current_state, path = queue.popleft()
            current_tuple = tuple(current_state)
            
            if current_tuple in visited:
                continue
                
            visited.add(current_tuple)
            moves_count += 1

            if moves_count % 1000 == 0:  # Cho phép UI cập nhật sau mỗi 1000 bước
                await asyncio.sleep(0)

            if np.array_equal(current_state, self.goal):
                return [np.array(p) for p in path] + [current_state]

            empty_index = np.where(current_state == 0)[0][0]
            possible_moves = self.get_possible_moves(empty_index)

            for move in possible_moves:
                new_state = current_state.copy()
                new_state[empty_index], new_state[move] = new_state[move], new_state[empty_index]
                
                if tuple(new_state) not in visited:
                    queue.append((new_state, path + [current_state.copy()]))

        return None  # Trả về None nếu không tìm thấy giải pháp

    def get_possible_moves(self, empty_index):
        """Lấy các bước di chuyển có thể từ vị trí hiện tại"""
        possible_moves = []
        grid_size = 3  # for 8-puzzle

        # Kiểm tra các hướng có thể di chuyển
        if empty_index % grid_size > 0:  # Có thể di chuyển sang trái
            possible_moves.append(empty_index - 1)
        if empty_index % grid_size < grid_size - 1:  # Có thể di chuyển sang phải
            possible_moves.append(empty_index + 1)
        if empty_index >= grid_size:  # Có thể di chuyển lên
            possible_moves.append(empty_index - grid_size)
        if empty_index < grid_size * (grid_size - 1):  # Có thể di chuyển xuống
            possible_moves.append(empty_index + grid_size)

        return possible_moves


game = EightPuzzleGame()


if sys.platform not in ("emscripten", "wasi"):
    from flask import Flask, jsonify, request, render_template

    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("game.html")

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
