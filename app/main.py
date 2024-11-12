import sys
import numpy as np
import pygame
import asyncio
from eightpuzzle import EightPuzzleGame
from fifteenpuzzle import FifteenPuzzleGame
import tkinter as tk
from tkinter import filedialog

XMAI = (255, 20, 147)
BLACK = (0, 0, 0)
PINK = (255, 105, 180)
BUTTON_COLOR = (135, 206, 235)
BORDER_WIDTH = 2
SOLUTION_SPEED = 300


class PuzzleGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 700))
        self.font = pygame.font.Font(None, 70)
        self.small_font = pygame.font.Font(None, 30)
        self.button_font = pygame.font.Font(None, 40)
        self.score_font = pygame.font.Font(None, 40)

        self.initialize_game("8")

        self.max_score = 1000
        self.score = self.max_score

        button_width, button_height, spacing = 120, 50, 60
        self.buttons = {
            "shuffle": pygame.Rect(50, 620, button_width, button_height),
            "solve": pygame.Rect(50 + button_width + spacing, 620, button_width, button_height),
            "image": pygame.Rect(50 + 2 * (button_width + spacing), 620, button_width, button_height),
            "3x3": pygame.Rect(50 + 3 * (button_width + spacing), 620, button_width, button_height),
            "4x4": pygame.Rect(50 + 4 * (button_width + spacing), 620, button_width, button_height),
        }

        self.image_loaded, self.image_pieces, self.original_image = False, [], None
        self.game_won, self.win_message, self.is_solving, self.solution_index = False, "", False, 0
        self.solution_path = []
        self.show_numbers = True

    def initialize_game(self, puzzle_type):
        self.current_puzzle = puzzle_type

        if puzzle_type == "8":
            self.game = EightPuzzleGame()
        else:
            self.game = FifteenPuzzleGame()

        self.game.shuffle_puzzle()

    def load_image(self, filepath):
        self.original_image = pygame.transform.scale(pygame.image.load(filepath), (600, 600))
        grid_size = 3 if self.current_puzzle == "8" else 4
        self.image_pieces = [
            self.original_image.subsurface(j * (600 // grid_size), i * (600 // grid_size), 600 // grid_size, 600 // grid_size)
            for i in range(grid_size)
            for j in range(grid_size)
        ]
        self.image_loaded = True

    def draw(self):
        self.screen.fill(XMAI)
        self.screen.blit(self.font.render("Nhóm 3", True, BLACK), (650, 160))

        if self.original_image:
            self.screen.blit(pygame.transform.scale(self.original_image, (300, 300)), (650, 200))

        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (650, 510))

        checkbox_color = BLACK if self.show_numbers else PINK
        checkbox_rect = pygame.Rect(650, 120, 15, 15)
        pygame.draw.rect(self.screen, checkbox_color, checkbox_rect)
        self.screen.blit(self.small_font.render("Show Numbers", True, BLACK), (670, 115))

        grid_size = 3 if self.current_puzzle == "8" else 4
        cell_size = 600 // grid_size

        for i in range(grid_size * grid_size):
            x, y = (i % grid_size) * cell_size, (i // grid_size) * cell_size
            pygame.draw.rect(self.screen, BLACK, (x, y, cell_size, cell_size), BORDER_WIDTH)
            if self.game.puzzle[i] != 0:
                piece = self.image_pieces[self.game.puzzle[i] - 1] if self.image_loaded else PINK
                (
                    self.screen.blit(piece, (x + BORDER_WIDTH, y + BORDER_WIDTH))
                    if self.image_loaded
                    else pygame.draw.rect(
                        self.screen,
                        PINK,
                        (x + BORDER_WIDTH, y + BORDER_WIDTH, cell_size - 2 * BORDER_WIDTH, cell_size - 2 * BORDER_WIDTH),
                    )
                )

                if self.show_numbers:
                    self.screen.blit(
                        self.font.render(str(self.game.puzzle[i]), True, BLACK),
                        (x + (cell_size - 40) / 2, y + (cell_size - 40) / 2),
                    )

        for key in self.buttons:
            pygame.draw.rect(self.screen, BUTTON_COLOR, self.buttons[key])
            self.screen.blit(
                self.button_font.render(key.capitalize(), True, BLACK), (self.buttons[key].x + 10, self.buttons[key].y + 10)
            )

        if self.game_won:
            win_text = self.font.render(self.win_message, True, BLACK)
            self.screen.blit(win_text, win_text.get_rect(center=(300, 350)))

        pygame.display.flip()

    def move(self, index):
        self.game.move_tile(index)
        self.score -= 20
        if self.score < 0:
            self.score = 0

        if np.array_equal(self.game.puzzle, self.game.goal):
            self.game_won = True
            self.win_message = "You win!"
            pygame.time.wait(100)

    def open_file_dialog(self):
        print("het loi nhung khong lay anh duoc")

    def change_puzzle(self, puzzle_type):
        self.initialize_game(puzzle_type)
        self.image_loaded, self.game_won, self.win_message = False, False, ""

    def get_possible_moves(self, empty_index):
        grid_size = 3 if self.current_puzzle == "8" else 4
        possible_moves = []

        if empty_index % grid_size > 0:
            possible_moves.append(empty_index - 1)
        if empty_index % grid_size < grid_size - 1:
            possible_moves.append(empty_index + 1)
        if empty_index // grid_size > 0:
            possible_moves.append(empty_index - grid_size)
        if empty_index // grid_size < grid_size - 1:
            possible_moves.append(empty_index + grid_size)

        return possible_moves

    async def run(self):
        running, clock = True, pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for key in self.buttons:
                        if self.buttons[key].collidepoint(event.pos):
                            if key == "shuffle":
                                self.game.shuffle_puzzle()
                                self.game_won, self.win_message = False, ""
                            elif key == "solve":
                                self.solution_path = self.game.solve_puzzle()
                                self.is_solving, self.solution_index = True, 0
                            elif key == "image":
                                self.open_file_dialog()
                            else:
                                self.change_puzzle("8" if key == "3x3" else "15")
                            break
                    else:
                        grid_size = 3 if self.current_puzzle == "8" else 4
                        x, y = event.pos
                        if y < 600:
                            clicked_index = (y // (600 // grid_size)) * grid_size + (x // (600 // grid_size))
                            empty_index = np.where(self.game.puzzle == 0)[0][0]
                            possible_moves = self.get_possible_moves(empty_index)

                            if clicked_index in possible_moves:
                                self.move(clicked_index)

                        if 650 <= event.pos[0] <= 665 and 120 <= event.pos[1] <= 135:
                            self.show_numbers = not self.show_numbers

            if self.is_solving and self.solution_index < len(self.solution_path):
                self.game.puzzle = self.solution_path[self.solution_index]
                self.solution_index += 1
                pygame.time.wait(SOLUTION_SPEED)
                if np.array_equal(self.game.puzzle, self.game.goal):
                    self.game_won = True
                    self.win_message = "You win!"

            self.draw()
            clock.tick(30)
            await asyncio.sleep(0)


if __name__ == "__main__":
    gui = PuzzleGUI()
    asyncio.run(gui.run())
