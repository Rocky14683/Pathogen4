import math, pygame

# Whether (x,y) is inside the rectangle described by (x1,y1) and (x2,y2)
def isInsideBox(x, y, x1, y1, x2, y2):
    x_min, x_max = min(x1, x2), max(x1, x2)
    y_min, y_max = min(y1, y2), max(y1, y2)
    return x_min <= x <= x_max and y_min <= y <= y_max

# Whether (x,y) is inside rectangle defined by x, y, width height
def isInsideBox2(x, y, topLeftX, topLeftY, width, height):
    return isInsideBox(x, y, topLeftX, topLeftY, topLeftX + width, topLeftY + height)

# Clamp a value between a minimum and a maximum value.
def clamp(value, minValue, maxValue):
    return max(min(value, maxValue), minValue)

def addTuples(tupleA: tuple, tupleB: tuple):
    assert len(tupleA) == len(tupleB)
    return [a+b for a,b in zip(tupleA, tupleB)]

def subtractTuples(tupleA: tuple, tupleB: tuple):
    assert len(tupleA) == len(tupleB)
    return [a-b for a,b in zip(tupleA, tupleB)]

def scaleTuple(nums: tuple, scalar: float):
    return [i * scalar for i in nums]

def divideTuple(nums: tuple, scalar: float):
    return [i / scalar for i in nums]

def clampTuple(nums: tuple, min: float, max: float):
    return [clamp(i, min, max) for i in nums]

def intTuple(nums: tuple):
    return [int(i) for i in nums]

def hypo(s1, s2):
    return math.sqrt(s1*s1 + s2*s2)

def distance(x1,y1,x2,y2):
    return hypo(y2-y1, x2-x1)

def distanceTuples(point1, point2):
    return distance(*point1, *point2)

# Distance between point (x, y) and line (x1, y1,),(x2,y2)
def distancePointToLine(x, y, x1, y1, x2, y2, signed: bool = False):
    ans = ((x2-x1)*(y1-y) - (x1-x)*(y2-y1)) / distance(x1, y1, x2, y2)
    if signed:
        return ans
    else:
        return abs(ans)

# Whether point is touching the line with some margin given by lineHitboxThickness
def pointTouchingLine(mouseX: int, mouseY: int, x1: int, y1: int, x2: int, y2: int, lineHitboxThickness: int) -> bool:

    if x1 == x2 and y1 == y2:
        return False
    
    if distancePointToLine(mouseX,mouseY, x1, y1, x2, y2) <= lineHitboxThickness:
        dist = distance(x1, y1, x2, y2)
        if distance(mouseX, mouseY, x1, y1) < dist and distance(mouseX, mouseY, x2, y2) < dist:
            return True
    return False

# Bound angle to between -pi and pi, preferring the smaller magnitude
def boundAngleRadians(angle: float) -> float:
    PI = 3.1415
    angle %= 2 * PI
    if angle < -PI:
        angle += 2*PI
    if angle > PI:
        angle -= 2*PI
    return angle
    
# Find the closest angle between two universal angles
def deltaInHeading(targetHeading: float, currentHeading: float) -> float:
    return boundAngleRadians(targetHeading - currentHeading)

# Vector projection algorithm
def pointOnLineClosestToPoint(pointX: int, pointY: int, firstX: int, firstY: int, secondX: int, secondY: int) -> tuple:
    ax = pointX - firstX
    ay = pointY - firstY
    bx = secondX - firstX
    by = secondY - firstY

    scalar = (ax * bx + ay * by) / (bx * bx + by * by)
    return [firstX + scalar * bx, firstY + scalar * by]

def clipLineToBox(point: tuple, theta: float, boxX, boxY, boxWidth, boxHeight): # returns start and end line

    line_start = point
    line_length = max(boxWidth, boxHeight) * 1.42
    line_theta = theta

    # calculate the end point of the line
    line_end_x = line_start[0] + line_length * math.cos(line_theta)
    line_end_y = line_start[1] + line_length * math.sin(line_theta)
    line_end = (line_end_x, line_end_y)

    rect = pygame.Rect(boxX, boxY, boxWidth, boxHeight)

    # clip the line so that it does not go past the screen
    line_rect = pygame.Rect(line_start, (line_length, 1))
    if not line_rect.colliderect(rect):
        # calculate the intersection points of the line with the edges of the screen
        intersections = []
        for edge in rect.inflate(-line_length, -line_length).as_lines():
            intersection_point = line_rect.clipline(edge)
            if intersection_point:
                intersections.append(intersection_point)
        if intersections:
            # clip the line to the closest intersection point
            line_end = min(intersections, key=lambda p: math.hypot(line_start[0] - p[0], line_start[1] - p[1]))

    return line_start, line_end