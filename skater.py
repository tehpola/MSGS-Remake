import pygame
from spritesheet import SpriteSheet


class Skater(SpriteSheet):
    def __init__(self, info):
        SpriteSheet.__init__(self, info)
        self.velocity = (0, 0)
        self.gravity = 0.025

    def update(self, dt, state, *args, **kwargs):
        ox, oy = self.rect.topleft

        # Apply gravity
        vx, vy = self.velocity
        vy += self.gravity * dt
        self.velocity = vx, vy

        self.rect.move_ip(*self.velocity)

        collision = pygame.sprite.collide_mask(state.env, self)
        if collision:
            if state.env.is_dangerous(collision):
                self.animate('falling')
            elif state.env.is_grindable(collision):
                self.rect.move_ip(0, -1)
                self.velocity = vx, 0
                self.animate('manual')
            elif state.env.is_rideable(collision):
                self.rect.move_ip(0, -1)
                self.velocity = vx, 0
                self.animate('riding')
            else:
                pass # wat do? Erorr!

        SpriteSheet.update(self, dt)

    def animate(self, animation):
        self.animation = animation
        self.frame = 0
