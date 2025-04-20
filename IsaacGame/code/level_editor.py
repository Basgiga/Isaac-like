import pygame
from settings import *
import numpy as np

class LevelEditor:
    def __init__(self, game):
        self.game = game
        self.grid_active = True
        self.grid_color = (100, 100, 100)
        self.tile_size = TILE_SIZE
        self.editor_active = False

        # Calculate grid dimensions to fit the screen
        self.grid_width = WIDTH // self.tile_size
        self.grid_height = HEIGHT // self.tile_size

        # Object types
        self.object_types = ['wall', 'enemy_greed', 'rock', 'coin']
        self.current_object_type_index = 0
        self.object_type_names = {
            'wall': "Wall",
            'enemy_greed': "En_G",
            'rock': "Rock",
            'coin': "Coin"
        }

        # UI setup
        self.font = pygame.font.Font(None, 30)
        self.ui_background_color = (50, 50, 50)
        self.ui_text_color = (255, 255, 255)
        self.ui_padding = 10
        self.ui_rect = pygame.Rect(0, 0, 150, 50)  # Initial size, will be positioned later
        self.ui_rect.bottomright = (WIDTH - 10, HEIGHT - 10)
        self.ui_text_surface = None  # To store the rendered text
        self.ui_text_rect = None     # To store the text rect
        self.last_action_time = 0
        self.action_cooldown = 200  # milliseconds

        self.update_ui()  # Initialize the UI

    def toggle_editor(self):
        self.editor_active = not self.editor_active

    def draw_grid(self):
        if not self.grid_active:
            return

        # Draw vertical lines
        for x in range(0, WIDTH + 1, self.tile_size):
            pygame.draw.line(self.game.screen, self.grid_color, (x, 0), (x, HEIGHT))

        # Draw horizontal lines
        for y in range(0, HEIGHT + 1, self.tile_size):
            pygame.draw.line(self.game.screen, self.grid_color, (0, y), (WIDTH, y))

    def run(self, dt):
        self.handle_input()
        if self.editor_active:
            self.draw_grid()
            self.draw_ui()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        if self.editor_active:  # Only handle space in editor mode
            if keys[pygame.K_x] and current_time - self.last_action_time > self.action_cooldown:
                self.change_object_type(1)  # Go forward
                self.last_action_time = current_time
            elif keys[pygame.K_z] and current_time - self.last_action_time > self.action_cooldown:
                self.change_object_type(-1) # Go backward
                self.last_action_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.toggle_editor()

    def change_object_type(self, direction):
        self.current_object_type_index = (self.current_object_type_index + direction) % len(self.object_types)
        self.update_ui()  # Update the UI when the type changes

    def update_ui(self):
        text_str = f"Adding: {self.object_type_names[self.object_types[self.current_object_type_index]]}"
        self.ui_text_surface = self.font.render(text_str, True, self.ui_text_color)
        self.ui_text_rect = self.ui_text_surface.get_rect(center=self.ui_rect.center)  # Center the text

    def draw_ui(self):
        pygame.draw.rect(self.game.screen, self.ui_background_color, self.ui_rect)
        self.game.screen.blit(self.ui_text_surface, self.ui_text_rect)