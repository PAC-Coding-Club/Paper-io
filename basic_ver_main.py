import pygame
from collections import deque

pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 10)

screen = pygame.display.set_mode((800, 800))
grid_size = 20

# Create a "timer_event" which will be triggered evey "time_delay" milliseconds. This will act as an event which will be processed in the event loop.
time_delay = 200
timer_event = pygame.USEREVENT + 1
pygame.time.set_timer(timer_event, time_delay)

area = {}


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


def points_within_polygon(polygon, grid_size=grid_size):
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
    def __init__(self, location, colour, controls, *groups: pygame.sprite.Group):
        super().__init__(*groups)

        self.head = pygame.Rect(location, (grid_size, grid_size))

        self.body = []
        self.controls = controls
        self.snakes = snakes

        self.sprite = pygame.surface.Surface((grid_size, grid_size))
        self.sprite.fill(colour)

        # We add the snakes to a list for easy looping.
        self.snakes.add(self)

        self.drawing = False
        self.isAlive = True
        self.direction = None

        self.colour = pygame.color.Color(colour)

        # Fill 9 squares around location
        area[location] = self.colour
        for i in range(3):
            for j in range(3):
                area[(location[0] - grid_size + j * grid_size, location[1] - grid_size + i * grid_size)] = self.colour

    def handle_event(self, event, snakes):
        if not self.isAlive:
            self.kill()
            return

        if event.type == pygame.KEYDOWN:
            if event.key == self.controls[0]:
                self.direction = 'left'
            elif event.key == self.controls[1]:
                self.direction = 'right'
            elif event.key == self.controls[2]:
                self.direction = 'up'
            elif event.key == self.controls[3]:
                self.direction = 'down'

        elif event.type == timer_event and self.direction:
            # Extend body, if not drawing this will be removed later
            self.body.insert(0, self.head.copy())

            # Move snake forward, clear direction values if it hits a wall
            if self.direction == 'left':
                self.head.x -= grid_size
                if self.head.centerx < 0:
                    self.direction = None
                    self.head.x += grid_size
            elif self.direction == 'right':
                self.head.x += grid_size
                if self.head.centerx > screen.get_width():
                    self.direction = None
                    self.head.x -= grid_size
            elif self.direction == 'up':
                self.head.y -= grid_size
                if self.head.centery < 0:
                    self.direction = None
                    self.head.y += grid_size
            elif self.direction == 'down':
                self.head.y += grid_size
                if self.head.centery > screen.get_height():
                    self.direction = None
                    self.head.x -= grid_size

            # Check collisions with other snakes
            other_snakes = [snake for snake in snakes if snake != self]
            for snake in other_snakes:
                if self.head.collidelistall(snake.body):
                    snake.isAlive = False

            # Calc drawing value and  filling area when drawing becomes False
            owned_locations = [key for key, value in area.items() if value == self.colour]
            if self.head.topleft in owned_locations:
                if self.drawing:
                    # Add the body to the area
                    for rect in self.body:
                        area[rect.topleft] = self.colour

                    start = self.head.topleft
                    end = self.body[-1].topleft
                    close_path = bfs_shortest_path(owned_locations, start, end, grid_size)  # shortest path between tail and head

                    # Get cords of body path and close hole across owned locations
                    self.body.reverse()
                    outline = close_path + [rect.topleft for rect in self.body]

                    # # Display order of outline
                    # for i, pos in enumerate(outline):
                    #     text_surface = font.render(str(i), False, (255, 0, 0))
                    #     screen.blit(text_surface, pos)
                    # pygame.display.update()
                    # input("Press Enter to continue")

                    # Add all points within path to area
                    new_points = points_within_polygon(outline)
                    for point in new_points:
                        area[point] = self.colour

                    # Clear the body and drawing value
                    self.body = []

                    self.drawing = False
            else:
                self.drawing = True

            # When not drawing the body is reduced to a max length of 1
            if not self.drawing and len(self.body) > 1:
                self.body.pop()

    def draw(self):
        for rect in self.body:
            pygame.draw.rect(screen, self.colour, rect)

        if self.drawing:
            pygame.draw.rect(screen, "purple", self.head)
        else:
            pygame.draw.rect(screen, "black", self.head)


# We have created the class, now we need to create objects. This creates instances (in this case 2) of the Snake class allowing us to make as many as we want without having to repeat the snake's logic.
snakes = pygame.sprite.Group()
Snake((15 * grid_size, 15 * grid_size), pygame.color.Color(200, 0, 0), (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN), snakes)
Snake((6 * grid_size, 6 * grid_size), pygame.color.Color(0, 200, 0), (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s), snakes)
Snake((25 * grid_size, 6 * grid_size), pygame.color.Color(0, 0, 200), (pygame.K_j, pygame.K_l, pygame.K_i, pygame.K_k), snakes)

# This is the entire game loop. Look how much smaller and easier it is to read now that we are using objects!
while True:
    # Event Loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        for snake in snakes:
            snake.handle_event(event, snakes)

    # Rendering
    for loc, colour in area.items():
        pygame.draw.rect(screen, colour, pygame.Rect(loc, (grid_size, grid_size)))
    for snake in snakes:
        snake.draw()

    # Don't forget to update the screen after rendering
    pygame.display.update()
    screen.fill("gray")
