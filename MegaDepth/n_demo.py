import tensorflow as tf
import torch
from torch.autograd import Variable    # autograd自动求导
import numpy as np
from MegaDepth.options.train_options import TrainOptions
from MegaDepth.models.models import create_model
from skimage import io, img_as_float, img_as_ubyte
from skimage.transform import resize
import os

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# 全局变量
parameters = None
img_path = 'MegaDepth/demo_img/demo.jpg'
input_height = 384
input_width = 512


def test_simple(model):
    # total_loss = 0
    # toal_count = 0
    print()
    print("============================= TEST ============================")
    model.switch_to_eval()

    img = io.imread(img_path)
    img = img_as_float(img)     # img = np.float32(img)/255.0
    img = resize(img, (input_height, input_width), order=1)
    input_img = torch.from_numpy(np.transpose(img, (2, 0, 1))).contiguous().float()
    input_img = input_img.unsqueeze(0)

    input_images = Variable(input_img.to(device))
    pred_log_depth = model.netG.forward(input_images)
    pred_log_depth = torch.squeeze(pred_log_depth)
    pred_depth = torch.exp(pred_log_depth)
    '''
    visualize prediction using inverse depth, so that we don't need sky segmentation 
    (if you want to use RGB map for visualizationyou have to run semantic segmentation to mask 
    the sky first since the depth of sky is random from CNN)
    '''
    pred_inv_depth = 1/pred_depth
    pred_inv_depth = pred_inv_depth.data.cpu().numpy()
    pred_inv_depth = pred_inv_depth/np.amax(pred_inv_depth)
    # you might also use percentile for better visualization
    pred_inv_depth = img_as_ubyte(pred_inv_depth)  # float to unit8
    po = 'MegaDepth/demo_img/demo1.jpg'
    io.imsave(po, pred_inv_depth)  # 保存预测深度图

    return pred_inv_depth                         # 返回深度信息


def run(image_in, parameter):
    global img_path, parameters
    image_in_number = io.imread(image_in)          # 从指定位置读取图片
    image_in_path = 'MegaDepth/demo_img/demo.jpg'
    io.imsave(image_in_path, image_in_number)      # 将图片保存到指定文件夹
    parameters = os.path.basename(parameter)       # 获得参数文件名
    parameters = parameters[0:-10:]                # 将参数文件名转化为指定文件名
    opt = TrainOptions().parse()                   # set CUDA_VISIBLE_DEVICES before import torch
    model = create_model(opt, parameters)
    pred_depth = test_simple(model)                # 获得深度信息
    position = 'MegaDepth/demo_img/demo1.jpg'
    io.imsave(position, pred_depth)                # 保存预测深度图
    print("We are done")
    return pred_depth, position                    # 返回深度信息和深度图位置



