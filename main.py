import pygame
import game
import menu

pygame.init()
pygame.font.init()

window_size = (800, 800)
main_screen = pygame.display.set_mode(window_size)


def main_loop():
    active_game = None
    selected = menu.Menu(main_screen, active_game, menu="main_menu").run()
    while True:
        match selected:
            case "play":
                active_game = game.Game(main_screen)
                selected = active_game.run()
            case "resume":
                selected = active_game.run()
            case "quit":
                pygame.quit()
                quit()

            # if the button does not return an action case
            # send button's id to the menu selector
            case _:
                selected = menu.Menu(main_screen, active_game, menu=selected).run()

                # Handle invalid menu case
                if selected is None:
                    selected = menu.Menu(main_screen, active_game, menu="main_menu").run()


main_loop()

# Install pyinstaller command:
# pip install pyinstaller

# Create .exe file with the following command:
# pyinstaller main.py --onefile --windowed
