"""Compute depth maps for images in the input folder.
"""
import torch
from MiDaS import utils
import cv2

from torchvision.transforms import Compose
from MiDaS.models.midas_net import MidasNet
from MiDaS.models.transforms import Resize, NormalizeImage, PrepareForNet

import numpy as np
from matplotlib import pyplot as plt

model_path = 'MiDaS/model.pt'


def write_depth(depth, bits=1):
    """Write depth map to pfm and png file.

    Args:
        path (str): filepath without extension
        depth (array): depth
    """

    depth_min = depth.min()
    depth_max = depth.max()

    max_val = (2**(8*bits))-1

    if depth_max - depth_min > np.finfo("float").eps:
        out = max_val * (depth - depth_min) / (depth_max - depth_min)
    else:
        out = 0

    return out


def get_depth(input_path):
    """Run MonoDepthNN to compute depth maps.

    Args:
        input_path (str): path to input folder
        model_path (str): path to saved model
    """
    # select device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("device: %s" % device)

    # load network
    model = MidasNet(model_path, non_negative=True)

    transform = Compose(
        [
            Resize(
                384,
                384,
                resize_target=None,
                keep_aspect_ratio=True,
                ensure_multiple_of=32,
                resize_method="upper_bound",
                image_interpolation_method=cv2.INTER_CUBIC,
            ),
            NormalizeImage(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            PrepareForNet(),
        ]
    )

    model.to(device)
    model.eval()

    # input

    img = utils.read_image(input_path)
    img_input = transform({"image": img})["image"]

    # compute
    with torch.no_grad():
        sample = torch.from_numpy(img_input).to(device).unsqueeze(0)
        prediction = model.forward(sample)
        prediction = (
            torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=img.shape[:2],
                mode="bicubic",
                align_corners=False,
            )
                .squeeze()
                .cpu()
                .numpy()
        )

    # output
    out = write_depth(prediction, bits=2)
    plt.imsave('pred.jpg', out)

    return prediction