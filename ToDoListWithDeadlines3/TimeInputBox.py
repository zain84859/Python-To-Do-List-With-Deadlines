import pygame
from TaskInputBox import TaskInputBox
from constants import CAL_FONT, BLACK

class TimeInputBox(TaskInputBox):
    # this input box only allows valid 24 hour time in HH:MM format

        def handle(self, event):  
            # only react when active
            if event.type == pygame.KEYDOWN and self.active:
                if event.key == pygame.K_BACKSPACE:
                    # remove last character
                    self.text = self.text[:-1]
                elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    # finish editing
                    self.done = True
                else:
                    # only allow digits
                    if event.unicode.isdigit():
                         # work with raw digits only (no colon)
                        raw = self.text.replace(":", "")
                        # do not allow more than 4 digits (HHMM)
                        if len(raw) >= 4:
                            return

                        d = event.unicode  # digit being typed

                        # ---- HOURS ----
                        if len(raw) == 0:
                            # first hour digit: only 0–2 allowed
                            if d not in "012":
                                return

                        elif len(raw) == 1:
                            # second hour digit
                            if raw[0] == "2" and d not in "0123":
                                return

                        # ---- MINUTES ----
                        elif len(raw) == 2:
                            # first minute digit: only 0–5 allowed
                            if d not in "012345":
                                return

                        elif len(raw) == 3:
                            # second minute digit: 0–9 allowed
                            pass

                        # add digit if all checks passed
                        raw += d

                        # format as HH:MM
                        if len(raw) <= 2:
                            self.text = raw
                        else:
                            self.text = raw[:2] + ":" + raw[2:]

                # update displayed text
                self.txt = CAL_FONT.render(self.text, True, BLACK)
