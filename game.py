import pygame as pg
import pymunk as pm

import sys
import math
import random

from assets import (Background,
                    Ground,
                    Ball,
                    Sling1,
                    Sling2,
                    Beam,
                    Column,
                    fetch_columns_and_beams)

from physics import (post_solve_ground_ball,
                     post_solve_wall_ball,
                     post_solve_ball_ball,
                     post_solve_wood_ball,
                     post_solve_column_column)

from constants import (SCREEN_HEIGHT,
                       SCREEN_WIDTH,
                       SPRITE_WIDTH,
                       SPRITE_HEIGHT)

from collections import deque
from pymunk.pygame_util import from_pygame
from os.path import join


MAROON = pg.Color(79, 32, 6)
WHITE = pg.Color(255, 255, 255)
BLACK = pg.Color(0, 0, 0)
YELLOW = pg.Color(255, 255, 0)

clock = pg.time.Clock()
space_step = 1/60
initial_ball_x, initial_ball_y = 90, 200


def main():
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("Angry snowball")

    pm.Segment.elasticity, pm.Segment.friction = 0, 0.4
    background = Background()
    ground = Ground()

    space = pm.Space()
    space.gravity = (0.0, 900.0) # Define initial gravity

    sling1 = Sling1()
    sling2 = Sling2()

    woods = fetch_columns_and_beams()

    font = pg.font.Font(join("fonts", "segoe-ui-symbol.ttf"), 20)
    alpha_bg = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    alpha_bg.set_alpha(128)
    alpha_bg.fill((BLACK))

    def build_tiles():

        # Build ground according to the size of the screen width
        for i in range(math.ceil(SCREEN_WIDTH / ground.image.get_rect().size[SPRITE_WIDTH])):
            ground.set_position(
                i * ground.image.get_rect().size[SPRITE_WIDTH], SCREEN_HEIGHT - ground.image.get_rect().size[SPRITE_HEIGHT])
            screen.blit(ground.image, ground.rect)

    def create_static_lines() -> list:

        body = pm.Body(body_type=pm.Body.STATIC)

        segment_1 = pm.Segment(body, (0, ground.rect.y),
                               (SCREEN_WIDTH, ground.rect.y), 2)

        # I am moving the right wall a little bit
        # to the left so beams and columns don't behave unexpectedly: SCREEN_WIDTH - 10
        segment_2 = pm.Segment(body, (SCREEN_WIDTH, 0),
                               (SCREEN_WIDTH - 10, SCREEN_HEIGHT + 10), 5)
        segment_3 = pm.Segment(body, (0, 0), (SCREEN_WIDTH, 0), 5)
        segment_4 = pm.Segment(body, (0, 0), (0, SCREEN_HEIGHT), 5)

        segment_1.collision_type = 1
        segment_2.collision_type = 2
        segment_3.collision_type = 3

        return[body, segment_1, segment_2, segment_3, segment_4]

    build_tiles()

    # Create snowflakes where position x, y and radius is random 
    snowflakes = [{"x": random.randint(0, SCREEN_WIDTH), "y": random.randint
                   (0, ground.rect.y), "radius": random.randint(1, 2), } for flakes in range(100)]

    def handle_snowflakes():

        # Draw snowflakes on the screen
        for flake in snowflakes:
            pg.draw.circle(
                screen, WHITE, (flake["x"], flake["y"]), flake["radius"], width=0)
            flake["y"] += 1

            if flake["y"] > ground.rect.y:
                # Move a little bit above the top of the screen
                flake["y"] = -10

    space.add(*create_static_lines())
    [space.add(wood.shape, wood.body) for wood in woods]

    sling1.set_position(100, ground.rect.y -
                        ground.image.get_rect().size[1] / 1.8)

    sling2.set_position(70, ground.rect.y -
                        ground.image.get_rect().size[1] / 1.7)

    # 1 -> segment ground  # 2 -> segment right side wall
    # 3 -> segment ceiling # 4 -> Ball shape
    # 5 -> Beam            # 6 -> Column
    space.add_collision_handler(1, 4).post_solve = post_solve_ground_ball
    space.add_collision_handler(2, 4).post_solve = post_solve_wall_ball
    space.add_collision_handler(3, 4).post_solve = post_solve_wall_ball
    space.add_collision_handler(4, 4).post_solve = post_solve_ball_ball

    space.add_collision_handler(4, 5).post_solve = post_solve_wood_ball
    space.add_collision_handler(4, 6).post_solve = post_solve_wood_ball
    space.add_collision_handler(6, 6).post_solve = post_solve_column_column

    # Add first ball
    ball = Ball()
    ball.set_position(initial_ball_x, initial_ball_y)
    ball.set_paused_ball()
    balls = deque([ball])

    # balls_: balls available to be thrown
    # balls : balls on deque to be thrown
    balls_ = [ball.image.copy()] * 7

    game_win = game_over = mouse_down = done = False
    while not done:

        screen.blit(background.image, background.rect)

        for b in balls:
            if b.shape in space.shapes:
                if b.shape.trigger_animation:
                    b.animate()
                else:
                    b.set_paused_ball()

                b.rotate()
            else:
                b.set_paused_ball()

        for event in pg.event.get():

            if event.type == pg.QUIT:
                done = True

            if event.type == pg.KEYDOWN:

                if event.key == pg.K_ESCAPE:
                    done = True

            if not game_over and not game_win and not \
                        len(balls_) - len(balls) < 1 :
                if event.type == pg.MOUSEBUTTONUP:
                    mouse_down = False

                    dx, dy = (initial_ball_x - mouse_x,
                              initial_ball_y - mouse_y)
                    balls[0].body.angle = math.atan2(dy, dx)
                    balls[0].rotate()
                    balls[0].set_position(initial_ball_x, initial_ball_y)
                    balls[0].is_thrown = True

                    speed = 800 - mouse_x * 10
                    if speed < 600:
                        balls[0].shape.trigger_animation = False

                    balls[0].shape.body.apply_impulse_at_local_point((speed, 0), (1, -0.2))
                    space.add(balls[0].shape, balls[0].body)

                    # Throw ball on queue and add new one to stack 
                    ball = Ball()
                    ball.set_position(initial_ball_x, initial_ball_y)
                    balls.appendleft(ball)

                
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_down = True
                    x, y = event.pos
                    mouse_x, mouse_y = x, y

                    # Limiting the sling
                    if x < 11:
                        mouse_x = 11

                    if x > 74:
                        mouse_x = 74

                    if y < 201:
                        mouse_y = 201

                    if y > 255:
                        mouse_y = 255

                if mouse_down:
                    if event.type == pg.MOUSEMOTION:

                        x, y = event.pos
                        if 10 < x < 75:
                            mouse_x = x

                        if 200 < y < 256:
                            mouse_y = y

        if not mouse_down:

            pg.draw.line(screen, MAROON, (75, 210), (145, 210), width=8)
            screen.blit(balls[0].rotate_image, balls[0].body.position)

        else:

            pg.draw.line(screen, MAROON, (mouse_x, mouse_y),
                         (145, 210), width=8)
            balls[0].set_position(mouse_x, mouse_y - 15)
            screen.blit(balls[0].rotate_image, balls[0].body.position)
            pg.draw.line(screen, MAROON, (mouse_x, mouse_y),
                         (75, 210), width=8)

        # For each ball blit image
        [screen.blit(b.rotate_image, b.body.position)
         for b in balls if b.is_thrown]

        screen.blit(sling1.image, sling1.rect)
        screen.blit(sling2.image, sling2.rect)

        is_dive = 0
        for wood in woods:
            screen.blit(wood.rotate_image,
                        (wood.body.position.x, wood.body.position.y))

            if wood.body.position.y > 250:
                wood.is_dive = True
                is_dive += 1
                if is_dive == len(woods) and not game_over:
                    screen.blit(alpha_bg, (0, 0))
                    label = font.render(
                        "VICTORY !!!", 1, YELLOW)
                    screen.blit(
                        label, (SCREEN_WIDTH / 2.5, SCREEN_HEIGHT / 2.5))
                    [space.remove(wood.shape, wood.body)
                     for wood in woods if wood.shape in space.shapes]
                    game_win = True

            if wood.shape.trigger_rotation:
                wood.rotate(screen)

        space.step(space_step)
        build_tiles()

        for i in range(len(balls_) - len(balls)):
            screen.blit(balls_[i], (i * 30, SCREEN_HEIGHT - 60))

        else:
            if len(balls_) - len(balls) < 1 and not game_win: # Maybe change this criteria
                screen.blit(alpha_bg, (0, 0))
                label = font.render(
                    "GAME OVER !!!", 1, YELLOW)
                screen.blit(label, (SCREEN_WIDTH / 2.5, SCREEN_HEIGHT / 2.5))
                game_over = True

        handle_snowflakes()
        pg.display.flip()
        clock.tick(30)  # FPS


if __name__ == "__main__":
    sys.exit(main())
