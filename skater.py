import pygame

import environment
from spritesheet import SpriteSheet


class Skater(SpriteSheet):
    def __init__(self, info, state):
        super().__init__(info)
        self.state = state
        self.velocity = pygame.math.Vector2()
        self.gravity = 0.0025
        self.input_look_back = 60
        self.input_look_ahead = 120
        self.depart()
        self.last_dir = None
        self.last_dir_time = -1
        self.latent_action = None
        self.latent_action_deadline = -1

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
            # Move to the next scene, if appropriate
            if self.rect.x > ew:
                self.state.update_environment(next=True)
            elif self.rect.x < -self.rect.width:
                self.state.update_environment(next=False)

            self.rect.topleft = (0, 0)
            self.velocity.x = min(max(self.velocity.x, -10), 10)
            self.velocity.y = 0
            self.animate('float')
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

    def do_flip(self, direction):
        if direction == 'left':
            self.animate('kickflip')
        elif direction == 'right':
            self.animate('heelflip')

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            ticks = pygame.time.get_ticks()
            name = pygame.key.name(event.key)

            # Handle look-ahead / look-back for directional inputs
            if name in ('up', 'down', 'left', 'right'):
                self.last_dir = name
                self.last_dir_time = pygame.time.get_ticks()
                if self.latent_action and ticks <= self.latent_action_deadline:
                    self.latent_action(name)
                    self.latent_action = None

            # Flip Tricks on X
            if name == 'x':
                if not self.is_grounded and self.animation not in ('ollie', 'float'):
                    # Consuming this input
                    return

                if self.is_grounded:
                    self.velocity.y = -1
                    self.depart()
                    self.animate('ollie')

                pressed = pygame.key.get_pressed()
                last_dir_valid = (ticks - self.last_dir_time) < self.input_look_back
                if pressed[pygame.K_LEFT] or last_dir_valid and self.last_dir == 'left':
                    self.do_flip('left')
                elif pressed[pygame.K_RIGHT] or last_dir_valid and self.last_dir == 'right':
                    self.do_flip('right')
                else:
                    self.latent_action = self.do_flip
                    self.latent_action_deadline = ticks + self.input_look_ahead
            # Grind Tricks on C
            elif name == 'c':
                # TODO: Initiate grind
                pass
            # Grounded Actions (Push / Slow / Ollie)
            elif self.is_grounded:
                if name == 'right':
                    self.velocity.x += 0.1
                elif name == 'left':
                    self.velocity.x -= 0.1
                elif name == 'space':
                    # TODO: Crouch logic?
                    self.velocity.y = -1
                    self.depart()
                    self.animate('ollie')

    def animate(self, animation):
        super().animate(animation)

        if self.info['animations'][self.animation].get('display'):
            self.state.update_combo(animation)
        elif animation in ('riding', 'falling', 'ded'):
            self.state.end_combo()
