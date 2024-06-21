import open3d as o3d
import numpy as np
import time
import sys
import copy
import os

# 将提供的矩阵M写入指定的.xf文件
def write_xf(file_name, M):
    dir = os.path.dirname(file_name)
    if (not os.path.exists(dir)):
        os.makedirs(dir)

    with open(file_name, "w") as f:
        for row in M:
            for val in row:
                f.write(str(val))
                f.write(' ')
            f.write('\n')
    return

# 从给定的.xf文件加载数据到4x4的np矩阵
def load_xf(file_name):
    with open(file_name) as f:
        data = f.read()
        rows = []
        for r in data.split('\n'):
            if (len(r) > 0):
                rows.append(r)

        if (len(rows) != 4):
            print("错误：在.xf文件中检测到的行数无效")
            rows = ["0 0 0 0" for i in range(4)]

        # 读取文件中的矩阵数据
        result = []
        for r in rows:
            c = []
            for v in r.split(' '):
                if (len(v) > 0):
                    c.append(float(v))
            if (len(c) != 4):
                print("错误：在{}中检测到的列数无效".format(file_name))
                c = [0, 0, 0, 0]
            result.append(c)

    return np.matrix(result)

def preprocess_point_cloud(pcd, voxel_size):
    print(":: 正在将点云下采样至体素大小为 %.3f." % voxel_size)
    pcd_down = pcd.voxel_down_sample(voxel_size)

    radius_normal = voxel_size * 3
    print(":: 使用搜索半径 %.3f 估计法线." % radius_normal)
    pcd_down.estimate_normals(
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=50))

    radius_feature = voxel_size * 6
    print(":: 使用搜索半径 %.3f 计算 FPFH 特征." % radius_feature)
    pcd_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        pcd_down,
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))
    return pcd_down, pcd_fpfh

def execute_fast_global_registration(source_down, target_down, source_fpfh, target_fpfh, voxel_size):
    distance_threshold = voxel_size * 1.5
    print(":: 正在应用快速全局配准，距离阈值为 %.3f" % distance_threshold)
    result = o3d.pipelines.registration.registration_fgr_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh,
        o3d.pipelines.registration.FastGlobalRegistrationOption(
            maximum_correspondence_distance=distance_threshold))
    return result

def draw_registration_result(source, target, transformation):
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)
    source_temp.paint_uniform_color([1, 0.706, 0])
    target_temp.paint_uniform_color([0, 0.651, 0.929])
    source_temp.transform(transformation)
    o3d.visualization.draw_geometries([source_temp, target_temp])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python registration.py 源点云路径 目标点云路径")
        sys.exit()

    source_path = sys.argv[1]
    target_path = sys.argv[2]

    # 加载源点云和目标点云
    source = o3d.io.read_point_cloud(source_path)
    target = o3d.io.read_point_cloud(target_path)

    # 设置体素大小
    voxel_size = 0.003  # 根据点云数据坐标值大小调整体素大小

    # 对源点云和目标点云进行预处理
    source_down, source_fpfh = preprocess_point_cloud(source, voxel_size)
    target_down, target_fpfh = preprocess_point_cloud(target, voxel_size)

    # 加载目标点云的转移矩阵（作为基准）
    # transformation_dir = "transformation"
    transformation_dir = "PLY_PTS"
    target_transformation_file = os.path.join(transformation_dir, os.path.splitext(os.path.basename(target_path))[0] + ".xf")
    if os.path.exists(target_transformation_file):
        target_transformation = load_xf(target_transformation_file)
        target_down.transform(target_transformation)

    # 执行快速全局配准
    start = time.time()
    result_fast = execute_fast_global_registration(source_down, target_down, source_fpfh, target_fpfh, voxel_size)
    print("快速全局配准花费 %.3f 秒." % (time.time() - start))
    print(result_fast)

    # 保存源点云的转移矩阵
    source_transformation_file = os.path.join(transformation_dir, os.path.splitext(os.path.basename(source_path))[0] + ".xf")
    write_xf(source_transformation_file, result_fast.transformation)
    print(f"转移矩阵已保存到：{source_transformation_file}")

    # 绘制配准后的点云图像
    draw_registration_result(source_down, target_down, result_fast.transformation)
