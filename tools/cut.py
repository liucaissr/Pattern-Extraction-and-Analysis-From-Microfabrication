#!/usr/bin/python
import re
from svgpathtools import *
from math import *
from bisect import *
from operator import attrgetter
import numpy as np
from tools.mt import *
from tools.geometry import *


class LineNavigation(object):
    def __init__(self, position, start, end, line):
        self.position = position
        self.start = start
        self.end = end
        self.line = line

    def __repr__(self):
        #return 'Path{} Line{} (start={}, end={}) \n' % (self.pathno, self.lineno, self.start, self.end)
        return '{} {} {}'.format(self.position, self.start, self.end)

    def __cmp__(self, other):
        if hasattr(other, 'position') and hasattr(other, 'start'):
            if(self.position > other.position):
                return 1
            elif(self.position < other.position):
                return -1
            else:
                if (self.start > other.start):
                    return 1
                elif (self.end < other.end):
                    return -1
                else:
                    return 0

# something like key define exist
class Vertex(object):
    def __init__(self, point, hline, vline):
        self.point = point
        self.hline = hline
        self.vline = vline

    def __repr__(self):
        #return 'Path{} Line{} (start={}, end={}) \n' % (self.pathno, self.lineno, self.start, self.end)
        return '{} {} {}'.format(self.point, self.hline, self.vline)

    def __cmp__(self, other):
        e = 0.0000001
        if hasattr(other, 'point'):
            if(self.point.imag - other.point.imag > e):
                return 1
            elif(self.point.imag - other.point.imag < -e ):
                return -1
            else:
                if (self.point.real - other.point.real > e ):
                    return 1
                elif (self.point.real  - other.point.real < -e):
                    return -1
                else:
                    return 0

class Coordinate(complex):

    def __lt__(self, other):
        e = 0.0000001
        if hasattr(other, 'imag') and hasattr(other, 'real'):
            if (self.real - other.real > e):
                return 0
            elif (self.real - other.real < -e):
                return 1
            else:
                if (self.imag - other.imag > e):
                    return 0
                elif (self.imag - other.imag < -e):
                    return 1
                else:
                    return 0
        else:
            return NotImplemented

    def __gt__(self, other):
        e = 0.0000001
        if hasattr(other, 'imag') and hasattr(other, 'real'):
            if (self.real - other.real > e):
                return 1
            elif (self.real - other.real < -e):
                return 0
            else:
                if (self.imag - other.imag > e):
                    return 1
                elif (self.imag - other.imag < -e):
                    return 0
                else:
                    return 0
        else:
            return NotImplemented

    def __le__(self, other):
        e = 0.0000001
        if hasattr(other, 'imag') and hasattr(other, 'real'):
            if (self.real - other.real > e):
                return 0
            elif (self.real - other.real < -e):
                return 1
            else:
                if (self.imag - other.imag > e):
                    return 0
                elif (self.imag - other.imag < -e):
                    return 1
                else:
                    return 1
        else:
            return NotImplemented

    def __ge__(self, other):
        e = 0.0000001
        if hasattr(other, 'imag') and hasattr(other, 'real'):
            if (self.real - other.real > e):
                return 1
            elif (self.real - other.real < -e):
                return 0
            else:
                if (self.imag - other.imag > e):
                    return 1
                elif (self.imag - other.imag < -e):
                    return 0
                else:
                    return 1
        else:
            return NotImplemented
    def __eq__(self, other):
        e = 0.0000001
        if hasattr(other, 'imag') and hasattr(other, 'real'):
            if (abs(self.real - other.real) < e) and (abs(self.imag - other.imag) < e):
                return 1
            else:
                return 0
        else:
            return NotImplemented

class MicroLine(Line):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if super(MicroLine, self).__eq__(other):
                return True
            elif self.end == other.start and self.start == other.end:
                return True
            else:
                return False
        else:
            return NotImplemented

    @property
    def direction(self):
        if self.start.imag == self.end.imag:
            return 'h'
        elif self.start.real == self.end.real:
            return 'v'
        else:
            return NotImplemented

    def __cmp__(self, other):
        if hasattr(other, 'start') and hasattr(other, 'end'):
            self = self.order()
            other = other.order()
            # assert if not parallel
            if self.direction == 'h' and other.direction == 'h':
                if (self.start.imag > other.start.imag):
                    return 1
                elif (self.start.imag < other.start.imag):
                    return -1
                else:
                    if (self.start.real > other.start.real):
                        return 1
                    elif (self.end.real < other.end.real):
                        return -1
                    else:
                        return 0
            elif self.direction == 'v' and other.direction == 'v':
                if (self.start.real > other.start.real):
                    return 1
                elif (self.start.real < other.start.real):
                    return -1
                else:
                    if (self.start.imag > other.start.imag):
                        return 1
                    elif (self.end.imag < other.end.imag):
                        return -1
                    else:
                        return 0
            else:
                return 0

    def order(self):
        orderedLine = MicroLine(min(self.start, self.end), max(self.start, self.end))
        return orderedLine

# rectlinear pattern
class Pattern(Path):

    def preprocess(self):
        hlines = []
        vlines = []
        filteredPath = Pattern()
        filteredVertexObj = []
        filteredVertex = []
        path = []

        # todo: twice offsetx,offsety(design_preprocess) (bi xu de)
        for line in self:
            start = Coordinate(round(line.start.real, 3), round(line.start.imag, 3))
            end = Coordinate(round(line.end.real, 3), round(line.end.imag, 3))
            newline = MicroLine(start, end)
            path.append(newline)

        for line in path:
            if line.start != line.end:
                if line.direction == 'h':
                    hlines.append(line)
                if line.direction == 'v':
                    vlines.append(line)

        sortedhlines = combineLines(hlines)
        sortedvlines = combineLines(vlines)
        filteredVlines = []
        filteredHlines = []

        for vline in sortedvlines:
            intersectpoints = []
            for hline in sortedhlines:
                x = line1_intersect_with_line2(vline, hline)
                if len(x) != 0:
                    intersectpoints.append(x[0][0])
            if len(intersectpoints) >= 2:
                newvline = MicroLine(Coordinate(vline.point(min(intersectpoints))),
                                     Coordinate(vline.point(max(intersectpoints))))
                filteredVlines.append(newvline)
        for hline in sortedhlines:
            intersectpoints = []
            for vline in sortedvlines:
                x = line1_intersect_with_line2(hline, vline)
                if len(x) != 0:
                    intersectpoints.append(x[0][0])
            if len(intersectpoints) >= 2:
                newhline = MicroLine(Coordinate(hline.point(min(intersectpoints))),
                                     Coordinate(hline.point(max(intersectpoints))))
                filteredHlines.append(newhline)

        # todo filteredPath not closed
        for line in path:
            if line.start != line.end:
                filteredPath.append(line)

        for line in filteredHlines:
            if line.start not in filteredVertex:
                filteredVertex.append(line.start)
                startPoint = Vertex(line.start, None, None)
                filteredVertexObj.append(startPoint)
            if line.end not in filteredVertex:
                filteredVertex.append(line.end)
                endPoint = Vertex(line.end, None, None)
                filteredVertexObj.append(endPoint)
            for pointobj in filteredVertexObj:
                if pointobj.point == line.start:
                    pointobj.hline = line
                if pointobj.point == line.end:
                    pointobj.hline = line

        for line in filteredVlines:
            if line.start not in filteredVertex:
                filteredVertex.append(line.start)
                startPoint = Vertex(line.start, None, None)
                filteredVertexObj.append(startPoint)
            if line.end not in filteredVertex:
                filteredVertex.append(line.end)
                endPoint = Vertex(line.end, None, None)
                filteredVertexObj.append(endPoint)
            for pointobj in filteredVertexObj:
                if pointobj.point == line.start:
                    pointobj.vline = line
                if pointobj.point == line.end:
                    pointobj.vline = line

        return sortedhlines, sortedvlines, filteredPath, filteredVertexObj




def preconfig(paths):
    offsetx = paths[0][0].start.real
    offsety = paths[0][0].start.imag
    for path in paths:
        for line in path:
            if line.start.real < offsetx:
                offsetx = line.start.real
            if line.end.real < offsetx:
                offsetx = line.end.real
            if line.start.imag < offsety:
                offsety = line.start.imag
            if line.end.imag < offsety:
                offsety = line.end.imag

    if offsety >= 0:
        offsety = -10
    else:
        offsety -= 10
    if offsetx >= 0:
        offsetx = -10
    else:
        offsetx -= 10

    return offsetx, offsety

# process based on attributes
# todo: 0906 combine original contacted patterns
# todo: how about closest pattern???-> combine needed should be merging conflict! -> combine needed are sharing same edge
def design_preprocess(paths, attributes, offsetx, offsety):
    length = len(attributes)
    scale = [1] * length
    newPathList = []
    result = []
    for i in range(0, length):
        if attributes[i].has_key(u'transform'):
            str = attributes[0].get(u'transform').encode('utf-8')
            scaleconfig = re.findall("scale\(+\d+\.\d+", str)
            if scaleconfig[0] != 0:
                scale[i] = float(re.findall("\d+\.\d+", scaleconfig[0])[0])
        else:
            scale[i] = 1
    for i in range(0, len(paths)):
        newPath = Pattern()
        for line in paths[i]:
            newPath.append(Line(line.start * scale[i], line.end * scale[i]))
        newPathList.append(newPath)
    for path in newPathList:
        newPath = Pattern()
        for line in path:
            start = Coordinate(round(line.start.real - offsetx, 3), round(line.start.imag - offsety, 3))
            end = Coordinate(round(line.end.real - offsetx, 3), round(line.end.imag - offsety, 3))
            newline = MicroLine(start, end)
            newPath.append(newline)
        result.append(newPath)
    offsetframe = calculateFrame(result, offsetx, offsety)
    return result, offsetframe

def calculateFrame(paths, offsetx, offsety):
    frame = Pattern()
    fb = paths[0].bbox()
    xmin = fb[0]
    xmax = fb[1]
    ymin = fb[2]
    ymax = fb[3]
    # create the frame of the layout
    for path1 in paths:
        b1 = path1.bbox()
        if len(path1) != 4:
            break
        frame = path1
        for path2 in paths:
            if path1 != path2:
                b2 = path2.bbox()
                if b1[0] <= b2[0] <= b1[1] and b1[0] <= b2[1] <= b1[1] and b1[2] <= b2[2] <= b1[3] and \
                        b1[2] <= b2[3] <= b1[3]:
                    pass
                else:
                    frame = Pattern()
                    break
        if frame != Pattern():
            break
    if frame == Pattern():
        for path in paths:
            b = path.bbox()
            if b[0] < xmin:
                xmin = b[0]
            if b[1] > xmax:
                xmax = b[1]
            if b[2] < ymin:
                ymin = b[2]
            if b[3] > ymax:
                ymax = b[3]
        offset = max(xmax - xmin, ymax - ymin) * 0.05
        frame = Pattern(MicroLine(Coordinate(xmin - offset, ymin - offset),
                               Coordinate(xmax + offset, ymin - offset)),
                     MicroLine(Coordinate(xmax + offset, ymin - offset),
                               Coordinate(xmax + offset, ymax + offset)),
                     MicroLine(Coordinate(xmax + offset, ymax + offset),
                               Coordinate(xmin - offset, ymax + offset)),
                     MicroLine(Coordinate(xmin - offset, ymax + offset),
                               Coordinate(xmin - offset, ymin - offset)))
    if frame in paths:
        paths.remove(frame)
    # todo: no offset, minues zai shuo

    return frame


# intersect = intersect lines on the paths
# intersectpath = intersect path if exists



def two_lines_distance(line1, line2):
    if line1.direction == line2.direction == 'h':
        dis = line1.start.imag - line2.start.imag
    elif line1.direction == line2.direction == 'v':
        dis = line1.start.real - line2.start.real
    else:
        return NotImplemented
    return dis

# intersectlines in lines for line
def line_intersectlines(line, lines):
    direct = line.direction
    l1 = line.order()
    intersectlines = []
    for l in lines:
        l2 = l.order()
        if l1 != l2:
            if l2.direction == direct == 'h':
                if l1.start.real <= l2.end.real and l1.end.real >= l2.start.real:
                    intersectlines.append(l2)
            if l2.direction == direct == 'v':
                if l1.start.imag <= l2.end.imag and l1.end.imag >= l2.start.imag:
                    intersectlines.append(l2)
    return intersectlines


def getDev(path, line):
    l0 = line.order()
    intersectlines = line_intersectlines(l0, path)
    dev = two_lines_distance(l0, intersectlines[0])
    for pl in intersectlines:
        if dev == 0:
            dev = two_lines_distance(l0, pl)
            continue
        dis = two_lines_distance(l0, pl)
        if abs(dis) < abs(dev) and dis != 0:
            dev = dis
    return dev


def changePath(path, index, dev, factor, large_ratio):
    newPath = Pattern()
    l0 = path[index]
    if abs(dev * factor) < large_ratio:
        devx = dev * 0.7
    else:
        devx = dev * factor
    if l0.direction == 'h':
        deviation = Coordinate(0, -devx)
    else:
        deviation = Coordinate(-devx, 0)
    for line in path:
        if line != l0:
            point = line1_intersect_with_line2(line, l0)
            if len(point) != 0:
                roundpoint = round(point[0][0], 3)
                if roundpoint == 1:
                    end = Coordinate(line.end + deviation)
                    newPath.append(MicroLine(line.start, end))
                if roundpoint == 0:
                    start = Coordinate(line.start + deviation)
                    newPath.append(MicroLine(start, line.end))
            else:
                newPath.append(line)
        else:
            newLine = MicroLine(Coordinate(l0.start + deviation), Coordinate(l0.end + deviation))
            newPath.append(newLine)

    return newPath

# Calculate distance when path length is larger than 4
def two_paths_distancex(path1, path2):
    dis = 0
    points1 = []
    points2 = []
    lines1 = []
    lines2 = []
    points1.append(path1.start)
    points2.append(path2.start)
    inter = path1.intersect(path2)
    if len(inter) != 0:
        return dis
    for l1 in path1:
        points1.append(l1.end)
        l = l1.order()
        lines1.append(l)
    for l2 in path2:
        points2.append(l2.end)
        l = l2.order()
        lines2.append(l)
    for p1 in points1:
        for l2 in lines2:
            if l2.direction == 'h' and l2.start.real < p1.real < l2.end.real:
                tmpdis = abs(l2.start.imag - p1.imag)
            elif l2.direction == 'v' and l2.start.imag < p1.imag < l2.end.imag:
                tmpdis = abs(l2.start.real - p1.real)
            else:
                tmpdis = min(sqrt((l2.start.real-p1.real) ** 2 + (l2.start.imag-p1.imag) ** 2), sqrt((l2.end.real-p1.real) ** 2 + (l2.end.imag-p1.imag) ** 2))
            if tmpdis < dis or dis == 0:
                dis = tmpdis
    for p2 in points2:
        for l1 in lines1:
            if l1.direction == 'h' and l1.start.real < p2.real < l1.end.real:
                tmpdis = abs(l1.start.imag - p2.imag)
            elif l1.direction == 'v' and l1.start.imag < p2.imag < l1.end.imag:
                tmpdis = abs(l1.start.real - p2.real)
            else:
                tmpdis = min(sqrt((l1.start.real-p2.real) ** 2 + (l1.start.imag-p2.imag) ** 2), sqrt((l1.end.real-p2.real) ** 2 + (l1.end.imag-p2.imag) ** 2))
            if tmpdis < dis or dis == 0:
                dis = tmpdis
    return dis

def two_paths_distance(path1, path2):
    dev = 0
    if len(path1) > 4 or len(path2) > 4:
        return two_paths_distancex(path1, path2)
    b1 = path1.bbox()
    b2 = path2.bbox()
    ls,path = two_paths_intersection(path1, path2)
    if len(ls) != 0 or path is not None:
        return 0
    if b1[1] < b2[0] and b1[2] > b2[2]:
        dev = sqrt((b2[0] - b1[1]) ** 2 + (b2[2] - b1[3]) ** 2)
    elif b2[1] < b1[0] and b2[3] < b1[2]:
        dev = sqrt((b2[1] - b1[0]) ** 2 + (b2[3] - b1[2]) ** 2)
    if b1[1]<b2[0] and b1[3]<b2[2]:
        dev = sqrt((b2[0] - b1[1]) ** 2 + (b2[2] - b1[3]) ** 2)
    elif b1[1]<b2[0] and b1[2]>b2[3]:
        dev = sqrt((b2[0] - b1[1]) ** 2 + (b1[2] - b2[3]) ** 2)
    elif b1[0]>b2[1] and b1[3]<b2[2]:
        dev = sqrt((b1[0] - b2[1]) ** 2 + (b2[2] - b1[3]) ** 2)
    elif b1[0]>b2[1] and b1[2]>b2[3]:
        dev = sqrt((b1[0] - b2[1]) ** 2 + (b1[2] - b2[3]) ** 2)
    elif b1[1] < b2[0]:
        dev = b2[0] - b1[1]
    elif b1[3] < b2[2]:
        dev = b2[2] - b1[3]
    elif b2[1] < b1[0]:
        dev = b1[0] - b2[1]
    elif b2[3] < b1[2]:
        dev = b1[2] - b2[3]
    return dev

def no_merge_conflict(path1, path2, factor, dis = None):
    if dis is None:
        dis = two_paths_distance(path1, path2)
    if 0 < dis < factor:
        return True,dis
    else:
        return False,dis

def no_absorption_conflict(path1, path2, factor):
    # factor = 0.2
    assert path1.isclosed() and path2.isclosed(), '%s is not closed' % (path1 if path1.isclosed() is False else path2)
    x, p = two_paths_intersection(path1, path2)
    factor_sqrt = sqrt(factor)
    selflengthfactor = 0.8
    interl = None
    if len(x) == 0 and p is None:
        return False,interl
    # assert len(x) == 1
    #todo: 0823 add for new situation
    #todo: 0903 add more robost check
    elif len(x) != 0 and p is None:
        length = float(x[0].length())
        interl = x[0]
        area = 0
        wholelength = 0
        if x[0] in path1:
            for line in path2:
                l, p = two_lines_intersection(x[0], line)
                if l is not None:
                    wholelength = float(line.length())
            area = float(abs(path2.area()))
        elif x[0] in path2:
            for line in path1:
                l, p = two_lines_intersection(x[0], line)
                if l is not None:
                    wholelength = float(line.length())
            area = float(abs(path1.area()))
        ratio = 1
        lengthratio = 1
        if area != 0:
            ratio = length / area
        if wholelength != 0:
            lengthratio = length / wholelength
        if ratio < factor or lengthratio < factor_sqrt:
            return True, interl
    elif p is not None:
        lengths = {}
        for l in p:
            lens = float(l.length())
            if lens not in lengths.keys():
                lengths[lens] = [0] * 2
            for line in path1:
                interl, p = two_lines_intersection(l, line)
                if interl is not None:
                    wholelength = float(line.length())
                    lengths[lens][0] = wholelength
            if lengths[lens][0] == 0:
                d = l.direction
                dist = 0
                for ll in path1:
                    dd = ll.direction
                    if d == dd:
                        temp = abs(two_lines_distance(l, ll))
                        if temp < dist or dist == 0:
                            dist = temp
                            lengths[lens][0] = float(ll.length())
            for line in path2:
                interl, p = two_lines_intersection(l, line)
                if interl is not None:
                    wholelength = float(line.length())
                    lengths[lens][1] = wholelength
            if lengths[lens][1] == 0:
                d = l.direction
                dist = 0
                for ll in path2:
                    dd = ll.direction
                    if d == dd:
                        temp = abs(two_lines_distance(l, ll))
                        if temp < dist or dist == 0:
                            dist = temp
                            lengths[lens][1] = float(ll.length())
        for k in lengths.keys():
            area1 = float(abs(path1.area()))
            area2 = float(abs(path2.area()))
            ratio1 = 1
            ratio2 = 1
            if area1 != 0:
                ratio1 = k / area1
            if area2 != 0:
                ratio2 = k / area2
            lengthratio1 = k / lengths[k][0]
            lengthratio2 = k / lengths[k][1]
            const12_1 = ratio1 < factor and lengthratio1 < factor_sqrt
            const12_2 = ratio2 < factor and lengthratio2 < factor_sqrt
            #turn off const3
            #const3_1 = lengthratio2 > selflengthfactor
            const3_1 = True
            #const3_2 = lengthratio1 > selflengthfactor
            const3_2 = True
            #if ((ratio1 < factor and lengthratio1 < factor_sqrt) and lengthratio2 > selflengthfactor) or ((ratio2 < factor and lengthratio2 < factor_sqrt) and lengthratio1 > selflengthfactor):
            if (const12_1 and const3_1) or (const12_2 and const3_2):
                return True, None
    return False, interl

def update_conflict(conflict, oldPath, newPath):
    if newPath not in conflict.keys():
        conflict[newPath] = []
    if oldPath in conflict.keys():
        for conflictpath in conflict[oldPath]:
            if conflictpath not in conflict[newPath]:
                # todo any unique list
                conflict[newPath].append(conflictpath)
        del conflict[oldPath]
    for k, v in conflict.items():
        if oldPath in v:
            v.remove(oldPath)
            if newPath not in v:
                v.append(newPath)

def unitdivision(frame):
    unitrectedge = 1
    # calculate area of unit
    # unitdim: approximate unit edge size
    # unitrectedge: unit edge size
    dimension = frame[0].length() * frame[1].length()
    unitdim = sqrt(np.true_divide(dimension, 10000) * 1.1)
    n = num_digit(unitdim)
    unitrectedge = round(unitdim, n+2)
    return unitrectedge



#todo move to path properties
#todo assert path close
def subunit(path, unitrect, offsetframe):
    num_line = len(path)
    #unit_points = []
    unit_points = {}
    unitrect = float(unitrect)
    if num_line == 4:
        b = path.bbox()
        x0 = int(floor((b[0] - offsetframe.start.real)/float(unitrect) + 1))
        x1 = int(ceil((b[1] - offsetframe.start.real)/float(unitrect) + 1))
        y0 = int(floor((b[2] - offsetframe.start.imag)/float(unitrect) + 1))
        y1 = int(ceil((b[3] - offsetframe.start.imag)/float(unitrect) + 1))
        for x in range(x0,x1):
            for y in range(y0,y1):
                l = 1.0
                w = 1.0
                if x==x0:
                    l=x - (b[0] - offsetframe.start.real)/unitrect
                elif x==(x1-1):
                    l=(b[1] - offsetframe.start.real)/unitrect-(x-1)
                if y==y0:
                    w = y-(b[2] - offsetframe.start.imag)/unitrect
                elif y==(y1-1):
                    w = (b[3] - offsetframe.start.imag)/unitrect-(y-1)
                if x0 == x1 - 1:
                    l = (b[1]-b[0])/unitrect
                if y0 == y1 - 1:
                    w = (b[3]-b[2])/unitrect
                per = round(l*w,6)
                point = (x,y)
                unit_points[point] = per
        return unit_points
    elif num_line > 4:
        rectpaths = rectangular_partition(path)[0]
        for p in rectpaths:
            new_points= subunit(p, unitrect, offsetframe)
            for k,v in new_points.items():
                if k in unit_points.keys():
                    unit_points[k]+=new_points[k]
                else:
                    unit_points[k]=v
        #unit_points = list(set(unit_points))
        return unit_points
    else:
        NotImplemented

def output_unit(folder, filename, context, unitrect, offsetframe):
    file = open(folder + filename, 'w')
    num_x = ceil(offsetframe[0].length() / unitrect)
    num_y = ceil(offsetframe[1].length() / unitrect)
    file.write('%d %d %f\n' % (num_x, num_y, unitrect))
    for k, v in context.items():
        index = k
        if len(v) != 0:
            l = len(v)
            file.write('o%s %d' % (index, l))
            for li,per in v.items():
                file.write(' (%d,%d, %f)' % (li[0], li[1], per))
            file.write('\n')
    file.write('FIN\n')
    file.close()

def output_conflict(folder, filename, context, distincthpaths):
    conflictfile = open(folder + filename, 'w')
    conflictfile.write('no merge conflict:\n')
    for k, v in context[0].items():
        index = distincthpaths.index(k)
        if len(v) != 0:
            l = len(v)
            conflictfile.write('o%s %d' % (index, l))
            for li in v:
                indexl = distincthpaths.index(li)
                conflictfile.write(' o%s' % (indexl))
            conflictfile.write('\n')
    conflictfile.write('FIN\n')
    conflictfile.write('\nno absorption conflict:\n')
    for k, v in context[1].items():
        index = distincthpaths.index(k)
        if len(v) != 0:
            stri = []
            for l in v:
                if abs(k.area()) < abs(l.area()):
                    indexl = distincthpaths.index(l)
                    if indexl not in stri:
                        stri.append('o' + str(indexl))
        if len(stri) != 0:
            l = len(stri)
            conflictfile.write('o%s %d' % (index, l))
            for s in stri:
                conflictfile.write(' %s' % (s))
            conflictfile.write('\n')
    conflictfile.write('FIN\n\n')
    conflictfile.write('distance:\n')
    for k, v in context[2].items():
        index = distincthpaths.index(k)
        if len(v) != 0:
            for o, d in v.items():
                indexl = distincthpaths.index(o)
                conflictfile.write('o%s o%s %f\n' % (index, indexl, d))
    conflictfile.write('FIN\n')
    conflictfile.close()

 # todo: add more unit and percentage and test with 0720
def rectangular_partition(path, large_ratio=0):
    # todo move large_ratio and removecutlines out
    cutvpointobjs = []
    cuthlines = []
    allhlines = []
    allcurcutlines = []
    curdistincthlines = []
    removecutline = []
    sortedhlines, sortedvlines, filteredPath, filteredVertex = path.preprocess()
    # todo pick one shorter line
    # todo if vline
    # todo if hline
    for pointobj in filteredVertex:
        # todo point to two cutlines
        cuthline = None
        cutvline = None
        intersecthlines = [x for x in sortedhlines if
                           x.start.real <= pointobj.point.real <= x.end.real]
        intersectvlines = [x for x in sortedvlines if
                           x.start.imag <= pointobj.point.imag <= x.end.imag]
        intersecthlinesy = map(attrgetter('start.imag'), intersecthlines)
        intersectvlinesx = map(attrgetter('start.real'), intersectvlines)
        if pointobj.point == pointobj.hline.start:
            # todo left extend
            end = pointobj.point
            leftvlineno = bisect_left(intersectvlinesx, end.real) - 1
            if len(intersectvlines) > leftvlineno >= 0:
                start = Coordinate(intersectvlines[leftvlineno].start.real, end.imag)
                leftcuthline = MicroLine(start, end)
                if line_is_contained_in_path(leftcuthline, filteredPath):
                    # todo add to cutlines hou bu
                    cuthline = leftcuthline
        else:
            # todo right extend
            start = pointobj.point
            rightvlineno = bisect_right(intersectvlinesx, start.real)
            if 0 < rightvlineno < len(intersectvlines):
                end = Coordinate(intersectvlines[rightvlineno].start.real, start.imag)
                rightcuthline = MicroLine(start, end)
                if line_is_contained_in_path(rightcuthline, filteredPath):
                    # todo add to cutlines hou bu
                    cuthline = rightcuthline

        if pointobj.point == pointobj.vline.start:
            # todo up extend
            end = pointobj.point
            uphlineno = bisect_left(intersecthlinesy, end.imag) - 1
            if len(intersecthlines) > uphlineno >= 0:
                start = Coordinate(end.real, intersecthlines[uphlineno].start.imag)
                upcutvline = MicroLine(start, end)
                if line_is_contained_in_path(upcutvline, filteredPath):
                    # todo add to cutlines hou bu
                    cutvline = upcutvline
                    cutvpoint = Vertex(start, intersecthlines[uphlineno], None)
        else:
            # todo down extend
            start = pointobj.point
            downhlineno = bisect_right(intersecthlinesy, start.imag)
            if 0 < downhlineno < len(intersecthlines):
                end = Coordinate(start.real, intersecthlines[downhlineno].start.imag)
                downcutvline = MicroLine(start, end)
                if line_is_contained_in_path(downcutvline, filteredPath):
                    # todo add to cutlines hou bu
                    cutvline = downcutvline
                    cutvpoint = Vertex(end, intersecthlines[downhlineno], None)

        # todo compare two line:
        cutvlinelength = 0
        cuthlinelength = 0
        curcutline = None
        if cutvline is not None:
            cutvlinelength = cutvline.length()
        if cuthline is not None:
            cuthlinelength = cuthline.length()
        if cutvlinelength != 0 and (cuthlinelength > cutvlinelength or cuthlinelength == 0):
            curcutline = cutvline
            cutvpointobjs.append(cutvpoint)
            # todo add above hline
        elif cuthlinelength != 0 and (cutvlinelength >= cuthlinelength or cutvlinelength == 0):
            curcutline = cuthline
            # todo change cuthlines, allhlines to cuthlines
            cuthlines.append(curcutline)
            allhlines.append(curcutline)

        if curcutline is not None:
            allcurcutlines.append(curcutline)

    # allcurcutlines: collection of cutlines
    cline_num = len(allcurcutlines)
    cutcutlines = []
    cutlinevpointobjs = []
    for i in range(0, cline_num):
        for j in range(i + 1, cline_num):
            x = line1_intersect_with_line2(allcurcutlines[i], allcurcutlines[j])
            if len(x) != 0:
                if x != [(0.0, 0.0)] and x != [(0.0, 1.0)] and x != [(1.0, 0.0)] and x != [(1.0, 1.0)]:
                    if allcurcutlines[i].direction() == 'h':
                        hcline = allcurcutlines[i]
                        vcline = allcurcutlines[j]
                    else:
                        hcline = allcurcutlines[j]
                        vcline = allcurcutlines[i]
                    intersectp = Coordinate(vcline.start.real, hcline.start.imag)
                    newvpoint = Vertex(intersectp, None, None)
                    cutvpointobjs.append(newvpoint)
                    cutlinevpointobjs.append(newvpoint)
                    for replacehline in [allcurcutlines[i], allcurcutlines[j]]:
                        cutcutlines.append(replacehline)
                else:
                    continue
    # cutcutlines: all intersected cutlines
    # allhlines: all h cutlines
    # cutlinevpointobjs: intersected points of cutlines
    replacehlines = []
    for h in allhlines:
        replacehlines.append(h)
    # if there are intersected cutlines, then combine them
    if len(cutlinevpointobjs):
        replacehlines = combineLinesWithPoints(allhlines, cutlinevpointobjs)
    # replacehlines: combined h cutlines
    # todo remove after testing
    for line in sortedhlines:
        allhlines.append(line)
    combinedhlines = combineLinesWithPoints(allhlines, cutvpointobjs)
    for line in combinedhlines:
        # todo delete obj
        curdistincthlines.append(line)
    # todo add cuthline to cur
    '''
    for line in cutcutlines:
        if line in cuthlines:
            cuthlines.remove(line)
    '''
    for line in replacehlines:
        curdistincthlines.append(line)
    # curdistincthlines: combinedhlines +  replacehlines
    # cuthlines: all cuthlines - cutcutlines
    curdistinctpaths = createrect(curdistincthlines)
    return curdistinctpaths, allcurcutlines