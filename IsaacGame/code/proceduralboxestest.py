import random
import numpy as np
from sprites import *
from settings import *
from collections import deque

class Room():
    def __init__(self, grid_x, grid_y, start=False, boss=False, shop=False):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.start = start
        self.boss = boss
        self.shop = shop
        self.door_left = False
        self.door_right = False
        self.door_up = False
        self.door_down = False
        self.surface = None  # Room surface will be created later
        self.rect = None  # Room rect will be created later
        self.world_x = 0
        self.world_y = 0
        self.collision_sprites = pygame.sprite.Group()
        self.loaded = False  # Track if the room is currently loaded

    def draw(self, surface, offset):
        if self.loaded:
            surface.blit(self.surface, (self.world_x - offset.x, self.world_y - offset.y))
            for sprite in self.collision_sprites:
                surface.blit(sprite.image, sprite.rect.topleft - offset)
def start_board(known_locations, rooms, HOW_MANY_ROOMS, fixed,fixed_grid_size):
    if not fixed:
        grid_size = HOW_MANY_ROOMS
    else:
        grid_size = fixed_grid_size

    grid = np.zeros((grid_size, grid_size), dtype=int)

    start_grid_x = grid_size // 2
    start_grid_y = grid_size // 2
    start_room = Room(grid_x=start_grid_x, grid_y=start_grid_y, start=True)

    known_locations.append((start_room.grid_x, start_room.grid_y))
    grid[start_room.grid_y, start_room.grid_x] = 1
    rooms.append(start_room)

    return grid

def check_placement(grid, check_grid_x, check_grid_y):
    grid_height, grid_width = grid.shape

    # Out of board
    if check_grid_x >= grid_width or check_grid_x < 0:
        return False
    if check_grid_y >= grid_height or check_grid_y < 0:
        return False

    # Already placed
    if grid[check_grid_y, check_grid_x] == 1:
        return False

    # Avoid squares, check:
    # Right down
    if check_grid_x + 1 < grid_width and check_grid_y + 1 < grid_height:
        if grid[check_grid_y + 1, check_grid_x] == 1 and grid[check_grid_y, check_grid_x + 1] == 1:
            return False
    # Right up
    if check_grid_x + 1 < grid_width and check_grid_y - 1 >= 0:
        if grid[check_grid_y - 1, check_grid_x] == 1 and grid[check_grid_y, check_grid_x + 1] == 1:
            return False
    # Left down
    if check_grid_x - 1 >= 0 and check_grid_y + 1 < grid_height:
        if grid[check_grid_y + 1, check_grid_x] == 1 and grid[check_grid_y, check_grid_x - 1] == 1:
            return False
    # Left up
    if check_grid_x - 1 >= 0 and check_grid_y - 1 >= 0:
        if grid[check_grid_y - 1, check_grid_x] == 1 and grid[check_grid_y, check_grid_x - 1] == 1:
            return False

    return True

def set_room_doors(grid, rooms):
    grid_height, grid_width = grid.shape

    for room in rooms:
        if room.grid_x + 1 < grid_width:
            if grid[room.grid_y, room.grid_x + 1] == 1:
                room.door_right = True
        if room.grid_x - 1 >= 0:
            if grid[room.grid_y, room.grid_x - 1] == 1:
                room.door_left = True
        if room.grid_y + 1 < grid_height:
            if grid[room.grid_y + 1, room.grid_x] == 1:
                room.door_down = True
        if room.grid_y - 1 >= 0:
            if grid[room.grid_y - 1, room.grid_x] == 1:
                room.door_up = True

    return rooms



def check_if_in_grid(grid, newx, newy):
    grid_height, grid_width = grid.shape
    if newx >= grid_width or newx < 0:
        return False
    if newy >= grid_height or newy < 0:
        return False
    return grid[newy][newx] == 1

def find_and_set_boss_room(grid, rooms, how_many_rooms=10):
    start_x, start_y = -1, -1
    for room in rooms:
        if room.start:
            start_x, start_y = room.grid_x, room.grid_y
            break

    if start_x == -1:
        print("Error: Starting room not found.")
        return

    room_distances = {(start_x, start_y): 0}
    reached_rooms = {(start_x, start_y)}
    queue = [(start_x, start_y, 0)]
    furthest_room = (start_x, start_y)
    max_distance = 0

    while queue and len(reached_rooms) < how_many_rooms:
        current_x, current_y, current_distance = queue.pop(0)



        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor_x, neighbor_y = current_x + dx, current_y + dy

            if check_if_in_grid(grid, neighbor_x, neighbor_y) and (neighbor_x, neighbor_y) not in reached_rooms:
                reached_rooms.add((neighbor_x, neighbor_y))
                room_distances[(neighbor_x, neighbor_y)] = current_distance + 1
                queue.append((neighbor_x, neighbor_y, current_distance + 1))

    furthest_room = max(room_distances, key = room_distances.get)
    #print("Room Distances:", room_distances)
    #print("Furthest Room:", furthest_room, "Distance:", max_distance)

    for room in rooms:
        if room.grid_x == furthest_room[0] and room.grid_y == furthest_room[1]:
            room.boss = True
            return
    print("Warning: Furthest room not found in rooms list.")




def generate_grid(HOW_MANY_ROOMS = 10, fixed = True ,fixed_grid_size = 7):
    rooms = []
    known_locations = []
    grid = start_board(known_locations, rooms, HOW_MANY_ROOMS, fixed,fixed_grid_size)
    rooms[0].start = True

    rooms_to_place = HOW_MANY_ROOMS -1
    while rooms_to_place > 0:
        los_index = random.randint(0, len(known_locations) - 1)
        current_grid_x, current_grid_y = known_locations[los_index]

        placed = False
        attempts = 0
        while not placed and attempts < 10:
            attempts += 1
            side = random.randint(1, 4)

            new_grid_x, new_grid_y = current_grid_x, current_grid_y  # Initialize new coordinates

            if side == 1:  # Left
                new_grid_x -= 1
            elif side == 2:  # Right
                new_grid_x += 1
            elif side == 3:  # Up
                new_grid_y -= 1
            else:  # Down
                new_grid_y += 1

            if check_placement(grid, new_grid_x, new_grid_y):
                known_locations.append((new_grid_x, new_grid_y))
                grid[new_grid_y, new_grid_x] = 1
                new_room = Room(grid_x=new_grid_x, grid_y=new_grid_y)
                rooms.append(new_room)
                placed = True
                rooms_to_place -= 1

    rooms = set_room_doors(grid, rooms)
    return grid, rooms

def create_room_surface(room, floor_image, door_image):
    room.surface = pygame.Surface((WIDTH, HEIGHT)).convert()
    room.surface.blit(floor_image, (0, 0))
    room.rect = room.surface.get_rect(topleft=(room.world_x, room.world_y))
    room.collision_sprites = pygame.sprite.Group()

    wall_thickness = 50  # Adjust as needed
    door_width = door_image.get_width()
    door_height = door_image.get_height()

    # Horizontal door y-position
    horizontal_door_y = HEIGHT // 2 - door_height // 2
    # Vertical door x-position
    vertical_door_x = WIDTH // 2 - door_width // 2

    horizontal_door_offset = 15

    # Top wall
    if not room.door_up:
        wall = CollisionSprite((WIDTH // 2, wall_thickness // 2), (WIDTH, wall_thickness), [room.collision_sprites])
    else:
        wall_left = CollisionSprite((vertical_door_x // 2, wall_thickness // 2), (vertical_door_x, wall_thickness), [room.collision_sprites])
        wall_right = CollisionSprite((vertical_door_x + door_width + (WIDTH - (vertical_door_x + door_width)) // 2, wall_thickness // 2), (WIDTH - (vertical_door_x + door_width), wall_thickness), [room.collision_sprites])

    # Bottom wall
    if not room.door_down:
        wall = CollisionSprite((WIDTH // 2, HEIGHT - wall_thickness // 2), (WIDTH, wall_thickness), [room.collision_sprites])
    else:
        wall_left = CollisionSprite((vertical_door_x // 2, HEIGHT - wall_thickness // 2), (vertical_door_x, wall_thickness), [room.collision_sprites])
        wall_right = CollisionSprite((vertical_door_x + door_width + (WIDTH - (vertical_door_x + door_width)) // 2, HEIGHT - wall_thickness // 2), (WIDTH - (vertical_door_x + door_width), wall_thickness), [room.collision_sprites])

    # LEFT WALL
    if not room.door_left:
        left_wall = CollisionSprite((wall_thickness // 2, HEIGHT // 2), (wall_thickness, HEIGHT),
                                    [room.collision_sprites])
    else:
        # Wall above the door
        top_height = horizontal_door_y
        wall_up = CollisionSprite((wall_thickness // 2, top_height // 2),
                                  (wall_thickness, top_height),
                                  [room.collision_sprites])

        # Wall below the door
        bottom_y = horizontal_door_y + door_height + 80
        bottom_height = HEIGHT - bottom_y
        wall_down = CollisionSprite((wall_thickness // 2, bottom_y + bottom_height // 2),
                                    (wall_thickness, bottom_height),
                                    [room.collision_sprites])

        # Optional invisible hitbox for the door (used only if needed for door checks)
        door_hitbox_left = CollisionSprite((0, horizontal_door_y), (wall_thickness, door_height), [])

        # Draw door image
        room.surface.blit(pygame.transform.rotate(door_image, 90),
                          (horizontal_door_offset - door_image.get_height() // 2 + wall_thickness // 2,
                           horizontal_door_y))

    # RIGHT WALL
    if not room.door_right:
        right_wall = CollisionSprite((WIDTH - wall_thickness // 2, HEIGHT // 2),
                                     (wall_thickness, HEIGHT),
                                     [room.collision_sprites])
    else:
        # Wall above the door
        top_height = horizontal_door_y
        wall_up = CollisionSprite((WIDTH - wall_thickness // 2, top_height // 2),
                                  (wall_thickness, top_height),
                                  [room.collision_sprites])


        # Wall below the door
        bottom_y = horizontal_door_y + door_height +80
        bottom_height = HEIGHT - bottom_y
        wall_down = CollisionSprite((WIDTH - wall_thickness // 2, bottom_y + bottom_height // 2),
                                    (wall_thickness, bottom_height),
                                    [room.collision_sprites])

        # Draw door image
        rotated_door = pygame.transform.rotate(door_image, 90)
        room.surface.blit(pygame.transform.flip(rotated_door, True, False),
                          (
                          WIDTH - rotated_door.get_width() - horizontal_door_offset + door_image.get_height() // 2 - wall_thickness // 2,
                          horizontal_door_y))

    # Draw up and down doors
    if room.door_up:
        room.surface.blit(pygame.transform.rotate(door_image, 0), (vertical_door_x, 0))
    if room.door_down:
        room.surface.blit(pygame.transform.rotate(pygame.transform.flip(door_image, False, True), 0), (vertical_door_x, HEIGHT - door_height))

    room.loaded = True
    return room
def unload_room_surface(room):
    room.surface = None
    room.rect = None
    room.collision_sprites.empty()
    room.loaded = False

def get_room_from_grid(rooms, grid_x, grid_y):
    for room in rooms:
        if room.grid_x == grid_x and room.grid_y == grid_y:
            return room
    return None
"""
grid, rooms = generate_grid()

print("Grid:")
print(grid)

print("\nRooms:")
for room in rooms:
    print(f"({room.grid_x}, {room.grid_y}) - Left:{room.door_left}, Right:{room.door_right}, Up:{room.door_up}, Down:{room.door_down}")
"""
grid, rooms = generate_grid()
find_and_set_boss_room(grid,rooms)
