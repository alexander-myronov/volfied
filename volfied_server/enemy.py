import random
import math
from algorithm import *
from algorithm import distance


class Enemy(object):
    def __init__(self, radius, image, speed):
        self.radius = radius
        self.image = image
        self.point = 0, 0
        self.velocity = 0
        self.base_speed = speed

    def spawn(self, point):
        self.point = point
        r = random.uniform(0, 2 * math.pi)
        self.velocity = math.cos(r) * self.base_speed, math.sin(r) * self.base_speed

    def next_step(self, contour):
        next_point = self.point[0] + self.velocity[0], self.point[1] + self.velocity[1]

        # my_line = normalize_line((next_point, self.point))
        for line in generate_lines_contour(contour):
            contour1 = [self.point, next_point, line[0]]
            contour2 = [self.point, next_point, line[1]]

            contour3 = [line[0], line[1], self.point]
            contour4 = [line[0], line[1], next_point]

            cw1 = is_strictly_clockwise(contour1)
            cw2 = is_strictly_clockwise(contour2)
            cw3 = is_strictly_clockwise(contour3)
            cw4 = is_strictly_clockwise(contour4)

            if cw1 != cw2 and cw3 != cw4:
                if line[0][0] == line[1][0]:
                    self.velocity = -self.velocity[0], self.velocity[1]
                elif line[0][1] == line[1][1]:
                    self.velocity = self.velocity[0], -self.velocity[1]
                else:
                    return
                break
        else:
            self.point = next_point

    def is_hitting_player(self, player_pos):
        return distance(player_pos, self.point) <= self.radius