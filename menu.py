import asyncio
import pygame


class Button:
    def __init__(self, screen, x, y, height, width, border, curve, buttonColour, textColour, hoverColour, id, text):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.Font('freesansbold.ttf', 80)

        self.screen = screen
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.border = border
        self.curve = curve
        self.buttonColour = buttonColour
        self.textColour = textColour
        self.hover_colour = hoverColour
        self.id = id
        self.text = text
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.highlighted = False

    def update(self, event):
        if not hasattr(event, "pos"):
            return

        if self.rect.collidepoint(event.pos):
            self.highlighted = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                return True
        elif not self.rect.collidepoint(event.pos):
            self.highlighted = False

    def draw(self):
        if self.highlighted:
            pygame.draw.rect(self.screen, self.hover_colour, self.rect, self.border, self.curve)
        else:
            pygame.draw.rect(self.screen, self.buttonColour, (self.x, self.y, self.width, self.height), self.border, self.curve)

        if self.text != "":
            text_surf = self.font.render(self.text, True, self.textColour)
            text_rect = text_surf.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            self.screen.blit(text_surf, text_rect)


class Menu:
    def __init__(self, main_screen, active_game, menu="main_menu"):
        self.screen = main_screen
        self.clock = pygame.time.Clock()
        self.fps = 60

        if menu == "main_menu":
            self.buttons = [
                Button(self.screen, 300, 250, 100, 200,  0, 7, "dark green", "white", "green", "play", "Play"),
                Button(self.screen, 225, 400, 100, 350, 0, 7, "dark blue", "white", "blue", "options_menu", "Options"),
            ]
            if active_game:
                self.buttons.append(Button(self.screen, 225, 100, 100, 350, 0, 7, "dark green", "white", "green", "resume", "Resume"))
        elif menu == "options_menu":
            self.buttons = [
                Button(self.screen, 75, 400, 100, 650, 0, 7, "dark blue", "white", "blue", "", "I do nothing lol"),
                Button(self.screen, 300, 550, 100, 200, 0, 7, "dark red", "white", "red", "main_menu", "Back"),
            ]
        else:
            self.buttons = []

    def run(self):
        if not self.buttons:
            print("Invalid menu")
            return

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                for button in self.buttons:
                    if button.update(event) and button.id:
                        return button.id

            for button in self.buttons:
                button.draw()

            pygame.display.update()
            self.screen.fill((60, 60, 60))
            self.clock.tick(self.fps)
            pygame.display.set_caption("FPS: " + str(int(self.clock.get_fps())))
