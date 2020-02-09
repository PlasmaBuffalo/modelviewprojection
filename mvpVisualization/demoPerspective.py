#Copyright (c) 2018-2020 William Emerison Six
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


import sys
import os
import numpy as np
import math
from OpenGL.GL import *
import OpenGL.GL.shaders as shaders
import glfw
import pyMatrixStack as ms
import atexit


# NEW - for shader location
pwd = os.path.dirname(os.path.abspath(__file__))

# NEW - for shaders
glfloat_size = 4
floatsPerVertex = 3
floatsPerColor = 3

if not glfw.init():
    sys.exit()

glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
# for osx
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

window = glfw.create_window(800,
                            800,
                            "ModelViewProjection Demo of Coordinates",
                            None,
                            None)
if not window:
    glfw.terminate()
    sys.exit()

# Make the window's context current
glfw.make_context_current(window)

# Install a key handler

def on_key(window, key, scancode, action, mods):
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, 1)


glfw.set_key_callback(window, on_key)

glClearColor(0.0,
             0.0,
             0.0,
             1.0)

# NEW - TODO - talk about opengl matricies and z pos/neg
glClearDepth(-1.0)
glDepthFunc(GL_GREATER)
glEnable(GL_DEPTH_TEST)


def on_exit():
    # delete the objects
    paddle1.__del__()
    paddle2.__del__()
    square.__del__()

    # normally in Python, you should call "del paddle1",
    # but that would not guarantee that the object would
    # actually be garbage collected at that moment, and
    # the OpenGL context could be destroyed before the garbage
    # collection happens, therefore, force the destruction
    # of the VAO and VBO by immediately calling __del__
    #
    # This is not normal Python practice to call
    # this type of method directly, but oh well.
atexit.register(on_exit)


class Paddle:
    def __init__(self, r, g, b, initial_position, rotation=0.0, input_offset_x=0.0, input_offset_y=0.0):
        self.r = r
        self.g = g
        self.b = b
        self.rotation = rotation
        self.input_offset_x = input_offset_x
        self.input_offset_y = input_offset_y
        self.initial_position = initial_position


    def vertices(self):
        return np.array([-10.0, -30.0,  0.0,
                         10.0,  -30.0,  0.0,
                         10.0,   30.0,  0.0,
                         10.0,   30.0,  0.0,
                         -10.0,  30.0,  0.0,
                         -10.0, -30.0,  0.0],
                        dtype=np.float32)

    def prepare_to_render(self):
        # GL_QUADS aren't available anymore, only triangles
        # need 6 vertices instead of 4
        vertices = self.vertices()
        self.numberOfVertices = np.size(vertices) // floatsPerVertex
        color = np.array([self.r, self.g, self.b,
                          self.r, self.g, self.b,
                          self.r, self.g, self.b,
                          self.r, self.g, self.b,
                          self.r, self.g, self.b,
                          self.r, self.g, self.b],
                         dtype=np.float32)
        self.numberOfColors = np.size(color) // floatsPerColor

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # initialize shaders

        with open(os.path.join(pwd, 'triangle.vert'), 'r') as f:
            vs = shaders.compileShader(f.read(), GL_VERTEX_SHADER)

        with open(os.path.join(pwd, 'triangle.frag'), 'r') as f:
            fs = shaders.compileShader(f.read(), GL_FRAGMENT_SHADER)

        self.shader = shaders.compileProgram(vs, fs)

        self.mvMatrixLoc = glGetUniformLocation(self.shader, "mvMatrix")


        # send the modelspace data to the GPU
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        position = glGetAttribLocation(self.shader, 'position')
        glEnableVertexAttribArray(position)

        glVertexAttribPointer(position,
                              floatsPerVertex,
                              GL_FLOAT,
                              False,
                              0,
                              ctypes.c_void_p(0))

        glBufferData(GL_ARRAY_BUFFER,
                     glfloat_size * np.size(vertices),
                     vertices,
                     GL_STATIC_DRAW)


        # send the modelspace data to the GPU
        vboColor = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vboColor)

        colorAttribLoc = glGetAttribLocation(self.shader, 'color_in')
        glEnableVertexAttribArray(colorAttribLoc)
        glVertexAttribPointer(colorAttribLoc,
                              floatsPerColor,
                              GL_FLOAT,
                              False,
                              0,
                              ctypes.c_void_p(0))

        glBufferData(GL_ARRAY_BUFFER,
                     glfloat_size * np.size(color),
                     color,
                     GL_STATIC_DRAW)


        # reset VAO/VBO to default
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    # destructor
    def __del__(self):
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])
        glDeleteProgram(self.shader)

    def render(self):
        glUseProgram(self.shader)
        glBindVertexArray(self.vao)

        # pass projection parameters to the shader
        fov_loc = glGetUniformLocation(self.shader, "fov");
        glUniform1f(fov_loc, 45.0);
        aspect_loc = glGetUniformLocation(self.shader, "aspectRatio");
        glUniform1f(aspect_loc, width/height);
        nearZ_loc = glGetUniformLocation(self.shader, "nearZ");
        glUniform1f(nearZ_loc, -0.1);
        farZ_loc = glGetUniformLocation(self.shader, "farZ");
        glUniform1f(farZ_loc, -10000.0);

        # ascontiguousarray puts the array in column major order
        glUniformMatrix4fv(self.mvMatrixLoc,
                           1,
                           GL_TRUE,
                           np.ascontiguousarray(
                               ms.getCurrentMatrix(
                                   ms.MatrixStack.modelview),
                               dtype=np.float32))
        glDrawArrays(GL_TRIANGLES,
                     0,
                     self.numberOfVertices)
        glBindVertexArray(0)


paddle1 = Paddle(r=0.578123,
                 g=0.0,
                 b=1.0,
                 initial_position=np.array([-90.0, 0.0, 0.0]),
                 input_offset_x = 0.0,
                 input_offset_y = 10.0)
paddle1.rotation = math.radians(45.0)

paddle1.prepare_to_render()
paddle2 = Paddle(r=1.0,
                 g=0.0,
                 b=0.0,
                 initial_position=np.array([90.0, 0.0, 0.0]),
                 input_offset_x = 0.0,
                 input_offset_y = 5.0)
paddle2.rotation = math.radians(-20.0)


paddle2.prepare_to_render()


class Square (Paddle):
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
        self.rotation = 0.0
        self.rotation_around_paddle1 = 0.0


    def vertices(self):
        return np.array([[-5.0, -5.0,  0.0],
                         [5.0, -5.0,  0.0],
                         [5.0,  5.0,  0.0],
                         [5.0,  5.0,  0.0],
                         [-5.0, 5.0,  0.0],
                         [-5.0, -5.0,  0.0]],
                        dtype=np.float32)

square = Square(r=0.0,
                g=0.0,
                b=1.0)

square.prepare_to_render()





class Ground:
    def __init__(self):
        pass


    def vertices(self):

        #glColor3f(0.1,0.1,0.1)
        glBegin(GL_LINES)
        verts = []
        for x in range(-200,201,20):
            for z in range(-200,201,20):
                verts.append(float(-x))
                verts.append(float(-50.0))
                verts.append(float(z))
                verts.append(float(x))
                verts.append(float(-50.0))
                verts.append(float(z))
                verts.append(float(x))
                verts.append(float(-50.0))
                verts.append(float(-z))
                verts.append(float(x))
                verts.append(float(-50.0))
                verts.append(float(z))

        return np.array(verts,
                        dtype=np.float32)

    def prepare_to_render(self):
        # GL_QUADS aren't available anymore, only triangles
        # need 6 vertices instead of 4
        vertices = self.vertices()
        self.numberOfVertices = np.size(vertices) // floatsPerVertex

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # initialize shaders

        with open(os.path.join(pwd, 'ground.vert'), 'r') as f:
            vs = shaders.compileShader(f.read(), GL_VERTEX_SHADER)

        with open(os.path.join(pwd, 'ground.frag'), 'r') as f:
            fs = shaders.compileShader(f.read(), GL_FRAGMENT_SHADER)

        self.shader = shaders.compileProgram(vs, fs)

        self.mvMatrixLoc = glGetUniformLocation(self.shader, "mvMatrix")


        # send the modelspace data to the GPU
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        position = glGetAttribLocation(self.shader, 'position')
        glEnableVertexAttribArray(position)

        glVertexAttribPointer(position,
                              floatsPerVertex,
                              GL_FLOAT,
                              False,
                              0,
                              ctypes.c_void_p(0))

        glBufferData(GL_ARRAY_BUFFER,
                     glfloat_size * np.size(vertices),
                     vertices,
                     GL_STATIC_DRAW)


        # send the modelspace data to the GPU
        # TODO, send color to the shader

        # reset VAO/VBO to default
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    # destructor
    def __del__(self):
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])
        glDeleteProgram(self.shader)

    def render(self):
        glUseProgram(self.shader)
        glBindVertexArray(self.vao)

        # pass projection parameters to the shader
        fov_loc = glGetUniformLocation(self.shader, "fov");
        glUniform1f(fov_loc, 45.0);
        aspect_loc = glGetUniformLocation(self.shader, "aspectRatio");
        glUniform1f(aspect_loc, width/height);
        nearZ_loc = glGetUniformLocation(self.shader, "nearZ");
        glUniform1f(nearZ_loc, -0.1);
        farZ_loc = glGetUniformLocation(self.shader, "farZ");
        glUniform1f(farZ_loc, -10000.0);

        # ascontiguousarray puts the array in column major order
        glUniformMatrix4fv(self.mvMatrixLoc,
                           1,
                           GL_TRUE,
                           np.ascontiguousarray(
                               ms.getCurrentMatrix(
                                   ms.MatrixStack.modelview),
                               dtype=np.float32))
        glDrawArrays(GL_LINES,
                     0,
                     self.numberOfVertices)
        glBindVertexArray(0)
ground = Ground()
ground.prepare_to_render()


class Axis:
    def __init__(self):
        pass


    def vertices(self):

        #glColor3f(0.1,0.1,0.1)
        glBegin(GL_LINES)
        verts = []
        verts.append(float(0.0))
        verts.append(float(0.0))
        verts.append(float(0.0))

        verts.append(float(0.0))
        verts.append(float(1.0))
        verts.append(float(0.0))


        # arrow
        verts.append(float(0.0))
        verts.append(float(1.0))
        verts.append(float(0.0))

        verts.append(float(0.25))
        verts.append(float(0.75))
        verts.append(float(0.0))


        verts.append(float(0.0))
        verts.append(float(1.0))
        verts.append(float(0.0))

        verts.append(float(-0.25))
        verts.append(float(0.75))
        verts.append(float(0.0))


        return np.array(verts,
                        dtype=np.float32)

    def prepare_to_render(self):
        # GL_QUADS aren't available anymore, only triangles
        # need 6 vertices instead of 4
        vertices = self.vertices()
        self.numberOfVertices = np.size(vertices) // floatsPerVertex

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # initialize shaders

        with open(os.path.join(pwd, 'axis.vert'), 'r') as f:
            vs = shaders.compileShader(f.read(), GL_VERTEX_SHADER)

        with open(os.path.join(pwd, 'axis.frag'), 'r') as f:
            fs = shaders.compileShader(f.read(), GL_FRAGMENT_SHADER)

        self.shader = shaders.compileProgram(vs, fs)

        self.mvMatrixLoc = glGetUniformLocation(self.shader, "mvMatrix")
        self.colorLoc = glGetUniformLocation(self.shader, "color")


        # send the modelspace data to the GPU
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        position = glGetAttribLocation(self.shader, 'position')
        glEnableVertexAttribArray(position)

        glVertexAttribPointer(position,
                              floatsPerVertex,
                              GL_FLOAT,
                              False,
                              0,
                              ctypes.c_void_p(0))

        glBufferData(GL_ARRAY_BUFFER,
                     glfloat_size * np.size(vertices),
                     vertices,
                     GL_STATIC_DRAW)


        # send the modelspace data to the GPU
        # TODO, send color to the shader

        # reset VAO/VBO to default
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    # destructor
    def __del__(self):
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])
        glDeleteProgram(self.shader)

    def render(self, grayed_out=False):
        glUseProgram(self.shader)
        glBindVertexArray(self.vao)

        # pass projection parameters to the shader
        fov_loc = glGetUniformLocation(self.shader, "fov");
        glUniform1f(fov_loc, 45.0);
        aspect_loc = glGetUniformLocation(self.shader, "aspectRatio");
        glUniform1f(aspect_loc, width/height);
        nearZ_loc = glGetUniformLocation(self.shader, "nearZ");
        glUniform1f(nearZ_loc, -0.1);
        farZ_loc = glGetUniformLocation(self.shader, "farZ");
        glUniform1f(farZ_loc, -10000.0);
        # TODO, set the color

        with ms.push_matrix(ms.MatrixStack.model):
            ms.scale(ms.MatrixStack.model,
                     10.0,
                     10.0,
                     10.0)

            # x axis
            with ms.push_matrix(ms.MatrixStack.model):
                ms.rotate_z(ms.MatrixStack.model,
                           math.radians(-90.0))

                glUniform3f(self.colorLoc, 1.0, 0.0, 0.0)
                if grayed_out:
                    glUniform3f(self.colorLoc, 0.5, 0.5, 0.5)

                # ascontiguousarray puts the array in column major order
                glUniformMatrix4fv(self.mvMatrixLoc,
                                   1,
                                   GL_TRUE,
                                   np.ascontiguousarray(
                                       ms.getCurrentMatrix(
                                           ms.MatrixStack.modelview),
                                       dtype=np.float32))
                glDrawArrays(GL_LINES,
                             0,
                             self.numberOfVertices)


            # z
            #glColor3f(0.0,0.0,1.0) # blue z
            with ms.push_matrix(ms.MatrixStack.model):
                ms.rotate_y(ms.MatrixStack.model,
                            math.radians(90.0))
                ms.rotate_z(ms.MatrixStack.model,
                            math.radians(90.0))

                glUniform3f(self.colorLoc, 0.0, 0.0, 1.0)
                if grayed_out:
                    glUniform3f(self.colorLoc, 0.5, 0.5, 0.5)
                # ascontiguousarray puts the array in column major order
                glUniformMatrix4fv(self.mvMatrixLoc,
                                   1,
                                   GL_TRUE,
                                   np.ascontiguousarray(
                                       ms.getCurrentMatrix(
                                           ms.MatrixStack.modelview),
                                       dtype=np.float32))
                glDrawArrays(GL_LINES,
                             0,
                             self.numberOfVertices)


            # y
            glUniform3f(self.colorLoc, 0.0, 1.0, 0.0)
            #glColor3f(0.0,1.0,0.0) # green y
            if grayed_out:
                glUniform3f(self.colorLoc, 0.5, 0.5, 0.5)
            # ascontiguousarray puts the array in column major order
            glUniformMatrix4fv(self.mvMatrixLoc,
                               1,
                               GL_TRUE,
                               np.ascontiguousarray(
                                   ms.getCurrentMatrix(
                                       ms.MatrixStack.modelview),
                                   dtype=np.float32))
            glDrawArrays(GL_LINES,
                         0,
                         self.numberOfVertices)
            glBindVertexArray(0)



axis = Axis()
axis.prepare_to_render()



class NDCCube:
    def __init__(self):
        pass


    def vertices(self):

        #glColor3f(0.1,0.1,0.1)
        glBegin(GL_LINES)
        verts = []
        verts.append(-1.0)
        verts.append(-1.0)
        verts.append(-1.0)

        verts.append(1.0,)
        verts.append(-1.0)
        verts.append(-1.0)


        verts.append(1.0,)
        verts.append(-1.0)
        verts.append(-1.0)

        verts.append(1.0,)
        verts.append(1.0,)
        verts.append(-1.0)


        verts.append(1.0,)
        verts.append(1.0,)
        verts.append(-1.0)

        verts.append(-1.0)
        verts.append(1.0,)
        verts.append(-1.0)


        verts.append(-1.0)
        verts.append(1.0,)
        verts.append(-1.0)

        verts.append(-1.0)
        verts.append(-1.0)
        verts.append(-1.0)


        verts.append(-1.0)
        verts.append(-1.0)
        verts.append(1.0)

        verts.append(1.0,)
        verts.append(-1.0)
        verts.append(1.0)


        verts.append(1.0,)
        verts.append(-1.0)
        verts.append(1.0)

        verts.append(1.0,)
        verts.append(1.0,)
        verts.append(1.0)


        verts.append(1.0,)
        verts.append(1.0,)
        verts.append(1.0)

        verts.append(-1.0)
        verts.append(1.0,)
        verts.append(1.0)


        verts.append(-1.0)
        verts.append(1.0,)
        verts.append(1.0)

        verts.append(-1.0)
        verts.append(-1.0)
        verts.append(1.0)





        # connect the squares
        verts.append(1.0,)
        verts.append(1.0,)
        verts.append(-1.0)

        verts.append(1.0,)
        verts.append(1.0,)
        verts.append(1.0)

        verts.append(1.0,)
        verts.append(-1.0)
        verts.append(-1.0)

        verts.append(1.0,)
        verts.append(-1.0)
        verts.append(1.0)

        verts.append(-1.0)
        verts.append(1.0,)
        verts.append(-1.0)

        verts.append(-1.0)
        verts.append(1.0,)
        verts.append(1.0)

        verts.append(-1.0)
        verts.append(-1.0)
        verts.append(-1.0)

        verts.append(-1.0)
        verts.append(-1.0)
        verts.append(1.0)



        return np.array(verts,
                        dtype=np.float32)

    def prepare_to_render(self):
        # GL_QUADS aren't available anymore, only triangles
        # need 6 vertices instead of 4
        vertices = self.vertices()
        self.numberOfVertices = np.size(vertices) // floatsPerVertex

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # initialize shaders

        with open(os.path.join(pwd, 'cube.vert'), 'r') as f:
            vs = shaders.compileShader(f.read(), GL_VERTEX_SHADER)

        with open(os.path.join(pwd, 'cube.frag'), 'r') as f:
            fs = shaders.compileShader(f.read(), GL_FRAGMENT_SHADER)

        self.shader = shaders.compileProgram(vs, fs)

        self.mvMatrixLoc = glGetUniformLocation(self.shader, "mvMatrix")


        # send the modelspace data to the GPU
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        position = glGetAttribLocation(self.shader, 'position')
        glEnableVertexAttribArray(position)

        glVertexAttribPointer(position,
                              floatsPerVertex,
                              GL_FLOAT,
                              False,
                              0,
                              ctypes.c_void_p(0))

        glBufferData(GL_ARRAY_BUFFER,
                     glfloat_size * np.size(vertices),
                     vertices,
                     GL_STATIC_DRAW)


        # send the modelspace data to the GPU
        # TODO, send color to the shader

        # reset VAO/VBO to default
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    # destructor
    def __del__(self):
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])
        glDeleteProgram(self.shader)

    def render(self):
        glUseProgram(self.shader)
        glBindVertexArray(self.vao)

        # pass projection parameters to the shader
        fov_loc = glGetUniformLocation(self.shader, "fov");
        glUniform1f(fov_loc, 45.0);
        aspect_loc = glGetUniformLocation(self.shader, "aspectRatio");
        glUniform1f(aspect_loc, width/height);
        nearZ_loc = glGetUniformLocation(self.shader, "nearZ");
        glUniform1f(nearZ_loc, -0.1);
        farZ_loc = glGetUniformLocation(self.shader, "farZ");
        glUniform1f(farZ_loc, -10000.0);

        # ascontiguousarray puts the array in column major order
        glUniformMatrix4fv(self.mvMatrixLoc,
                           1,
                           GL_TRUE,
                           np.ascontiguousarray(
                               ms.getCurrentMatrix(
                                   ms.MatrixStack.modelview),
                               dtype=np.float32))
        glDrawArrays(GL_LINES,
                     0,
                     self.numberOfVertices)
        glBindVertexArray(0)
cube = NDCCube()
cube.prepare_to_render()





moving_camera_r = 300
moving_camera_rot_y = math.radians(45.0)
moving_camera_rot_x = math.radians(35.264)


square_rotation = math.radians(90.0)
rotation_around_paddle1 = math.radians(30.0)


def handle_inputs():
    global rotation_around_paddle1
    if glfw.get_key(window, glfw.KEY_E) == glfw.PRESS:
        rotation_around_paddle1 += 0.1

    global square_rotation
    if glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS:
        square_rotation += 0.1

    global moving_camera_rot_y
    global moving_camera_rot_x

    move_multiple = 15.0
    if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
        moving_camera_rot_y -= math.radians(1.0) % 360.0
    if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
        moving_camera_rot_y += math.radians(1.0) % 360.0
    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
        moving_camera_rot_x -= math.radians(1.0) % 360.0
    if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
        moving_camera_rot_x += math.radians(1.0) % 360.0

    global paddle1, paddle2

    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        paddle1.offset_y -= 10.0
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        paddle1.offset_y += 10.0
    if glfw.get_key(window, glfw.KEY_K) == glfw.PRESS:
        paddle2.offset_y -= 10.0
    if glfw.get_key(window, glfw.KEY_I) == glfw.PRESS:
        paddle2.offset_y += 10.0

    global paddle_1_rotation, paddle_2_rotation

    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        paddle1.rotation += 0.1
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        paddle1.rotation -= 0.1
    if glfw.get_key(window, glfw.KEY_J) == glfw.PRESS:
        paddle2.rotation += 0.1
    if glfw.get_key(window, glfw.KEY_L) == glfw.PRESS:
        paddle2.rotation -= 0.1



virtual_camera_position = np.array([-40.0, 0.0,  80.0], dtype=np.float32)
virtual_camera_rot_y = math.radians(-30.0)
virtual_camera_rot_x = math.radians(15.0)






def draw_frustum():
    glLoadMatrixf(np.ascontiguousarray(ms.getCurrentMatrix(ms.MatrixStack.modelview).T))

    #glColor3f(1.0,1.0,1.0)
    glLineWidth(3.0)
    glBegin(GL_LINES)
    glVertex3f(-1.0, -1.0, -1.0)
    glVertex3f(1.0, -1.0, -1.0)
    glEnd()




TARGET_FRAMERATE = 60 # fps

# to try to standardize on 60 fps, compare times between frames
time_at_beginning_of_previous_frame = glfw.get_time()

animation_time = 0.0
animation_paused = False

# Loop until the user closes the window
while not glfw.window_should_close(window):
    # poll the time to try to get a constant framerate
    while glfw.get_time() < time_at_beginning_of_previous_frame +  1.0/TARGET_FRAMERATE:
        pass
    # set for comparison on the next frame
    time_at_beginning_of_previous_frame = glfw.get_time()

    if not animation_paused:
        animation_time += 1.0/60.0

    # Poll for and process events
    glfw.poll_events()


    width, height = glfw.get_framebuffer_size(window)
    glViewport(0, 0, width, height)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # render scene
    handle_inputs()

    ms.setToIdentityMatrix(ms.MatrixStack.model)
    ms.setToIdentityMatrix(ms.MatrixStack.view)
    ms.setToIdentityMatrix(ms.MatrixStack.projection)

    # set the projection matrix to be perspective
    ms.perspective(fov=45.0,
                   aspectRatio=1.0,  #since the viewport is always square
                   nearZ=0.1,
                   farZ=10000.0)

    # note - opengl matricies use degrees
    ms.translate(ms.MatrixStack.view,
                 0.0,
                 0.0,
                 -moving_camera_r)
    ms.rotate_x(ms.MatrixStack.view,
                moving_camera_rot_x)
    ms.rotate_y(ms.MatrixStack.view,
                -moving_camera_rot_y)



    # draw NDC in global space, so that we can see the camera space
    # go to NDC
    with ms.PushMatrix(ms.MatrixStack.model):
        ms.scale(ms.MatrixStack.model,
                 5.0,
                 5.0,
                 5.0)
        cube.render()
    ground.render()

    if(animation_time > 85.0):
        ms.rotate_x(ms.MatrixStack.model,
                    -virtual_camera_rot_x   * min(1.0, (animation_time - 85.0) / 5.0))
    if(animation_time > 80.0):
        ms.rotate_y(ms.MatrixStack.model,
                    -virtual_camera_rot_y  * min(1.0, (animation_time - 80.0) / 5.0))
    if(animation_time > 75.0):
        ms.translate(ms.MatrixStack.model,
                     -virtual_camera_position[0]   * min(1.0, (animation_time - 75.0) / 5.0),
                     -virtual_camera_position[1]   * min(1.0, (animation_time - 75.0) / 5.0),
                     -virtual_camera_position[2]   * min(1.0, (animation_time - 75.0) / 5.0))

    #draw virtual camera
    if animation_time > 60:
        with ms.push_matrix(ms.MatrixStack.model):
            if animation_time > 60:
                ms.translate(ms.MatrixStack.model,
                             virtual_camera_position[0]  * min(1.0, (animation_time - 60.0) / 5.0),
                             virtual_camera_position[1]  * min(1.0, (animation_time - 60.0) / 5.0),
                             virtual_camera_position[2]  * min(1.0, (animation_time - 60.0) / 5.0))
            if animation_time > 65:
                ms.rotate_y(ms.MatrixStack.model,
                            virtual_camera_rot_y  * min(1.0, (animation_time - 65.0) / 5.0))
            if animation_time > 70:
               ms.rotate_x(ms.MatrixStack.model,
                            virtual_camera_rot_x   * min(1.0, (animation_time - 70.0) / 5.0))

            axis.render()
            ms.scale(ms.MatrixStack.model,
                     5.0,
                     5.0,
                     5.0)

            cube.render()

    if animation_time < 5.0 or (animation_time > 40.0 and animation_time < 45.0):
        axis.render()
    else:
        axis.render(grayed_out=True)


    with ms.PushMatrix(ms.MatrixStack.model):

        if animation_time > 5.0:
            # draw paddle 1
            ms.translate(ms.MatrixStack.model,
                         paddle1.input_offset_x * min(1.0, (animation_time - 5.0) / 5.0),
                         paddle1.input_offset_y * min(1.0, (animation_time - 5.0) / 5.0),
                         0.0)

        if animation_time > 10.0:
            ms.translate(ms.MatrixStack.model,
                         paddle1.initial_position[0] * min(1.0, (animation_time - 10.0) / 5.0),
                         paddle1.initial_position[1] * min(1.0, (animation_time - 10.0) / 5.0),
                         0.0)
        if(animation_time > 15.0):
            ms.rotate_z(ms.MatrixStack.model,
                        paddle1.rotation * min(1.0, (animation_time - 15.0) / 5.0))

        if animation_time > 5.0 and animation_time < 20.0:
            axis.render()
        if animation_time > 20.0:
            # ascontiguousarray puts the array in column major order
            paddle1.render()

        # # draw the square

        if animation_time > 20.0:
            ms.translate(ms.MatrixStack.model,
                         0.0,
                         0.0,
                         -10.0 * min(1.0, (animation_time - 20.0) / 5.0))
        if animation_time > 25.0:
            ms.rotate_z(ms.MatrixStack.model,
                        rotation_around_paddle1 * min(1.0, (animation_time - 25.0) / 5.0))
        if animation_time > 30.0:
            ms.translate(ms.MatrixStack.model,
                         20.0 * min(1.0, (animation_time - 30.0) / 5.0),
                         0.0,
                         0.0)
        if animation_time > 35.0:
            ms.rotate_z(ms.MatrixStack.model,
                        square_rotation * min(1.0, (animation_time - 35.0) / 5.0))

        if animation_time > 20.0 and animation_time < 40.0:
            axis.render()

        if animation_time > 40.0:
            square.render()

    #get back to center of global space


    with ms.PushMatrix(ms.MatrixStack.model):

        # draw paddle 2
        if(animation_time > 45.0):

            ms.translate(ms.MatrixStack.model,
                         paddle2.input_offset_x * min(1.0, (animation_time - 45.0) / 5.0),
                         paddle2.input_offset_y * min(1.0, (animation_time - 45.0) / 5.0),
                         0.0)
        if(animation_time > 50.0):
            ms.translate(ms.MatrixStack.model,
                         paddle2.initial_position[0] * min(1.0, (animation_time - 50.0) / 5.0),
                         paddle2.initial_position[1] * min(1.0, (animation_time - 50.0) / 5.0),
                         0.0)
        if(animation_time > 55.0):
            ms.rotate_z(ms.MatrixStack.model,
                        paddle2.rotation * min(1.0, (animation_time - 55.0) / 5.0))

        if animation_time > 45.0 and animation_time < 60.0:
            axis.render()

        if(animation_time > 60.0):
            paddle2.render()



    # done with frame, flush and swap buffers
    # Swap front and back buffers
    glfw.swap_buffers(window)


glfw.terminate()