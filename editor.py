import pygame
from enum import Enum
import tkinter as tk
from environment import Environment


size = (width, height) = (960, 720)
nothing = pygame.Color(0, 0, 0, 0)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)


class Action(Enum):
    Select = 0
    Move = 1
    Resize_NE = 2
    Resize_SE = 3
    Resize_SW = 4
    Resize_NW = 5


class EditorGeo(pygame.sprite.Sprite):
    def __init__(self, geo, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geo = geo
        self.rect = geo.rect

    def redraw(self):
        self.image = pygame.surface.Surface(self.rect.size).convert_alpha()
        color = pygame.Color(self.geo.get_editor_color())
        color.a = 32
        self.image.fill(color)
        color.a = 128
        pygame.draw.rect(self.image, color, pygame.Rect((0, 0), self.rect.size), 2)


class State(object):
    def __init__(self, clock: pygame.time.Clock, screen):
        self.tk = tk.Tk()
        self.clock = clock
        self.screen = screen
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.env = None
        self.world = pygame.sprite.Group()
        self.tool_geo = None
        self.tool_action = Action.Select
        self.tool_offset = pygame.math.Vector2()
        self.tool_string = ''
        self.tool_surface = None
        self.tool_rect = None
        self.geo = set()

        self.tk.withdraw()
        self.load('assets/Cow.json')

    def load(self, filename):
        self.world.remove(self.geo)
        self.world.remove(self.env)
        self.geo.clear()

        self.env = Environment(filename, size)
        for geo in self.env.geo:
            sprite = EditorGeo(geo)
            sprite.redraw()
            self.geo.add(sprite)

        self.world.add(self.env)
        self.world.add(self.geo)

    def _get_geo_under_cursor(self):
        pos = pygame.mouse.get_pos()
        for geo in self.geo:
            if geo.rect.collidepoint(pos):
                return geo

    _corner_threshold = 64

    def _check_corner(self, pos, corner, action):
        corner = pygame.math.Vector2(corner)
        distsq = corner.distance_squared_to(pos)
        if distsq < self._corner_threshold:
            return (action, corner - pos)
        else:
            return None

    def _detect_geo_corner_under_cursor(self, geo):
        if not geo:
            return Action.Select, pygame.math.Vector2()

        pos = pygame.mouse.get_pos()
        rect = geo.rect

        result = self._check_corner(pos, rect.topleft, Action.Resize_NW)
        if result:
            return result

        result = self._check_corner(pos, rect.topright, Action.Resize_NE)
        if result:
            return result

        result = self._check_corner(pos, rect.bottomright, Action.Resize_SE)
        if result:
            return result

        result = self._check_corner(pos, rect.bottomleft, Action.Resize_SW)
        if result:
            return result

        center = pygame.math.Vector2(rect.center)
        return Action.Move, center - pos

    def handle(self, event):
        if event.type == pygame.MOUSEMOTION:
            pos = pygame.math.Vector2(pygame.mouse.get_pos())
            if self.tool_action == Action.Select:
                geo = self._get_geo_under_cursor()
                if geo:
                    self.update_tool(geo)
                else:
                    self.clear_tool()
            elif self.tool_action == Action.Move:
                self.tool_geo.rect.center = pos + self.tool_offset
            elif self.tool_action == Action.Resize_SE:
                topleft = pygame.math.Vector2(self.tool_geo.rect.topleft)
                self.tool_geo.rect.size = pos - topleft + self.tool_offset
                self.tool_geo.redraw()
            elif self.tool_action == Action.Resize_NE:
                bottomleft = pygame.math.Vector2(self.tool_geo.rect.bottomleft)
                size = pos - bottomleft + self.tool_offset
                size.y = -size.y
                self.tool_geo.rect.size = size
                self.tool_geo.rect.bottomleft = bottomleft
                self.tool_geo.redraw()
            elif self.tool_action == Action.Resize_NW:
                bottomright = pygame.math.Vector2(self.tool_geo.rect.bottomright)
                size = pos - bottomright + self.tool_offset
                size *= -1
                self.tool_geo.rect.size = size
                self.tool_geo.rect.bottomright = bottomright
                self.tool_geo.redraw()
            elif self.tool_action == Action.Resize_SW:
                topright = pygame.math.Vector2(self.tool_geo.rect.topright)
                size = pos - topright + self.tool_offset
                size.x = -size.x
                self.tool_geo.rect.size = size
                self.tool_geo.rect.topright = topright
                self.tool_geo.redraw()


        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.tool_geo = self._get_geo_under_cursor()
            self.tool_action, self.tool_offset = self._detect_geo_corner_under_cursor(self.tool_geo)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.tool_action = Action.Select
            self.tool_offset.update(0, 0)
            self.tool_geo = None
            self.clear_tool()

        # TODO: Process clicks and hotkeys

    _action_cursors = {
        Action.Select: pygame.SYSTEM_CURSOR_ARROW,
        Action.Move: pygame.SYSTEM_CURSOR_CROSSHAIR,
        Action.Resize_NW: pygame.SYSTEM_CURSOR_SIZENWSE,
        Action.Resize_SE: pygame.SYSTEM_CURSOR_SIZENWSE,
        Action.Resize_SW: pygame.SYSTEM_CURSOR_SIZENESW,
        Action.Resize_NE: pygame.SYSTEM_CURSOR_SIZENESW,
    }

    def update_tool(self, geo):
        # Cannot reuse font surfaces - must destroy and recreate
        if self.tool_surface:
            self.world.remove(self.tool_surface)

        self.tool_string = str(geo.geo.surftype)

        self.tool_surface = self.font.render(self.tool_string, True, green.lerp(red, 0.5))
        self.tool_rect = self.tool_surface.get_rect()
        self.tool_rect.center = (width / 2, self.tool_rect.height)

        action, _ = self._detect_geo_corner_under_cursor(geo)
        pygame.mouse.set_cursor(self._action_cursors[action])

    def clear_tool(self):
        self.tool_string = ''
        self.world.remove(self.tool_surface)
        self.tool_surface = None

        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


def blend(t, t0, t1):
    return (t - t0) / (t1 - t0)


def editor_tick(state, dt):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        else:
            state.handle(event)

    state.screen.fill('black')

    state.world.update(dt, state)
    state.world.draw(state.screen)

    if state.tool_surface:
        state.screen.blit(state.tool_surface, state.tool_rect)

    pygame.display.flip()

    return True


def main():
    pygame.init()
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Mike Slegeir\'s Gnar Editor')
    clock = pygame.time.Clock()
    state = State(clock, screen)

    t, lt = 0, 0
    while editor_tick(state, t - lt):
        clock.tick(60)
        lt = t
        t = pygame.time.get_ticks()

    pygame.quit()


if __name__ == '__main__':
    import code
    #code.interact(local=locals())
    main()
