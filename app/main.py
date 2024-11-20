import sys
import numpy as np
import pygame
import asyncio
from eightpuzzle import EightPuzzleGame
from fifteenpuzzle import FifteenPuzzleGame
import logging
from asyncio import Queue

logging.basicConfig(level=logging.DEBUG)

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
        self.solving_queue = Queue()
        self.is_solving = False

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
        
        # Vẽ grid và các mảnh puzzle
        grid_size = 3 if self.current_puzzle == "8" else 4
        cell_size = 600 // grid_size

        for i in range(grid_size * grid_size):
            x, y = (i % grid_size) * cell_size, (i // grid_size) * cell_size
            pygame.draw.rect(self.screen, BLACK, (x, y, cell_size, cell_size), BORDER_WIDTH)
            
            current_value = self.game.puzzle[i]
            if current_value != 0:  # Không vẽ ô trống
                if self.image_loaded and self.image_pieces:
                    try:
                        piece_index = current_value - 1
                        if 0 <= piece_index < len(self.image_pieces):
                            piece = self.image_pieces[piece_index]
                            # Thêm padding để tránh overlap với border
                            dest_rect = (
                                x + BORDER_WIDTH,
                                y + BORDER_WIDTH,
                                cell_size - 2 * BORDER_WIDTH,
                                cell_size - 2 * BORDER_WIDTH
                            )
                            # Scale piece to fit the cell if needed
                            scaled_piece = pygame.transform.scale(piece, (dest_rect[2], dest_rect[3]))
                            self.screen.blit(scaled_piece, (dest_rect[0], dest_rect[1]))
                    except Exception as e:
                        print(f"Error drawing piece {i}: {str(e)}")
                        # Fallback to colored rectangle if image fails
                        pygame.draw.rect(
                            self.screen,
                            PINK,
                            (x + BORDER_WIDTH, y + BORDER_WIDTH, 
                             cell_size - 2 * BORDER_WIDTH, cell_size - 2 * BORDER_WIDTH)
                        )
                else:
                    pygame.draw.rect(
                        self.screen,
                        PINK,
                        (x + BORDER_WIDTH, y + BORDER_WIDTH, 
                         cell_size - 2 * BORDER_WIDTH, cell_size - 2 * BORDER_WIDTH)
                    )

                if self.show_numbers:
                    number_text = self.font.render(str(current_value), True, BLACK)
                    text_rect = number_text.get_rect(
                        center=(x + cell_size // 2, y + cell_size // 2)
                    )
                    self.screen.blit(number_text, text_rect)

        # Vẽ preview ảnh gốc
        if self.original_image:
            scaled_preview = pygame.transform.scale(self.original_image, (300, 300))
            self.screen.blit(scaled_preview, (650, 200))

        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (650, 510))

        checkbox_color = BLACK if self.show_numbers else PINK
        checkbox_rect = pygame.Rect(650, 120, 15, 15)
        pygame.draw.rect(self.screen, checkbox_color, checkbox_rect)
        self.screen.blit(self.small_font.render("Show Numbers", True, BLACK), (670, 115))

        for key in self.buttons:
            pygame.draw.rect(self.screen, BUTTON_COLOR, self.buttons[key])
            self.screen.blit(
                self.button_font.render(key.capitalize(), True, BLACK), (self.buttons[key].x + 10, self.buttons[key].y + 10)
            )

        if self.game_won:
            win_text = self.font.render(self.win_message, True, BLACK)
            self.screen.blit(win_text, win_text.get_rect(center=(300, 350)))

        if self.image_loaded:
            print("Image is loaded")
            print(f"Number of pieces: {len(self.image_pieces)}")
            print(f"Original image size: {self.original_image.get_size()}")

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
        try:
            from platform import window
            
            input_element = window.document.createElement('input')
            input_element.type = 'file'
            input_element.accept = 'image/*'
            
            def handle_file(event):
                print("File selected")
                file = event.target.files[0]
                if file:
                    url = window.URL.createObjectURL(file)
                    print(f"Created URL: {url}")
                    asyncio.create_task(self.load_image_from_url(url))
            
            input_element.addEventListener('change', handle_file)
            input_element.click()
        except Exception as e:
            print(f"Error opening file dialog: {str(e)}")

    async def load_image_from_url(self, url):
        print("Starting image load...")
        try:
            from platform import window
            response = await window.fetch(url)
            array_buffer = await response.arrayBuffer()
            
            # Chuyển đổi array buffer thành Uint8Array
            uint8_array = window.Uint8Array.new(array_buffer)
            
            # Tạo một Blob từ array buffer
            blob = window.Blob.new([uint8_array], {'type': 'image/png'})
            image_url = window.URL.createObjectURL(blob)
            
            img = window.Image.new()
            
            def image_loaded(event):
                try:
                    # Tạo canvas với kích thước cố định 600x600
                    canvas = window.document.createElement('canvas')
                    canvas.width = 600
                    canvas.height = 600
                    ctx = canvas.getContext('2d')
                    
                    # Vẽ và scale ảnh về kích thước 600x600
                    ctx.drawImage(img, 0, 0, 600, 600)
                    
                    # Lấy dữ liệu pixel
                    image_data = ctx.getImageData(0, 0, 600, 600).data
                    
                    # Chuyển đổi thành surface Pygame
                    surf = pygame.image.frombuffer(bytes(image_data), (600, 600), 'RGBA')
                    self.original_image = surf
                    
                    # Tạo các mảnh puzzle
                    grid_size = 3 if self.current_puzzle == "8" else 4
                    piece_size = 600 // grid_size
                    
                    self.image_pieces = []
                    for i in range(grid_size):
                        for j in range(grid_size):
                            piece = pygame.Surface((piece_size, piece_size), pygame.SRCALPHA)
                            piece.blit(
                                self.original_image,
                                (0, 0),
                                (j * piece_size, i * piece_size, piece_size, piece_size)
                            )
                            self.image_pieces.append(piece)
                    
                    self.image_loaded = True
                    window.URL.revokeObjectURL(image_url)
                    print(f"Successfully created {len(self.image_pieces)} pieces")
                    
                except Exception as e:
                    print(f"Error in image processing: {str(e)}")
            
            def image_error(event):
                print(f"Error loading image: {event}")
            
            img.addEventListener('load', image_loaded)
            img.addEventListener('error', image_error)
            img.src = image_url
            
        except Exception as e:
            print(f"Error in load_image_from_url: {str(e)}")

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

    async def solve_async(self):
        """Giải puzzle theo cách không đồng bộ"""
        if self.is_solving:
            return
            
        self.is_solving = True
        self.solution_path = []
        self.solution_index = 0
        
        try:
            # Tạo một task riêng để giải puzzle
            solution = await asyncio.create_task(self.game.solve_puzzle_async())
            if solution:
                self.solution_path = solution
                # Thực hiện các bước giải từng bước một
                while self.solution_index < len(self.solution_path):
                    if not self.is_solving:  # Cho phép dừng giải
                        break
                    self.game.puzzle = self.solution_path[self.solution_index].copy()
                    self.solution_index += 1
                    await asyncio.sleep(SOLUTION_SPEED / 1000)  # Chuyển đổi ms sang giây
                
                if self.solution_index >= len(self.solution_path):
                    self.game_won = True
                    self.win_message = "You win!"
        except Exception as e:
            print(f"Error solving puzzle: {str(e)}")
        finally:
            self.is_solving = False

    async def run(self):
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for key in self.buttons:
                        if self.buttons[key].collidepoint(event.pos):
                            if key == "shuffle":
                                self.game.shuffle_puzzle()
                                self.game_won = False
                                self.win_message = ""
                                self.is_solving = False  # Dừng giải nếu đang giải
                            elif key == "solve":
                                # Bắt đầu giải puzzle
                                asyncio.create_task(self.solve_async())
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

            self.draw()
            clock.tick(30)
            await asyncio.sleep(0)  # Cho phép các coroutine khác chạy

    def print_debug_info(self):
        print(f"Image loaded: {self.image_loaded}")
        print(f"Number of pieces: {len(self.image_pieces) if self.image_pieces else 0}")
        print(f"Current puzzle state: {self.game.puzzle}")
        print(f"Grid size: {3 if self.current_puzzle == '8' else 4}")


if __name__ == "__main__":
    gui = PuzzleGUI()
    asyncio.run(gui.run())
