import pygame  # imports the pygame library
import sys  # imports system library for exiting the program
import sqlite3  # imports sqlite3 so we can use a database
from Calendar import Calendar  
import random  # imports random so we can randomise revision methods
from datetime import datetime, timedelta  
from plyer import notification  # used for showing Windows notifications
from constants import *
from database_utils import *  
from InputBox import InputBox  
from Button import Button  
from TaskInputBox import TaskInputBox
from TimeInputBox import TimeInputBox
from RevisionPanel import RevisionPanel
from helper_functions import show_message
from TaskPanel import TaskPanel
from Login_ID import *

screen = pygame.display.set_mode((WIDTH, HEIGHT))  # creates the window with that size
pygame.display.set_caption("Login System")  # sets the title at the top of the window

pygame.init()  # starts pygame so we can use it

init_database()  # calls the function to set up the database when the program starts

# this looks up a user by username and returns the row if found
def find_user(username):
    

    conn = sqlite3.connect(DB_NAME)  # opens the database
    c = conn.cursor()  # gets cursor

    c.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    row = c.fetchone()  # gets one result

    conn.close()  # closes the database

    return row  # returns the row or None if not found

def create_user(username, password):
    # this tries to create a new user and returns True if it worked

    conn = sqlite3.connect(DB_NAME)  # opens database
    c = conn.cursor()  # gets cursor

    try:
        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()  # saves new user
        conn.close()  # closes db
        return True  # tells caller it worked
    except sqlite3.IntegrityError:
        # this error happens if the username is already taken because of UNIQUE
        conn.close()  # still close db
        return False  # tells caller it failed
    
def set_menu_screen():
    global screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Login System")


def draw_button(surface, text, x, y, w, h):
    # this draws a simple button and returns its rectangle

    rect = pygame.Rect(x, y, w, h)  # rectangle for button
    pygame.draw.rect(surface, GREY, rect, border_radius=6)  # draw button background

    label = MENU_DEFAULT_FONT.render(text, True, BLACK)  # render button text
    surface.blit(label, (x + (w - label.get_width()) // 2, y + (h - label.get_height()) // 2))  # center text

    return rect  # returns rect for click detection

def draw_nav_buttons():
    # this draws the back and next buttons at the top and returns their rects

    back = pygame.Rect(20, 20, 100, 40)  # rect for the back button
    nxt = pygame.Rect(WIDTH - 120, 20, 100, 40)  # rect for the next button on the right

    pygame.draw.rect(screen, GREY, back, border_radius=6)  # draws the back button
    pygame.draw.rect(screen, GREY, nxt, border_radius=6)  # draws the next button

    btxt = MENU_DEFAULT_FONT.render("Back", True, BLACK)  # renders the back text
    ntxt = MENU_DEFAULT_FONT.render("Next", True, BLACK)  # renders the next text

    screen.blit(btxt, (back.centerx - btxt.get_width() // 2, back.centery - btxt.get_height() // 2))  # centers back text on button
    screen.blit(ntxt, (nxt.centerx - ntxt.get_width() // 2, nxt.centery - ntxt.get_height() // 2))  # centers next text on button

    return back, nxt  # returns both buttons so we can check for clicks

def register_screen():
    # this shows the register screen and handles making a new user

    username_box = InputBox(200, 150, 240, 40)  # input for username
    password_box = InputBox(200, 220, 240, 40, is_password=True)  # input for password, hidden

    while True:  # loop until user leaves this screen
        screen.fill(WHITE)  # clears screen every frame

        title = MENU_DEFAULT_FONT.render("Register", True, BLACK)  # title text
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))  # draws title at top

        u_label = MENU_DEFAULT_FONT.render("Username:", True, BLACK)  # label for username
        p_label = MENU_DEFAULT_FONT.render("Password:", True, BLACK)  # label for password
        screen.blit(u_label, (username_box.rect.x, username_box.rect.y - 30))  # draws username label above box
        screen.blit(p_label, (password_box.rect.x, password_box.rect.y - 30))  # draws password label above box

        back_btn, next_btn = draw_nav_buttons()  # draws back and next buttons

        username_box.draw(screen)  # draws username box
        password_box.draw(screen)  # draws password box

        pygame.display.flip()  # updates the screen with everything drawn

        for event in pygame.event.get():  # goes through all events
            if event.type == pygame.QUIT:  # if user closes window
                pygame.quit()  # shuts down pygame
                sys.exit()  # fully exits the program

            if event.type == pygame.KEYDOWN:  # handles keyboard shortcuts here
                if event.key == pygame.K_ESCAPE:  # esc to go back to main menu
                    return  # leaves the register screen
                if event.key == pygame.K_RETURN:  # enter key tries to register
                    uname = username_box.get_text().strip()  # gets username from box
                    pwd = password_box.get_text().strip()  # gets password from box
                    if not uname or not pwd:  # checks if either is empty
                        show_message(screen, "Please fill both fields")  # warns user
                    else:
                        ok = create_user(uname, pwd)  # tries to make user in database
                        if not ok:  # if username already exists
                            show_message(screen, "User already exists")  # shows taken message
                        else:
                            show_message(screen, "Registered!")  # tells user it worked
                            return  # goes back to main menu

            username_box.handle_event(event)  # passes event into username box
            password_box.handle_event(event)  # passes event into password box

            if event.type == pygame.MOUSEBUTTONDOWN:  # handles mouse clicks
                if back_btn.collidepoint(event.pos):  # clicked back button
                    return  # leaves this screen
                if next_btn.collidepoint(event.pos):  # clicked next button
                    uname = username_box.get_text().strip()  # gets username
                    pwd = password_box.get_text().strip()  # gets password
                    if not uname or not pwd:  # checks if both are filled
                        show_message(screen, "Please fill both fields")  # warns user
                    else:
                        ok = create_user(uname, pwd)  # tries to add user
                        if not ok:  # username taken
                            show_message(screen, "User already exists")  # warns about duplicate
                        else:
                            show_message(screen, "Registered!")  # confirms
                            return  # returns to main menu

def signin_screen():
    # this shows the sign in screen and checks login details

    username_box = InputBox(200, 150, 240, 40)  # username input box
    password_box = InputBox(200, 220, 240, 40, is_password=True)  # password input box

    while True:  # loop until user signs in or goes back
        screen.fill(WHITE)  # clears screen

        title = MENU_DEFAULT_FONT.render("Sign In", True, BLACK)  # title text
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))  # draws title in middle

        u_label = MENU_DEFAULT_FONT.render("Username:", True, BLACK)  # username label
        p_label = MENU_DEFAULT_FONT.render("Password:", True, BLACK)  # password label
        screen.blit(u_label, (username_box.rect.x, username_box.rect.y - 30))  # draws username label
        screen.blit(p_label, (password_box.rect.x, password_box.rect.y - 30))  # draws password label

        back_btn, next_btn = draw_nav_buttons()  # draws back and next buttons

        username_box.draw(screen)  # draws username box
        password_box.draw(screen)  # draws password box

        pygame.display.flip()  # shows updated screen 

        for event in pygame.event.get():  # processes events
            if event.type == pygame.QUIT:  # window closed
                pygame.quit()  # shuts pygame
                sys.exit()  # exits program

            if event.type == pygame.KEYDOWN:  # keyboard shortcut handling
                if event.key == pygame.K_ESCAPE:  # esc to go back
                    return  # leaves signin screen
                if event.key == pygame.K_RETURN:  # enter to sign in
                    uname = username_box.get_text().strip()  # gets username
                    pwd = password_box.get_text().strip()  # gets password

                    row = find_user(uname)  # look up user
                    if row and row[2] == pwd:  # checks if correct login
                        set_current_user_id(row[0])  # saves the user id
                        show_message(screen, "Login successful!")  # tells user it worked
                        logged_in_user_id = get_current_user_id()
                        result = run_calendar_app(logged_in_user_id)  # goes to main calendar app
                        set_menu_screen()
                        return  # comes back here after calendar closes
                    else:
                        show_message(screen, "Invalid details")  # wrong username or password

            username_box.handle_event(event)  # passes event into username box
            password_box.handle_event(event)  # passes event into password box

            if event.type == pygame.MOUSEBUTTONDOWN:  # handles mouse clicks
                if back_btn.collidepoint(event.pos):  # clicked back button
                    return  # goes back to main menu
                if next_btn.collidepoint(event.pos):  # clicked next button
                    uname = username_box.get_text().strip()  # gets username
                    pwd = password_box.get_text().strip()  # gets password

                    row = find_user(uname)  # look up user
                    if row and row[2] == pwd:  # checks login
                        set_current_user_id(row[0])  # store user id
                        show_message(screen, "Login successful!")  # success message
                        logged_in_user_id = get_current_user_id()
                        result = run_calendar_app(logged_in_user_id)  # open the calendar app
                        set_menu_screen()
                        return  # returns here after calendar closes
                    else:
                        show_message(screen, "Invalid details")  # error message

# this is the main menu where you choose register, sign in or quit
def main_menu():

    while True:  # loop so the menu stays on
        screen.fill(WHITE)  # clears the screen

        title = MENU_DEFAULT_FONT.render("Main Menu", True, BLACK)  # main menu text
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))  # draws the title

        reg_btn = draw_button(screen, "Register", 220, 150, 200, 50)  # register button
        log_btn = draw_button(screen, "Sign In", 220, 220, 200, 50)  # sign in button
        quit_btn = draw_button(screen, "Quit", 220, 290, 200, 50)  # quit button

        pygame.display.flip()  # updates the window

        for event in pygame.event.get():  # processes events
            if event.type == pygame.QUIT:  # window closed
                pygame.quit()  # shut pygame down
                sys.exit()  # exit whole program

            if event.type == pygame.MOUSEBUTTONDOWN:  # handles mouse button presses
                if reg_btn.collidepoint(event.pos):  # clicked on register
                    register_screen()  # go to register screen
                elif log_btn.collidepoint(event.pos):  # clicked on sign in
                    signin_screen()  # go to login screen
                elif quit_btn.collidepoint(event.pos):  # clicked on quit
                    pygame.quit()  # closes pygame
                    sys.exit()  # exits program

# calendar system section and database helpers for tasks

def run_calendar_app(user_id):
    # this runs the calendar and lets the user add, edit and delete tasks with time and difficulty

    global screen  # lets us change the screen size for the calendar layout
   
    screen = pygame.display.set_mode((CAL_WIDTH, CAL_HEIGHT))  # updates window size
    pygame.display.set_caption("Calendar and Tasks")  # changes title of window

    clock = pygame.time.Clock()  # clock object to limit fps

    cal = Calendar(screen)  # creates the calendar object
    running = True  # controls main loop
    notified_tasks = set()  # stores reminders already sent

    while running:  # calendar main loop
        for event in pygame.event.get():  # goes through pygame events
            if event.type == pygame.QUIT:  # if window closed
                running = False  # stop the loop
            result = cal.handle_event(event)  # send event into calendar
            if result == "logout":  # user chose to log out
                set_current_user_id(None)  # clears the current user id
                return "Main Menu"  # goes back to main menu


        check_task_notifications(user_id, notified_tasks)  # checks deadlines and shows notifications

        cal.draw(screen)  # tell calendar to draw everything
        pygame.display.flip()  # updates the screen
        clock.tick(30)  # limits the fps to 30

    # when calendar loop finishes, we shut pygame and exit whole program
    pygame.quit()
    sys.exit()

# program entry point

if __name__ == "__main__":  # this checks that the file was run directly
    main_menu()  # this starts your whole program at the main menu
