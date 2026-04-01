import pygame
from constants import CAL_FONT, BLACK

class TaskInputBox:
        # this is used for typing task descriptions in the side panel

        def __init__(self, x, y, w, h, text=""):
            self.rect = pygame.Rect(x, y, w, h)  # rectangle of input box
            self.text = text  # text stored inside
            self.col = (230, 230, 230)  # box background colour
            self.txt = CAL_FONT.render(self.text, True, BLACK)  # rendered text surface
            self.active = False  # starts not active, we turn it on manually
            self.done = False  # tracks whether user finished input

        def handle(self, event):
            # this reacts to key presses when the box is active

            if event.type == pygame.KEYDOWN and self.active:  # only respond if active
                if event.key == pygame.K_RETURN:  # enter means finish input
                    self.done = True  # marks input as finished
                elif event.key == pygame.K_ESCAPE:  # escape also finishes / cancels
                    self.done = True  # also marks as finished
                elif event.key == pygame.K_BACKSPACE:  # deletes last char
                    self.text = self.text[:-1]  # removes last character
                else:
                    if len(self.text) < 60:  # stops text getting too long
                        self.text += event.unicode  # adds typed character

                self.txt = CAL_FONT.render(self.text, True, BLACK)  # re-render text

        def draw(self, surf):
            # this draws the input box and its text

            pygame.draw.rect(surf, self.col, self.rect)  # draws box background
            pygame.draw.rect(surf, BLACK, self.rect, 2)  # draws border
            surf.blit(self.txt, (self.rect.x + 5, self.rect.y + 5))  # draws text inside
