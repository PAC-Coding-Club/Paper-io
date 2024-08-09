import pygame
from collections import deque


def lighten_colour(colour, amount):
    colour = pygame.Color(colour)
    colour.r = min(255, colour.r + amount)
    colour.g = min(255, colour.g + amount)
    colour.b = min(255, colour.b + amount)
    return colour


def is_point_in_polygon(point, polygon):
    """Uses the ray-casting algorithm to determine if a point is in the polygon."""
    x_intersections = 0
    px, py = point
    n = len(polygon)

    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]  # Wrap around to the first point for the last segment

        # Check if point is on the same y-coordinate and between the y-coordinates of the segment
        if (y1 > py) != (y2 > py):
            # Compute the x coordinate of the intersection of the line with the y-coordinate of the point
            x_intersect = (x2 - x1) * (py - y1) / (y2 - y1) + x1

            # Check if the point is to the left of the test point
            if px < x_intersect:
                x_intersections += 1

    # Point is inside if the number of intersections is odd
    return x_intersections % 2 == 1


def points_within_polygon(polygon, grid_size):
    """Returns all integer points within the polygon."""
    min_x = min(polygon, key=lambda p: p[0])[0]
    max_x = max(polygon, key=lambda p: p[0])[0]
    min_y = min(polygon, key=lambda p: p[1])[1]
    max_y = max(polygon, key=lambda p: p[1])[1]
    points_inside = []

    for x in range(int(min_x) // grid_size, (int(max_x) + (grid_size * 3)) // grid_size):
        for y in range(int(min_y) // grid_size, (int(max_y) + grid_size) // grid_size):
            if is_point_in_polygon((x * grid_size, y * grid_size), polygon):
                points_inside.append((x * grid_size, y * grid_size))

    return points_inside


def bfs_shortest_path(grid, start, end, grid_size):
    directions = [(-grid_size, 0), (grid_size, 0), (0, -grid_size), (0, grid_size)]  # Up, Down, Left, Right

    grid_dict = {}
    for location in grid:
        grid_dict[location] = 0

    queue = deque([(start, [start])])
    visited = set([start])

    while queue:
        (r, c), path = queue.popleft()

        if (r, c) == end:
            return path

        for dr, dc in directions:
            nr, nc = r + dr, c + dc

            if (nr, nc) in grid_dict.keys() and grid_dict[(nr, nc)] == 0 and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append(((nr, nc), path + [(nr, nc)]))

    print("no path found")
    return []


class Snake(pygame.sprite.Sprite):
    def __init__(self, game, location, colour, controls, *groups: pygame.sprite.Group):
        super().__init__(*groups)
        self.game = game
        self.game.snakes.add(self)

        self.head = pygame.Rect(location, (game.grid_size, game.grid_size))
        self.display_rect = self.head.copy()
        self.display_position = pygame.Vector2(location)
        self.body = []
        self.controls = controls

        if len(self.controls) < 4:
            print("Not enough controls")

        self.drawing = False
        self.direction = None
        self.input_direction = None

        self.colour = pygame.color.Color(colour)

        # Fill 9 squares around location
        self.game.area[location] = self.colour
        for i in range(3):
            for j in range(3):
                self.game.area[(location[0] - self.game.grid_size + j * self.game.grid_size, location[1] - self.game.grid_size + i * self.game.grid_size)] = self.colour

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.controls[0]:
                if self.direction != 'right' or not self.drawing:
                    self.input_direction = 'left'
            elif event.key == self.controls[1]:
                if self.direction != 'left' or not self.drawing:
                    self.input_direction = 'right'
            elif event.key == self.controls[2]:
                if self.direction != 'down' or not self.drawing:
                    self.input_direction = 'up'
            elif event.key == self.controls[3]:
                if self.direction != 'up' or not self.drawing:
                    self.input_direction = 'down'

        elif event.type == self.game.timer_event and (self.direction or self.input_direction):
            if self.direction:
                # Extend body, if not drawing this will be removed later
                self.body.insert(0, self.head.copy())

                # When not drawing the body is reduced to a max length of 1
                if not self.drawing and len(self.body) > 1:
                    self.body.pop()

                # Move snake forward, clear direction values if it hits a wall
                if self.direction == 'left':
                    self.head.x -= self.game.grid_size
                    if self.head.centerx < 0:
                        self.direction = None
                        self.head.x += self.game.grid_size
                        self.body.pop(0)
                elif self.direction == 'right':
                    self.head.x += self.game.grid_size
                    if self.head.centerx > self.game.screen.get_width():
                        self.direction = None
                        self.head.x -= self.game.grid_size
                        self.body.pop(0)
                elif self.direction == 'up':
                    self.head.y -= self.game.grid_size
                    if self.head.centery < 0:
                        self.direction = None
                        self.head.y += self.game.grid_size
                        self.body.pop(0)
                elif self.direction == 'down':
                    self.head.y += self.game.grid_size
                    if self.head.centery > self.game.screen.get_height():
                        self.direction = None
                        self.head.y -= self.game.grid_size
                        self.body.pop(0)

            # Direction is stored as self.input direction until after the next move has occurred.
            # This stops the square moving in the preferred direction before the display_rect has reached the next square
            self.direction = self.input_direction
            self.display_position = pygame.Vector2(self.head.topleft)
            self.display_rect = self.head.copy()

            # Calc drawing value and filling area when drawing becomes False
            owned_locations = [key for key, value in self.game.area.items() if value == self.colour]
            if self.head.topleft in owned_locations:
                if self.drawing:
                    # Add the body to the area
                    for rect in self.body:
                        self.game.area[rect.topleft] = self.colour

                    start = self.head.topleft
                    end = self.body[-1].topleft
                    close_path = bfs_shortest_path(owned_locations, start, end, self.game.grid_size)  # shortest path between tail and head

                    # Get cords of body path and close hole across owned locations
                    self.body.reverse()
                    outline = close_path + [rect.topleft for rect in self.body]

                    # # Display order of outline
                    # for i, pos in enumerate(outline):
                    #     pygame.draw.rect(self.game.screen, "green", pygame.Rect(pos, (self.game.grid_size, self.game.grid_size)))
                    #     # text_surface = self.game.font.render(str(i), False, (255, 0, 0))
                    #     # self.game.screen.blit(text_surface, pos)
                    # pygame.display.update()
                    # input("Press Enter to continue")

                    # Add all points within path to area
                    new_points = points_within_polygon(outline, self.game.grid_size)
                    for point in new_points:
                        self.game.area[point] = self.colour

                    # Clear the body and drawing value
                    self.body = []

                    self.drawing = False
            else:
                self.drawing = True

            # Check death cases
            other_snakes = [snake for snake in self.game.snakes if snake != self]
            for snake in other_snakes:
                if self.head.collidelistall(snake.body) and snake.drawing:
                    self.game.area = {location: colour for location, colour in self.game.area.items() if colour != snake.colour}
                    snake.kill()
                    del snake
            if self.head.collidelistall(self.body):
                self.game.area = {location: colour for location, colour in self.game.area.items() if colour != self.colour}
                self.kill()
                del self

    def update_display_rect(self):
        move_amount = (self.game.grid_size / self.game.time_delay * 1000) * (1/self.game.fps)

        if self.direction == 'left':
            self.display_position.x -= move_amount
        elif self.direction == 'right':
            self.display_position.x += move_amount
        elif self.direction == 'up':
            self.display_position.y -= move_amount
        elif self.direction == 'down':
            self.display_position.y += move_amount

        self.display_rect.topleft = self.display_position

        # make sure display_rect cannot go off-screen to fix any visual artifacts
        if self.display_rect.left < 0:
            self.display_rect.left = 0
        if self.display_rect.top < 0:
            self.display_rect.top = 0
        if self.display_rect.right > self.game.screen.get_width():
            self.display_rect.right = self.game.screen.get_width()
        if self.display_rect.bottom > self.game.screen.get_height():
            self.display_rect.bottom = self.game.screen.get_height()

    def draw(self):
        for i, rect in enumerate(self.body):
            pygame.draw.rect(self.game.screen, lighten_colour(self.colour, 35), rect)
            if i == len(self.body) - 1:
                pygame.draw.rect(self.game.screen, self.colour, rect)

        if self.drawing:
            pygame.draw.rect(self.game.screen, lighten_colour(self.colour, 35), self.head)
            pygame.draw.rect(self.game.screen, "purple", self.display_rect)
        else:
            pygame.draw.rect(self.game.screen, self.colour, self.head)
            pygame.draw.rect(self.game.screen, "black", self.display_rect)
