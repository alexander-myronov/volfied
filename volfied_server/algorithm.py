import itertools


def generate_lines_contour(contour):
    for i, (x1, y1) in enumerate(contour):
        x2, y2 = contour[(i + 1) % len(contour)]

        if x1 == x2:
            yield (x1, min(y1, y2)), (x1, max(y1, y2))
        elif y1 == y2:
            yield ((min(x1, x2), y1), (max(x1, x2), y1))
        else:
            raise AssertionError


def generate_lines(points):
    for i, (x1, y1) in enumerate(points[:-1]):
        x2, y2 = points[i + 1]

        if x1 == x2:
            yield (x1, min(y1, y2)), (x1, max(y1, y2))
        elif y1 == y2:
            yield ((min(x1, x2), y1), (max(x1, x2), y1))
        else:
            raise AssertionError


def is_point_on_line(point, line):
    return line[0][0] <= point[0] <= line[1][0] and line[0][1] <= point[1] <= line[1][1]


def is_clockwise(contour):
    sum = 0
    for i, (x1, y1) in enumerate(contour):
        x2, y2 = contour[(i + 1) % len(contour)]
        sum += (x2 - x1) * (y2 + y1)
    if sum == 0:
        return False
    return sum / abs(sum) == -1


def is_strictly_clockwise(contour):
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

    direct_path = list(itertools.chain(split_path, direct_part))
    for i in to_remove:
        direct_path.remove(i)
    smooth_path(direct_path)

    to_remove = list(filter(lambda v: v in reverse_part, split_path))
    reverse_path = list(itertools.chain(reverse_part, split_path[::-1]))
    for i in to_remove:
        reverse_path.remove(i)
    smooth_path(reverse_path)

    return direct_path, reverse_path


def smooth_path(path):
    i = 0
    c = 0
    while c < len(path):
        p0 = path[i % len(path)]
        p1 = path[(i + 1) % len(path)]
        p2 = path[(i + 2) % len(path)]

        if p0[0] == p1[0] == p2[0] or p0[1] == p1[1] == p2[1]:
            path.remove(p1)
            c = 0
        else:
            c += 1
            i = (i + 1) % len(path)


def split_into_rectangles(contour):
    # processed_points_set = set()
    contour = list(contour)
    rectangles = []
    while len(contour) >= 4:

        try:
            min_x = min(contour, key=lambda p: p[0])
        except ValueError:
            break

        min_index = contour.index(min_x)

        cw_neighbour = contour[(min_index + 1) % len(contour)]
        ccw_neighbour = contour[(min_index - 1) % len(contour)]

        if cw_neighbour[0] == min_x[0]:
            neighbour = cw_neighbour
            neighbour_index = (min_index + 1) % len(contour)

            point3_index = (min_index + 2) % len(contour)
            point4_index = (min_index - 1) % len(contour)

        elif ccw_neighbour[0] == min_x[0]:
            neighbour = ccw_neighbour
            neighbour_index = (min_index - 1) % len(contour)

            point3_index = (min_index - 2) % len(contour)
            point4_index = (min_index + 1) % len(contour)
        else:
            contour.pop(min_index)
            continue

        point3 = contour[point3_index]
        point4 = contour[point4_index]

        if point3[0] <= point4[0]:
            new_point = point3[0], point4[1]
            if cw_neighbour == neighbour:
                rect = neighbour, new_point
            else:
                rect = min_x, point3
            contour[min_index] = new_point
            contour.pop(neighbour_index)
            contour.pop(contour.index(point3))
        else:
            new_point = point4[0], point3[1]
            if cw_neighbour == neighbour:
                rect = neighbour, point4
            else:
                rect = min_x, new_point
            contour[neighbour_index] = new_point
            contour.pop(min_index)
            contour.pop(contour.index(point4))

        rectangles.append(rect)
    return rectangles


def project(point, line):
    assert line[0][0] == line[1][0] or line[0][1] == line[1][1]
    if line[0][0] == line[1][0]:
        return line[0][0], point[1]
    else:
        return point[0], line[0][1]


def is_intersecting_contour(line, contour):
    line = normalize_line(line)
    for l in generate_lines_contour(contour):
        if is_intersecting_strict(l, line):
            return True
    return False


def normalize_line(line):
    assert line[0][0] == line[1][0] or line[0][1] == line[1][1]
    return (min(line[0][0], line[1][0]), min(line[0][1], line[1][1])), \
           (max(line[0][0], line[1][0]), max(line[0][1], line[1][1]))


def is_intersecting_strict(line1, line2):
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
    # line1 = normalize_line(line1)
    # line2 = normalize_line(line2)

    if length(line1) < length(line2):
        line1, line2 = line2, line1

    if line1[0][0] == line1[1][0]:  # vertical
        if line2[0][0] == line2[1][0]:  # vertical
            return line1[0][0] == line2[0][0] and (
                line1[0][1] <= line2[0][1] <= line1[1][1] or line1[0][1] <= line2[1][1] <= line1[1][1])
        else:  # horizontal
            return line2[0][0] <= line1[0][0] <= line2[1][0] and \
                   line1[0][1] <= line2[0][1] <= line1[1][1]
    else:  # horizontal
        if line2[0][1] == line2[1][1]:  # horizontal
            return line1[0][1] == line2[0][1] and (
                line1[0][0] <= line2[0][0] <= line1[1][0] or line1[0][0] <= line2[1][0] <= line1[1][0])
        else:  # vertical
            return line2[0][1] <= line1[0][1] <= line2[1][1] and \
                   line1[0][0] <= line2[0][0] <= line1[1][0]


def length(line):
    # assert line[0][0] == line[1][0] or line[0][1] == line[1][1]
    dx, dy = abs(line[0][0] - line[1][0]), abs(line[0][1] - line[1][1])
    assert dx == 0 or dy == 0
    return max(dx, dy)


def split_into_rectangles2(contour):
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

        assert p2[0] == p3[0] or p2[1] == p3[1]

        try:
            l12 = length((p1, p2))
            l34 = length((p3, p4))
        except AssertionError:
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

        rect_points = list(itertools.chain(split_line, points[1:3]))
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
    return reduce(lambda s, r: (r[1][0] - r[0][0]) * (r[1][1] - r[0][1]) + s, rectangles, 0)


def is_inside_rect(point, rect):
    return rect[0][0] <= point[0] <= rect[1][0] and rect[0][1] <= point[1] <= rect[1][1]


def is_inside_rect_strict(point, rect):
    return rect[0][0] < point[0] < rect[1][0] and rect[0][1] < point[1] < rect[1][1]


def select_active_contour(contour, split_path):
    direct_path, reverse_path = split_contour(contour, split_path)

    rectangles_direct = split_into_rectangles2(direct_path)
    rectangles_reverse = split_into_rectangles2(reverse_path)

    sum_direct = area(rectangles_direct)
    sum_reverse = area(rectangles_reverse)

    if sum_direct >= sum_reverse:
        return direct_path, rectangles_direct, sum_direct
    else:
        return reverse_path, rectangles_reverse, sum_reverse


if __name__ == '__main__':

    from Tkinter import *

    master = Tk()

    canvas_size = 500.0, 500.0
    world_size = 10.0, 10.0


    def to_screen(x, y):
        return int((x / world_size[0]) * canvas_size[0]) + 5, int((y / world_size[1]) * canvas_size[1]) + 5


    w = Canvas(master, width=canvas_size[0] + 50, height=canvas_size[1] + 50)
    w.pack()


    def draw_contour(contour, join=True, color="black"):
        points = map(lambda p: to_screen(*p), contour)
        if join:
            points = itertools.chain(points, [to_screen(*contour[0])])

        w.create_line(*points, fill=color, dash=(2, 4), width=5)

    main_contour = [(0, 0), (10, 0), (10, 10), (8, 10), (8, 8), (2, 8), (2, 10), (0, 10)]

    split_path = [(8, 8), (8, 5), (5, 5), (5, 8)]

    # split_path = [(0, 3), (1, 3), (1, 4), (5, 4), (5, 10)]
    # split_path = [(2, 0), (2, 2), (5, 2), (5, 0)]

    # split_path = [(10, 2), (8, 2), (8, 5), (10, 5)]

    # split_path.reverse()

    direct_path, reverse_path = split_contour(main_contour, split_path)


    # main_contour = reverse_path
    # split_path = [(3,0), (3,4)]
    # direct_path, reverse_path = split_contour(main_contour, split_path)



    rectangles_direct = split_into_rectangles2(direct_path)
    rectangles_reverse = split_into_rectangles2(reverse_path)

    sum_direct = area(rectangles_direct)
    sum_reverse = area(rectangles_reverse)

    if sum_direct >= sum_reverse:
        rectangles = rectangles_direct
    else:
        rectangles = rectangles_reverse

    for r in rectangles:
        w.create_rectangle(to_screen(*r[0]), to_screen(*r[1]), fill='green')

    draw_contour(main_contour, join=True)
    draw_contour(direct_path, join=True, color='green')
    draw_contour(reverse_path, join=True, color='blue')
    draw_contour(split_path, join=False, color="red")

    # for r in rectangles:
    # w.create_rectangle(to_screen(r[0]), to_screen(r[2]), fill='blue')

    mainloop()
