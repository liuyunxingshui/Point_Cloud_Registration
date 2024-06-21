# 点云配准

此项目是在Reilly Bova公开的[Point-Cloud-Registration](https://github.com/ReillyBova/Point-Cloud-Registration)基础上的拓展，新增了基于FPFH特征的快速全局配准（Fast Global Registration）功能。
通过Open3D库中的FPFH特征描述符和特征匹配算法，本项目实现了点云数据的快速粗配准，为精确配准提供了一个接近正确的初始对齐估计。

这个代码库包含了一个使用 Python 3 编写的脚本，实现了点云的迭代最近点（ICP）算法，用于 3D 点云的配准。由于是ICP点对面算法，主要针对带有法向量的bunny数据集进行适配，也可对计算法向量后的bunny点云数据集进行配准。
增加txt格式的输出，以方便配合CloudCompare使用。

数据集：源自斯坦福3D扫描存储库，一个在学术界广泛认可的资源，提供原始的PLY格式点云数据。

数据集路径为`bunny/`。

## 开始

按照以下说明，您可以在本地机器上运行这个脚本（注意：这个脚本只在 windows 11 上测试过，但也应该适用于其他系统）。

### 先决条件和安装

这个项目配准部分只需要 Python 3 和 [NumPy](http://www.numpy.org/) Python 库。用户可使用 pip 或 conda 来安装 NumPy。

要对没有法向量的数据集进行法向量计算，则需要安装Open3D 软件包，使用现有的Open3D的库函数进行法向量计算，并将格式转为pts格式。
```
python PLY_PTS.py bunny/data/bun000.ply
python PLY_PTS.py bunny/data/bun045.ply
python PLY_PTS.py bunny/data/bun090.ply
python PLY_PTS.py bunny/data/bun180.ply
python PLY_PTS.py bunny/data/bun270.ply
python PLY_PTS.py bunny/data/bun315.ply
python PLY_PTS.py bunny/data/chin.ply
python PLY_PTS.py bunny/data/ear_back.ply
python PLY_PTS.py bunny/data/top2.ply
python PLY_PTS.py bunny/data/top3.ply
```
并进行快速全局配准（Fast Global Registration）粗配准，获取转移矩阵，得到一个较好的初始位置。
获得的转移矩阵文件需要放到对应配准点云数据文件夹下。

```
python registration.py bunny/data/bun045.ply bunny/data/bun000.ply
python registration.py bunny/data/bun090.ply bunny/data/bun045.ply
python registration.py bunny/data/bun315.ply bunny/data/bun000.ply
python registration.py bunny/data/bun270.ply bunny/data/bun315.ply
python registration.py bunny/data/bun180.ply bunny/data/bun090.ply
python registration.py bunny/data/chin.ply bunny/data/bun315.ply
python registration.py bunny/data/ear_back.ply bunny/data/bun180.ply
python registration.py bunny/data/top2.ply bunny/data/bun180.ply
python registration.py bunny/data/top3.ply bunny/data/bun045.ply
```

### 运行脚本

运行这个脚本需要两对文件（总共四个文件）：`file1.pts`、`file1.xf`、`file2.pts` 和 `file2.xf`。当运行时，脚本将尝试调整 `file1.xf` 中的刚体变换，以使 `file1.pts` 中的点与通过 `file2.xf` 中的矩阵变换后的目标点对齐。最后，脚本将在 `./output/` 输出结果。

程序的执行方式如下：

```
python icp_ply_pts.py file1.pts file2.pts

```

注意 `.xf` 文件是隐含的。程序会首先在输出路径如 `./output/` 中查找 `file.xf`，然后是在提供的文件路径中查找该文件。这样做是为了避免用原始（不准确的）变换覆盖已对齐的变换。

路径`output/`为原项目输出路径， `icp_ply_pts.py` 默认输出路径为 `output01/`， `icp_pts_txt.py` 默认输出路径为 `output02/`，如果需要，用户可以更改输出路径。

## 程序解释

### 实现细节

这个程序使用了一个自定义的 Python 实现的 kd 树。

此外，该脚本严重依赖于 NumPy 库提供的矩阵操作和线性代数方法。

### 迭代点云算法

在每次 ICP 迭代中，从源数据集（`file1`）中随机采样 1000 个点，然后计算每个采样点在目标数据集（`file2`）中的最近邻。然后，应用异常值剔除，并将剩余的点输入到过度约束的线性系统中。解决这个问题后，计算出应用于源数据集的新变换矩阵，如果有显著改进的话，继续开始新的迭代周期。否则，ICP 算法终止，并给出了一个刚体变换矩阵，将源数据集中的点与目标数据集中的点对齐。

有关此算法的更多细节可以在[这里](http://www.cs.princeton.edu/courses/archive/fall18/cos526/notes/cos526_f18_lecture10_acquisition_registration.pdf)找到。

### 其他说明

这个程序包含了相当健全的错误处理，但是还没有经过严格的测试以发现错误。

## 结果

|                           配准前                           | 配准后 |
|:-------------------------------------------------------:|:----------------:|
| ![Before alignment](/results/bunny_before.png?raw=true) | ![After alignment](/results/bunny_after.png?raw=true) |

查看此项目配准前后结果，需配合CloudCompare进行查看。

要自己生成对齐的兔子，请先在icp_ply_pts.py或icp_pts_txt.py设置输出路径，或者删除原有输出文件夹，然后运行这些命令：

数据集
```

python icp_ply_pts.py .\PLY_PTS\bun045.pts .\PLY_PTS\bun000.pts
python icp_ply_pts.py .\PLY_PTS\bun090.pts .\PLY_PTS\bun045.pts
python icp_ply_pts.py .\PLY_PTS\bun315.pts .\PLY_PTS\bun000.pts
python icp_ply_pts.py .\PLY_PTS\bun270.pts .\PLY_PTS\bun315.pts
python icp_ply_pts.py .\PLY_PTS\bun180.pts .\PLY_PTS\bun270.pts
python icp_ply_pts.py .\PLY_PTS\chin.pts .\PLY_PTS\bun315.pts
python icp_ply_pts.py .\PLY_PTS\ear_back.pts .\PLY_PTS\bun180.pts
python icp_ply_pts.py .\PLY_PTS\top2.pts .\PLY_PTS\bun180.pts
python icp_ply_pts.py .\PLY_PTS\top3.pts .\PLY_PTS\bun000.pts

```

采样的平均距离的结果输出会追加到对应的txt文件中。

## 作者

* **熊泰** 


## 参考文献
[1] Rusinkiewicz, S.; Levoy, M. Efficient Variants of the ICP Algorithm. In Proceedings Third International Conference on 3-D Digital Imaging and Modeling; 2001; pp 145–152. https://doi.org/10.1109/IM.2001.924423. 

## 许可证

此项目根据 MIT 许可证获得许可 - 有关详细信息，请参见 [LICENSE.md](LICENSE.md) 文件。

## 致谢

特别感谢 Reilly Bova 公开其 [Point-Cloud-Registration](https://github.com/ReillyBova/Point-Cloud-Registration) 项目。该项目不仅为我提供了实践点云配准算法的宝贵资源，还极大地启发了我的思路和方法。

此外，还要对Open3D社区表示衷心的感谢，Open3D是一个功能强大且易于使用的开源库。

