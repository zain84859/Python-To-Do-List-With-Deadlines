import pygame
import random
from constants import *
from constants import CAL_FONT, SMALL_FONT, TEXT, BLUE1

class RevisionPanel:
        # this panel is for looking at revision sessions (read only)

        def __init__(self, date_str, revision_list):
            self.date_str = date_str  # save date we are showing
            self.revision_list = revision_list  # list of revision tasks for this day

            # main panel shape on the right
            self.rect = pygame.Rect(CAL_WIDTH - PANEL_W, 80,
                                    PANEL_W - 20, CAL_HEIGHT - 140)

            # close button near the bottom
            self.btn_close = pygame.Rect(self.rect.right - 120, self.rect.bottom - 60, 100, 40)
            self.btn_tasks = pygame.Rect(self.rect.left + 15, self.rect.bottom - 120, self.rect.width -30, 40) # 


            # this shuffles the order so it looks random when you open the panel
            self.shuffled = self.revision_list[:]  # makes a copy of the list
            random.shuffle(self.shuffled)  # shuffles the copy

        # draw panel background
        def draw(self, surf):
            pygame.draw.rect(surf, (45, 45, 45), self.rect, border_radius=10)
            pygame.draw.rect(surf, (200, 200, 200), self.rect, 2, border_radius=10)
            pygame.draw.rect(surf, BLUE1, self.btn_tasks, border_radius=8)
            surf.blit(SMALL_FONT.render("View Tasks", True, TEXT),(self.btn_tasks.centerx - 40, self.btn_tasks.centery - 10))

            # panel title
            title = CAL_FONT.render(f"Revision for {self.date_str}", True, TEXT)
            surf.blit(title, (self.rect.centerx - title.get_width() // 2, self.rect.top + 10))

            # show each revision session
            y = self.rect.top + 70  # starting position for listing items

            for r in self.shuffled:  # loops through shuffled revision sessions
                # this shows task + method (practice questions / past paper / etc)
                method = r["method"] if r.get("method") else "Revision"  # fallback if method missing
                line = f"{r['desc']}  -  {method}  ({r['diff']})"  # builds the display text
                txt = SMALL_FONT.render(line, True, TEXT)  # renders text
                surf.blit(txt, (self.rect.left + 15, y))  # draws text
                y += 30  # move down for next one

            # draw the close button
            pygame.draw.rect(surf, BLUE1, self.btn_close, border_radius=8)
            surf.blit(SMALL_FONT.render("Close", True, TEXT), (self.btn_close.centerx - 22, self.btn_close.centery - 10))

        def handle(self, event):
            # only thing we can click is close
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_close.collidepoint(event.pos):
                    return "close"  # tells calendar to close the panel
                
                if self.btn_tasks.collidepoint(event.pos):
                    return "open_tasks" # tells calendar to open tasks panel

            return None  # nothing else to do