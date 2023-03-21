import pygame
from spritesheet import SpriteSheet


class Skater(SpriteSheet):
    def __init__(self, info):
        SpriteSheet.__init__(self, info)
        self.velocity = (0, 0)
        self.gravity = 0.025
        self.is_grounded = False

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
                # TODO: Only collide while coming down...
                self.land()
                self.animate('manual')
            elif state.env.is_rideable(collision):
                self.land()
                self.animate('riding')
            else:
                pass # wat do? Erorr!

        SpriteSheet.update(self, dt)

    def land(self):
        vx, _ = self.velocity
        self.rect.move_ip(0, -1)
        self.velocity = vx, 0
        self.is_grounded = True

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            name = pygame.key.name(event.key)
            vx, vy = self.velocity
            if name == 'right':
                self.velocity = vx + 2, vy
            elif name == 'left':
                self.velocity = vx - 2, vy
            elif name == 'space' and self.is_grounded:
                self.velocity = vx, -15
                self.is_grounded = False
                self.animate('ollie')
