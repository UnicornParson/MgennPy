import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
import cv2
import numpy as np

def draw_cube():
    glBegin(GL_QUADS)

    # Передняя грань
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-0.5, -0.5,  0.5)
    glVertex3f( 0.5, -0.5,  0.5)
    glVertex3f( 0.5,  0.5,  0.5)
    glVertex3f(-0.5,  0.5,  0.5)

    # Задняя грань
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f( 0.5, -0.5, -0.5)
    glVertex3f( 0.5,  0.5, -0.5)
    glVertex3f(-0.5,  0.5, -0.5)

    # Верхняя грань
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(-0.5,  0.5, -0.5)
    glVertex3f(-0.5,  0.5,  0.5)
    glVertex3f( 0.5,  0.5,  0.5)
    glVertex3f( 0.5,  0.5, -0.5)

    # Нижняя грань
    glColor3f(1.0, 1.0, 0.0)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5,  0.5)
    glVertex3f( 0.5, -0.5,  0.5)
    glVertex3f( 0.5, -0.5, -0.5)

    # Правая грань
    glColor3f(1.0, 0.0, 1.0)
    glVertex3f( 0.5, -0.5, -0.5)
    glVertex3f( 0.5, -0.5,  0.5)
    glVertex3f( 0.5,  0.5,  0.5)
    glVertex3f( 0.5,  0.5, -0.5)

    # Левая грань
    glColor3f(0.0, 1.0, 1.0)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5,  0.5)
    glVertex3f(-0.5,  0.5,  0.5)
    glVertex3f(-0.5,  0.5, -0.5)

    glEnd()

def main():
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

    glTranslatef(0.0,0.0, -5)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 30.0, display)
    framenum = 0
    while framenum < 500:
        framenum += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

        glRotatef(1, 3, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        draw_cube()
        pygame.display.flip()
        #pygame.time.wait(10)

        #buffer = pygame.image.tostring(pygame.display.get_surface(), 'RGB', True)

        #surface_buffer = pygame.image.tostring(screen, 'RGB')
        surface_buffer = pygame.image.tostring(pygame.display.get_surface(), 'RGB', True)
        #surface_np = np.frombuffer(surface_buffer, dtype=np.uint8).reshape((display[1], display[0], 3))
        surface_np = np.frombuffer(surface_buffer, dtype=np.uint8).reshape((display[1], display[0], 3))
        print(surface_np.shape)
        cv2_image = cv2.cvtColor(surface_np, cv2.COLOR_RGB2BGR)

        #decoded = cv2.imdecode(np.fromstring(buffer, np.uint8), cv2.IMREAD_COLOR)
        #img = decoded.astype(np.uint8)[:, :, ::-1]
        #out.write(cv2_image)

        cv2.imwrite(f"./i/{framenum}.png", cv2_image)
    out.release()
    cv2.destroyAllWindows()
main()


