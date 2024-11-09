import sys
import numpy as np
import heapq
import random


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
        self.puzzle = np.array(range(9))
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
        solver = EightPuzzleSolver(self.puzzle)
        self.solution_path = solver.solve()
        return self.solution_path

    def move_tile(self, index):
        blank_index = np.where(self.puzzle == 0)[0].item()
        if index in (blank_index - 1, blank_index + 1, blank_index - 3, blank_index + 3):
            self.puzzle[blank_index], self.puzzle[index] = self.puzzle[index], self.puzzle[blank_index]

    def get_puzzle(self):
        return self.puzzle.tolist()


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
