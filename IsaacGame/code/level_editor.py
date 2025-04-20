# level_editor.py
import time

import pygame
from settings import *
# Import necessary sprite classes
from sprites import CollisionSprite, Enemy_Greed, Rock, Coin
import numpy as np
import json # Import the json library
import os # Import os for path joining

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

        # Object types - Keep original lowercase keys
        # Map internal types to the classes for saving identification
        self.object_types = ['wall', 'enemy_greed', 'rock', 'coin']
        self.current_object_type_index = 0
        self.object_type_names = {
            'wall': "Wall",
            'enemy_greed': "En_G",
            'rock': "Rock",
            'coin': "Coin"
        }
        # Map object types to their classes for saving check
        self.type_to_class = {
            'wall': Rock, # Assuming 'wall' places a Rock sprite
            'enemy_greed': Enemy_Greed,
            'rock': Rock,
            'coin': Coin
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
        if self.editor_active:
            print("Editor Activated")
        else:
            print("Editor Deactivated")

    def draw_grid(self):
        # Only draw grid if editor is active
        if not self.grid_active or not self.editor_active:
            return

        # Draw vertical lines
        for x in range(0, WIDTH + 1, self.tile_size):
            pygame.draw.line(self.game.screen, self.grid_color, (x, 0), (x, HEIGHT))

        # Draw horizontal lines
        for y in range(0, HEIGHT + 1, self.tile_size):
            pygame.draw.line(self.game.screen, self.grid_color, (0, y), (WIDTH, y))

    def run(self, dt):
        # This method now only handles drawing editor elements when active
        if self.editor_active:
            self.draw_grid()
            self.draw_ui()

    # Renamed from handle_input to handle_editor_event
    # This will be called from the main game loop for each event
    def handle_editor_event(self, event):
        if not self.editor_active:
            return # Do nothing if editor isn't active

        current_time = pygame.time.get_ticks()

        if event.type == pygame.KEYDOWN:
            # Handle changing object type (Z/X)
            if event.key == pygame.K_x and current_time - self.last_action_time > self.action_cooldown:
                self.change_object_type(1)  # Go forward
                self.last_action_time = current_time
            elif event.key == pygame.K_z and current_time - self.last_action_time > self.action_cooldown:
                self.change_object_type(-1) # Go backward
                self.last_action_time = current_time
            # K_TAB is handled in main.py to toggle the editor
            # *** ADDED: Save functionality on 'S' key press ***
            elif event.key == pygame.K_s:
                 self.save_room_template()


        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle placing object on left click
            if event.button == 1: # Left mouse button
                # Need to adjust mouse position by camera offset if camera is active
                # For now, assume editor operates in screen coordinates
                # If objects should be placed in world coordinates, adjust event.pos
                # mouse_world_pos = (event.pos[0] + self.game.camera_offset.x, event.pos[1] + self.game.camera_offset.y)
                # self.place_object(mouse_world_pos)
                self.place_object(event.pos) # Use screen coordinates for now

    def place_object(self, mouse_pos):
        # Snap to grid based on mouse position (screen coordinates)
        grid_x = mouse_pos[0] // self.tile_size
        grid_y = mouse_pos[1] // self.tile_size

        # Calculate center position for the grid cell in screen coordinates
        center_x_screen = grid_x * self.tile_size + self.tile_size // 2
        center_y_screen = grid_y * self.tile_size + self.tile_size // 2

        # Convert screen coordinates to world coordinates using camera offset
        # This ensures objects are placed correctly relative to the game world
        center_x_world = center_x_screen + self.game.camera_offset.x
        center_y_world = center_y_screen + self.game.camera_offset.y
        pos = (center_x_world, center_y_world)


        object_type = self.object_types[self.current_object_type_index]

        # Get the current room's collision group from the game instance
        # Ensure game.current_room and its collision_sprites group exist
        if not hasattr(self.game, 'current_room') or self.game.current_room is None or not hasattr(self.game.current_room, 'collision_sprites'):
             print("Error: Cannot place object. Current room or collision sprites group not found.")
             return

        # Use the main collision group from the game instance, which points to the current room's group
        current_room_collisions = self.game.collision_sprites
        # Use the game's all_sprites group which contains all sprites
        all_sprites_group = self.game.all_sprites

        print(f"Placing {object_type} at grid ({grid_x}, {grid_y}), world pos {pos}")

        # Instantiate and add the object
        # Note: 'wall' uses Rock sprite as a placeholder for collidable walls.
        if object_type == 'wall':
             # Place a Rock sprite, add to all_sprites and current room's collision_sprites.
             Rock(pos, (all_sprites_group, current_room_collisions), current_room_collisions)
             print(f"Placed Wall (using Rock sprite) at {pos}")
        elif object_type == 'enemy_greed':
             # Enemy needs collision group reference for its logic. Adds only to all_sprites.
             Enemy_Greed(pos, (all_sprites_group,), current_room_collisions)
             print(f"Placed Enemy_Greed at {pos}")
        elif object_type == 'rock':
             # Rock is collidable. Adds to all_sprites and current room's collision_sprites.
             Rock(pos, (all_sprites_group, current_room_collisions), current_room_collisions)
             print(f"Placed Rock at {pos}")
        elif object_type == 'coin':
             # Coin is not collidable. Adds only to all_sprites.
             Coin(pos, (all_sprites_group,))
             print(f"Placed Coin at {pos}")
        else:
             print(f"Warning: Unknown object type '{object_type}'")


    def change_object_type(self, direction):
        self.current_object_type_index = (self.current_object_type_index + direction) % len(self.object_types)
        self.update_ui()  # Update the UI when the type changes
        print(f"Selected object type: {self.object_types[self.current_object_type_index]}")


    def update_ui(self):
        # Use the name from object_type_names dictionary
        type_key = self.object_types[self.current_object_type_index]
        display_name = self.object_type_names.get(type_key, "Unknown") # Default to "Unknown" if key not found
        text_str = f"Adding: {display_name} (S to Save)" # Updated UI text
        self.ui_text_surface = self.font.render(text_str, True, self.ui_text_color)
        # Adjust UI rect width based on text size + padding
        self.ui_rect.width = self.ui_text_surface.get_width() + self.ui_padding * 2
        self.ui_rect.bottomright = (WIDTH - 10, HEIGHT - 10) # Reposition after width change
        self.ui_text_rect = self.ui_text_surface.get_rect(center=self.ui_rect.center)  # Center the text

    def draw_ui(self):
        # Only draw UI if editor is active
        if not self.editor_active:
            return
        pygame.draw.rect(self.game.screen, self.ui_background_color, self.ui_rect)
        if self.ui_text_surface: # Ensure surface is created before drawing
             self.game.screen.blit(self.ui_text_surface, self.ui_text_rect)

    # *** ADDED: Method to save room layout to JSON ***
    import time
    def save_room_template(self, filename=f"room_template_{time.time()}.json"):
        if not self.editor_active:
            print("Error: Cannot save, editor is not active.")
            return
        if not hasattr(self.game, 'all_sprites'):
            print("Error: Cannot save, game object does not have 'all_sprites' group.")
            return
        if not hasattr(self.game, 'current_room') or self.game.current_room is None:
             print("Error: Cannot save. Current room not found.")
             return

        print(f"Attempting to save room layout to {filename}...")

        room_data = {"objects": []}
        # Get the current room's top-left corner in world coordinates
        room_origin_x = self.game.current_room.world_x
        room_origin_y = self.game.current_room.world_y


        # Iterate through all sprites in the game
        for sprite in self.game.all_sprites:
            obj_data = None
            # Check sprite type and save relevant info
            # We need to determine the 'type' string ('wall', 'enemy_greed', etc.)
            # based on the sprite's class.
            sprite_type_str = None
            for type_str, cls in self.type_to_class.items():
                 # Special handling for 'wall' which uses Rock class
                 if type_str == 'wall' and isinstance(sprite, Rock):
                     # Need a way to distinguish wall-Rocks from normal Rocks if needed.
                     # For now, assume any Rock could be a wall or a rock. Saving as 'rock'.
                     # If distinction is crucial, sprite needs an attribute.
                     # Let's prioritize 'rock' if it's a Rock instance.
                     # A better approach might be needed if 'wall' must be saved differently.
                     if sprite_type_str is None or sprite_type_str != 'rock':
                          sprite_type_str = 'rock' # Defaulting Wall-Rocks to 'rock'
                 elif type_str != 'wall' and isinstance(sprite, cls):
                      sprite_type_str = type_str
                      break # Found the specific type

            # If we identified the sprite type among the placeable objects
            if sprite_type_str:
                # Calculate position relative to the current room's top-left corner (0,0)
                # This makes the template independent of the room's world position
                relative_x = sprite.rect.centerx - room_origin_x
                relative_y = sprite.rect.centery - room_origin_y

                # Convert relative world coordinates back to grid coordinates for consistency
                # This assumes the editor places objects snapped to the grid
                grid_x = (sprite.rect.centerx - room_origin_x) // self.tile_size
                grid_y = (sprite.rect.centery - room_origin_y) // self.tile_size

                obj_data = {
                    "type": sprite_type_str,
                    # Saving grid coordinates relative to the room
                    "grid_x": grid_x,
                    "grid_y": grid_y
                    # Optionally save precise relative pixel coords if needed:
                    # "relative_x": relative_x,
                    # "relative_y": relative_y
                }

            if obj_data:
                room_data["objects"].append(obj_data)

        # Save to JSON file
        try:
            # Ensure the path is correct (save in the same directory as the script for simplicity)
            filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)),'layouts', filename)
            with open(filepath, 'w') as f:
                json.dump(room_data, f, indent=4)
            print(f"Room layout saved successfully to {filepath}")
            print(f"Saved {len(room_data['objects'])} objects.")
        except Exception as e:
            print(f"Error saving room layout: {e}")