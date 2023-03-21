import pygame
from spritesheet import SpriteSheet


class Skater(SpriteSheet):
    def __init__(self, info):
        SpriteSheet.__init__(self, info)

    def update(self, dt, *args, **kwargs):
        SpriteSheet.update(self, dt)
