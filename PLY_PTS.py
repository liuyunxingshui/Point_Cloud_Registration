import open3d as o3d
import numpy as np
import sys
import os

def load_ply(file_name):
    pcd = o3d.io.read_point_cloud(file_name)
    return pcd

def write_pts(file_name, points, normals):
    with open(file_name, 'w') as f:
        for point, normal in zip(points, normals):
            f.write(' '.join(map(str, point)) + ' ' + ' '.join(map(str, normal)) + '\n')

def convert_ply_to_pts(ply_file, output_dir):
    # 加载PLY文件
    pcd = load_ply(ply_file)

    # 放大点坐标
    scale_factor = 1  # 根据需要调整缩放因子，保持1即可，如要放大，则对应的初始转移矩阵需要重新计算，要用.pts文件里的点坐标进行计算
    points = np.asarray(pcd.points)
    points *= scale_factor  # 放大点坐标

    # 将points转换为Vector3dVector对象
    pcd.points = o3d.utility.Vector3dVector(points)

    # 计算法向量
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1 * scale_factor, max_nn=30))

    # 获取点和法向量
    points = np.asarray(pcd.points)
    normals = np.asarray(pcd.normals)

    # 将points转换为Vector3dVector对象
    pcd.points = o3d.utility.Vector3dVector(points)

    # 构造输出目录和PTS文件名
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    pts_file = os.path.join(output_dir, os.path.splitext(os.path.basename(ply_file))[0] + '.pts')

    # 写入PTS文件
    write_pts(pts_file, points, normals)
    print(f"转换完成：{pts_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法：python PLY_PTS.py <ply_file>")
        sys.exit(1)

    ply_file = sys.argv[1]

    if not os.path.isfile(ply_file):
        print(f"错误：找不到文件 {ply_file}")
        sys.exit(1)

    output_dir = 'PLY_PTS'
    convert_ply_to_pts(ply_file, output_dir)
