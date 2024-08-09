import random

import pygame
import snakefile


class Game:
    def __init__(self, main_screen):
        self.font = pygame.font.Font('freesansbold.ttf', 35)

        self.screen = main_screen
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.grid_size = 20

        # Create a "timer_event" which will be triggered evey "time_delay" milliseconds. This will act as an event which will be processed in the event loop.
        self.time_delay = 140
        self.timer_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.timer_event, self.time_delay)

        self.area = {}

        # We have created the class, now we need to create objects. This creates instances (in this case 2) of the Snake class allowing us to make as many as we want without having to repeat the snake's logic.
        self.snakes = pygame.sprite.Group()

        self.players = [
            {"display": "Red", "colour": pygame.color.Color(200, 0, 0), "controls": [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]},
            {"display": "Green", "colour": pygame.color.Color(0, 200, 0), "controls": [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s]},
            {"display": "Blue", "colour": pygame.color.Color(0, 0, 200), "controls": [pygame.K_j, pygame.K_l, pygame.K_i, pygame.K_k]},
        ]
        for i in range(self.players.__len__()):
            snake_pos = (random.randint(0, (self.screen.get_width()//self.grid_size) - 1) * self.grid_size, random.randint(0, (self.screen.get_height()//self.grid_size) - 1) * self.grid_size)
            snakefile.Snake(self, snake_pos, self.players[i]["colour"], self.players[i]["controls"], self.snakes)

    def run(self):
        # This is the entire game loop. Look how much smaller and easier it is to read now that we are using objects!
        while True:
            # Event Loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "main_menu"
                for snake in self.snakes:
                    snake.handle_event(event)

            for snake in self.snakes:
                snake.update_display_rect()

            if len(self.snakes) < len(self.players):
                for player in self.players:
                    if player["colour"] not in [snake.colour for snake in self.snakes]:
                        snake_pos = (random.randint(0, (self.screen.get_width() // self.grid_size) - 1) * self.grid_size, random.randint(0, (self.screen.get_height() // self.grid_size) - 1) * self.grid_size)
                        snakefile.Snake(self, snake_pos, player["colour"], player["controls"], self.snakes)

            # Rendering
            for loc, colour in self.area.items():
                pygame.draw.rect(self.screen, colour, pygame.Rect(loc, (self.grid_size, self.grid_size)))
            for snake in self.snakes:
                snake.draw()

            # draw text
            for i, player in enumerate(self.players):
                score = sum(1 for colour in self.area.values() if colour == player["colour"])
                text = self.font.render(f"{player['display']}: {score}", True, "white")
                self.screen.blit(text, (0, i * 30))

            # Don't forget to update the screen after rendering
            pygame.display.update()
            self.screen.fill("gray")
            self.clock.tick(self.fps)
            pygame.display.set_caption("FPS: " + str(int(self.clock.get_fps())))
