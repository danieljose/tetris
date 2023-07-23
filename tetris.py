import sys
import pygame
import random
import json
import datetime
from pygame.locals import *

GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_SIZE = 25
WINDOW_WIDTH = GRID_WIDTH * GRID_SIZE + 200
WINDOW_HEIGHT = GRID_HEIGHT * GRID_SIZE

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

TETROMINOES = {
    'I': {'rotations': 2, 'colors': CYAN},
    'O': {'rotations': 1, 'colors': YELLOW},
    'T': {'rotations': 4, 'colors': MAGENTA},
    'S': {'rotations': 2, 'colors': GREEN},
    'Z': {'rotations': 2, 'colors': RED},
    'J': {'rotations': 4, 'colors': BLUE},
    'L': {'rotations': 4, 'colors': ORANGE}
}

SHAPES = {
    'I': [[[1, 1, 1, 1]], [[1], [1], [1], [1]]],
    'O': [[[1, 1], [1, 1]]],
    'T': [[[0, 1, 0], [1, 1, 1]], [[1, 0], [1, 1], [1, 0]], [[1, 1, 1], [0, 1, 0]], [[0, 1], [1, 1], [0, 1]]],
    'S': [[[0, 1, 1], [1, 1, 0]], [[1, 0], [1, 1], [0, 1]]],
    'Z': [[[1, 1, 0], [0, 1, 1]], [[0, 1], [1, 1], [1, 0]]],
    'J': [[[1, 0, 0], [1, 1, 1]], [[1, 1], [1, 0], [1, 0]], [[1, 1, 1], [0, 0, 1]], [[0, 1], [0, 1], [1, 1]]],
    'L': [[[0, 0, 1], [1, 1, 1]], [[1, 1], [0, 1], [0, 1]], [[1, 1, 1], [1, 0, 0]], [[1, 0], [1, 0], [1, 1]]]
}

SCORES = {'1': 40, '2': 100, '3': 300, '4': 1200}

class Tetromino:
    def __init__(self, shape):
        self.shape = shape
        self.rotation = 0
        self.color = TETROMINOES[shape]['colors']
        self.rotations = TETROMINOES[shape]['rotations']
        self.x = GRID_WIDTH // 2 - 1
        self.y = 1

    def rotate(self):
        self.rotation = (self.rotation + 1) % self.rotations

    def get_coordinates(self):
        shape = SHAPES[self.shape][self.rotation]
        coords = []
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    coords.append((x + self.x, y + self.y))
        return coords

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def draw(self, screen):
        for x, y in self.get_coordinates():
            pygame.draw.rect(screen, self.color, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

class Tetris:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        self.grid = [[0] * GRID_HEIGHT for _ in range(GRID_WIDTH)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.level = 1
        self.paused = False
        self.game_over = False
        self.score_updated = False
        self.high_scores = self.load_high_scores()

    def new_piece(self):
        return Tetromino(random.choice(list(TETROMINOES)))

    def draw_grid(self):
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if self.grid[x][y]:
                    pygame.draw.rect(self.screen, self.grid[x][y], (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    def draw_next_piece(self):
        for x, y in self.next_piece.get_coordinates():
            pygame.draw.rect(self.screen, self.next_piece.color, ((x + GRID_WIDTH) * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    def draw_score(self):
        font = pygame.font.Font(None, 36)
        text = font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(text, (GRID_WIDTH * GRID_SIZE + 50, WINDOW_HEIGHT // 2))

    def draw_level(self):
        font = pygame.font.Font(None, 36)
        text = font.render(f'Level: {self.level}', True, WHITE)
        self.screen.blit(text, (GRID_WIDTH * GRID_SIZE + 50, WINDOW_HEIGHT // 2 + 50))

    def draw_game_over(self):
        font = pygame.font.Font(None, 72)
        text = font.render('Game Over', True, RED)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        pygame.draw.rect(self.screen, BLACK, text_rect.inflate(20,20))
        self.screen.blit(text, text_rect)

        font = pygame.font.Font(None, 36)
        new_game_text = font.render('Press N to start a new game', True, WHITE)
        new_game_text_rect = new_game_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        pygame.draw.rect(self.screen, BLACK, new_game_text_rect.inflate(20,20))
        self.screen.blit(new_game_text, new_game_text_rect)

        text_scores = font.render('Press S to view high scores', True, WHITE)
        high_scores_text_rect = text_scores.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 45))
        pygame.draw.rect(self.screen, BLACK, high_scores_text_rect.inflate(20,20))
        self.screen.blit(text_scores, high_scores_text_rect)

    def draw_pause(self):
        font = pygame.font.Font(None, 72)
        text = font.render('Paused', True, WHITE)
        self.screen.blit(text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 100))

    def draw_controls(self):
        font = pygame.font.Font(None, 24)
        controls_text = [
            "Controls:",
            "Left/Right: Move",
            "Up: Rotate",
            "Down: Soft Drop",
            "Space: Hard Drop",
            "P: Pause/Resume"
        ]
        for i, text in enumerate(controls_text):
            surface = font.render(text, True, WHITE)
            self.screen.blit(surface, (GRID_WIDTH * GRID_SIZE + 10, WINDOW_HEIGHT // 2 + 100 + i * 25))

    def load_high_scores(self):
        try:
            with open("high_scores.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save_high_scores(self):
        with open("high_scores.json", "w") as file:
            json.dump(self.high_scores, file)

    def update_high_scores(self):
        if not self.score_updated:
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            self.high_scores.append((self.score, current_datetime))  # Save score along with the datetime
            self.high_scores.sort(key=lambda x: x[0], reverse=True)  # Sort by the score, which is the first element of the tuple
            self.high_scores = self.high_scores[:20]  # Keep only the top 20 scores
            self.save_high_scores()
            self.score_updated = True

    def draw_high_scores(self):
        # Save the current game screen
        game_screen_copy = self.screen.copy()

        # Clear the game window
        self.screen.fill((0, 0, 0))  # Adjust the color as necessary

        # Load a font for displaying the scores
        font = pygame.font.Font(None, 24)  # Reduced font size to make the scores fit

        # Iterate over the high scores and draw each one
        for i, score in enumerate(self.high_scores):
            # Create a text surface for the score
            score_surface = font.render('Score: ' + str(score), True, (255, 255, 255))  # Adjust the color as necessary

            # Draw the score
            self.screen.blit(score_surface, (50, 100 + 30 * i))  # Adjust the position as necessary

        # Create a text surface for the "Press ESC to return to game" message
        return_msg = font.render('Press ESC to return to game', True, (255, 255, 255))  # Adjust the color as necessary

        # Draw the message
        self.screen.blit(return_msg, (50, 50))  # Adjust the position as necessary

        # Update the display
        pygame.display.flip()

        while True:
            # Process events
            for event in pygame.event.get():
                # User pressed a key
                if event.type == KEYDOWN:
                    # ESC key was pressed
                    if event.key == K_ESCAPE:
                        # Restore the game screen
                        self.screen.blit(game_screen_copy, (0, 0))
                        pygame.display.flip()
                        return  # Return to the main game

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()
        self.current_piece.draw(self.screen)
        self.draw_next_piece()
        self.draw_score()
        self.draw_level()
        self.draw_controls()
        pygame.draw.line(self.screen, WHITE, (GRID_WIDTH * GRID_SIZE, 0), (GRID_WIDTH * GRID_SIZE, WINDOW_HEIGHT), 5)
        if self.game_over:
            self.draw_game_over()
        elif self.paused:
            self.draw_pause()
        pygame.display.flip()

    def can_move(self, dx, dy):
        for x, y in self.current_piece.get_coordinates():
            if x + dx < 0 or x + dx >= GRID_WIDTH or y + dy >= GRID_HEIGHT or self.grid[x + dx][y + dy]:
                return False
        return True

    def can_rotate(self):
        self.current_piece.rotate()
        allowed = all(0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT and not self.grid[x][y] for x, y in self.current_piece.get_coordinates())
        self.current_piece.rotate()
        self.current_piece.rotate()
        self.current_piece.rotate()
        return allowed

    def freeze(self):
        for x, y in self.current_piece.get_coordinates():
            self.grid[x][y] = self.current_piece.color
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        if not self.can_move(0, 0):
            self.game_over = True

    def clear_lines(self):
        lines_cleared = 0
        for y in range(GRID_HEIGHT):
            if all(self.grid[x][y] for x in range(GRID_WIDTH)):
                lines_cleared += 1
                for x in range(GRID_WIDTH):
                    self.grid[x][y] = 0
                for x in range(GRID_WIDTH):
                    for yy in range(y, 1, -1):
                        self.grid[x][yy] = self.grid[x][yy - 1]
        if lines_cleared > 0:  # Only add to the score if lines were cleared
            self.score += SCORES[str(lines_cleared)] * self.level
        self.level = self.score // 1000 + 1
		
    def confirm_quit(self):
        # Create a text surface for the confirmation message
        font = pygame.font.Font(None, 36)

        # Split the confirmation message into two lines
        confirm_msg1 = font.render('Press Y to quit', True, (255, 255, 255))  # Adjust the color as necessary
        confirm_msg2 = font.render('or any other key to resume', True, (255, 255, 255))  # Adjust the color as necessary

        # Calculate the size of the box to draw
        box_width = max(confirm_msg1.get_width(), confirm_msg2.get_width()) + 20  # Add some padding
        box_height = confirm_msg1.get_height() + confirm_msg2.get_height() + 20  # Add some padding

        # Calculate the position of the box
        box_x = (WINDOW_WIDTH - box_width) // 2
        box_y = (WINDOW_HEIGHT - box_height) // 2

        # Draw the black box
        pygame.draw.rect(self.screen, (0, 0, 0), (box_x, box_y, box_width, box_height))

        # Calculate the position of the messages
        msg1_x = (WINDOW_WIDTH - confirm_msg1.get_width()) // 2
        msg1_y = box_y + 10  # Add some padding
        msg2_x = (WINDOW_WIDTH - confirm_msg2.get_width()) // 2
        msg2_y = msg1_y + confirm_msg1.get_height()

        # Draw the messages
        self.screen.blit(confirm_msg1, (msg1_x, msg1_y))
        self.screen.blit(confirm_msg2, (msg2_x, msg2_y))

        # Update the display
        pygame.display.flip()

        while True:
            # Process events
            for event in pygame.event.get():
                # User pressed a key
                if event.type == KEYDOWN:
                    if event.key == K_y:
                        return True
                    else:
                        return False
					
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.confirm_quit():
                        pygame.quit()
                        sys.exit()
                    else:
                        self.draw()  # Redraw the game state
                        pygame.display.flip()  # Update the display
                elif event.key == K_p:
                    self.paused = not self.paused
                elif event.key == K_s:
                    if self.game_over:
                        self.draw_high_scores()
                elif event.key == K_n:
                    if self.game_over:
                        self.__init__()
                elif not self.paused and not self.game_over:
                    if event.key == K_LEFT:
                        if self.can_move(-1, 0):
                            self.current_piece.move(-1, 0)
                    elif event.key == K_RIGHT:
                        if self.can_move(1, 0):
                            self.current_piece.move(1, 0)
                    elif event.key == K_DOWN:
                        if self.can_move(0, 1):
                            self.current_piece.move(0, 1)
                    elif event.key == K_UP:
                        if self.can_rotate():
                            self.current_piece.rotate()
                    elif event.key == K_SPACE:
                        while self.can_move(0, 1):
                            self.current_piece.move(0, 1)

    def main_loop(self):
        fall_time = 0
        fall_speed = max(1000 - self.level * 50, 50)
        self.draw()
        while True:
            fall_time += self.clock.get_time()
            self.handle_events()
            if not self.paused and not self.game_over:
                if fall_time > fall_speed:
                    fall_time = 0
                    if self.can_move(0, 1):
                        self.current_piece.move(0, 1)
                    else:
                        self.freeze()
                        self.clear_lines()
                self.draw()
            self.clock.tick(60)
            if self.game_over and not self.score_updated:
                self.update_high_scores()

if __name__ == '__main__':
    tetris = Tetris()
    tetris.game_over = True
    tetris.main_loop()
