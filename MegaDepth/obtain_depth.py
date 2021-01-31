import torch
from torch.autograd import Variable
import numpy as np
from MegaDepth.options.train_options import TrainOptions
from MegaDepth.models.models import create_model
from skimage import io
from skimage.transform import resize

import os
import matplotlib.pyplot as plt


model_path = 'MegaDepth/checkpoints/test_local/best_generalization_net_G.pth'

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

input_height = 384
input_width = 512


def test_simple(img_path, model):
    total_loss =0
    toal_count = 0
    print("============================= TEST ============================")
    model.switch_to_eval()

    img = np.float32(io.imread(img_path))/255.0
    img = resize(img, (input_height, input_width), order=1)
    input_img = torch.from_numpy(np.transpose(img, (2, 0, 1))).contiguous().float()
    input_img = input_img.unsqueeze(0)

    input_images = Variable(input_img.to(device))
    pred_log_depth = model.netG.forward(input_images)
    pred_log_depth = torch.squeeze(pred_log_depth)

    pred_depth = torch.exp(pred_log_depth)

    # visualize prediction using inverse depth, so that we don't need sky segmentation (if you want to use RGB map for visualization, \
    # you have to run semantic segmentation to mask the sky first since the depth of sky is random from CNN)
    pred_inv_depth = 1/pred_depth
    pred_inv_depth = pred_inv_depth.data.cpu().numpy()
    # you might also use percentile for better visualization
    pred_inv_depth = pred_inv_depth/np.amax(pred_inv_depth)

    plt.imsave('pred.jpg', pred_inv_depth)
    # print(pred_inv_depth.shape)

    return pred_inv_depth


def get_depth(img_path):
    parameters = os.path.basename(model_path)
    parameters = parameters[0:-10:]
    opt = TrainOptions().parse()  # set CUDA_VISIBLE_DEVICES before import torch
    model = create_model(opt, parameters)
    pred_depth = test_simple(img_path, model)
    return pred_depth
