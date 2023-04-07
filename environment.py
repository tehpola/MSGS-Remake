from enum import Enum, IntEnum
import json
import jsonpickle
import pygame


class SurfaceType(Enum):
    Pavement = 1
    Ledge = 2
    Hazard = 3


class Surface(object):
    def __init__(self, surftype, *args, **kwargs):
        self.rect = pygame.Rect(*args, **kwargs)
        self.surftype = surftype

    _surftypecolors = {
        SurfaceType.Pavement:   pygame.color.Color(0, 255, 0),
        SurfaceType.Ledge:      pygame.color.Color(0, 0, 255),
        SurfaceType.Hazard:     pygame.color.Color(255, 0, 0),
    }

    def get_editor_color(self):
        return self._surftypecolors[self.surftype]


class Environment(pygame.sprite.Sprite):
    def __init__(self, info, size):
        # Construct the base sprite and load our configuration
        pygame.sprite.Sprite.__init__(self)
        self.filename = info
        with open(info, 'r') as file:
            self.info = json.load(file)

        # Load in the art and geometry images
        self.image = pygame.image.load(self.info['art']).convert()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        with open(self.info['geo']) as geo_file:
            self.geo = jsonpickle.decode(geo_file.read())

    def get_surface_at(self, rect) -> Surface:
        for idx in rect.collidelistall(self.geo):
            surf = self.geo[idx]
            # TODO: Here I can do more refined testing for collisions with ramps
            return surf

        return None
