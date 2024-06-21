# 项目：点云配准
#
# 文件：point.py
# 简介：实现了一个n维点

from math import *
import numpy as np

# 需要对象吗？
# 接受一个n维长度的位置数组，可选地接受法线数组作为输入
class Point:
    # 构造函数（可选地）接受位置数组和法线数组
    def __init__(self, s=[], n=[]):
        self.s = s.copy()
        self.n = n.copy()
        self.d = len(s)

    # 返回深拷贝
    def copy(self):
        newS = self.s.copy()
        newN = self.n.copy()
        newP = Point(newS, newN)

        return newP

    # 返回两个相同维度点之间的欧几里得距离
    def distTo(self, p):
        return sqrt(self.distSqdTo(p))

    # 返回两个相同维度点之间的平方欧几里得距离
    def distSqdTo(self, p):
        if (type(self) != type(p)):
            print("错误：期望一个点，但接收到的是 {}".format(type(p)))
            return 0.0

        if (p.d != self.d):
            print("错误：无法计算不同维度点之间的距离")
            return 0.0

        distSqd = 0.0
        for i in range(self.d):
            distSqd += (self.s[i] - p.s[i])**2
        return distSqd

    def transform(self, m):
        if (type(m) != np.matrix):
            print("错误：变换方法未接收到一个np矩阵！")
            return self
        if (len(m.shape) != 2):
            print("错误：变换方法需要一个2D矩阵！")
            return self
        if (m.shape[1] != (self.d + 1)):
            print("错误：变换方法接收到的矩阵维度不正确！")
            return self

        # 转换为齐次坐标
        old = self.s.copy()
        old.append(1.0)
        new = m.dot(old).tolist()[0]
        w = new[-1]
        self.s = [v/w for v in new[:-1]]

        return self