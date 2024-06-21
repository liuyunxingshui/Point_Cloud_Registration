# 项目：点云配准
#
# 文件：testkdtree.py
# 简介：一个简单的脚本，用于测试kdtree.py

from .kdtree import KdTree
from .point import Point
from random import random

# 基本功能测试
t = KdTree()
p1 = Point([1, 2, 3])
p2 = Point([5, -4, 9])
p3 = Point([100, -29, 30])
t.insert(p1)
t.insert(p2)
t.insert(p1)  # 测试重复插入点
t.insert(p3)
assert (t.nearest(Point([99, -28, 37])).s == p3.s)  # 测试最近邻查找

def bruteForce_nearest(p, points):
    if (len(points) == 0):
        return None
    pbest = points[0]
    dist_best = p.distSqdTo(pbest)  # 暴力查找最近邻

    for ptest in points:
        dist_test = p.distSqdTo(ptest)
        if (dist_test < dist_best):
            dist_best = dist_test
            pbest = ptest

    return pbest

print("通过基本测试")

# 插入1000个随机n维点
for d in range(1, 6):
    t = KdTree(d)
    points = []
    for i in range(5000):
        p = Point([(random() * 2000.0 - 1000.0) for j in range(d)])
        points.append(p)
        t.insert(p)

    # 测试1000个点
    for i in range(1000):
        p = Point([(random() * 2000.0 - 1000.0) for j in range(d)])
        q = t.nearest(p)
        b = bruteForce_nearest(p, points)

        assert (p.distSqdTo(q) == p.distSqdTo(b))  # 测试k-d树与暴力查找的一致性

print("通过一致性测试")

# 压力测试
t = KdTree(5)
points = []
for i in range(1000000):
    p = Point([(random() * 2000.0 - 1000.0) for j in range(d)])
    points.append(p)
    t.insert(p)

print("开始使用100万个点的树进行压力测试.....")

# 测试5个点
for i in range(5):
    p = Point([(random() * 2000.0 - 1000.0) for j in range(d)])
    # print("开始k-d树搜索....")
    q = t.nearest(p)
    # print("开始暴力搜索....")
    b = bruteForce_nearest(p, points)
    assert (p.distSqdTo(q) == p.distSqdTo(b))  # 测试k-d树在压力下的表现

    # print(p.s)
    # print(q.s)
    # print(b.s)
    # print()

print("通过所有测试")