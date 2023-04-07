import pygame

import environment
from spritesheet import SpriteSheet


class Skater(SpriteSheet):
    def __init__(self, info, state):
        super().__init__(info)
        self.state = state
        self.velocity = pygame.math.Vector2()
        self.gravity = 0.0025
        self.depart()

        self.debug_overlay = pygame.sprite.Sprite()
        self.debug_overlay.image = pygame.surface.Surface(self.image.get_size()).convert_alpha()
        pygame.draw.circle(self.debug_overlay.image, (255, 0, 0), (4, 4), 4)
        self.debug_overlay.rect = self.debug_overlay.image.get_rect()

    def update(self, dt, *args, **kwargs):
        ox, oy = self.rect.topleft
        self.debug_overlay.image.fill((0, 0, 0, 0))

        # Apply gravity
        if not self.is_grounded:
            self.velocity.y += self.gravity * dt

        # Draw debug lines
        center = pygame.math.Vector2(self.rect.size)/2
        pygame.draw.line(self.debug_overlay.image, (0, 0, 255), center, center + self.velocity * dt)

        # Move according to the velocity
        self.rect.move_ip(*(self.velocity * dt))
        self.debug_overlay.rect = self.rect

        # Detect the character moving off the screen
        ew, eh = self.state.env.rect.size
        # FIXME: Use a screen rect
        if self.rect.x > ew or self.rect.y > eh or self.rect.x < -self.rect.width:
            self.rect.topleft = (0, 0)
            self.velocity.x = min(max(self.velocity.x, -10), 10)
            self.velocity.y = 0
            self.animate('float')
            # TODO: Move to the next scene
            return

        # Environmental collision detection
        collision = self.state.env.get_surface_at(self.rect)
        if collision:
            center = pygame.math.Vector2(collision.rect.center)
            pygame.draw.circle(self.debug_overlay.image, (255, 0, 0), center - self.rect.topleft, 4)
            self.state.world.add(self.debug_overlay)

            if collision.surftype == environment.SurfaceType.Hazard:
                self.animate('falling')
            elif collision.surftype == environment.SurfaceType.Ledge:
                # TODO: Just flag this?
                pass
                #self.land()
                #self.animate('manual')
            elif collision.surftype == environment.SurfaceType.Pavement:
                self.land(collision, dt)
                self.animate('riding')
            else:
                raise NotImplementedError()
        else:
            self.state.world.remove(self.debug_overlay)

            # Check whether we're rolling off the ground...
            if self.surface:
                start = pygame.math.Vector2(self.rect.midbottom)
                end = start.copy()
                end.y += self.gravity * dt

                if not self.surface.rect.clipline(start, end):
                    self.depart()


        SpriteSheet.update(self, dt)

    def land(self, collision, dt):
        self.surface = collision
        self.is_grounded = True
        # FIXME: Assuming all ground is flat
        self.velocity.y = 0

        # Resolve penetration
        back = pygame.math.Vector2(self.rect.center) - collision.rect.center
        corner = pygame.math.Vector2()
        corner.x = self.rect.right if back.x < 0 else collision.rect.left
        corner.y = self.rect.bottom if back.y < 0 else collision.rect.top
        out = collision.rect.clipline(self.rect.center, corner)
        if out:
            v1, v2 = out
            self.rect.move_ip(*(pygame.math.Vector2(v1) - v2))

    def depart(self):
        self.is_grounded = False
        self.surface = None

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            name = pygame.key.name(event.key)
            if self.is_grounded:
                # Grounded inputs: push / slow / ollie
                if name == 'right':
                    self.velocity.x += 0.1
                elif name == 'left':
                    self.velocity.x -= 0.1
                elif name == 'space':
                    self.velocity.y = -1
                    self.depart()
                    self.animate('ollie')

    def animate(self, animation):
        super().animate(animation)

        if self.info['animations'][self.animation].get('display'):
            self.state.update_combo(animation)
        elif animation in ('riding', 'falling', 'ded'):
            self.state.end_combo()
