# 项目：点云配准
#
# 文件：box.py
# 简介：实现了一个n维的盒子；改编自COS 226的RectHV

from math import *
from .point import Point

# 一个n维的轴对齐盒子
class Box:
    # 构造函数接受两个点：pMin和pMax，它们定义了盒子的n维对角线
    def __init__(self, pMin, pMax):
        if (type(pMin) != Point):
            print("错误：pMin不是Point类型")
            pMin = Point([0])
        if (type(pMax) != Point):
            print("错误：pMax不是Point类型")
            pMax = Point([0])
        if (pMin.d != pMax.d):
            print("错误：pMin和pMax不是同一维度的！")
            pMin = Point([0])
            pMax = Point([0])
        if (pMin.d < 1):
            print("错误：盒子的维度必须是正数")
            pMin = Point([0])
            pMax = Point([0])

        self.sMin = pMin.s.copy()
        self.sMax = pMax.s.copy()
        self.d = pMin.d
        for i, (min_val, max_val) in enumerate(zip(pMin.s, pMax.s)):
            if (min_val > max_val):
                print("错误：盒子的维度必须是正数")
                self.sMin[i] = max_val
                self.sMax[i] = min_val

    def copy(self):
        return Box(Point(self.sMin), Point(self.sMax))

    # 使用val更新sMax的第dim维
    def updateMax(self, val, dim):
        # 首先检查边界
        if (val < self.sMin[dim]):
            print("错误：不能更新盒子的最大值使其在同一维度下落到最小值以下")
            return
        else:
            self.sMax[dim] = val

    # 使用val更新sMin的第dim维
    def updateMin(self, val, dim):
        # 首先检查边界
        if (val > self.sMax[dim]):
            print("错误：不能更新盒子的最小值使其在同一维度上超过最大值")
            return
        else:
            self.sMin[dim] = val

    # 返回指定维度内盒子的范围
    def range(self, dim):
        if (dim < 0 or dim >= self.d):
            print("错误：无法计算无效维度的范围")
            return 0

        return self.sMax[dim] - self.sMin[dim]

    # 如果这个盒子与那个盒子（包括只有边界相交的情况）相交返回True，两者维度相同
    def intersects(self, that):
        if (type(that) != Box):
            print("错误：交集参数不是Box类型")
            return False
        if (that.d != self.d):
            print("错误：无法计算不同维度的盒子之间的交集")
            return False

        for min_val, max_val in zip(that.sMin, self.sMax):
            if (max_val < min_val):
                return False
        for min_val, max_val in zip(self.sMin, that.sMax):
            if (max_val < min_val):
                return False

        return True

    # 如果这个盒子包含相同维度的点返回True
    def contains(self, p):
        if (type(p) != Point):
            print("错误：包含参数不是Point类型")
            return False
        if (p.d != self.d):
            print("错误：一个盒子不能包含不同维度的点")
            return False

        for pval, max_val in zip(p.s, self.sMax):
            if (pval > max_val):
                return False
        for pval, min_val in zip(p.s, self.sMin):
            if (pval < min_val):
                return False
        for min_val, max_val in zip(self.sMin, that.sMax):  # 我认为原项目这里的that是多余的，但不影响结果，于是保留
            if (max_val < min_val):
                return False
        return True

    # 返回这个盒子和点之间的欧几里得距离
    def distTo(self, p):
        return sqrt(self.distSqdTo(p))

    # 返回这个矩形和点之间的欧几里得距离的平方
    def distSqdTo(self, p):
        if (type(p) != Point):
            print("错误：距离参数不是Point类型")
            return 0.0
        if (p.d != self.d):
            print("错误：不能计算来自不同维度的点的距离")
            return 0.0

        distSqd = 0.0
        for pval, min_val, max_val in zip(p.s, self.sMin, self.sMax):
            dv = 0.0
            if (pval < min_val):
                dv = pval - min_val
            elif (pval > max_val):
                dv = pval - max_val
            distSqd += dv*dv

        return distSqd