# TASK1

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# for numpy, run from terminal ---> code runner doesnt seem to run from environment for some reason
# import numpy as np
# a = np.array([1,2,3])
# print(a)

import math
import random
import time

first_time = time.time()

R = 0
G = 0
B = 0
WIDTH = 500
HEIGHT = 500

# box = [x, width, y, height]
# box here basically does the AABB collision functionality using bounding boxes
class Pivot:
    def __init__(self, x, y, radius = None, special = False, grow = False, box = None):
        self.x = x
        self.y = y
        self.radius = radius
        self.special = special
        self.grow = grow
        self.box = box

bullets = []

rocket = Pivot(0, -190)

back = Pivot(-220, 230)
pause = Pivot(0, 230)
cross = Pivot(220, 230)

bubbles = []

score = 0

missed_shot_counter = 0
missed_bubble_counter = 0

difficulty = 0

game_over_state = False

pause_state = False

time_diff = None

show_bounds = False

print(f'Score: {score}')


def draw_point(x, y):
    glBegin(GL_POINTS)
    glVertex2f(x,y) 
    glEnd()

# convert is for going back to zone 0
# it is in the form - swap, xneg, yneg
# e.g. if, when going from any zone to zone 0, we swapped positions, x became negative, y became negative
# then convert = [True, True, True]
def find_and_convert_zone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1

    if dx >= 0 and dy >= 0:  
        if abs(dx) >= abs(dy):  
            # Zone 0
            convert = [False, False, False]
        else:  
            # Zone 1
            x1, y1 = y1, x1
            x2, y2 = y2, x2
            convert = [True, False, False]

    elif dx < 0 and dy >= 0: 
        if abs(dx) >= abs(dy):  
            # Zone 3
            x1, y1 = -x1, y1
            x2, y2 = -x2, y2
            convert = [False, True, False]
        else:  
            # Zone 2
            x1, y1 = y1, -x1
            x2, y2 = y2, -x2
            convert = [True, True, False]

    elif dx < 0 and dy < 0:  
        if abs(dx) >= abs(dy):  
            # Zone 4
            x1, y1 = -x1, -y1
            x2, y2 = -x2, -y2
            convert = [False, True, True]
        else:  
            # Zone 5
            x1, y1 = -y1, -x1
            x2, y2 = -y2, -x2
            convert = [True, True, True]

    elif dx >= 0 and dy < 0:  
        if abs(dx) >= abs(dy):  
            # Zone 7
            x1, y1 = x1, -y1
            x2, y2 = x2, -y2
            convert = [False, False, True]
        else:  
            # Zone 6
            x1, y1 = -y1, x1
            x2, y2 = -y2, x2
            convert = [True, False, True]

    return x1, y1, x2, y2, convert
        

def draw_line(x1, y1, x2, y2):

    x1, y1, x2, y2, convert = find_and_convert_zone(x1, y1, x2, y2)

    dx = x2 - x1
    dy = y2 - y1
    d = 2*dy - dx
    delE = 2*dy
    delNE = 2 * (dy - dx)

    # x_temp, y_temp = x1, y1

    while x1 <= x2:
        # convert back to original zone
        x_draw, y_draw = x1, y1
        if convert[0]:  # Swap
            x_draw, y_draw = y_draw, x_draw
        if convert[1]:  # Negate X
            x_draw = -x_draw
        if convert[2]:  # Negate Y
            y_draw = -y_draw

        draw_point(x_draw, y_draw)  

        if d > 0:
            y1 += 1
            d += delNE
        else:
            d += delE
        x1 += 1
    
def draw_quad(x1, y1, x2, y2, x3, y3, x4, y4):
    draw_line(x1, y1, x2, y2)
    draw_line(x2, y2, x3, y3)
    draw_line(x3, y3, x4, y4)
    draw_line(x4, y4, x1, y1)

def draw_triangle(x1, y1, x2, y2, x3, y3):
    draw_line(x1, y1, x2, y2)
    draw_line(x2, y2, x3, y3)
    draw_line(x3, y3, x1, y1)


def draw_circle(x0, y0, radius):

    x_temp = 0
    y_temp = radius
    d = 1 - radius

    while x_temp <= y_temp:
        draw_point(x_temp + x0, y_temp + y0)  # Zone 1
        draw_point(y_temp + x0, x_temp + y0)  # Zone 0
        draw_point(-x_temp + x0, y_temp + y0) # Zone 2
        draw_point(-y_temp + x0, x_temp + y0) # Zone 3
        draw_point(-x_temp + x0, -y_temp + y0) # Zone 5
        draw_point(-y_temp + x0, -x_temp + y0) # Zone 4
        draw_point(x_temp + x0, -y_temp + y0)  # Zone 6
        draw_point(y_temp + x0, -x_temp + y0)  # Zone 7

        if d >= 0:
            d += 2 * (x_temp - y_temp) + 5
            y_temp -= 1
        else:
            d += 2 * x_temp + 3

        x_temp += 1



def iterate():
    global WIDTH, HEIGHT

    glViewport(0, 0, WIDTH, HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-250, 250, -250, 250, 0, 1)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

def animate():
    global bullets, bubbles, score, missed_shot_counter, missed_bubble_counter, difficulty, game_over_state, pause_state, time_diff, first_time

    bullets_to_remove = set()
    bubbles_to_remove = set()

    if pause_state == False:
        for bullet in bullets:
            bullet.y += 3.0
            if bullet.y>=250:
                missed_shot_counter += 1
                bullets_to_remove.add(bullet)

        for bubble in bubbles:
            if bubble.special == True:
                if bubble.grow==True:
                    bubble.radius +=0.06
                    if bubble.radius>30:
                        bubble.grow = False
                else:
                    bubble.radius -=0.06
                    if bubble.radius<20:
                        bubble.grow = True
            
            bubble.y -= 0.045 + difficulty
            if bubble.y<= -250:
                missed_bubble_counter += 1
                bubbles_to_remove.add(bubble)

            # bubble rocket collision
            # box = [x, width, y, height]
            if (rocket.box[0] < bubble.box[0] + bubble.box[1]  and
            rocket.box[0] + rocket.box[1] > bubble.box[0]  and
            rocket.box[2] < bubble.box[2] + bubble.box[3] and
            rocket.box[2] + rocket.box[3] > bubble.box[2]):
                print(f'Game Over: Bubble Rocket Collision')
                print(f'Final Score: {score}')
                game_over_state = True
                

    for bullet in bullets:
        for bubble in bubbles:
            distance = math.sqrt((bullet.x - bubble.x)**2 + (bullet.y - bubble.y)**2)
            if distance <= (bullet.radius + bubble.radius):
                bullets_to_remove.add(bullet)
                bubbles_to_remove.add(bubble)
                if bubble.special == True:
                    score += 5
                else:
                    score += 1
                print(f'Score: {score}')
                break  # Stop checking other bubbles for this bullet

    bullets = [bullet for bullet in bullets if bullet not in bullets_to_remove]
    bubbles = [bubble for bubble in bubbles if bubble not in bubbles_to_remove]

    if missed_shot_counter==3:
        if game_over_state == False:
            print(f'Game Over: 3 missed shots')
            print(f'Final Score: {score}')
            game_over_state = True

    if missed_bubble_counter==3:
        if game_over_state == False:
            print(f'Game Over: 3 missed bubbles')
            print(f'Final Score: {score}')
            game_over_state = True

    if game_over_state == True:
        bubbles = []
        bullets = []

    if pause_state == True:
        # for preserving the time difference between each bubble generated
        current_time = time.time()
        first_time = current_time - time_diff
        # print(time_diff)
        # print(current_time)
        # print(first_time)
    else:
        difficulty += 0.00002

    glutPostRedisplay()

def KeyboardListen(key, x, y):
    global rocket, bullets, game_over_state, pause_state, show_bounds

    # print(key)

    if game_over_state == False and pause_state == False:
        if key==b'a': 
            rocket.x -= 8
            if rocket.x < -250:
                rocket.x = -250
        if key==b'd':
            rocket.x += 8
            if rocket.x > 250:
                rocket.x = 250
        # if key==b'w':
        #     rocket.y += 8
        #     if rocket.y > 250:
        #         rocket.y = 250
        # if key==b's':
        #     rocket.y -= 8
        #     if rocket.y < -250:
        #         rocket.y = -250
        if key==b' ':
            bullet = Pivot(rocket.x, rocket.y+45, 5)
            bullets.append(bullet)

        if key==b'\r':
            if show_bounds == True:
                show_bounds = False
            else:
                show_bounds = True

    glutPostRedisplay()

def mouseListener(button, state, x, y):   

    global back, pause, cross, pause_state, time_diff, first_time, bullets, bubbles, score, missed_shot_counter, missed_bubble_counter, difficulty, game_over_state, rocket
        
    if button==GLUT_RIGHT_BUTTON:
        # if i dont have glut_down, this runs twice once when clicking the button once when letting go
        if state == GLUT_DOWN: 	
            pass

    if button==GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            # print(x-250, 250-y)
            # box = [x, width, y, height]
            if ((x-250)>=cross.box[0]) and ((x-250)<=(cross.box[0]+cross.box[1])) and ((250-y)>=cross.box[2]) and ((250-y)<=(cross.box[2]+cross.box[3])):
                # exit
                print(f'Final Score: {score}')
                glutLeaveMainLoop() 

            if ((x-250)>=pause.box[0]) and ((x-250)<=(pause.box[0]+pause.box[1])) and ((250-y)>=pause.box[2]) and ((250-y)<=(pause.box[2]+pause.box[3])):
                # pause
                if pause_state == False:
                    pause_state = True
                    time_diff = time.time() - first_time
                else:
                    pause_state = False 

            if ((x-250)>=back.box[0]) and ((x-250)<=(back.box[0]+back.box[1])) and ((250-y)>=back.box[2]) and ((250-y)<=(back.box[2]+back.box[3])):
                # restart
                print("Starting Over")

                first_time = time.time()
                bullets = []
                bubbles = []
                score = 0

                missed_shot_counter = 0
                missed_bubble_counter = 0

                difficulty = 0

                game_over_state = False

                pause_state = False

                time_diff = None

                rocket = Pivot(0, -190)

                print(f'Score: {score}')

        elif state == GLUT_UP:
            pass
                    
                    
    glutPostRedisplay()

def showScreen():
    global R, G, B, rocket, bullets, bubbles, first_time, back, pause, cross, pause_state, difficulty, game_over_state, show_bounds

    # background
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(R/255, G/255, B/255, 0);	
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    iterate()

    #call the draw methods here

    glPointSize(2) 

    # testing examples for each zone

    # x1, y1, x2, y2
    # draw_line(-200, -100, 50, 0) # 0
    # draw_line(-200, -100, -150, 50) # 1
    # draw_line(50, -50, -50, 200) # 2
    # draw_line(200, -100, -50, 50) # 3
    # draw_line(200, 100, -100, -50) # 4
    # draw_line(50, 50, -50, -200) # 5 
    # draw_line(-200, 50, -150, -100) # 6 
    # draw_line(-200, 100, 50, -50) # 7


    # BACK BUTTON
    glColor3f(12/255, 159/255, 181/255)

    draw_line(back.x-20, back.y, back.x+10, back.y)
    draw_line(back.x-20, back.y, back.x-10, back.y+5)
    draw_line(back.x-20, back.y, back.x-10, back.y-5)

    glColor3f(63/255, 152/255, 69/255)
    back.box = [back.x-20, 30, back.y-5, 10]
    if show_bounds == True:
        draw_quad(back.box[0], back.box[2], back.box[0], back.box[2]+back.box[3], back.box[0]+back.box[1], back.box[2]+back.box[3], back.box[0]+back.box[1], back.box[2])


    # CROSS BUTTON
    glColor3f(179/255, 1/255, 4/255)
    draw_line(cross.x-10, cross.y+10, cross.x+10, cross.y-10)
    draw_line(cross.x-10, cross.y-10, cross.x+10, cross.y+10)

    glColor3f(63/255, 152/255, 69/255)
    cross.box = [cross.x-10, 20, cross.y-10, 20]
    if show_bounds == True:
        draw_quad(cross.box[0], cross.box[2], cross.box[0], cross.box[2]+cross.box[3], cross.box[0]+cross.box[1], cross.box[2]+cross.box[3], cross.box[0]+cross.box[1], cross.box[2])


    # PAUSE BUTTON
    glColor3f(229/255, 156/255, 40/255)

    draw_triangle(pause.x-10, pause.y+10, pause.x+10, pause.y, pause.x-10, pause.y-10)

    glColor3f(63/255, 152/255, 69/255)
    pause.box = [pause.x-10, 20, pause.y-10, 20]
    if show_bounds == True:
        draw_quad(pause.box[0], pause.box[2], pause.box[0], pause.box[2]+pause.box[3], pause.box[0]+pause.box[1], pause.box[2]+pause.box[3], pause.box[0]+pause.box[1], pause.box[2])



    # ROCKET
    glColor3f(229/255, 156/255, 40/255)
    # x1, y1, x2, y2, x3, y3, x4, y4
    draw_quad(rocket.x-10, rocket.y-25, rocket.x-10, rocket.y+25, rocket.x+10, rocket.y+25, rocket.x+10, rocket.y-25)

    # x1, y1, x2, y2, x3, y3
    draw_triangle(rocket.x-10, rocket.y+25, rocket.x+0, rocket.y+45, rocket.x+10, rocket.y+25)

    draw_triangle(rocket.x-10, rocket.y-25, rocket.x-30, rocket.y-25, rocket.x-10, rocket.y-10)
    draw_triangle(rocket.x+10, rocket.y-25, rocket.x+30, rocket.y-25, rocket.x+10, rocket.y-10)

    draw_quad(rocket.x-12, rocket.y-30, rocket.x-8, rocket.y-30, rocket.x-8, rocket.y-50, rocket.x-12, rocket.y-50)
    draw_quad(rocket.x-2, rocket.y-30, rocket.x+2, rocket.y-30, rocket.x+2, rocket.y-50, rocket.x-2, rocket.y-50)
    draw_quad(rocket.x+12, rocket.y-30, rocket.x+8, rocket.y-30, rocket.x+8, rocket.y-50, rocket.x+12, rocket.y-50)

    glColor3f(63/255, 152/255, 69/255)
    rocket.box = [rocket.x-25, 50, rocket.y-50, 95]
    if show_bounds == True:
        draw_quad(rocket.box[0], rocket.box[2], rocket.box[0], rocket.box[2]+rocket.box[3], rocket.box[0]+rocket.box[1], rocket.box[2]+rocket.box[3], rocket.box[0]+rocket.box[1], rocket.box[2])


    # BULLETS
    glColor3f(229/255, 156/255, 40/255)

    for bullet in bullets:
        draw_circle(bullet.x, bullet.y, bullet.radius)


    # BUBBLES
    prob = random.random()
    current_time = time.time()
    if (current_time - first_time)>=(2-difficulty-0.00004): # difficulty
        if pause_state == False and game_over_state == False:
            if prob<0.1:
                # special bubble 
                bubble = Pivot(random.randint(-240, 240), 240, 20, True)
            else:
                bubble = Pivot(random.randint(-240, 240), 240, 20)
            bubbles.append(bubble)
            first_time = current_time


    if bubbles == []:
        pass
    else:
        for bubble in bubbles:
            if bubble.special == True:
                glColor3f(20/255, 242/255, 21/255)
                draw_circle(bubble.x, bubble.y, bubble.radius)

            else:
                glColor3f(229/255, 156/255, 40/255)
                draw_circle(bubble.x, bubble.y, bubble.radius)

            glColor3f(63/255, 152/255, 69/255)
            bubble.box = [bubble.x-bubble.radius, 2*bubble.radius, bubble.y-bubble.radius, 2*bubble.radius]
            if show_bounds == True:
                draw_quad(bubble.box[0], bubble.box[2], bubble.box[0], bubble.box[2]+bubble.box[3], bubble.box[0]+bubble.box[1], bubble.box[2]+bubble.box[3], bubble.box[0]+bubble.box[1], bubble.box[2])


    glPointSize(5) 
    if game_over_state == True:
        # Game over screen + score
        glColor3f(179/255, 1/255, 4/255)
        draw_line(-20, 20, 20, -20)
        draw_line(-20, -20, 20, 20)
    if pause_state == True:
        # Pause Screen
        glColor3f(229/255, 156/255, 40/255)
        draw_triangle(-20, -20, -20, +20, +20, 0)
        

    glutSwapBuffers()



glutInit()
glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(WIDTH, HEIGHT) #window size
glutInitWindowPosition(530, 130)
wind = glutCreateWindow(b"423 LAB 02") #window name
glutDisplayFunc(showScreen)

glutIdleFunc(animate)

glutKeyboardFunc(KeyboardListen)
glutMouseFunc(mouseListener)

glutMainLoop()


