import pygame
import sqlite3
from datetime import datetime, timedelta  # imports datetime and timedelta for dates and times
from constants import *
from TimeInputBox import TimeInputBox
from TaskInputBox import TaskInputBox
from helper_functions import show_message
from database_utils import update_task_in_db, save_task_to_db, delete_task_from_db, delete_revision_for_task
from Login_ID import *

class TaskPanel:
        # this is the side panel that opens when you click a day

        def __init__(self, date_str, task_list, calendar_obj, screen):
            self.date_str = date_str  # current date being edited
            self.tasks = task_list  # list of tasks for this date
            self.calendar = calendar_obj  # this lets the panel refresh revision dots
            self.screen = screen
            # panel rectangle on the right
            self.rect = pygame.Rect(CAL_WIDTH - PANEL_W, 80, PANEL_W - 20, CAL_HEIGHT - 140)

            self.input_desc = None  # input box for description
            self.input_time = None  # input box for time
            self.edit_index = None  # which task we are editing (None means new)

            self.diff = "Easy"  # default difficulty

            # buttons at the bottom
            self.btn_add = pygame.Rect(self.rect.left + 15, self.rect.bottom - 60, 120, 40)
            self.btn_close = pygame.Rect(self.rect.right - 120, self.rect.bottom - 60, 100, 40)

            # save button now sits under difficulty buttons
            self.btn_save = pygame.Rect(self.rect.left + 15, self.rect.top + 260, 200, 40)

            self.btn_revision = pygame.Rect(self.rect.left + 15, self.rect.bottom - 120, self.rect.width- 30, 40)


            self.edit_buttons = []  # stores edit button rects
            self.delete_buttons = []  # stores delete button rects
            self.complete_buttons = []  # stores complete tick buttons

        
        
        def generate_revision_plan(self, user_id, task_id, original_date_str, desc, diff):
            # this creates spaced revision sessions using a fixed revision-method pattern

            base_date = datetime.strptime(original_date_str, "%Y-%m-%d").date()  # converts date string to date object

            # chooses revision spacing based on difficulty
            if diff == "Easy":
                offsets = [3, 7]
            elif diff == "Medium":
                offsets = [2, 5, 10]
            else:  # Hard
                offsets = [1, 3, 7, 14]

            conn = sqlite3.connect(DB_NAME)  # opens database
            c = conn.cursor()  # gets cursor

            for i, offset in enumerate(offsets):
                rev_date = base_date + timedelta(days=offset)  # calculates revision date
                rev_str = rev_date.strftime("%Y-%m-%d")  # converts date back to string

                # picks revision method using fixed sequence (cycles safely)
                method = REVISION_METHOD_SEQUENCE[i % len(REVISION_METHOD_SEQUENCE)]

                # inserts revision session into database
                c.execute(
                    "INSERT INTO revision_tasks (user_id, task_id, original_date, revision_date, description, difficulty, method) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (user_id, task_id, original_date_str, rev_str, desc, diff, method))

            conn.commit()  # saves changes
            conn.close()  # closes database


        def start_add(self):
            # this sets up new input boxes for adding a task

            # description box near top of panel
            self.input_desc = TaskInputBox(self.rect.left + 15, self.rect.top + 70, self.rect.width - 30, 40,"")
            self.input_desc.active = True  # start focused on description

            # time box using TimeInputBox (only digits + formats HH:MM)
            self.input_time = TimeInputBox(self.rect.left + 15, self.rect.top + 150, 120,40, "")
            self.input_time.active = False  # time not active yet

            self.edit_index = None  # means we are adding not editing

        def start_edit(self, idx):
            # this loads an existing task into the input boxes so we can edit it

            task = self.tasks[idx]  # gets the task we are editing

            self.input_desc = TaskInputBox(self.rect.left + 15, self.rect.top + 70, self.rect.width - 30, 40, task["desc"])
            self.input_desc.active = True  # focus stays on description first

            self.input_time = TimeInputBox(self.rect.left + 15, self.rect.top + 150, 120, 40, task["time"] if task["time"] else "")
            self.input_time.active = False  # time will activate when clicked

            self.diff = task["diff"]  # loads difficulty
            self.edit_index = idx  # stores which row we are editing

        def draw(self, surf):
            # this draws the whole panel

            pygame.draw.rect(surf, (45, 45, 45), self.rect, border_radius=10)  # panel bg
            pygame.draw.rect(surf, (200, 200, 200), self.rect, 2, border_radius=10)  # border

            title = CAL_FONT.render(f"Tasks for {self.date_str}", True, TEXT)  # header text
            surf.blit(title, (self.rect.centerx - title.get_width() // 2, self.rect.top + 10))  # draw header

            # labels
            surf.blit(SMALL_FONT.render("Description:", True, TEXT), (self.rect.left + 15, self.rect.top + 50))

            surf.blit(SMALL_FONT.render("Time (HH:MM):", True, TEXT), (self.rect.left + 15, self.rect.top + 130))

            # draw input boxes if they exist
            if self.input_desc:
                self.input_desc.draw(surf)
            if self.input_time:
                self.input_time.draw(surf)

            # difficulty buttons under time box
            easy_r = pygame.Rect(self.rect.left + 15, self.rect.top + 210, 60, 30)
            med_r = pygame.Rect(self.rect.left + 80, self.rect.top + 210, 80, 30)
            hard_r = pygame.Rect(self.rect.left + 165, self.rect.top + 210, 80, 30)

            pygame.draw.rect(surf, (70, 200, 70) if self.diff == "Easy" else (100, 100, 100), easy_r)
            pygame.draw.rect(surf, (200, 200, 70) if self.diff == "Medium" else (100, 100, 100), med_r)
            pygame.draw.rect(surf, (200, 70, 70) if self.diff == "Hard" else (100, 100, 100), hard_r)

            surf.blit(SMALL_FONT.render("Easy", True, BLACK), (easy_r.x + 8, easy_r.y + 5))
            surf.blit(SMALL_FONT.render("Med", True, BLACK), (med_r.x + 10, med_r.y + 5))
            surf.blit(SMALL_FONT.render("Hard", True, BLACK), (hard_r.x + 10, hard_r.y + 5))

            # draw save button below difficulty buttons
            pygame.draw.rect(surf, BLUE1, self.btn_save, border_radius=8)
            save_txt = SMALL_FONT.render("Save Task", True, TEXT)
            surf.blit(save_txt, (self.btn_save.centerx - save_txt.get_width() // 2, self.btn_save.centery - save_txt.get_height() // 2))

            # draw add button at bottom left
            pygame.draw.rect(surf, BLUE1, self.btn_add, border_radius=8)
            add_txt = SMALL_FONT.render("Add", True, TEXT)
            surf.blit(add_txt, (self.btn_add.centerx - add_txt.get_width() // 2, self.btn_add.centery - add_txt.get_height() // 2))

            # draw close button at bottom right
            pygame.draw.rect(surf, BLUE1, self.btn_close, border_radius=8)
            close_txt = SMALL_FONT.render("Close", True, TEXT)
            surf.blit(close_txt, (self.btn_close.centerx - close_txt.get_width() // 2, self.btn_close.centery - close_txt.get_height() // 2))

            # draw revision button near bottom
            pygame.draw.rect(surf, BLUE1, self.btn_revision, border_radius=8)
            surf.blit(SMALL_FONT.render("View Revision", True, TEXT),(self.btn_revision.centerx - 55, self.btn_revision.centery - 10))


            # list of tasks starts further down now so it doesn’t clash with inputs
            self.edit_buttons = []  # reset the edit button list
            self.delete_buttons = []  # reset the delete button list
            self.complete_buttons = []  # reset complete buttons

            y = self.rect.top + 320  # starting y for task list
            for i, t in enumerate(self.tasks):  # loops through each task for this date
                # builds text like "HH:MM  description (Diff)"
                line = f"{t['time'] or '--:--'}  {t['desc']} ({t['diff']})"
                if t["completed"]:
                    line = "[DONE] " + line  # marks done tasks in text

                surf.blit(SMALL_FONT.render(line, True, TEXT), (self.rect.left + 15, y))

                er = pygame.Rect(self.rect.right - 150, y, 35, 25)  # edit button rect
                dr = pygame.Rect(self.rect.right - 105, y, 35, 25)  # delete button rect
                cr = pygame.Rect(self.rect.right - 60, y, 35, 25)  # complete toggle button rect

                pygame.draw.rect(surf, (80, 180, 80), er)  # draws edit button
                pygame.draw.rect(surf, (200, 60, 60), dr)  # draws delete button
                pygame.draw.rect(surf, (180, 180, 180), cr)  # draws complete button

                surf.blit(SMALL_FONT.render("E", True, TEXT), (er.x + 10, er.y + 4))  # edit label
                surf.blit(SMALL_FONT.render("X", True, TEXT), (dr.x + 10, dr.y + 4))  # delete label
                surf.blit(SMALL_FONT.render("✓", True, TEXT), (cr.x + 8, cr.y + 3))  # tick label

                self.edit_buttons.append((er, i))  # stores edit button and index
                self.delete_buttons.append((dr, i))  # stores delete button and index
                self.complete_buttons.append((cr, i))  # stores complete button and index

                y += 35  # moves down for next task

        def handle(self, event):
            # this handles clicking / typing for the panel

            if event.type == pygame.MOUSEBUTTONDOWN:  # mouse click events

                if self.btn_revision.collidepoint(event.pos):
                        return "open_revision" # tells calendar to open revision panel
                
                # clicking inside description box
                if self.input_desc and self.input_desc.rect.collidepoint(event.pos):
                    self.input_desc.active = True  # activates description input
                    if self.input_time:
                        self.input_time.active = False  # deactivates time input

                # clicking inside time box
                elif self.input_time and self.input_time.rect.collidepoint(event.pos):
                    self.input_time.active = True  # activates time input
                    if self.input_desc:
                        self.input_desc.active = False  # deactivates description

                # difficulty buttons
                easy_r = pygame.Rect(self.rect.left + 15, self.rect.top + 210, 60, 30)
                med_r = pygame.Rect(self.rect.left + 80, self.rect.top + 210, 80, 30)
                hard_r = pygame.Rect(self.rect.left + 165, self.rect.top + 210, 80, 30)

                if easy_r.collidepoint(event.pos):
                    self.diff = "Easy"  # sets difficulty to easy
                elif med_r.collidepoint(event.pos):
                    self.diff = "Medium"  # sets difficulty to medium
                elif hard_r.collidepoint(event.pos):
                    self.diff = "Hard"  # sets difficulty to hard

                # close button
                if self.btn_close.collidepoint(event.pos):
                    return "close"  # tells calendar to close the panel

                # add button
                if self.btn_add.collidepoint(event.pos):
                    self.start_add()  # prepares the panel for a new task

                # save button
                    # this runs when the user clicks the save button to save or edit a task
                if self.btn_save.collidepoint(event.pos):


                    desc = self.input_desc.text.strip() if self.input_desc else ""   # gets the task description text
                    time_str = self.input_time.text.strip() if self.input_time else ""  # gets the time text
                    diff = self.diff  # gets the selected difficulty

                    # check that the description is not empty
                    if not desc:
                        show_message(self.screen, "Enter a task description")  # tells user what is missing
                        return  # stop saving

                    # check time is written in HH:MM format
                    if len(time_str) != 5 or ":" not in time_str:
                        show_message(self.screen,"Time must be HH:MM")  # warns user about format
                        return  # stop saving

                    hh, mm = time_str.split(":")  # splits hours and minutes

                    # check both parts are numbers
                    if not (hh.isdigit() and mm.isdigit()):
                        show_message(self.screen,"Time must be numbers only")  # warns user
                        return  # stop saving

                    hh = int(hh)  # converts hours to integer
                    mm = int(mm)  # converts minutes to integer

                    # check hours and minutes are within valid ranges
                    if hh < 0 or hh > 23 or mm < 0 or mm > 59:
                        show_message(self.screen,"Invalid time entered")  # tells user the time is not valid
                        return  # stop saving

                    
                    if self.edit_index is None:  # adding a new task
                        current_user_id = get_current_user_id()  # gets the logged in user id
                        new_task_id = save_task_to_db(current_user_id, self.date_str, desc, time_str, diff)  # inserts into db
                        self.tasks.append({  # add to in-memory list
                            "id": new_task_id,
                            "desc": desc,
                            "time": time_str,
                            "diff": diff,
                            "completed": False
                        })
                        current_user_id = get_current_user_id()  # gets the logged in user id
                        self.generate_revision_plan(current_user_id, new_task_id, self.date_str, desc, diff)  # creates revision sessions

                    else:  # editing existing task

                        # SAFETY CHECK: edit_index may be invalid after delete/complete
                        if self.edit_index is None or self.edit_index >= len(self.tasks):
                            self.edit_index = None
                            return
                        t = self.tasks[self.edit_index]  # gets the task being edited

                        old_diff = t["diff"]  # stores old difficulty so we can compare

                        t["desc"] = desc  # updates description in memory
                        t["time"] = time_str  # updates time in memory
                        t["diff"] = diff  # updates difficulty in memory
                        update_task_in_db(t["id"], desc, time_str, diff, t["completed"])  # updates database row

                        # this deletes and regenerates revision plan if difficulty changed
                        if diff != old_diff:
                            delete_revision_for_task(t["id"])  # deletes old revision sessions for this task
                            logged_in_user_id = get_current_user_id()  # gets the logged in user id
                            self.generate_revision_plan(logged_in_user_id, t["id"], self.date_str, desc, diff)  # makes new ones

                        # this refreshes revision dots instantly (no restart needed)
                    self.calendar.reload_revision()  # reloads revision tasks for this user

                        # after saving, clear the input boxes and edit index
                    self.input_desc = None
                    self.input_time = None
                    self.edit_index = None

                # edit / delete / complete buttons in the list
                for rect, idx in self.edit_buttons:
                    if rect.collidepoint(event.pos):  # if clicked an edit button
                        self.start_edit(idx)  # load that task into the input boxes

                for rect, idx in self.delete_buttons:
                    if rect.collidepoint(event.pos):  # if clicked a delete button
                        t = self.tasks[idx]  # gets the task
                        delete_revision_for_task(t["id"])  # deletes linked revision sessions
                        delete_task_from_db(t["id"])  # removes from database
                        del self.tasks[idx]  # removes from in-memory list
                        self.edit_index = None  # reset edit state
                        self.calendar.reload_revision()  # refreshes dots
                        return

                for rect, idx in self.complete_buttons:
                    if rect.collidepoint(event.pos):  # clicked the tick box
                        t = self.tasks[idx]  # gets the task
                        t["completed"] = not t["completed"]  # toggles the completed flag
                        update_task_in_db(t["id"], t["desc"], t["time"], t["diff"], t["completed"])  # save to db
                        self.edit_index = None  # reset edit state
                        return

            # keyboard input goes to whichever box is active
            if self.input_desc:
                self.input_desc.handle(event)  # send keys to description box
            if self.input_time:
                self.input_time.handle(event)  # send keys to time box

            return None  # nothing special to return
