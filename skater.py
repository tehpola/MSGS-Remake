import pygame
from spritesheet import SpriteSheet


class Skater(SpriteSheet):
    def __init__(self, info):
        SpriteSheet.__init__(self, info)
        self.velocity = (0, 0)
        self.gravity = 0.025

    def update(self, dt, state, *args, **kwargs):
        SpriteSheet.update(self, dt)
        ox, oy = self.rect.topleft

        # Apply gravity
        vx, vy = self.velocity
        vy += self.gravity * dt
        self.velocity = vx, vy

        self.rect.move_ip(*self.velocity)

        collision = pygame.sprite.collide_mask(self, state.env)
        if collision:
            # Dumb impl for right now - bounce back
            self.rect.topleft = ox, oy
            self.velocity = vx, -15
