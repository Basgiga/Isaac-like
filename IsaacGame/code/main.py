import pygame
import sys
import random

from pygame import K_LEFT
from settings import *
from player import Player
from sprites import *
from os.path import join, dirname, abspath
from proceduralboxestest import generate_grid, find_and_set_boss_room, create_room_surface, unload_room_surface, get_room_from_grid
from level_editor import LevelEditor  # Import the LevelEditor


class Game:
    def __init__(self, WIDTH, HEIGHT):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Issac-Like")

        self.clock = pygame.time.Clock()
        self.running = True

        self.load_images()

        # Generate level
        self.grid, self.rooms = generate_grid()
        find_and_set_boss_room(self.grid, self.rooms)
        self.current_room = self.rooms[0]
        create_room_surface(self.current_room, self.floor_image, self.door_image)  # Load the starting room

        # Groups
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = self.current_room.collision_sprites  # Initial collision sprites
        self.tear_sprites = pygame.sprite.Group()

        # Player setup
        self.player = Player((WIDTH // 2, HEIGHT // 2), self.all_sprites, self.collision_sprites)
        self.all_sprites.add(self.player)

        # Tear timer
        self.can_shoot = True
        self.shoot_time = 0
        self.tear_cooldown = 1000

        # Camera setup
        self.camera_offset = pygame.math.Vector2(0, 0)
        self.update_camera()

        # Transition variables
        self.transitioning = False
        self.transition_timer = 0
        self.transition_duration = 200  # milliseconds

        # Minimap setup
        self.minimap_scale = 0.20
        self.minimap_x = 10
        self.minimap_y = 10
        self.grid_width, self.grid_height = self.grid.shape
        self.room_size_on_minimap = int(min(WIDTH, HEIGHT) * self.minimap_scale / max(self.grid_width, self.grid_height))
        self.current_room_color = (255, 255, 255)
        self.room_color = (100, 100, 100)
        self.door_color = (0, 100, 0)

        # Level Editor
        self.level_editor = LevelEditor(self)  # Pass the Game instance

    def load_images(self):
        # Load assets
        base_folder = dirname(dirname(abspath(__file__)))
        flooar_path = join(base_folder, 'images', 'assets', 'floor.png')
        door_path = join(base_folder, 'images', 'assets', 'door.png')

        # floor img
        new_width = 1400
        new_height = 800
        self.floor_image = pygame.image.load(flooar_path).convert()
        self.floor_image = pygame.transform.scale(self.floor_image, (new_width, new_height))

        # door img
        new_width = 161
        new_height = 86
        self.door_image = pygame.image.load(door_path).convert_alpha()
        self.door_image = pygame.transform.scale(self.door_image, (new_width, new_height))

        # tear img
        tear_path = join(base_folder, 'images', 'assets', 'tear.png')
        self.tear_surf = pygame.image.load(tear_path).convert_alpha()

    def input(self):
        keys = pygame.key.get_pressed()
        if self.can_shoot and not self.level_editor.editor_active:  # Only shoot if not in editor
            direction = pygame.math.Vector2(0, 0)
            rotation = 0
            offset_x = 0
            offset_y = 0

            if keys[pygame.K_LEFT]:
                direction.x = -1
                rotation = -90
                offset_x = -30
            elif keys[pygame.K_RIGHT]:
                direction.x = 1
                rotation = 90
                offset_x = 30
            elif keys[pygame.K_UP]:
                direction.y = -1
                rotation = 180
                offset_y = -30
            elif keys[pygame.K_DOWN]:
                direction.y = 1
                rotation = 0
                offset_y = 30
            else:
                return

            if direction.magnitude():
                pos = self.player.rect.center + self.player.direction * 10
                rotated_tear_surf = pygame.transform.rotate(self.tear_surf, rotation)

                new_pos = (pos[0] + offset_x, pos[1] + offset_y)
                scale_factor = 0.8
                new_width = int(rotated_tear_surf.get_width() * scale_factor)
                new_height = int(rotated_tear_surf.get_height() * scale_factor)
                scaled_tear_surf = pygame.transform.scale(rotated_tear_surf, (new_width, new_height))

                Tear(scaled_tear_surf, new_pos, direction, (self.all_sprites, self.tear_sprites),
                     self.collision_sprites)
                print("shoot")
                self.can_shoot = False
                self.shoot_time = pygame.time.get_ticks()

    def tear_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.tear_cooldown:
                self.can_shoot = True

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        self.level_editor.toggle_editor()

            self.all_sprites.update(dt)
            self.tear_timer()
            self.input()
            self.update(dt)
            self.level_editor.run(dt)  # Crucial line: Run the editor every frame
            self.draw()

        pygame.quit()

    def update(self, dt):
        if not self.transitioning and not self.level_editor.editor_active:
            self.player.update(dt)
            self.update_camera()
            self.check_room_transition()
        elif self.transitioning:
            current_time = pygame.time.get_ticks()
            if current_time - self.transition_timer >= self.transition_duration:
                self.transitioning = False
            for tear in self.tear_sprites:
                tear.kill()
            self.can_shoot = True

        #self.level_editor.run(dt)  # Run the level editor every frame #This line was moved to the run function

    def update_camera(self):
        # Center the camera on the player
        self.camera_offset.x = self.player.rect.centerx - WIDTH // 2
        self.camera_offset.y = self.player.rect.centery - HEIGHT // 2

        # Clamp camera to room bounds
        self.camera_offset.x = max(self.current_room.world_x,
                                   min(self.camera_offset.x, self.current_room.world_x + WIDTH - WIDTH))
        self.camera_offset.y = max(self.current_room.world_y,
                                   min(self.camera_offset.y, self.current_room.world_y + HEIGHT - HEIGHT))

    def check_room_transition(self):
        player_rect = self.player.hitbox_rect  # Use the hitbox
        room_rect = self.current_room.rect
        door_threshold = 10  # Adjust this value as needed
        door_threshold_lr = 15
        if player_rect.left < room_rect.left + door_threshold_lr and self.current_room.door_left:
            self.change_room(-1, 0)
        elif player_rect.right > room_rect.right - door_threshold_lr and self.current_room.door_right:
            self.change_room(1, 0)
        elif player_rect.top < room_rect.top + door_threshold and self.current_room.door_up:
            self.change_room(0, -1)
        elif player_rect.bottom > room_rect.bottom - door_threshold and self.current_room.door_down:
            self.change_room(0, 1)

    def change_room(self, dx, dy):
        if not self.transitioning:
            self.transitioning = True
            self.transition_timer = pygame.time.get_ticks()

            current_grid_x = self.current_room.grid_x
            current_grid_y = self.current_room.grid_y
            new_grid_x = current_grid_x + dx
            new_grid_y = current_grid_y + dy

            new_room = get_room_from_grid(self.rooms, new_grid_x, new_grid_y)
            if new_room:
                # Unload old rooms (optional, depending on memory management)
                # self.unload_adjacent_rooms()

                # Load new room and adjacent rooms
                self.current_room = new_room
                if not self.current_room.loaded:
                    create_room_surface(self.current_room, self.floor_image, self.door_image)
                elif self.current_room.start == True:
                    create_room_surface(self.current_room, self.floor_image, self.door_image)
                self.collision_sprites.empty()
                self.collision_sprites.add(self.current_room.collision_sprites)
                self.player.collision_sprites = self.collision_sprites  # Update player's collision sprites
                self.load_adjacent_rooms()

                # Adjust player position (example: center of the door)
                if dx > 0:
                    self.player.rect.left = self.current_room.rect.left + 50
                elif dx < 0:
                    self.player.rect.right = self.current_room.rect.right - 50
                elif dy > 0:
                    self.player.rect.top = self.current_room.rect.top + 50
                elif dy < 0:
                    self.player.rect.bottom = self.current_room.rect.bottom - 50

                # Update hitbox_rect to match
                self.player.hitbox_rect.center = self.player.rect.center
                self.update_camera()

    def load_adjacent_rooms(self):
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            grid_x = self.current_room.grid_x + dx
            grid_y = self.current_room.grid_y + dy
            adjacent_room = get_room_from_grid(self.rooms, grid_x, grid_y)
            if adjacent_room and not adjacent_room.loaded:
                create_room_surface(adjacent_room, self.floor_image, self.door_image)

    def unload_adjacent_rooms(self):
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)]:
            grid_x = self.current_room.grid_x + dx
            grid_y = self.current_room.grid_y + dy
            adjacent_room = get_room_from_grid(self.rooms, grid_x, grid_y)
            if adjacent_room and adjacent_room != self.current_room and adjacent_room.loaded:
                unload_room_surface(adjacent_room)

    def draw_minimap(self):
        for room in self.rooms:
            rect_x = self.minimap_x + room.grid_x * self.room_size_on_minimap
            rect_y = self.minimap_y + room.grid_y * self.room_size_on_minimap
            rect = pygame.Rect(rect_x, rect_y, self.room_size_on_minimap, self.room_size_on_minimap)
            rect_border = pygame.Rect(rect_x, rect_y, self.room_size_on_minimap, self.room_size_on_minimap)

            # Highlight current room
            if room == self.current_room:
                pygame.draw.rect(self.screen, self.current_room_color, rect)
                pygame.draw.rect(self.screen, (0, 0, 0), rect_border, 1)
            else:
                pygame.draw.rect(self.screen, self.room_color, rect, 0)  # Filled rectangle
                pygame.draw.rect(self.screen, (0, 0, 0), rect_border, 1)
            # Draw doors
            door_size = self.room_size_on_minimap // 3
            door_offset = self.room_size_on_minimap // 3

            font_size = self.room_size_on_minimap
            font = pygame.font.Font(None, font_size)
            s_color = (255, 100, 0)

            if room.start == True:
                s_text = font.render("S", True, s_color)
                text_rect = s_text.get_rect(center=rect.center)
                self.screen.blit(s_text, text_rect)

            if room.boss == True:
                s_text = font.render("B", True, s_color)
                text_rect = s_text.get_rect(center=rect.center)
                self.screen.blit(s_text, text_rect)

            if room.door_left:
                pygame.draw.rect(self.screen, self.door_color,
                             (rect_x, rect_y + door_offset, door_size // 2, door_size))
            if room.door_right:
                pygame.draw.rect(self.screen, self.door_color,
                             (rect_x + self.room_size_on_minimap - door_size // 2, rect_y + door_offset,
                              door_size // 2, door_size))
            if room.door_up:
                pygame.draw.rect(self.screen, self.door_color,
                             (rect_x + door_offset, rect_y, door_size, door_size // 2))
            if room.door_down:
                pygame.draw.rect(self.screen, self.door_color,
                             (rect_x + door_offset, rect_y + self.room_size_on_minimap - door_size // 2,
                              door_size, door_size // 2))

    def draw(self):
        if not self.level_editor.editor_active:  # Only draw game elements if editor is inactive
            self.screen.fill((0, 0, 0, 0))
            self.current_room.draw(self.screen, self.camera_offset)
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, sprite.rect.topleft - self.camera_offset)
            self.all_sprites.draw(self.screen)
            self.draw_minimap()
        #else:
        # self.screen.fill((0, 0, 0, 0))  # Clear the screen to black in editor mode
        self.level_editor.run(0)  # Run the level editor every frame
        pygame.display.update()


if __name__ == '__main__':
    game = Game(WIDTH, HEIGHT)
    game.run()