import pygame

pygame.init()  # starts pygame so we can use it

WIDTH, HEIGHT = 640, 480  # sets the window size for login and menu
CAL_WIDTH, CAL_HEIGHT = 1000, 700  # sets new window size for the calendar

WHITE = (255, 255, 255)  # rgb for white
GREY = (200, 200, 200)  # rgb for grey
BLACK = (0, 0, 0)  # rgb for black
BLUE = (0, 120, 215)  # rgb for blue (used for selected input box)
BLUE1 = (70, 130, 180)  # normal button colour
BLUE2 = (100, 160, 210)  # hover button colour
YELLOW = (255, 215, 0)  # dot colour for dates with tasks

CAL_FONT = pygame.font.SysFont("arial", 24)  # font for calendar numbers
SMALL_FONT = pygame.font.SysFont("arial", 18)  # small font for tasks in panel
MENU_DEFAULT_FONT = pygame.font.SysFont(None, 36)  # main font for menus and titles

BG = (30, 30, 30)  # background colour
TEXT = (255, 255, 255)  # main text colour

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]  # names of days

PANEL_W = 320  # width of the task side panel

DB_NAME = "todolist.db"  # name of the sqlite file we will use for storing tasks

REVISION_METHOD_SEQUENCE = [
    "Flashcards",
    "Practice questions",
    "Blurting",
    "Past paper",
    "Mind map",
    "Teach it to someone"
]

DIFF_WEIGHT = {
    "Easy": 1,
    "Medium": 2,
    "Hard": 3
}

URGENCY_DUE_TODAY = 80
URGENCY_OVERDUE = 100
URGENCY_DAY_DECAY = 10