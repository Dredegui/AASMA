COLORS = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'white': (255, 255, 255),
    'grey': (128, 128, 128),
    'orange': (255, 165, 0),
    'black': (0, 0, 0)
}
# Screen details
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
# Player details
PLAYER_SPEED = 5
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 40
PLAYER_TEAM_LEFT = 0
PLAYER_TEAM_RIGHT = 1
# Ball details
BALL_SPEED = 16
BALL_RADIUS = 8
BALL_DIAMETER = BALL_RADIUS * 2
# Wall/Goal details
BORDER_WIDTH = 10
GOAL_HEIGHT = 225
GOAL_TOP = SCREEN_HEIGHT/2 - GOAL_HEIGHT/2
GOAL_BOTTOM = SCREEN_HEIGHT/2 + GOAL_HEIGHT/2
# Game details
MAX_SCORE = 5
# Movement details
MOVE_UP = 0
MOVE_DOWN = 1
MOVE_LEFT = 2
MOVE_RIGHT = 3
DONT_MOVE = 4
# User mode details
NO_USER = 0
ONE_USER = 1
TWO_USER = 2