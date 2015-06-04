import random
import algorithm


class Round(object):
    def __init__(self, w, h, img_back, img_fore, area_required):
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


    def start(self):
        self.active_contour = [(0, 0), (self.dimensions[0], 0), (self.dimensions[0], self.dimensions[1]),
                               (0, self.dimensions[1])]
        self.rectangles = algorithm.split_into_rectangles2(self.active_contour)

        self.point = (random.randrange(0, self.dimensions[0]), self.dimensions[1])
        self.line = []
        self.progress = 0


    def tick(self, controls):

        dx, dy = 0, 0
        if controls['up']:
            dy += -self.speed
        if controls['down']:
            dy += self.speed
        if dy == 0:
            if controls['left']:
                dx += -self.speed
            if controls['right']:
                dx += self.speed

        if dx == 0 and dy == 0:
            return

        new_pos = self.point[0] + dx, self.point[1] + dy
        new_pos = max(new_pos[0], 0), max(new_pos[1], 0)
        new_pos = min(new_pos[0], self.dimensions[0]), min(new_pos[1], self.dimensions[1])

        active = self.belongs_to_active_contour(new_pos)

        inside = self.is_inside_active_contour(new_pos)



        if len(self.line) == 0:
            if not active:
                return
            if self.is_on_active_contour(self.point):
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
                        self.line = []
                    break
            else:
                if not self.append_to_line(new_pos):
                    self.line = []

        self.point = new_pos


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
        status = 0
        if self.progress > self.area_required:
            status = 1
        response = {'progress': self.progress, 'x': self.point[0], 'y': self.point[1], 'line': self.line,
                    'active_rectangles': self.rectangles, 'status': status}
        return response


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








