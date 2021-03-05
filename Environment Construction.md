# 环境搭建说明

1. 安装Anaconda和Pycharm

   Anaconda下载地址：[https://www.anaconda.com/products/individual](https://www.anaconda.com/products/individual)

   Pycharm下载地址：[http://www.jetbrains.com/pycharm/download/#section=windows](http://www.jetbrains.com/pycharm/download/#section=windows)

2. 创建基于python3.6的虚拟环境

3. 安装依赖包

   + 安装tensorflow

     ```
     pip install tensorflow==1.14.0
     ```
      注：若已安装tensorflow 2.0版本，可将FCRN\obtain_depth.py和FCRN\predict.py和FCRN\models\network.py中
      ```
      import tensorflow as tf
      ```
       改为
      ```
      import tensorflow.compat.v1 as tf
      tf.disable_v2_behavior()
      ```
   + 安装pytorch

     ```
     pip install torch==1.7.1+cpu torchvision==0.8.2+cpu torchaudio===0.7.2 -f https://download.pytorch.org/whl/torch_stable.html
     ```

   + 安装其它依赖包

4. 下载权重文件，并放置于指定文件夹
   + 文件：NYU_FCRN.ckpt.data-00000-of-00001 
   
     放置于文件夹：Distance-measure-based-on-depth-estimation-master\FCRN
    
     下载地址：
   + 文件：model.pt
  
     放置于文件夹：Distance-measure-based-on-depth-estimation-master\MiDaS
   
     下载地址：
     
   + 文件：best_generalization_net_G.pth
  
     放置于文件夹：Distance-measure-based-on-depth-estimation-master\MegaDepth\checkpoints\test_local
   
     下载地址：http://www.cs.cornell.edu/projects/megadepth/dataset/models/best_generalization_net_G.pth
5. 运行`main.py`文件

# 软件使用说明

![软件界面](C:\Users\linyihong\AppData\Roaming\Typora\typora-user-images\image-20210222102009010.png)

1. 打开图片

   依次点击菜单栏中的`文件`按钮，`打开`按钮，会弹出一个文件对话框，选择需要的图片文件并打开即可。图像将会显示在工作区左侧。

2. 生成深度估计图

   在工具栏**深度估计**框架中的`算法`下拉栏选择算法，点击`生成`按钮，图像会根据选定的算法生成深度估计图并显示在工作区右侧。

3. 选点测距

4. 可视化效果

   在工具栏**可视化效果**框架中的`颜色`下拉栏选择颜色映射方案（可通过鼠标滚轮快速预览）。深度图颜色映射效果会实时显示在工作区右侧。
   
   在工具栏**可视化效果**框架中的`方向`栏点击`顺时针转动`可改变图片的方向。旋转后图片及其深度图将显示在工作区。

5. 保存深度估计图

   以此点击菜单栏中的`文件`按钮，`保存`按钮，会弹出一个文件对话框，选择保存图像的位置并点击保存即可。
