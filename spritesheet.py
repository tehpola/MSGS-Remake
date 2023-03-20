import json
import pygame


class SpriteSheet(pygame.sprite.Sprite):
    """
    Sprite Sheets represent an animated sprite.
    All of the animations for the character are packed into a single image.
    A JSON file describes the animations and their layout in the sheet image.
    """
    def __init__(self, info):
        # Construct the base sprite and load our configuration
        pygame.sprite.Sprite.__init__(self)
        with open(info, 'r') as file:
            self.info = json.load(file)

        # Load in the sheet and construct our visible surface
        self.sheet = pygame.image.load(self.info['filename']).convert_alpha()
        self.image = pygame.Surface((self.info['width'], self.info['height'])).convert_alpha()
        self.rect = self.image.get_rect()

        # Initialize animation
        self.animation = self.info['start']
        self.frame = 0
        self.frame_time = 0
        self._blit()

    def _blit(self):
        anim = self.info['animations'][self.animation]
        frame = anim['frames'][self.frame]
        x, y, w, h = frame['x'], frame['y'], frame['w'], frame['h']
        self.image.fill((0, 0, 0, 0))
        self.image.blit(self.sheet, (0, 0), (x, y, w, h))

    def update(self, dt, *args, **kwargs):
        # Animate the sprite
        self.frame_time += dt
        anim = self.info['animations'][self.animation]
        if self.frame_time > anim['frames'][self.frame]['t']:
            self.frame_time = 0
            self.frame += 1
            if self.frame >= len(anim['frames']):
                self.frame = 0
                if not anim.get('looping', False):
                    self.animation = anim.get('next', self.info['start'])

            self._blit()
