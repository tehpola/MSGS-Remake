# /// script
# dependencies = [
#   "jsonpickle",
# ]
# ///

import asyncio
import pygame
import sys
from skater import Skater
from environment import Environment


is_dev_mode = True
size = (width, height) = (960, 720)
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
        self.font = pygame.font.Font('freesansbold.ttf', 64)
        self.bob = Skater('assets/Skata.json', self)
        self.env = Environment('assets/Basic.json', size)
        self.world = pygame.sprite.Group()
        self.combo_string = ''
        self.combo_surface = None
        self.combo_rect = None

    def update_combo(self, trick):
        # Cannot reuse font surfaces - must destroy and recreate
        if self.combo_surface:
            self.world.remove(self.combo_surface)

        if self.combo_string:
            self.combo_string += ' + ' + trick
        else:
            self.combo_string = trick

        self.combo_surface = self.font.render(self.combo_string, True, green)
        self.combo_rect = self.combo_surface.get_rect()
        self.combo_rect.center = (width / 2, self.combo_rect.height)

    def end_combo(self):
        self.combo_string = ''

    def update_environment(self, next=True):
        self.world.remove(self.env)
        self.world.remove(self.bob)

        next = self.env.get_next() if next else self.env.get_prev()
        if next:
            self.env = Environment(next, size)

        self.world.add(self.env)
        self.world.add(self.bob)


def blend(t, t0, t1):
    return (t - t0) / (t1 - t0)


def intro_tick(state):
    if is_dev_mode:
        state.is_intro_completed = True
        state.world.add(state.env)
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
        textRect.center = (width/2, height/2)
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
        textRect.center = (width/2, height/2)
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
        textRect.center = (1280/2, 720/2)
        state.screen.blit(text, textRect)
    else:
        state.is_intro_completed = True
        state.world.add(state.env)
        state.world.add(state.bob)


def game_tick(state, dt):
    sys.stdout.write('%.1f\r' % dt)

    for event in pygame.event.get():
        if event.type == pygame.QUIT or \
                (event.type == pygame.KEYDOWN and pygame.key.name(event.key) == 'escape'):
            return False
        else:
            # Assuming the player handles all events for now
            state.bob.handle(event)

    state.screen.fill('black')

    if not state.is_intro_completed:
        intro_tick(state)
    else:
        state.world.update(dt, state)
        state.world.draw(state.screen)

        if state.combo_surface:
            state.screen.blit(state.combo_surface, state.combo_rect)

    pygame.display.flip()

    return True


async def main():
    pygame.init()
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Mike Slegeir\'s Gnar Skater')
    clock = pygame.time.Clock()
    state = State(clock, screen)

    t, lt = 0, 0
    while game_tick(state, t - lt):
        clock.tick(60)
        await asyncio.sleep(0)  # Required for webasm via pygbag
        lt = t
        t = pygame.time.get_ticks()

    pygame.quit()


if __name__ == '__main__':
    import code
    #code.interact(local=locals())
    asyncio.run(main())
