import random
import algorithm
from volfied_server.enemy import Enemy, ShapeShiftingEnemy, SpeedingEnemy


class Round(object):
    def __init__(self, w, h, img_back, img_fore, area_required, enemies):
        self.point = (0, 0)
        self.img_back = img_back,
        self.img_fore = img_fore
        self.active_contour = []
        self.rectangles = []
        self.line = []
        self.dimensions = (w, h)
        self.area_required = area_required
        self.progress = 0
        self.speed = 3
        self.enemies = list(enemies)
        self.dead = False
        self.shield = 0
        self.on_active = True
        self.radius = 2
        self.area_captured = False


    def start(self):
        self.active_contour = [(0, 0), (self.dimensions[0], 0), (self.dimensions[0], self.dimensions[1]),
                               (0, self.dimensions[1])]
        self.rectangles = algorithm.split_into_rectangles2(self.active_contour)

        self.point = (random.randrange(0, self.dimensions[0]), self.dimensions[1])
        self.line = []
        self.progress = 0
        self.shield = 999

        for e in self.enemies:
            e.spawn((random.randrange(0, self.dimensions[0]), random.randrange(1, self.dimensions[1])))


    def tick(self, controls):
        self.area_captured = False
        add_score = 0
        if self.is_completed():
            return add_score, False

        self.shield = max(0, self.shield - 1)
        self.on_active = self.is_on_active_contour(self.point)

        for e in self.enemies:
            e.next_step(self.active_contour)
            if (self.shield == 0 or not self.on_active) and e.is_hitting_player(self.point, self.radius):
                rand_line = random.choice(
                    filter(lambda l: l[0][1] == l[1][1], algorithm.generate_lines_contour(self.active_contour)))

                self.point = (random.randrange(rand_line[0][0], rand_line[1][0]), rand_line[0][1])

                self.line = []
                return add_score, True
            if len(self.line) > 0:
                enemy_line = e.last_point, e.point
                for l in algorithm.generate_lines(self.line):
                    if algorithm.is_intersecting_angle(enemy_line, l):
                        self.line = []
                        break

        dx, dy = 0, 0
        if controls[0] == 1:
            dy += -self.speed
        if controls[1] == 1:
            dy += self.speed
        if dy == 0:
            if controls[2] == 1:
                dx += -self.speed
            if controls[3] == 1:
                dx += self.speed

        if dx == 0 and dy == 0:
            return add_score, False

        new_pos = self.point[0] + dx, self.point[1] + dy
        new_pos = max(new_pos[0], 0), max(new_pos[1], 0)
        new_pos = min(new_pos[0], self.dimensions[0]), min(new_pos[1], self.dimensions[1])

        active = self.belongs_to_active_contour(new_pos)

        if len(self.line) == 0:
            if not active:
                return add_score, False
            if self.on_active and not self.is_on_active_contour(new_pos):
                self.line = [self.point, new_pos]
        else:

            last_step = algorithm.normalize_line((self.point, new_pos))
            for l in algorithm.generate_lines_contour(self.active_contour):
                if algorithm.is_intersecting(l, last_step):
                    new_pos = algorithm.project(new_pos, l)
                    if self.append_to_line(new_pos):
                        try:

                            self.active_contour, self.rectangles, area = \
                                algorithm.select_active_contour(self.active_contour, self.line)
                        except KeyError:
                            break
                        self.progress = 1 - float(area) / (self.dimensions[0] * self.dimensions[1])
                        killed = [e for e in self.enemies if not self.belongs_to_active_contour(e.point)]
                        for e in killed:
                            self.enemies.remove(e)
                            add_score += 100
                        self.line = []
                        self.area_captured = True
                    break
            else:
                if not self.append_to_line(new_pos):
                    self.line = []

        self.point = new_pos
        return add_score, False


    def append_to_line(self, new_pos):
        assert len(self.line) >= 2

        if (self.line[-2][0] == self.line[-1][0] and new_pos[0] == self.line[-1][0]) or \
                (self.line[-2][1] == self.line[-1][1] and new_pos[1] == self.line[-1][1]):
            new_line = self.line[-2], new_pos
        else:
            new_line = self.line[-1], new_pos

        try:
            norm_new_line = algorithm.normalize_line(new_line)
        except AssertionError:
            return False
        for line in algorithm.generate_lines(self.line[:-2]):
            if algorithm.is_intersecting(norm_new_line, line):
                return False

        if new_line[0] == self.line[-2]:
            self.line[-1] = new_pos
        else:
            self.line.append(new_pos)

        return True


    def get_response(self):

        response = {
            'progress': self.progress,
            'x': self.point[0],
            'y': self.point[1],
            'line': self.line,
            'on_active': self.on_active,
            'shield': self.shield,
            'enemies': [
                {
                    'x': e.point[0],
                    'y': e.point[1],
                    'radius': e.radius,
                    'image': e.image
                } for e in self.enemies
            ]
        }
        if self.area_captured:
            response['active_rectangles'] = self.rectangles
        return response

    def get_init_message(self):
        return {
            'cmd': 'init',
            'dimensions': self.dimensions,
            'radius': self.radius,
            'active_rectangles': self.rectangles
        }


    def belongs_to_active_contour(self, point):
        for rect in self.rectangles:
            if algorithm.is_inside_rect(point, rect):
                return True
        return False


    def is_inside_active_contour(self, point):
        for rect in self.rectangles:
            if algorithm.is_inside_rect_strict(point, rect):
                return True
        return False


    def is_on_active_contour(self, point):
        for line in algorithm.generate_lines_contour(self.active_contour):
            if algorithm.is_point_on_line(point, line):
                return True
        return False

    def is_completed(self):
        return self.progress >= self.area_required


    @staticmethod
    def get_round(index):
        rounds = [
            Round(100, 100, '', '', 0.8, [
                Enemy(5, 1, ''),
                Enemy(4, 2, ''),
                Enemy(3, 2, ''),
                Enemy(2, 2, ''),
                SpeedingEnemy(1, 3, ''),
                ShapeShiftingEnemy(20, 1, '')
            ])
        ]
        return rounds[index]








