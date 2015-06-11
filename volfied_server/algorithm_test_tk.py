from Tkinter import *
from itertools import chain
from algorithm import split_contour, split_into_rectangles, area

master = Tk()

canvas_size = 500.0, 500.0
world_size = 10.0, 10.0


def to_screen(x, y):
    return int((x / world_size[0]) * canvas_size[0]) + 5, int(
        (y / world_size[1]) * canvas_size[1]) + 5


w = Canvas(master, width=canvas_size[0] + 50, height=canvas_size[1] + 50)
w.pack()


def draw_contour(contour, join=True, color="black"):
    points = map(lambda p: to_screen(*p), contour)
    if join:
        points = chain(points, [to_screen(*contour[0])])

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



rectangles_direct = split_into_rectangles(direct_path)
rectangles_reverse = split_into_rectangles(reverse_path)

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