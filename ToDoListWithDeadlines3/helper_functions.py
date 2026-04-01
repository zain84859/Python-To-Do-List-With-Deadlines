import pygame
from constants import WHITE, BLACK, MENU_DEFAULT_FONT, WIDTH, HEIGHT

# this shows a message in the middle of the screen
def show_message(screen, text):

    screen.fill(WHITE)  # clear screen
    msg = MENU_DEFAULT_FONT.render(text, True, BLACK)  # render message text
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - msg.get_height() // 2))  # draw centered
    pygame.display.flip()  # update display
    pygame.time.delay(900)  # pause shortly so message is readable
