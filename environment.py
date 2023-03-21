import json
import pygame


class Environment(pygame.sprite.Sprite):
    def __init__(self, info):
        # Construct the base sprite and load our configuration
        pygame.sprite.Sprite.__init__(self)
        with open(info, 'r') as file:
            self.info = json.load(file)

        # Load in the art and geometry images
        self.image = pygame.image.load(self.info['art']).convert()
        self.rect = self.image.get_rect()
        self.geo = pygame.image.load(self.info['geo']).convert_alpha()
