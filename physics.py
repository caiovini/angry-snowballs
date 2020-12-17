
import pygame as pg
import pymunk as pm

import math

from constants import SPRITE_WIDTH, SPRITE_HEIGHT


class Body():

    def __init__(self, position, mass, moment, body_type=pm.Body.DYNAMIC):
        self.body = pm.Body(mass=mass, moment=moment, body_type=body_type)
        self.body.position = position.x, position.y

    def rotate(self):

        """
            Rotate ball and keep its center
            This is only used by the ball body
        """

        try:
            orig_rect = self.image.get_rect()
            rot_image = pg.transform.rotate(
                self.image, -math.degrees(float(str(self.body.angle)[:5])))
            rot_rect = orig_rect.copy()
            rot_rect.center = rot_image.get_rect().center
            self.rotate_image = rot_image.subsurface(rot_rect).copy()
        except Exception as e:
            print(e)


class Circle(Body):
    def __init__(self, position, collision_type, *, radius):

        mass = 1
        moment = pm.moment_for_circle(
            mass=mass, inner_radius=0, outer_radius=radius)
        Body.__init__(self, position, mass, moment)

        self.shape = pm.Circle(self.body, radius)
        self.shape.elasticity = 0.5
        self.shape.friction = 0.5
        self.shape.trigger_animation = True

        self.shape.collision_type = collision_type


class Rectangle(Body):
    def __init__(self, position, collision_type, *, size):

        if collision_type != 5:
            # Column
            vertices = [pm.Vec2d(size[SPRITE_WIDTH]/2, -size[SPRITE_HEIGHT]/4),
                        pm.Vec2d(size[SPRITE_WIDTH]/2, size[SPRITE_HEIGHT]),
                        pm.Vec2d(-size[SPRITE_WIDTH]/2, size[SPRITE_HEIGHT]),
                        pm.Vec2d(-size[SPRITE_WIDTH]/2, -size[SPRITE_HEIGHT]/4)]

        else:
            # Beam
            vertices = [pm.Vec2d(size[SPRITE_WIDTH]/8, -size[SPRITE_HEIGHT]/4),
                        pm.Vec2d(size[SPRITE_WIDTH]/8, size[SPRITE_HEIGHT]/8),
                        pm.Vec2d(-size[SPRITE_WIDTH]/4, size[SPRITE_HEIGHT]/8),
                        pm.Vec2d(-size[SPRITE_WIDTH]/4, -size[SPRITE_HEIGHT]/4)]

        mass = 1
        moment = pm.moment_for_poly(mass=mass, vertices=vertices)
        Body.__init__(self, position, mass, moment)
        self.shape = pm.Poly(self.body, vertices=vertices, radius=0.5)

        self.shape.density = .0001
        self.shape.elasticity = 0.4

        self.shape.friction = 0.1
        self.shape.trigger_rotation = False

        self.shape.collision_type = collision_type
        self.angle = 0

    def rotate(self, screen):

        """
            Rotate the rectangle shapes
            This is only used by beams and columns 
        """

        self.angle = -math.degrees(float(str(self.body.angle)[:10]))
        self.rotate_image = pg.transform.rotate(self.image, self.angle)


def post_solve_ground_ball(arbiter, space, _):
    _, shape = arbiter.shapes
    space.remove(shape, shape.body)


def post_solve_wall_ball(arbiter, space, _):
    _, shape = arbiter.shapes
    shape.trigger_animation = False


def post_solve_wood_ball(arbiter, space, _):
    shape1, shape2 = arbiter.shapes
    shape1.trigger_animation = False

    if shape2.collision_type != 5:
        shape2.trigger_rotation = True


def post_solve_column_column(arbiter, space, _):
    shape1, shape2 = arbiter.shapes
    shape1.trigger_rotation = True
    shape2.trigger_rotation = True


def post_solve_ball_ball(arbiter, space, _):
    shape1, shape2 = arbiter.shapes
    shape1.trigger_animation = False
    shape2.trigger_animation = False
