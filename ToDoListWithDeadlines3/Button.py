from constants import *
import pygame

class Button:
        # this is a simple button used in the calendar screen

        def __init__(self, rect, text, callback=None):
            self.rect = pygame.Rect(rect)  # rectangle of button
            self.text = text  # button label
            self.callback = callback  # function to run when clicked
            self.hover = False  # tracks whether mouse is over the button

        def draw(self, surf):
            colour = BLUE2 if self.hover else BLUE1  # picks colour based on hover
            pygame.draw.rect(surf, colour, self.rect, border_radius=10)  # draws button
            txt = CAL_FONT.render(self.text, True, TEXT)  # renders button label
            surf.blit(txt, (self.rect.centerx - txt.get_width() // 2, self.rect.centery - txt.get_height() // 2))  # centers text

        def handle(self, event):
            if event.type == pygame.MOUSEMOTION:  # checks mouse movement
                self.hover = self.rect.collidepoint(event.pos)  # sets hover state
            if event.type == pygame.MOUSEBUTTONDOWN and self.hover:  # checks click on button
                if self.callback:  # only run if a callback exists
                    self.callback()  # runs assigned function