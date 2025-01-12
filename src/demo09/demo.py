# Copyright (c) 2018-2024 William Emerison Six
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# all the import statements
# note how some modules are imported which must be used to call their functions
# other imports are for functions themselves, which can be called without calling from the module
from __future__ import annotations  # to appease Python 3.7-3.9
import sys
import math
from OpenGL.GL import (
    glMatrixMode,
    glLoadIdentity,
    GL_PROJECTION,
    GL_MODELVIEW,
    glClear,
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    glViewport,
    glClearColor,
    glColor3f,
    glBegin,
    GL_QUADS,
    glVertex2f,
    glEnd,
    glEnable,
    GL_SCISSOR_TEST,
    glScissor,
    glDisable,
)
import glfw

from dataclasses import dataclass

# if glfw doesn't initialize, we can't continue
if not glfw.init():
    sys.exit()

# opengl version specified for the graphics card/driver
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 1)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 4)

# create a windowed mode window and its OpenGL context
# if the window isn't successfully created, we can't continue
window = glfw.create_window(500, 500, "ModelViewProjection Demo 9", None, None)
if not window:
    glfw.terminate()
    sys.exit()

# make the window's context current, meaning that commands will affect this window
glfw.make_context_current(window)

# define closing the window as a function
def on_key(window, key, scancode, action, mods):
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, 1)

# set the function on_key to be called when any key is pressed, i think
glfw.set_key_callback(window, on_key)

# first clear color is a dark gray
glClearColor(0.0289, 0.071875, 0.0972, 1.0)


glMatrixMode(GL_PROJECTION)
glLoadIdentity()
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()

# this function 
def draw_in_square_viewport() -> None:
    glClearColor(0.2, 0.2, 0.2, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)

    width, height = glfw.get_framebuffer_size(window)
    min = width if width < height else height

    glEnable(GL_SCISSOR_TEST)
    glScissor(
        int((width - min) / 2.0),
        int((height - min) / 2.0),
        min,
        min,
    )

    glClearColor(0.0289, 0.071875, 0.0972, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)
    glDisable(GL_SCISSOR_TEST)

    glViewport(
        int(0.0 + (width - min) / 2.0),
        int(0.0 + (height - min) / 2.0),
        min,
        min,
    )


@dataclass
class Vertex:
    x: float
    y: float

    def translate(self: Vertex, tx: float, ty: float) -> Vertex:
        return Vertex(x=self.x + tx, y=self.y + ty)

    def scale(self: Vertex, scale_x: float, scale_y: float) -> Vertex:
        return Vertex(x=self.x * scale_x, y=self.y * scale_y)

    def rotate(self: Vertex, angle_in_radians: float) -> Vertex:
        return Vertex(
            x=self.x * math.cos(angle_in_radians) - self.y * math.sin(angle_in_radians),
            y=self.x * math.sin(angle_in_radians) + self.y * math.cos(angle_in_radians),
        )


@dataclass
class Paddle:
    vertices: list[Vertex]
    r: float
    g: float
    b: float
    position: Vertex
    rotation: float = 0.0


paddle1: Paddle = Paddle(
    vertices=[
        Vertex(x=-10.0, y=-30.0),
        Vertex(x=10.0, y=-30.0),
        Vertex(x=10.0, y=30.0),
        Vertex(x=-10.0, y=30.0),
    ],
    r=0.578123,
    g=0.0,
    b=1.0,
    position=Vertex(-90.0, 0.0),
)

paddle2: Paddle = Paddle(
    vertices=[
        Vertex(x=-10.0, y=-30.0),
        Vertex(x=10.0, y=-30.0),
        Vertex(x=10.0, y=30.0),
        Vertex(x=-10.0, y=30.0),
    ],
    r=1.0,
    g=0.0,
    b=0.0,
    position=Vertex(90.0, 0.0),
)


def handle_movement_of_paddles() -> None:
    global paddle1, paddle2

    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        paddle1.position.y -= 10.0
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        paddle1.position.y += 10.0
    if glfw.get_key(window, glfw.KEY_K) == glfw.PRESS:
        paddle2.position.y -= 10.0
    if glfw.get_key(window, glfw.KEY_I) == glfw.PRESS:
        paddle2.position.y += 10.0

    global paddle_1_rotation, paddle_2_rotation

    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        paddle1.rotation += 0.1
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        paddle1.rotation -= 0.1
    if glfw.get_key(window, glfw.KEY_J) == glfw.PRESS:
        paddle2.rotation += 0.1
    if glfw.get_key(window, glfw.KEY_L) == glfw.PRESS:
        paddle2.rotation -= 0.1


TARGET_FRAMERATE: int = 60

time_at_beginning_of_previous_frame: float = glfw.get_time()

# doc-region-begin 5748cc21902ad56527c65e167b4ef44bd62f392e
while not glfw.window_should_close(window):
    # doc-region-end 5748cc21902ad56527c65e167b4ef44bd62f392e
    while (
        glfw.get_time() < time_at_beginning_of_previous_frame + 1.0 / TARGET_FRAMERATE
    ):
        pass

    time_at_beginning_of_previous_frame = glfw.get_time()

    glfw.poll_events()

    width, height = glfw.get_framebuffer_size(window)
    glViewport(0, 0, width, height)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    draw_in_square_viewport()
    handle_movement_of_paddles()

    # draw paddle 1
    # fmt: off
    # doc-region-begin 4b0942ba3ffc80751d54b9a578c2c1da5cf438bd
    glColor3f(paddle1.r, paddle1.g, paddle1.b)

    glBegin(GL_QUADS)
    for model_space in paddle1.vertices:
        # doc-region-begin 3b78276e1dad210e845c0455857c6ccad704f7c7
        world_space: Vertex = model_space.rotate(paddle1.rotation) \
                                         .translate(tx=paddle1.position.x,
                                                    ty=paddle1.position.y)
        # doc-region-end 3b78276e1dad210e845c0455857c6ccad704f7c7
        # doc-region-begin bcc181dd2b611eaf23f0bffbb6dfbd5c9fc061d4
        ndc_space: Vertex = world_space.scale(scale_x=1.0 / 100.0,
                                              scale_y=1.0 / 100.0)
        # doc-region-end bcc181dd2b611eaf23f0bffbb6dfbd5c9fc061d4
        glVertex2f(ndc_space.x, ndc_space.y)
    glEnd()
    # doc-region-end 4b0942ba3ffc80751d54b9a578c2c1da5cf438bd
    # fmt: on

    # draw paddle 2
    # fmt: off
    # doc-region-begin c12bd0c9543cbc91aedc5ec4fc21a612d2129f61
    glColor3f(paddle2.r, paddle2.g, paddle2.b)

    glBegin(GL_QUADS)
    for model_space in paddle2.vertices:
        world_space: Vertex = model_space.rotate(paddle2.rotation) \
                                         .translate(tx=paddle2.position.x,
                                                    ty=paddle2.position.y)
        ndc_space: Vertex = world_space.scale(scale_x=1.0 / 100.0,
                                              scale_y=1.0 / 100.0)
        glVertex2f(ndc_space.x, ndc_space.y)
    glEnd()
    # doc-region-end c12bd0c9543cbc91aedc5ec4fc21a612d2129f61
    # fmt: on
    glfw.swap_buffers(window)

glfw.terminate()
