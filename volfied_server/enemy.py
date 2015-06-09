import random
import math
from algorithm import *
from algorithm import distance


class Enemy(object):
    def __init__(self, radius, speed, image):
        self.radius = radius
        self.image = image
        self.point = 0, 0
        self.velocity = 0
        self.base_speed = speed
        self.last_point = 0, 0

    def spawn(self, point):
        self.point = point
        r = random.uniform(0, 2 * math.pi)
        self.velocity = math.cos(r), math.sin(r)

    def next_step(self, contour):
        next_point = self.point[0] + self.velocity[0] * self.base_speed, \
                     self.point[1] + self.velocity[1] * self.base_speed

        # my_line = (next_point, self.point)

        my_vec = next_point[0] - self.point[0], next_point[1] - self.point[1]
        my_vec_length = math.sqrt(my_vec[0] ** 2 + my_vec[1] ** 2)
        my_vec_desired_length = my_vec_length + self.radius
        my_vec = my_vec[0] * my_vec_desired_length / my_vec_length, my_vec[1] * my_vec_desired_length / my_vec_length
        my_line = self.point, (self.point[0] + my_vec[0], self.point[1] + my_vec[1])

        for line in generate_lines_contour(contour):
            if is_intersecting_angle(my_line, line):
                if line[0][0] == line[1][0]:
                    self.velocity = -self.velocity[0], self.velocity[1]
                elif line[0][1] == line[1][1]:
                    self.velocity = self.velocity[0], -self.velocity[1]
                else:
                    return
                break
        else:
            self.last_point, self.point = self.point, next_point

    def is_hitting_player(self, player_pos, player_radius):
        return distance(player_pos, self.point) <= self.radius + player_radius


class ShapeShiftingEnemy(Enemy):
    def __init__(self, radius, speed, image):
        super(ShapeShiftingEnemy, self).__init__(radius, speed, image)
        self.base_radius = radius
        self.grow = False

    def next_step(self, contour):
        super(ShapeShiftingEnemy, self).next_step(contour)
        if self.grow:
            if self.radius < self.base_radius:
                self.radius += 1
            else:
                self.grow = False
        else:
            if self.radius > 1:
                self.radius -= 1
            else:
                self.grow = True

    pass


class SpeedingEnemy(Enemy):
    def __init__(self, radius, speed, image):
        super(SpeedingEnemy, self).__init__(radius, speed, image)
        self.accelerate = False
        self.max_speed = self.base_speed

    def next_step(self, contour):
        super(SpeedingEnemy, self).next_step(contour)
        if self.accelerate:
            if self.base_speed < self.max_speed:
                self.base_speed += 0.1
            else:
                self.accelerate = False
        else:
            if self.base_speed > 1:
                self.base_speed -= 0.1
            else:
                self.accelerate = True

    pass