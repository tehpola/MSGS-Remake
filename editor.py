import pygame
from enum import Enum
import jsonpickle
import tkinter as tk
import tkinter.filedialog as tkfiledialog
from environment import Environment, Surface, SurfaceType


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
    Add = 6
    Remove = 7
    Pavify = 8
    Ledgify = 9
    Hazardify = 10


class EditorGeo(pygame.sprite.Sprite):
    def __init__(self, geo, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geo = geo
        self.rect = geo.rect

    def updated(self):
        # Update the underlying geo
        self.geo.rect = self.rect

        # Redraw the sprite
        self.image = pygame.surface.Surface(self.rect.size).convert_alpha()
        color = pygame.Color(self.geo.get_editor_color())
        color.a = 32
        self.image.fill(color)
        color.a = 128
        pygame.draw.rect(self.image, color, pygame.Rect((0, 0), self.rect.size), 2)

    def get_geo(self):
        return Surface(self.geo.surftype, self.rect)


class State(object):
    def __init__(self, clock: pygame.time.Clock, screen: pygame.Surface):
        self.tk = tk.Tk()
        self.clock = clock
        self.screen = screen
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.env: Environment = None
        self.world = pygame.sprite.Group()
        self.tool_geo: EditorGeo = None
        self.tool_action = Action.Select
        self.tool_offset = pygame.math.Vector2()
        self.tool_string = ''
        self.tool_surface: pygame.Surface = None
        self.tool_rect: pygame.Rect = None
        self.geo = set()

        # Action palette
        self.tools = pygame.sprite.Group()
        self.tool_palette_pos = pygame.math.Vector2(16, 8)
        self.tool_select = self.create_tool('select', Action.Select)
        self.tool_new = self.create_tool('new', Action.Add)
        self.tool_delete = self.create_tool('delete', Action.Remove)
        self.tool_pavement = self.create_tool('pavement', Action.Pavify)
        self.tool_ledge = self.create_tool('ledge', Action.Ledgify)
        self.tool_hazard = self.create_tool('hazard', Action.Hazardify)

        self.tk.withdraw()
        self.load('assets/Cow.json')

    def create_tool(self, name: str, action: Action):
        sprite = pygame.sprite.Sprite()
        sprite.image = pygame.image.load('assets/editor/%s.png' % name).convert_alpha()
        sprite.rect = sprite.image.get_rect()

        sprite.tool_name = name
        sprite.tool_action = action

        sprite.rect.topleft = self.tool_palette_pos
        self.tool_palette_pos.x += sprite.rect.width + 8

        self.tools.add(sprite)


    def load(self, filename):
        self.world.remove(self.geo)
        self.world.remove(self.env)
        self.geo.clear()

        self.env = Environment(filename, size)
        for geo in self.env.geo:
            sprite = EditorGeo(geo)
            sprite.updated()
            self.geo.add(sprite)

        self.world.add(self.env)
        self.world.add(self.geo)

    def _get_tool_under_cursor(self):
        pos = pygame.mouse.get_pos()
        for tool in self.tools:
            if tool.rect.collidepoint(pos):
                return tool

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
        if not geo or type(geo) is not EditorGeo:
            return self.tool_action, pygame.math.Vector2()

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
            if self.tool_action == Action.Move:
                self.tool_geo.rect.center = pos + self.tool_offset
            elif self.tool_action == Action.Resize_SE:
                topleft = pygame.math.Vector2(self.tool_geo.rect.topleft)
                self.tool_geo.rect.size = pos - topleft + self.tool_offset
                self.tool_geo.updated()
            elif self.tool_action == Action.Resize_NE:
                bottomleft = pygame.math.Vector2(self.tool_geo.rect.bottomleft)
                size = pos - bottomleft + self.tool_offset
                size.y = -size.y
                self.tool_geo.rect.size = size
                self.tool_geo.rect.bottomleft = bottomleft
                self.tool_geo.updated()
            elif self.tool_action == Action.Resize_NW:
                bottomright = pygame.math.Vector2(self.tool_geo.rect.bottomright)
                size = pos - bottomright + self.tool_offset
                size *= -1
                self.tool_geo.rect.size = size
                self.tool_geo.rect.bottomright = bottomright
                self.tool_geo.updated()
            elif self.tool_action == Action.Resize_SW:
                topright = pygame.math.Vector2(self.tool_geo.rect.topright)
                size = pos - topright + self.tool_offset
                size.x = -size.x
                self.tool_geo.rect.size = size
                self.tool_geo.rect.topright = topright
                self.tool_geo.updated()
            else:
                tool = self._get_tool_under_cursor()
                geo = self._get_geo_under_cursor()
                if tool:
                    self.update_tool(tool)
                elif geo:
                    self.update_tool(geo)
                else:
                    self.clear_tool()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            tool = self._get_tool_under_cursor()
            if tool:
                self.tool_action = tool.tool_action
            else:
                self.tool_geo = self._get_geo_under_cursor()
                if self.tool_action == Action.Select:
                    self.tool_action, self.tool_offset = self._detect_geo_corner_under_cursor(self.tool_geo)
                elif self.tool_action == Action.Pavify:
                    self.tool_geo.geo.surftype = SurfaceType.Pavement
                    self.tool_geo.updated()
                elif self.tool_action == Action.Ledgify:
                    self.tool_geo.geo.surftype = SurfaceType.Ledge
                    self.tool_geo.updated()
                elif self.tool_action == Action.Hazardify:
                    self.tool_geo.geo.surftype = SurfaceType.Hazard
                    self.tool_geo.updated()
                elif self.tool_action == Action.Remove:
                    self.geo.remove(self.tool_geo)
                    self.world.remove(self.tool_geo)
                    self.tool_geo = None
                elif self.tool_action == Action.Add:
                    pos = pygame.math.Vector2(pygame.mouse.get_pos())
                    self.tool_geo = EditorGeo(Surface(SurfaceType.Pavement, pos, (32, 32)))
                    self.tool_geo.updated()
                    self.geo.add(self.tool_geo)
                    self.world.add(self.tool_geo)

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.tool_action in (Action.Move, Action.Resize_SE, Action.Resize_NW, Action.Resize_NE, Action.Resize_SW):
                self.tool_action = Action.Select
            self.tool_offset.update(0, 0)
            self.tool_geo = None
            self.clear_tool()

        elif event.type == pygame.KEYDOWN:
            key = pygame.key.name(event.key)

            if event.mod & pygame.KMOD_CTRL:
                # Control keys
                if key == 's':
                    print('Saving %s...' % self.env.info['geo'])
                    env_geo = [geo.get_geo() for geo in self.geo]
                    with open(self.env.info['geo'], 'w') as geo_file:
                        geo_file.write(jsonpickle.encode(env_geo))
                elif key == 'o':
                    filename = tkfiledialog.askopenfilename()
                    if filename:
                        print('Loading %s...' % filename)
                        self.load(filename)

        # TODO: Process clicks and hotkeys

    _action_cursors = {
        Action.Select: pygame.SYSTEM_CURSOR_ARROW,
        Action.Move: pygame.SYSTEM_CURSOR_CROSSHAIR,
        Action.Resize_NW: pygame.SYSTEM_CURSOR_SIZENWSE,
        Action.Resize_SE: pygame.SYSTEM_CURSOR_SIZENWSE,
        Action.Resize_SW: pygame.SYSTEM_CURSOR_SIZENESW,
        Action.Resize_NE: pygame.SYSTEM_CURSOR_SIZENESW,
        Action.Add: pygame.SYSTEM_CURSOR_CROSSHAIR,
        Action.Remove: pygame.SYSTEM_CURSOR_NO,
        Action.Pavify: pygame.SYSTEM_CURSOR_HAND,
        Action.Ledgify: pygame.SYSTEM_CURSOR_HAND,
        Action.Hazardify: pygame.SYSTEM_CURSOR_HAND,
    }

    def update_tool(self, geo):
        # Cannot reuse font surfaces - must destroy and recreate
        if self.tool_surface:
            self.world.remove(self.tool_surface)

        if type(geo) is EditorGeo:
            self.tool_string = '%s %s' % (self.tool_action, geo.geo.surftype)
        else:
            self.tool_string = geo.tool_name

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
        if event.type == pygame.QUIT or \
                (event.type == pygame.KEYDOWN and pygame.key.name(event.key) == 'escape'):
            return False
        else:
            state.handle(event)

    state.screen.fill('black')

    state.world.update(dt, state)
    state.world.draw(state.screen)

    state.tools.update(dt, state)
    state.tools.draw(state.screen)

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
