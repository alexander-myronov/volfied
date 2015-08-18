"""Single round logic"""
import random
from volfied_server.enemy import Enemy, ShapeShiftingEnemy, SpeedingEnemy
from volfied_server.algorithm import generate_lines_contour, generate_lines, \
    is_intersecting_angle, normalize_line, is_intersecting, split_into_rectangles, \
    select_active_contour, project, is_inside_rect_strict, is_point_on_line, is_inside_rect


class Round(object):
    """Class for a single round in game"""

    def __init__(self, w, h, img_back, img_fore, area_required, enemies):
        self.point = (0, 0)
        self.img_back = img_back
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
        """starts the round"""
        self.active_contour = [
            (0, 0),
            (self.dimensions[0], 0),
            (self.dimensions[0], self.dimensions[1]),
            (0, self.dimensions[1])]
        self.rectangles = split_into_rectangles(self.active_contour)

        self.point = (random.randrange(0, self.dimensions[0]), self.dimensions[1])
        self.line = []
        self.progress = 0
        self.shield = 999

        for enemy in self.enemies:
            enemy.spawn((random.randrange(
                0, self.dimensions[0]), random.randrange(1, self.dimensions[1])))


    def tick(self, controls):
        """calculates new round state based on the previous one"""
        self.area_captured = False
        add_score = 0
        if self.is_completed():
            return add_score, False

        self.shield = max(0, self.shield - 1)
        self.on_active = self.is_on_active_contour(self.point)

        for enemy in self.enemies:
            enemy.next_step(self.active_contour)
            if (self.shield == 0 or not self.on_active) and \
                    enemy.is_hitting_player(self.point, self.radius):
                rand_line = random.choice(
                    filter(lambda l: l[0][1] == l[1][1],
                           generate_lines_contour(self.active_contour)))

                self.point = (random.randrange(rand_line[0][0], rand_line[1][0]), rand_line[0][1])

                self.line = []
                return add_score, True
            if len(self.line) > 0:
                enemy_line = enemy.last_point, enemy.point
                for line in generate_lines(self.line):
                    if is_intersecting_angle(enemy_line, line):
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

            last_step = normalize_line((self.point, new_pos))
            for line in generate_lines_contour(self.active_contour):
                if is_intersecting(line, last_step):
                    new_pos = project(new_pos, line)
                    if self.append_to_line(new_pos):
                        old_progress = self.progress
                        try:

                            self.active_contour, self.rectangles, area = \
                                select_active_contour(self.active_contour, self.line)
                        except KeyError:
                            break
                        self.progress = 1 - float(area) / (self.dimensions[0] * self.dimensions[1])
                        add_score += int((self.progress - old_progress) * 1000)
                        killed = [enemy for enemy in self.enemies if
                                  not self.belongs_to_active_contour(enemy.point)]
                        for enemy in killed:
                            self.enemies.remove(enemy)
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
        """ appends a point to line if it is not self-intersecting
        :param new_pos: point to append
        :return: true if point was appended, false if the line is self-intersecting
        """
        assert len(self.line) >= 2

        if (self.line[-2][0] == self.line[-1][0] and new_pos[0] == self.line[-1][0]) or \
                (self.line[-2][1] == self.line[-1][1] and new_pos[1] == self.line[-1][1]):
            new_line = self.line[-2], new_pos
        else:
            new_line = self.line[-1], new_pos

        try:
            norm_new_line = normalize_line(new_line)
        except AssertionError:
            return False
        for line in generate_lines(self.line[:-2]):
            if is_intersecting(norm_new_line, line):
                return False

        if new_line[0] == self.line[-2]:
            self.line[-1] = new_pos
        else:
            self.line.append(new_pos)

        return True


    def get_response(self):
        """
        Prepares a response to player js client
        :return: dictionary with a game state
        """

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
        """
        prepares the initial message to be sent to player
        """
        return {
            'cmd': 'init',
            'dimensions': self.dimensions,
            'radius': self.radius,
            'active_rectangles': self.rectangles
        }


    def belongs_to_active_contour(self, point):
        """
        tests if the point is inside active contour or lies on it
        """
        for rect in self.rectangles:
            if is_inside_rect(point, rect):
                return True
        return False


    def is_inside_active_contour(self, point):
        """
        tests if the point is inside active contour
        """
        for rect in self.rectangles:
            if is_inside_rect_strict(point, rect):
                return True
        return False


    def is_on_active_contour(self, point):
        """
        tests if the point lies on active contour
        """
        for line in generate_lines_contour(self.active_contour):
            if is_point_on_line(point, line):
                return True
        return False

    def is_completed(self):
        """
        :return: true if the required area was captured
        """
        return self.progress >= self.area_required


    @staticmethod
    def get_round(index):
        """
        static method to get rounds
        """
        rounds = [
            Round(100, 100, '', '', 0.8, [
                Enemy(4, 2, ''),
                Enemy(3, 2, ''),
                Enemy(2, 2, ''),
            ]),
            Round(100, 100, '', '', 0.8, [
                Enemy(5, 1, ''),
                Enemy(4, 2, ''),
                Enemy(3, 2, ''),
                Enemy(2, 2, ''),
                SpeedingEnemy(1, 3, ''),
                ShapeShiftingEnemy(7, 1, '')
            ])
        ]
        return rounds[index]








