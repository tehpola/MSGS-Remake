import pygame
from spritesheet import SpriteSheet


class Skater(SpriteSheet):
    def __init__(self, info, state):
        super().__init__(info)
        self.state = state
        self.velocity = pygame.math.Vector2()
        self.gravity = 0.0025
        self.is_grounded = False

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

        center = pygame.math.Vector2(self.rect.size)/2
        pygame.draw.line(self.debug_overlay.image, (0, 0, 255), center, center + self.velocity * dt)

        # Move according to the velocity
        self.rect.move_ip(*(self.velocity * dt))
        self.debug_overlay.rect = self.rect

        # Detect the character moving off the screen
        ew, eh = self.state.env.rect.size
        if self.rect.x > ew or self.rect.y > eh or self.rect.x < -self.rect.width:
            self.rect.topleft = (0, 0)
            self.velocity.x = min(max(self.velocity.x, -10), 10)
            self.velocity.y = 0
            self.animate('float')
            # TODO: Move to the next scene
            return

        # Environmental collision detection
        collision = pygame.sprite.collide_mask(self.state.env, self)
        if collision:
            icol = collision
            collision = pygame.math.Vector2(collision)
            pygame.draw.circle(self.debug_overlay.image, (255, 0, 0), collision - self.rect.topleft, 4)
            self.state.world.add(self.debug_overlay)

            if self.state.env.is_dangerous(icol):
                self.animate('falling')
            elif self.state.env.is_grindable(icol):
                # TODO: Just flag this?
                pass
                #self.land()
                #self.animate('manual')
            elif self.state.env.is_rideable(icol):
                self.land(collision, dt)
                self.animate('riding')
            else:
                pass # wat do? Erorr!
        else:
            self.state.world.remove(self.debug_overlay)

            # Check whether we're rolling off the ground...
            gx, gy = self.rect.bottomleft
            gy += 2
            gx += (1 if self.velocity.x >= 0 else 2) * (0.3 * self.rect.width)
            if not self.state.env.is_rideable((int(gx), int(gy))):
                self.is_grounded = False

        SpriteSheet.update(self, dt)

    def land(self, collision, dt):
        # Resolve penetration
        if self.velocity:
            to_col = collision - self.rect.center
            corner = pygame.math.Vector2()
            corner.x = self.rect.left if to_col.x < 0 else self.rect.right
            corner.y = self.rect.top if to_col.y < 0 else self.rect.bottom
            back = (collision - corner).project(-self.velocity * dt)
            self.rect.move_ip(*back)

        self.velocity.y = 0
        self.is_grounded = True

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            name = pygame.key.name(event.key)
            if name == 'right':
                self.velocity.x += 0.1
            elif name == 'left':
                self.velocity.x -= 0.1
            elif name == 'space' and self.is_grounded:
                self.velocity.y = -1
                self.is_grounded = False
                self.animate('ollie')

    def animate(self, animation):
        super().animate(animation)

        if self.info['animations'][self.animation].get('display'):
            self.state.update_combo(animation)
        elif animation in ('riding', 'falling', 'ded'):
            self.state.end_combo()
