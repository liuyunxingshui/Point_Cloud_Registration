# 项目：点云配准
#
# 文件：kdtree.py
# 简介：实现了一个点的k-d树

from math import *
from .box import Box
from .point import Point

# 节点类，用于维护数据结构
class Node:
    # 接受一个点、一个浮点数和一个盒子作为输入
    def __init__(self, p, key, bounds):
        # 与节点关联的键（维度坐标）
        self.key = key

        # 与节点关联的点
        if (type(p) == Point):
            self.p = p
        else:
            self.p = None

        # 与节点关联的边界
        self.bounds = bounds
        if (type(bounds) == Box):
            self.bounds = bounds
        else:
            self.bounds = None

        # 左右链接
        self.left = None
        self.right = None

# 一个k-d树
class KdTree:
    # 构造函数接受整数k，定义了维度的数量
    def __init__(self, k=3):
        self.k = k
        self.size = 0
        self.root = None
        self.minP = [-inf for i in range(k)]
        self.maxP = [inf for i in range(k)]

    # 插入点的外部方法
    def insert(self, p):
        if (type(p) != Point):
            print("错误：插入方法未提供有效点")
            return
        if (p.d != self.k):
            print("错误：点和KdTree必须具有相同的维度")
            return

        bounds = Box(Point(self.minP), Point(self.maxP))
        self.root = self.put(self.root, p, 0, bounds)

    # 插入点的内部方法
    def put(self, node, p, dim, bounds):
        # 基本情况
        if (node == None):
            self.size += 1
            key = p.s[dim]
            return Node(p, key, bounds)

        # 比较点和节点，并相应地进行操作
        cmp = p.s[dim] - node.key
        if (cmp < 0):
            # 如果较小，则向左走；更新上界
            upperBounds = bounds.copy()
            upperBounds.updateMax(node.key, dim)
            node.left = self.put(node.left, p, (dim + 1) % self.k, upperBounds)
        else:
            # 否则向右走；更新下界
            lowerBounds = bounds.copy()
            lowerBounds.updateMin(node.key, dim)
            node.right = self.put(node.right, p, (dim + 1) % self.k, lowerBounds)

        return node

    # 返回k-d树中点p的最近邻；如果树为空则返回None
    def nearest(self, p):
        if (type(p) != Point):
            print("错误：最近邻方法未提供有效点")
            return
        if (p.d != self.k):
            print("错误：点和KdTree必须具有相同的维度")
            return
        # 角落情况，没有最近邻点（k-d树为空）
        if (self.size == 0):
            return None

        # 从根开始，递归地在两个子树中搜索，使用以下剪枝规则：
        # 如果到目前为止发现的最近点比查询点与对应节点的盒子之间的距离更近，
        # 那么就没有必要探索该节点（或其子树）。也就是说，我们只应该搜索可能
        # 包含比到目前为止找到的最近点更近的点的节点。

        # 剪枝规则的有效性取决于快速找到附近的点。为了做到这一点，递归方法
        # 组织得当，以便在有两个可能的子树可以向下走时，它首先选择查询点在分割线
        # 同一侧的子树；在探索第一个子树时找到的最近点可能启用剪枝第二个子树。
        root = self.root
        nearest_p, dist = self.find_nearest(root, p, 0, root.p, p.distSqdTo(root.p))
        return nearest_p

    # 查找最近点p的内部方法
    def find_nearest(self, node, p, dim, candidate, dist):
        # 基本情况
        if (node == None):
            return candidate, dist

        # 检查最近候选点的最远距离是否小于边界框的距离
        if (dist < node.bounds.distSqdTo(p)):
            return candidate, dist

        # 如果更近，则替换候选点
        newDist = p.distSqdTo(node.p)
        if (newDist < dist):
            candidate = node.p
            dist = newDist

        # 确定树应该先向左走还是先向右走
        # 注：如果查询点在左边，则先向左走
        go_left = (p.s[dim] < node.key)

        for i in range(2):
            if (go_left):
                # 沿着树向左走
                candidate, dist = self.find_nearest(node.left, p, (dim + 1) % self.k, candidate, dist)
            else:
                # 沿着树向右走
                candidate, dist = self.find_nearest(node.right, p, (dim + 1) % self.k, candidate, dist)

            go_left = not go_left

        return candidate, dist