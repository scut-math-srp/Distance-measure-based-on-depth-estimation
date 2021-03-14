# Distance-measure-based-on-depth-estimation
This is a repository of SRP2020 for bears. Here we make a software to measure the distance between any two points on any images based on some depth estimation algorithms. 

## TODO list
- [ ] A better UI
- [ ] Use focal length into the calculating of distances

## parameter files:
- put in MiDaS: [model.pt](https://drive.google.com/file/d/1zQAV1YODL9uaalPBOZGVGevctCYiY8-l/view?usp=sharing)
- put in FRCN: 
  - [NYU_FCRN.ckpt.data-00000-of-00001](https://drive.google.com/file/d/1TTDdFT3LcKoVTDCFEFTYarhOKpISmHPN/view?usp=sharing)
  - [NYU_FCRN.ckpt.meta](https://drive.google.com/file/d/1wdUh-22jxhBHLKHK8qvFsHXHncCoMsFO/view?usp=sharing)


# Distance-measure-based-on-depth-estimation 2.0

## 更新重点

1. 重写用户界面，其风格类似word，交互逻辑更为清晰，其结构如下
   - 菜单栏 menu bar（暂无功能）
   - 工具栏 tool bar
      - **深度估计**
      - **距离测量**（暂无功能），
      - **可视化效果**（暂无功能）
   - 工作区 working area
      - 原图显示区
      - 深度图显示区
   - 状态栏 status bar
      - A点：坐标，深度
      - B点：坐标，深度
      - 两点距离
2. 整理代码，提高可读性，便于维护

   - 将函数部分与界面部分分开，每个函数补充注释内容，使函数更容易理解
   
   - 将`show_input`函数中关于打开并加载图片到工作区的部分分离出来单独写一个函数，这样`show_output`函数也可以调用这一部分，减少不必要的代码
   
   - 规范`show_output`函数，识别用户选择的算法后，使用一个函数实现**保存深度图到根目录**、**返回深度值矩阵**两个功能（通过修改对应算法文件中的函数），再将深度图加载到工作区
   
     > 目前仅完成**FCRN**函数的修改，**MiDaS**和**MegaDepth**已经在修改中，将会在后续版本中给出

# Distance-measure-based-on-depth-estimation 3.0

## 更新重点

1. 整理main2.py文件，取消global变量的使用，添加了tkwindow类，窗口相关定义放在类中
   
2. 将深度估计、距离计算、状态栏显示等方法放在utils.py文件中

     > 四种算法的深度估计均已完成，除**FRCN**算法无返回深度矩阵外，其他均已完成距离计算
     

# Distance-measure-based-on-depth-estimation 4.0

## 更新重点

1. 新增
   + 菜单栏
     + 打开图片功能
     + 保存深度图功能
   + 工具栏
     + 深度估计——权重显示功能（暂不具备权重选择功能）
     + 可视化效果——颜色映射
     + 可视化效果——图片方向转换功能
2. 优化
   + get_depth函数
     + 统一对于不同算法的调用模式
     + 分离保存深度图片功能
3. 修复
   + MegaDepth算法找不到权重文件的问题


## References
[1] Ranftl, René, Katrin Lasinger, David Hafner, Konrad Schindler, and Vladlen Koltun. “Towards Robust Monocular Depth Estimation: Mixing Datasets for Zero-Shot Cross-Dataset Transfer.” ArXiv:1907.01341 [Cs], December 6, 2019. http://arxiv.org/abs/1907.01341.  
[2] Laina, Iro, Christian Rupprecht, Vasileios Belagiannis, Federico Tombari, and Nassir Navab. “Deeper Depth Prediction with Fully Convolutional Residual Networks.” ArXiv:1606.00373 [Cs], September 19, 2016. http://arxiv.org/abs/1606.00373.  
