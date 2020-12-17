import pygame as pg


from constants import (SCREEN_HEIGHT,
                       SCREEN_WIDTH,
                       SPRITE_WIDTH,
                       SPRITE_HEIGHT)

from os.path import join
from json import loads
from physics import Circle, Rectangle

_background_path = join("assets", "png", "BG", "BG.png")
_beam = join("assets", "wood", "beam.png")
_column = join("assets", "wood", "column.png")
_Tile = join("assets", "png", "Tiles", "2.png")
_ball = join("assets", "snowball")
_sling = join("assets", "sling")

_level_1_path = join("assets", "level", "level_1.json")

_sling1_scale = (50, 75)
_sling2_scale = (50, 50)
_ball_scale = (60, 40)


class Base(pg.sprite.Sprite):

    def __init__(self, image):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()

    def set_position(self, x, y) -> None:

        # Change my rectangle

        self.rect.x = x
        self.rect.y = y


class Background(Base):

    def __init__(self):
        image = pg.transform.scale(pg.image.load(_background_path)
                                   .convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT))
        Base.__init__(self, image)


class Ground(Base):

    def __init__(self):
        image = pg.image.load(_Tile).convert_alpha()
        Base.__init__(self, image)


class Sling1(Base):

    def __init__(self):
        image = pg.transform.scale(pg.image.load(
            join(_sling, "sling1.png")).convert_alpha(), _sling1_scale)
        Base.__init__(self, image)


class Sling2(Base):

    def __init__(self):
        image = pg.transform.scale(pg.image.load(
            join(_sling, "sling2.png")).convert_alpha(), _sling2_scale)
        Base.__init__(self, image)


class Ball(Base, Circle):

    def __init__(self):
        self.__images = [pg.transform.flip(
            pg.transform.scale(pg.image.load(
                join(_ball, "snowball_0" + str(i) + ".png")), _ball_scale), True, False) for i in range(1, 7)]

        self.__images.append(pg.transform.flip(
            pg.transform.scale(pg.image.load(
                join(_ball, "snowball_07.png")), (30, 30)), True, False))

        self.__is_thrown = False
        self.__index = 0
        self.rotate_image = self.__images[self.__index]
        image = self.__images[self.__index]
        Base.__init__(self, image)
        Circle.__init__(self, self.rect, collision_type=4, radius=15)

    @property
    def is_thrown(self):
        return self.__is_thrown

    @is_thrown.setter
    def is_thrown(self, value):
        assert type(value) == bool
        self.__is_thrown = value

    def animate(self):

        if self.__index == len(self.__images) - 1:
            self.__index = 0

        self.image = self.__images[self.__index]
        self.__index += 1

    def set_paused_ball(self):
        self.rotate_image = self.image = self.__images[-1]

    def set_position(self, x: float, y: float) -> None:
        self.body.position = (x, y)


class Beam(Base, Rectangle):

    def __init__(self, pos):
        self.rotate_image = image = pg.image.load(_beam).convert_alpha()
        self.is_dive = False
        Base.__init__(self, image)

        self.rect.x, self.rect.y = pos[0], pos[1]
        Rectangle.__init__(self, self.rect, collision_type=5, size=(
            image.get_rect().size[SPRITE_WIDTH], image.get_rect().size[SPRITE_HEIGHT]))

    def set_position(self, x: float, y: float) -> None:
        self.body.position = (x, y)


class Column(Base, Rectangle):

    def __init__(self, pos):
        self.rotate_image = image = pg.image.load(_column).convert_alpha()
        self.is_dive = False
        Base.__init__(self, image)

        self.rect.x, self.rect.y = pos[0], pos[1]
        Rectangle.__init__(self, self.rect, collision_type=6, size=(
            image.get_rect().size[SPRITE_WIDTH], image.get_rect().size[SPRITE_HEIGHT]))

    def set_position(self, x: float, y: float) -> None:
        self.body.position = (x, y)


def fetch_columns_and_beams():


    """
        Fetch columns and beams using json file
        returns:
            list: woods lists 

    """

    switcher = {
        "column": Column,
        "beam": Beam,
    }

    woods = []
    with open(_level_1_path, "r") as myfile:  # Open json file
        data = myfile.read()
        obj = loads(data)
        for wood in obj:
            w = switcher.get(wood["type"])
            woods.append(w((wood["x"], wood["y"])))

    return woods
