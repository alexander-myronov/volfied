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
        self.point = next_point
        # my_line = normalize_line((next_point, self.point))
        for line in generate_lines_contour(contour):
            pass

    def is_hitting_player(self, player_pos):
        return distance(player_pos, self.point) <= self.radius