import pygame
import sys
from spritesheet import SpriteSheet


is_dev_mode = True
nothing = pygame.Color(0, 0, 0, 0)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)


class Config(object):
    def __init__(self):
        self.intro_name_times = (
            (500, 1000),
            (2000, 2500),
        )
        self.intro_pres_times = (
            (3000, 3500),
            (4500, 5000),
        )
        self.intro_tit_times = (
            (6000, 6500),
            (8500, 9000),
        )


class State(object):
    def __init__(self, clock: pygame.time.Clock, screen):
        self.config = Config()
        self.clock = clock
        self.screen = screen
        self.is_intro_completed = False
        self.intro_time = 0
        self.font = pygame.font.Font('freesansbold.ttf', 64)
        self.bob = SpriteSheet('assets/Skata.json')
        self.world = pygame.sprite.Group()


def blend(t, t0, t1):
    return (t - t0) / (t1 - t0)


def intro_tick(state):
    if is_dev_mode:
        state.is_intro_completed = True
        state.world.add(state.bob)
        return

    time = pygame.time.get_ticks()
    (nfis, nfie), (nfos, nfoe) = state.config.intro_name_times
    (pfis, pfie), (pfos, pfoe) = state.config.intro_pres_times
    (tfis, tfie), (tfos, tfoe) = state.config.intro_tit_times

    sys.stdout.write('%.2f\r' % time)

    if time < nfis:
        return
    elif time < nfoe:
        alpha = min(1, blend(time, nfis, nfie)) \
            if time < nfos else \
            1.0 - blend(time, nfos, nfoe)
        color = nothing.lerp(red, alpha)
        text = state.font.render('Mike Slegeir', True, color)
        textRect = text.get_rect()
        textRect.center = (1280/2, 720/2) # FIXME
        state.screen.blit(text, textRect)

    if time < pfis:
        return
    elif time < pfoe:
        alpha = min(1, blend(time, pfis, pfie)) \
            if time < pfos else \
            1.0 - blend(time, pfos, pfoe)
        color = nothing.lerp(green, alpha)
        text = state.font.render('PRESENTS...', True, color)
        textRect = text.get_rect()
        textRect.center = (1280/2, 720/2) # FIXME
        state.screen.blit(text, textRect)

    if time < tfis:
        return
    elif time < tfoe:
        alpha = min(1, blend(time, tfis, tfie)) \
            if time < tfos else \
            1.0 - blend(time, tfos, tfoe)
        color = nothing.lerp(blue, alpha)
        text = state.font.render('G N A R   S K A T A !', True, color)
        textRect = text.get_rect()
        textRect.center = (1280/2, 720/2) # FIXME
        state.screen.blit(text, textRect)
    else:
        state.is_intro_completed = True
        state.world.add(state.bob)


def game_tick(state, dt):
    sys.stdout.write('%.1f\r' % dt)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

    state.screen.fill('black')

    if not state.is_intro_completed:
        intro_tick(state)
    else:
        state.world.update(dt)
        state.world.draw(state.screen)

    pygame.display.flip()

    return True


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption('Mike Slegeir\'s Gnar Skater')
    clock = pygame.time.Clock()
    state = State(clock, screen)

    t, lt = 0, 0
    while game_tick(state, t - lt):
        clock.tick(60)
        lt = t
        t = pygame.time.get_ticks()

    pygame.quit()


if __name__ == '__main__':
    main()
