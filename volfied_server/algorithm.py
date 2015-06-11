"""
core functions for the volfied game
point - tuple of 2 numbers
line - tuple of 2 points
rectangle - tuple of 2 points (left top and right bottom)
path - list of points (and, conceptually, of lines)
contour - path, which is closed
"""
from itertools import chain
from math import sqrt


def generate_lines_contour(contour):
    """
    generate subsequent lines from a list of points and the line from last to first,
    thus closing the contour
    point sequence must be orthogonal
    :param points: [(0,0), (10,0), (10,10)]
    :return: [((0,0),(10,0)), ((10,0),(10,10)), ((10,10),(0,10))]
    """
    for i, (x1, y1) in enumerate(contour):
        x2, y2 = contour[(i + 1) % len(contour)]

        if x1 == x2:
            yield (x1, min(y1, y2)), (x1, max(y1, y2))
        elif y1 == y2:
            yield ((min(x1, x2), y1), (max(x1, x2), y1))
            # else:
            # raise AssertionError


def generate_lines(points):
    """
    generate subsequent lines from a list of points
    point sequence must be orthogonal
    :param points: [(0,0), (10,0), (10,10)]
    :return: [((0,0),(10,0)), ((10,0),(10,10))]
    """
    for i, (x1, y1) in enumerate(points[:-1]):
        x2, y2 = points[i + 1]

        if x1 == x2:
            yield (x1, min(y1, y2)), (x1, max(y1, y2))
        elif y1 == y2:
            yield ((min(x1, x2), y1), (max(x1, x2), y1))
        else:
            raise AssertionError


def is_point_on_line(point, line):
    """
    tests if point is on line
    line must be orthogonal
    """
    return line[0][0] <= point[0] <= line[1][0] and line[0][1] <= point[1] <= line[1][1]


def is_clockwise(contour):
    """
    check if a contour is "mostly" clockwise
    it may be concave
    """
    s = 0
    for i, (x1, y1) in enumerate(contour):
        x2, y2 = contour[(i + 1) % len(contour)]
        s += (x2 - x1) * (y2 + y1)
    if s == 0:
        return False
    return s / abs(s) == -1


def is_strictly_clockwise(contour):
    """
    checks if contour is strictly clockwise: clockwise and convex
    """
    for i, (x1, y1) in enumerate(contour[:-2]):
        x2, y2 = contour[(i + 1) % len(contour)]
        x3, y3 = contour[(i + 2) % len(contour)]

        v1 = x2 - x1, y2 - y1
        v2 = x3 - x2, y3 - y2

        val = v1[0] * v2[1] - v1[1] * v2[0]
        if val < 0:
            return False

    return True


def split_contour(main_contour, split_path):
    """
    splits a contour by a split path into direct and reverse contours
    """
    first = split_path[0]
    last = split_path[-1]

    i_first = -1
    i_last = -1

    for i, line in enumerate(generate_lines_contour(main_contour)):
        if is_point_on_line(first, line):
            i_first = i
        if is_point_on_line(last, line):
            i_last = i

    start, end = (i_first + 1) % len(main_contour), (i_last + 1) % len(main_contour)
    cw = is_clockwise(split_path)

    direct_part = []
    if start != end or not cw:
        i = end
        while i != start or len(direct_part) == 0:
            direct_part.append(main_contour[i])
            i = (i + 1) % len(main_contour)

    reverse_part = []
    if start != end or cw:
        i = start
        while i != end or len(reverse_part) == 0:
            reverse_part.append(main_contour[i])
            i = (i + 1) % len(main_contour)

    to_remove = list(filter(lambda v: v in direct_part, split_path))

    direct_path = list(chain(split_path, direct_part))
    for i in to_remove:
        direct_path.remove(i)
    smooth_path(direct_path)

    to_remove = list(filter(lambda v: v in reverse_part, split_path))
    reverse_path = list(chain(reverse_part, split_path[::-1]))
    for i in to_remove:
        reverse_path.remove(i)
    smooth_path(reverse_path)

    return direct_path, reverse_path


def smooth_path(path):
    """
    removes any non-orthogonal points on a path and joins lines if possible
    """
    i = 0
    c = 0
    while c < len(path):
        p0 = path[i % len(path)]
        p1 = path[(i + 1) % len(path)]
        p2 = path[(i + 2) % len(path)]

        if p0[0] != p1[0] and p0[1] != p1[1]:
            if abs(p0[0] - p1[0]) < abs(p0[1] - p1[1]):
                p1 = p0[0], p1[1]
            else:
                p1 = p1[0], p0[1]

        elif p0[0] == p1[0] == p2[0] or p0[1] == p1[1] == p2[1]:
            path.remove(p1)
            c = 0
        else:
            c += 1
            i = (i + 1) % len(path)


def project(point, line):
    """
    projects a point onto line
    line must be orthogonal
    """
    assert line[0][0] == line[1][0] or line[0][1] == line[1][1]
    if line[0][0] == line[1][0]:
        return line[0][0], point[1]
    else:
        return point[0], line[0][1]


def is_intersecting_contour(line, contour):
    """
    check if a line is intersecting a contour
    """
    line = normalize_line(line)
    for l in generate_lines_contour(contour):
        if is_intersecting_strict(l, line):
            return True
    return False


def normalize_line(line):
    """
    lesser x before greater x, same with y
    line must be orthogonal
    """
    assert line[0][0] == line[1][0] or line[0][1] == line[1][1]
    return (min(line[0][0], line[1][0]), min(line[0][1], line[1][1])), \
           (max(line[0][0], line[1][0]), max(line[0][1], line[1][1]))


def is_intersecting_strict(line1, line2):
    """
    check if 2 orthogonal lines are strictly intersecting
    if an end of line 1 lies on line 2 - this will return False (not strict intersection)
    """
    # line1 = normalize_line(line1)
    # line2 = normalize_line(line2)

    if length(line1) < length(line2):
        line1, line2 = line2, line1

    if line1[0][0] == line1[1][0]:  # vertical
        if line2[0][0] == line2[1][0]:  # vertical
            return line1[0][0] == line2[0][0] and (
                line1[0][1] < line2[0][1] < line1[1][1] or line1[0][1] < line2[1][1] < line1[1][1])
        else:  # horizontal
            return line2[0][0] < line1[0][0] < line2[1][0] and \
                   line1[0][1] < line2[0][1] < line1[1][1]
    else:  # horizontal
        if line2[0][1] == line2[1][1]:  # horizontal
            return line1[0][1] == line2[0][1] and (
                line1[0][0] < line2[0][0] < line1[1][0] or line1[0][0] < line2[1][0] < line1[1][0])
        else:  # vertical
            return line2[0][1] < line1[0][1] < line2[1][1] and \
                   line1[0][0] < line2[0][0] < line1[1][0]


def is_intersecting(line1, line2):
    """
    check if 2 orthogonal lines are strictly intersecting
    if an end of line 1 lies on line 2 - this will return True
    """
    # line1 = normalize_line(line1)
    # line2 = normalize_line(line2)

    if length(line1) < length(line2):
        line1, line2 = line2, line1

    if line1[0][0] == line1[1][0]:  # vertical
        if line2[0][0] == line2[1][0]:  # vertical
            return line1[0][0] == line2[0][0] and (
                line1[0][1] <= line2[0][1] <= line1[1][1] or \
                line1[0][1] <= line2[1][1] <= line1[1][1])
        else:  # horizontal
            return line2[0][0] <= line1[0][0] <= line2[1][0] and \
                   line1[0][1] <= line2[0][1] <= line1[1][1]
    else:  # horizontal
        if line2[0][1] == line2[1][1]:  # horizontal
            return line1[0][1] == line2[0][1] and (
                line1[0][0] <= line2[0][0] <= line1[1][0] or \
                line1[0][0] <= line2[1][0] <= line1[1][0])
        else:  # vertical
            return line2[0][1] <= line1[0][1] <= line2[1][1] and \
                   line1[0][0] <= line2[0][0] <= line1[1][0]


def is_intersecting_angle(line1, line2):
    """
    check if 2 lines are intersecting
    assume that they are not parallel
    if they are parallel and 1 line belong to another - will return False
    """
    contour1 = [line1[0], line1[1], line2[0]]
    contour2 = [line1[0], line1[1], line2[1]]

    contour3 = [line2[0], line2[1], line1[0]]
    contour4 = [line2[0], line2[1], line1[1]]

    cw1 = is_strictly_clockwise(contour1)
    cw2 = is_strictly_clockwise(contour2)
    cw3 = is_strictly_clockwise(contour3)
    cw4 = is_strictly_clockwise(contour4)

    return cw1 != cw2 and cw3 != cw4


def length(line):
    """
    length of an orthogonal line
    """
    # assert line[0][0] == line[1][0] or line[0][1] == line[1][1]
    dx, dy = abs(line[0][0] - line[1][0]), abs(line[0][1] - line[1][1])
    assert dx == 0 or dy == 0
    return max(dx, dy)



def split_into_rectangles(contour):
    """
    split a contour into rectangles
    """
    rectangles = []
    contour = list(contour)
    i = 0
    while len(contour) >= 4:
        p1 = contour[i % len(contour)]
        p2 = contour[(i + 1) % len(contour)]
        p3 = contour[(i + 2) % len(contour)]
        p4 = contour[(i + 3) % len(contour)]

        points = [p1, p2, p3, p4]

        if not is_strictly_clockwise(points):
            i = (i + 1) % len(contour)
            continue

        try:
            assert p2[0] == p3[0] or p2[1] == p3[1]
            l12 = length((p1, p2))
            l34 = length((p3, p4))
        except AssertionError:
            print (p1, p2, p3, p4)
            return

        if l12 == l34:
            new_segment = []
            split_line = p1, p4
        elif l12 < l34:
            new_point = project(p1, (p3, p4))
            split_line = p1, new_point
            new_segment = [new_point, p4]
        else:
            new_point = project(p4, (p1, p2))
            split_line = new_point, p4
            new_segment = [p1, new_point]

        if is_intersecting_contour(split_line, contour):
            i = (i + 1) % len(contour)
            continue

        rect_points = list(chain(split_line, points[1:3]))
        x_list = [p[0] for p in rect_points]
        y_list = [p[1] for p in rect_points]
        left_top = min(x_list), min(y_list)
        right_bottom = max(x_list), max(y_list)
        rectangles.append((left_top, right_bottom))

        l = len(contour)

        for p in points:
            contour.remove(p)

        for j, p in enumerate(new_segment):
            contour.insert((i + j) % l, p)

    return rectangles


def area(rectangles):
    """
    calculate the area of a list of rectangles
    """
    try:
        return reduce(lambda s, r: (r[1][0] - r[0][0]) * (r[1][1] - r[0][1]) + s, rectangles, 0)
    except TypeError, e:
        return 0


def is_inside_rect(point, rect):
    """
    check if point is inside rectangle or on its boundary
    """
    return rect[0][0] <= point[0] <= rect[1][0] and rect[0][1] <= point[1] <= rect[1][1]


def is_inside_rect_strict(point, rect):
    """
    check if point is inside rectangle (but not on its boundary)
    """
    return rect[0][0] < point[0] < rect[1][0] and rect[0][1] < point[1] < rect[1][1]


def select_active_contour(contour, split_path):
    """
    split the contour by path and select a bigger one as new contour
    core of the Volfied game
    """
    direct_path, reverse_path = split_contour(contour, split_path)

    rectangles_direct = split_into_rectangles(direct_path)
    rectangles_reverse = split_into_rectangles(reverse_path)

    sum_direct = area(rectangles_direct)
    sum_reverse = area(rectangles_reverse)

    if sum_direct >= sum_reverse:
        return direct_path, rectangles_direct, sum_direct
    else:
        return reverse_path, rectangles_reverse, sum_reverse


def distance(p1, p2):
    """
    Euclidean distance
    """
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
