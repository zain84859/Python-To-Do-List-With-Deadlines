import pygame
from constants import CAL_FONT, SMALL_FONT, BLUE1, TEXT

class LogoutConfirmPanel:
    # this panel asks the user to confirm logging out

    def __init__(self, calendar_obj):
        self.calendar = calendar_obj  # lets us control the calendar state

        self.rect = pygame.Rect(300, 200, 400, 200)  # panel box

        self.btn_yes = pygame.Rect(self.rect.left + 50, self.rect.bottom - 70, 120, 40)
        self.btn_cancel = pygame.Rect(self.rect.right - 170, self.rect.bottom - 70, 120, 40)

    def draw(self, surf):
        # draws the confirmation panel

        pygame.draw.rect(surf, (45, 45, 45), self.rect, border_radius=10)
        pygame.draw.rect(surf, (200, 200, 200), self.rect, 2, border_radius=10)

        msg = CAL_FONT.render("Are you sure you want to log out?", True, TEXT)
        surf.blit(msg, (self.rect.centerx - msg.get_width() // 2, self.rect.top + 40))

        pygame.draw.rect(surf, BLUE1, self.btn_yes, border_radius=8)
        pygame.draw.rect(surf, BLUE1, self.btn_cancel, border_radius=8)

        surf.blit(SMALL_FONT.render("Yes", True, TEXT), (self.btn_yes.centerx - 15, self.btn_yes.centery - 10))
        surf.blit(SMALL_FONT.render("Cancel", True, TEXT), (self.btn_cancel.centerx - 25, self.btn_cancel.centery - 10))

    # handles clicks on the confirmation buttons
    def handle(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_yes.collidepoint(event.pos):
                return "logout"  # tells calendar to log out
            if self.btn_cancel.collidepoint(event.pos):
                return "close"  # closes the panel

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "close"  # escape cancels logout

        return None 