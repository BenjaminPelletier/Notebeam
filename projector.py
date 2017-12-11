from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from threading import Thread, Event
import time
from screeninfo import get_monitors  # sudo pip install screeninfo


class Projector:
    def __init__(self):
        self.shown = False
        self.shutdown = False
        self.width = None
        self.height = None
        self.monitor = None

    def show(self, monitor_index=0):
        """
        Show the GLUT window, if it has not yet been shown.
        Close the window by calling stop().
        """
        if self.shown:
            return

        self.monitor = get_monitors()[monitor_index]

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

    def getMonitor(self):
        return self.monitor

    def _init(self):
        glutInit([])
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowPosition(self.monitor.x, self.monitor.y)
        self.window = glutCreateWindow('Projector')
        glutFullScreen()

        glClearColor(0., 0., 0., 1.)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        lightZeroPosition = [10., 4., 10., 1.]
        lightZeroColor = [0.8, 1.0, 0.8, 1.0]  # green tinged
        glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
        glEnable(GL_LIGHT0)

        glutIdleFunc(self._idle)
        glutDisplayFunc(self._display)
        glutKeyboardFunc(self._keypress)
        glutMouseFunc(self._mouse)

        glMatrixMode(GL_PROJECTION)
        gluPerspective(40., 1., 1., 40.)
        glMatrixMode(GL_MODELVIEW)
        gluLookAt(0, 0, 10,
                  0, 0, 0,
                  0, 1, 0)
        glPushMatrix()

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

    def _display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        color = [1.0, 0., 0., 1.]
        glMaterialfv(GL_FRONT, GL_DIFFUSE, color)
        glutSolidSphere(2, 20, 20)
        glPopMatrix()
        glutSwapBuffers()
        return

    def _keypress(self, key, x, y):
        pass

    def _mouse(self, button, state, x, y):
        pass
