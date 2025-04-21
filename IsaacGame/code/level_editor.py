# level_editor.py
import time
import pygame
from settings import *
from sprites import CollisionSprite, Enemy_Greed, Rock, Coin, Spider
from player import Player # <<< --- FIX 1: Import Player --- >>>
import numpy as np
import json
import os

class LevelEditor:
    def __init__(self, game):
        # Kept original init
        self.game = game
        self.grid_active = True
        self.grid_color = (100, 100, 100)
        self.tile_size = TILE_SIZE
        self.editor_active = False
        self.grid_width = WIDTH // self.tile_size
        self.grid_height = HEIGHT // self.tile_size
        self.object_types = ['wall', 'enemy_greed', 'spider', 'rock', 'coin']
        self.current_object_type_index = 0
        self.object_type_names = {'wall': "Wall", 'enemy_greed': "En_G", 'spider': "Spdr", 'rock': "Rock", 'coin': "Coin"}
        self.type_to_class = {'wall': Rock, 'enemy_greed': Enemy_Greed, 'spider': Spider, 'rock': Rock, 'coin': Coin}
        self.font = pygame.font.Font(None, 30)
        self.ui_background_color = (50, 50, 50)
        self.ui_text_color = (255, 255, 255)
        self.ui_padding = 10
        self.ui_rect = pygame.Rect(0, 0, 150, 50)
        self.ui_rect.bottomright = (WIDTH - 10, HEIGHT - 10)
        self.ui_text_surface = None
        self.ui_text_rect = None
        self.last_action_time = 0
        self.action_cooldown = 200
        self.update_ui()

    def toggle_editor(self): # Kept original
        self.editor_active = not self.editor_active
        print("Editor Activated" if self.editor_active else "Editor Deactivated")

    def draw_grid(self): # Kept original
        if not self.grid_active or not self.editor_active: return
        display_surface = self.game.screen
        start_x = int(-self.game.camera_offset.x % self.tile_size)
        for x in range(start_x, WIDTH + 1, self.tile_size): pygame.draw.line(display_surface, self.grid_color, (x, 0), (x, HEIGHT))
        start_y = int(-self.game.camera_offset.y % self.tile_size)
        for y in range(start_y, HEIGHT + 1, self.tile_size): pygame.draw.line(display_surface, self.grid_color, (0, y), (WIDTH, y))

    def run(self, dt): # Kept original
        if self.editor_active:
            self.draw_grid()
            self.draw_ui()

    def handle_editor_event(self, event): # Kept original
        if not self.editor_active: return
        current_time = pygame.time.get_ticks()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x and current_time - self.last_action_time > self.action_cooldown: self.change_object_type(1); self.last_action_time = current_time
            elif event.key == pygame.K_z and current_time - self.last_action_time > self.action_cooldown: self.change_object_type(-1); self.last_action_time = current_time
            elif event.key == pygame.K_s: self.save_room_template()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: self.place_object(event.pos)
            elif event.button == 3: self.remove_object(event.pos)

    def place_object(self, mouse_pos_screen):
        # Kept original coordinate conversion
        mouse_x_world = mouse_pos_screen[0] + self.game.camera_offset.x
        mouse_y_world = mouse_pos_screen[1] + self.game.camera_offset.y
        grid_x_world = (mouse_x_world // self.tile_size) * self.tile_size
        grid_y_world = (mouse_y_world // self.tile_size) * self.tile_size
        center_x_world = grid_x_world + self.tile_size // 2
        center_y_world = grid_y_world + self.tile_size // 2
        pos_world = (center_x_world, center_y_world)

        object_type = self.object_types[self.current_object_type_index]

        # Kept original checks for game attributes
        if not hasattr(self.game, 'current_room') or self.game.current_room is None: return
        if not hasattr(self.game, 'player'): return
        if not hasattr(self.game, 'enemy_sprites'): return

        # Get necessary references (kept original)
        all_sprites_group = self.game.all_sprites
        collision_group = self.game.collision_sprites
        enemy_group = self.game.enemy_sprites # Get enemy group ref
        player_ref = self.game.player

        # Kept original overlap check
        for sprite in all_sprites_group:
             if 'Player' in globals() or 'Player' in locals(): # Check added previously
                 if sprite.rect.collidepoint(pos_world) and not isinstance(sprite, Player):
                       print(f"Blocked: Object already exists near {pos_world}")
                       # return # Original was commented out
             elif sprite.rect.collidepoint(pos_world):
                   print(f"Blocked: Object already exists near {pos_world}")
                   # return # Original was commented out

        print(f"Placing {object_type} at world pos {pos_world}")

        # Instantiate objects
        if object_type == 'wall': Rock(pos_world, (all_sprites_group, collision_group), collision_group)
        elif object_type == 'enemy_greed':
             # <<< --- FIX 2: Pass enemy_group to constructor --- >>>
             Enemy_Greed(pos_world, (all_sprites_group, enemy_group), collision_group, player_ref, enemy_group)
        elif object_type == 'spider':
             # <<< --- FIX 3: Pass enemy_group to constructor --- >>>
             Spider(pos_world, (all_sprites_group, enemy_group), collision_group, player_ref, enemy_group)
        elif object_type == 'rock': Rock(pos_world, (all_sprites_group, collision_group), collision_group)
        elif object_type == 'coin': Coin(pos_world, (all_sprites_group,))
        else: print(f"Warning: Unknown object type '{object_type}'")

    def remove_object(self, mouse_pos_screen): # Kept original
        mouse_x_world = mouse_pos_screen[0] + self.game.camera_offset.x
        mouse_y_world = mouse_pos_screen[1] + self.game.camera_offset.y
        pos_world = (mouse_x_world, mouse_y_world)
        sprite_to_remove = None
        for sprite in self.game.all_sprites:
             if 'Player' in globals() or 'Player' in locals(): # Check added previously
                 if not isinstance(sprite, (Player, CollisionSprite)) and sprite.rect.collidepoint(pos_world): sprite_to_remove = sprite; break
             elif not isinstance(sprite, CollisionSprite) and sprite.rect.collidepoint(pos_world): sprite_to_remove = sprite; break
        if sprite_to_remove: print(f"Removing {type(sprite_to_remove).__name__} at {pos_world}"); sprite_to_remove.kill()
        else: print(f"No removable object found at {pos_world}")

    def change_object_type(self, direction): # Kept original
        self.current_object_type_index = (self.current_object_type_index + direction) % len(self.object_types)
        self.update_ui()
        print(f"Selected object type: {self.object_types[self.current_object_type_index]}")

    def update_ui(self): # Kept original
        type_key = self.object_types[self.current_object_type_index]
        display_name = self.object_type_names.get(type_key, "Unknown")
        text_str = f"Adding: {display_name} (S to Save)"
        self.ui_text_surface = self.font.render(text_str, True, self.ui_text_color)
        self.ui_rect.width = self.ui_text_surface.get_width() + self.ui_padding * 2
        self.ui_rect.bottomright = (WIDTH - 10, HEIGHT - 10)
        self.ui_text_rect = self.ui_text_surface.get_rect(center=self.ui_rect.center)

    def draw_ui(self): # Kept original
        if not self.editor_active: return
        pygame.draw.rect(self.game.screen, self.ui_background_color, self.ui_rect)
        if self.ui_text_surface: self.game.screen.blit(self.ui_text_surface, self.ui_text_rect)

    def save_room_template(self, filename=None): # Kept original
        if not self.editor_active: return
        if not hasattr(self.game, 'all_sprites'): return
        if not hasattr(self.game, 'current_room') or self.game.current_room is None: return
        if filename is None: room_coords = f"{self.game.current_room.grid_x}_{self.game.current_room.grid_y}"; filename = f"room_{room_coords}_{int(time.time())}.json"
        print(f"Attempting to save room layout to {filename}...")
        room_data = {"objects": []}
        room_origin_x = self.game.current_room.world_x
        room_origin_y = self.game.current_room.world_y
        if 'Player' in globals() or 'Player' in locals(): sprites_to_save = [sprite for sprite in self.game.all_sprites if not isinstance(sprite, (Player, CollisionSprite))]
        else: sprites_to_save = [sprite for sprite in self.game.all_sprites if not isinstance(sprite, CollisionSprite)]
        for sprite in sprites_to_save:
            obj_data = None; sprite_type_str = None
            for type_str, cls in self.type_to_class.items():
                if isinstance(sprite, cls):
                     if isinstance(sprite, Rock): sprite_type_str = 'rock'; break
                     else: sprite_type_str = type_str; break
            if sprite_type_str and hasattr(sprite, 'rect'):
                grid_x = (sprite.rect.centerx - room_origin_x) // self.tile_size
                grid_y = (sprite.rect.centery - room_origin_y) // self.tile_size
                obj_data = {"type": sprite_type_str, "grid_x": grid_x, "grid_y": grid_y}
            elif sprite_type_str: print(f"Warning: Sprite {sprite} of type {sprite_type_str} lacks 'rect'.")
            if obj_data: room_data["objects"].append(obj_data)
        try:
            layouts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'layouts'); os.makedirs(layouts_dir, exist_ok=True)
            filepath = os.path.join(layouts_dir, filename)
            with open(filepath, 'w') as f: json.dump(room_data, f, indent=4)
            print(f"Room layout saved to {filepath}. Saved {len(room_data['objects'])} objects.")
        except Exception as e: print(f"Error saving room layout: {e}")