from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from threading import Thread, Event
import time
from screeninfo import get_monitors  # sudo pip install screeninfo
import numpy, math


class Projector:
    def __init__(self):
        self.shown = False
        self.shutdown = False
        self.width = None
        self.height = None
        self.monitor = None
        self.display_routine = None
        self.displayed = Event()
        self.displayed.set()

    def show(self, monitor_index=0):
        """
        Show the GLUT window, if it has not yet been shown.
        Close the window by calling stop().
        """
        if self.shown:
            return

        self.monitor = get_monitors()[monitor_index]

        self.p2_xn = int(math.ceil(math.log(self.monitor.width, 2)))
        self.p2_x0 = int(math.floor((self.p2_xn - self.monitor.width) / 2))
        self.p2_yn = int(math.ceil(math.log(self.monitor.height, 2)))
        self.p2_y0 = int(math.floor((self.p2_yn - self.monitor.height) / 2))

        self.shutdown_received = Event()
        self.shown = True
        t = Thread(target=self._init)
        t.start()

    def stop(self):
        """
        Stop displaying the GLUT window if it is currently shown.
        If the GLUT window is closed, the entire process will be killed.  This is a quirk of glutLeaveMainLoop(); wrap
        this class in a ProcessProxy to avoid killing the instantiating process.
        """
        if not self.shown:
            return
        #print("Projector.stop")
        self.shutdown = True
        if self.shown:
            #print("Projector.stop waiting for shutdown_received")
            self.shutdown_received.wait()
            self.shown = False
        #print("Projector.stop finished")

    def get_monitor(self):
        return self.monitor

    def get_gray_bits_width(self):
        return self.p2_xn

    def get_gray_bits_height(self):
        return self.p2_yn

    def show_gray_cols(self, bit):
        if not self.shown:
            raise Exception("Cannot show_gray_cols on a Projector that is not yet shown")

        block = gray_block(self.p2_xn)

        def display_cols():
            glBegin(GL_QUADS)
            glColor3f(1, 1, 1)
            for i in range(self.monitor.width):
                if block[i + self.p2_x0, bit] > 0:
                    glVertex2f(i, 0)
                    glVertex2f(i, self.monitor.height)
                    glVertex2f(i + 1, self.monitor.height)
                    glVertex2f(i + 1, 0)
            glEnd()

        self._exec_display_routine(display_cols)

    def show_gray_rows(self, bit):
        if not self.shown:
            raise Exception("Cannot show_gray_rows on a Projector that is not yet shown")

        block = gray_block(self.p2_yn)

        def display_rows():
            glBegin(GL_QUADS)
            glColor3f(1, 1, 1)
            for i in range(self.monitor.height):
                if block[i + self.p2_x0, bit] > 0:
                    glVertex2f(0, i)
                    glVertex2f(self.monitor.width, i)
                    glVertex2f(self.monitor.width, i + 1)
                    glVertex2f(0, i + 1)
            glEnd()

        self._exec_display_routine(display_rows)

    def _exec_display_routine(self, routine):
        self.display_routine = routine
        self.displayed.clear()
        self.displayed.wait()

    def _init(self):
        glutInit([])
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowPosition(self.monitor.x, self.monitor.y)
        self.window = glutCreateWindow('Projector')
        glutFullScreen()

        glOrtho(0, self.monitor.width, self.monitor.height, 0, -1, 1)

        glClearColor(0, 0, 0, 1)

        glutIdleFunc(self._idle)
        glutDisplayFunc(self._display)
        glutKeyboardFunc(self._keypress)
        glutMouseFunc(self._mouse)

        glutMainLoop()

    def _idle(self):
        time.sleep(0.01)
        if self.shutdown:
            #print("Projector._idle: self.shutdown=True")
            self.shutdown_received.set()
            #print("Projector._idle: glutDestroyWindow")
            glutDestroyWindow(self.window)
            #print("Projector._idle: glutLeaveMainLoop")
            glutLeaveMainLoop()
            #print("Projector._idle: all done")
        if not self.displayed.isSet():
            glutPostRedisplay()

    def _display(self):
        #glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClear(GL_COLOR_BUFFER_BIT)

        if self.display_routine is not None:
            self.display_routine()

        glutSwapBuffers()

        self.displayed.set()

    def _keypress(self, key, x, y):
        pass

    def _mouse(self, button, state, x, y):
        pass


def gray_block(n_bits, dtype=int):
    """
    Returns a 2^n_bits x n_bits numpy array where the ith row contains the ith Gray code in the sequence
    """
    block = numpy.array([[0, 0], [0, 1], [1, 1], [1, 0]], dtype=dtype)
    for i in range(2, n_bits):
        block1 = numpy.zeros((block.shape[0], block.shape[1]+1), dtype=dtype)
        block1[:,1:] = block
        block2 = numpy.ones(block1.shape, dtype=dtype)
        block2[:,1:] = numpy.flipud(block)
        block = numpy.concatenate((block1, block2), axis=0)
    return block
