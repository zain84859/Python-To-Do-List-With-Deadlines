from constants import *
import pygame

# this handles typing into boxes for username and password
class InputBox:
    
    def __init__(self, x, y, w, h, text="", is_password=False):
        self.rect = pygame.Rect(x, y, w, h)  # rectangle for the input box
        self.color = GREY  # default colour of the box border
        self.text = text  # current text inside the box
        self.is_password = is_password  # if true, hides characters
        self.txt_surface = MENU_DEFAULT_FONT.render(self.get_display_text(), True, BLACK)  # surface for the drawn text
        self.active = False  # if true, this box is focused and accepts input

    # this returns stars if it's a password, otherwise the text itself
    def get_display_text(self):
        
        if self.is_password:  # checks if we should hide characters
            return "*" * len(self.text)  # returns same length of stars
        return self.text  # returns real text for normal boxes
    
    # this reacts to mouse clicks and key presses for the box
    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:  # checks for mouse clicks
            self.active = self.rect.collidepoint(event.pos)  # sets active if click inside box
            self.color = BLUE if self.active else GREY  # changes colour if selected

        if event.type == pygame.KEYDOWN and self.active:  # if box is active and a key is pressed
            if event.key == pygame.K_RETURN:  # user pressed enter inside this input
                return self.text  # returns the text to caller (if they want to use it)
            elif event.key == pygame.K_BACKSPACE:  # backspace to delete
                self.text = self.text[:-1]  # removes last character
            else:
                if len(self.text) < 30:  # limit text length so it doesn't overflow
                    self.text += event.unicode  # adds the typed character

            self.txt_surface = MENU_DEFAULT_FONT.render(self.get_display_text(), True, BLACK)  # updates the displayed text
            
        # this draws the text and the box border
    def draw(self, surface):

        surface.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))  # draws text slightly inside the box
        pygame.draw.rect(surface, self.color, self.rect, 2)  # draws the box border

    # this just returns the current text
    def get_text(self):

        return self.text  # gives the collected text back

