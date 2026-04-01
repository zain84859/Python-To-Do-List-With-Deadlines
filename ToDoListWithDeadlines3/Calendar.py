import pygame
import calendar
from constants import CAL_WIDTH, CAL_HEIGHT, PANEL_W, BG, TEXT, BLUE1, YELLOW, CAL_FONT, SMALL_FONT, DAYS
from database_utils import load_tasks_from_db, load_revision_tasks_from_db
from datetime import datetime
from Button import Button
from TaskPanel import TaskPanel
from RevisionPanel import RevisionPanel
from Login_ID import get_current_user_id
from LogoutConfirmPanel import LogoutConfirmPanel
from priority_utils import calculate_task_priority


class Calendar:
        # this controls the whole calendar screen and handles drawing / clicks

    def __init__(self, screen):
        now = datetime.now()  # gets current date and time
        self.year = now.year  # stores current year
        self.month = now.month  # stores current month
        self.screen = screen
        logged_in_user_id = get_current_user_id()
        self.tasks = load_tasks_from_db(logged_in_user_id)  # loads all tasks for this user
        self.revision = load_revision_tasks_from_db(logged_in_user_id)  # loads revision tasks for this user

        self.list_view = False  # false means calendar view, true means list view
        self.buttons = []  # this will store the day cell rectangles
        self.panel = None  # this will hold TaskPanel or RevisionPanel when a day is opened

        # create buttons for changing months and toggling view
        self.btn_prev = Button((50, 20, 180, 40), "<< Previous Month", self.prev_month)
        self.btn_next = Button((CAL_WIDTH - 230, 20, 180, 40), "Next Month >>", self.next_month)
        # logout button under next month button
        self.btn_logout = Button((CAL_WIDTH - 230, 70, 180, 40),"Log Out",self.logout)# positioned under next month button
        self.btn_toggle = Button((CAL_WIDTH // 2 - 150, 20, 300, 40), "Switch to List View", self.toggle_view)

    def reload_revision(self):
        # this reloads revision tasks from the database so dots update straight away
        logged_in_user_id = get_current_user_id()
        self.revision = load_revision_tasks_from_db(logged_in_user_id)  # reloads revision tasks for this user

    def prev_month(self):
        # this goes to the previous month

        if self.month == 1:  # if currently January
            self.month = 12  # wrap around to December
            self.year -= 1  # go back a year
        else:
            self.month -= 1  # just go back one month
        self.panel = None  # close any open panel

    def next_month(self):
        # this goes to the next month

        if self.month == 12:  # if currently December
            self.month = 1  # wrap around to January
            self.year += 1  # go forward a year
        else:
            self.month += 1  # go forward one month
        self.panel = None  # close any open panel

    def toggle_view(self):
        # this switches between list view and calendar view

        self.list_view = not self.list_view  # flips between true and false
        self.panel = None  # closes any open panel

        if self.list_view:  # updates button text
            self.update_task_priorities()  # update priorities when switching to list view
            self.btn_toggle.text = "Switch to Calendar View"
            
        else:
            self.btn_toggle.text = "Switch to List View"
    
    def logout(self):
        # this asks the user if they are sure they want to log out

        self.panel = LogoutConfirmPanel(self)  # opens the logout confirmation panel

    def do_logout(self):
        # clear the logged-in user
        from Login_ID import set_current_user_id
        set_current_user_id(None)

        # reset calendar state (optional but safe)
        self.panel = None
        self.list_view = False

        # tell main loop to go back to main menu
        return "logout"

    def handle_event(self, event):
        # this deals with all events on the calendar screen

        # let the top buttons check if they got clicked or hovered
        self.btn_logout.handle(event)
        self.btn_toggle.handle(event)

        if not self.list_view:
            self.btn_prev.handle(event)
            self.btn_next.handle(event)

        # if a task panel or revision panel is open then only it should get events
        if self.panel:
            result = self.panel.handle(event)  # send event to the panel
            if result == "close":  # panel says close
                self.panel = None  # remove it

            elif result == "logout":  # panel says log out
                return self.do_logout()  # perform logout
            
            elif result == "open_tasks":
                date = self.panel.date_str
                if date not in self.tasks:
                    self.tasks[date] = []
                self.panel = TaskPanel(date, self.tasks[date], self, self.screen)

            elif result == "open_revision":
                date = self.panel.date_str
                self.panel = RevisionPanel(date, self.revision.get(date, []))

            return  # stop here so nothing else happens

        # list view is just for reading so nothing to click
        if self.list_view:
            return

        # mouse click inside calendar cells
        if event.type == pygame.MOUSEBUTTONDOWN:
            for rect, date_str in self.buttons:  # loop through every day square
                if rect.collidepoint(event.pos):  # check if the click was in this one

                    if date_str not in self.tasks:
                        self.tasks[date_str] = []

                    self.panel = TaskPanel(date_str, self.tasks[date_str], self, self.screen)
                    self.panel.start_add()
                    return # stop after opening one panel

    def draw_calendar_view(self, surf):
        # this draws the normal calendar grid view

        month_name = calendar.month_name[self.month]  # gets month name from number
        title = pygame.font.SysFont("arial", 34, bold=True).render(
            f"{month_name} {self.year}", True, TEXT)  # render month and year title
        surf.blit(title, (CAL_WIDTH // 2 - title.get_width() // 2, 70))  # draw title at top middle

        start_x = 50  # left margin for calendar grid
        start_y = 130  # top margin for calendar grid
        cell_w = (CAL_WIDTH - PANEL_W - 100) // 7  # width of each day cell
        cell_h = 80  # height of each day cell

        # draw day names row
        for i, d in enumerate(DAYS):  # loops through each day name
            label = CAL_FONT.render(d, True, TEXT)  # renders day name
            surf.blit(label, (start_x + i * cell_w + (cell_w - label.get_width()) // 2,
                                start_y))  # draws day name in column

        cal = calendar.Calendar(firstweekday=0)  # calendar starting from Monday
        days = list(cal.itermonthdays(self.year, self.month))  # list of day numbers and zeros
        self.buttons = []  # clear previous day cells

        row = 0  # row counter in calendar grid
        col = 0  # column counter in calendar grid

        for day in days:  # loop through each cell
            if day == 0:  # zero means this cell is from other month
                col += 1  # move to next column
                if col > 6:  # if beyond last column
                    col = 0  # reset column
                    row += 1  # move down to next row
                continue  # skip drawing

            x = start_x + col * cell_w + 5  # x position for the day cell
            y = start_y + 40 + row * cell_h + 5  # y position for the day cell
            rect = pygame.Rect(x, y, cell_w - 10, cell_h - 10)  # rectangle for the day

            date_str = f"{self.year:04d}-{self.month:02d}-{day:02d}"  # build date key as string

            today = datetime.now()  # gets today's date
            if today.year == self.year and today.month == self.month and today.day == day:
                pygame.draw.rect(surf, (50, 100, 200), rect, border_radius=10)  # highlight today
            else:
                pygame.draw.rect(surf, BLUE1, rect, border_radius=10)  # normal day cell

            # yellow dot when this day has normal tasks
            if date_str in self.tasks and self.tasks[date_str]:
                pygame.draw.circle(surf, YELLOW, (rect.right - 15, rect.bottom - 15), 7)

            # red dot when this day has revision sessions
            if date_str in self.revision and self.revision[date_str]:
                pygame.draw.circle(surf, (255, 80, 80), (rect.right - 30, rect.bottom - 15), 6)

            day_txt = CAL_FONT.render(str(day), True, TEXT)  # render the day number
            surf.blit(day_txt, (rect.x + 10, rect.y + 8))  # draw day number near top-left of cell

            self.buttons.append((rect, date_str))  # store rect and date for click detection

            col += 1  # go to next column
            if col > 6:  # if past Sunday
                col = 0  # reset to Monday column
                row += 1  # go to next row

    def draw_list_view(self, surf):
        # this draws a list of all tasks instead of the calendar grid

        title = CAL_FONT.render("All Tasks (List View)", True, TEXT)  # title for list view
        surf.blit(title, (CAL_WIDTH // 2 - title.get_width() // 2, 80))  # draw title

        y = 140  # starting y position for the list

        if not self.tasks:  # if there are no tasks at all
            msg = SMALL_FONT.render("No tasks yet.", True, (180, 180, 180))  # message to show
            surf.blit(msg, (CAL_WIDTH // 2 - msg.get_width() // 2, y))  # center it
            return  # nothing else to draw

        for d in sorted(self.tasks.keys()):
        # loops through each date in chronological order

            tasks_sorted = sorted(
                self.tasks[d],                      # all tasks for this date
                key=lambda t: t.get("priority", 0), # sort by priority score
                reverse=True)                        # highest priority first

            for t in tasks_sorted:
                # loop through tasks in priority order
                base = f"[{t['priority']}] {d}  {t['time'] or '--:--'}  {t['desc']} ({t['diff']})"
                # builds the display string for the task
                if t["completed"]:
                    base = "[DONE] " + base
                    # marks completed tasks clearly
                txt = SMALL_FONT.render(base, True, TEXT)
                # converts text into drawable surface
                surf.blit(txt, (60, y))
                # draws the task on screen
                y += 26
                # moves down for next task
                if y > CAL_HEIGHT - 40:
                    return
                    # stop drawing if we reach bottom of screen
                    
    def update_task_priorities(self):
        for date_str, tasks in self.tasks.items():
            for task in tasks:
                task["priority"] = calculate_task_priority(task, date_str)
                
    def draw(self, surf):
        # this draws the whole calendar screen including panel

        surf.fill(BG)  # fills background with dark colour

        if not self.list_view:
            self.btn_prev.draw(surf)  # draws previous month button
            self.btn_next.draw(surf)  # draws next month button

        self.btn_logout.draw(surf)  # draws logout button
        self.btn_toggle.draw(surf)  # draws toggle view button

        if self.list_view:  # if we are in list view
            self.draw_list_view(surf)  # draw list view
        else:
            self.draw_calendar_view(surf)  # draw the calendar with days

        if self.panel:  # if a task panel is open
            self.panel.draw(surf)  # draw the panel on top


