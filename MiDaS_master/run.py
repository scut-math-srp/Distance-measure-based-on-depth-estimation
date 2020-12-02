"""Compute depth maps for images in the input folder.
"""
import os
import glob
import torch
from MiDaS_master import utils
import cv2
import numpy as np
from torchvision.transforms import Compose
from MiDaS_master.models.midas_net import MidasNet
from MiDaS_master.models.transforms import Resize, NormalizeImage, PrepareForNet


def run(input_path, output_path, model_path):
    """Run MonoDepthNN to compute depth maps.

    Args:
        input_path (str): path to input folder
        output_path (str): path to output folder
        model_path (str): path to saved model
    """
    print("initialize")
    prediction_lst = []
    # select device
    device = torch.device("cuda")
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

    # get input
    img_names = glob.glob(os.path.join(input_path, "*"))
    num_images = len(img_names)

    # create output folder
    os.makedirs(output_path, exist_ok=True)

    print("start processing")
    for ind, img_name in enumerate(img_names):
        print("  processing {} ({}/{})".format(img_name, ind + 1, num_images))

        # input

        img = utils.read_image(img_name)
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
        filename = os.path.join(
            output_path, os.path.splitext(os.path.basename(img_name))[0]
        )
        utils.write_depth(filename, prediction, bits=2)
        prediction_lst.append(prediction)  # 添加
    print("finished")
    return prediction_lst  # 添加


def new_run(input_path, output_path, model_path):
    """
    对run函数的改动
    用于新程序
    """
    # select device
    device = torch.device("cuda")
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

    # create output folder
    os.makedirs(output_path, exist_ok=True)

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
    filename = os.path.join(
        output_path, os.path.splitext(os.path.basename(input_path))[0]
    )
    out = utils.write_depth(filename, prediction, bits=2)

    return prediction, out


if __name__ == "__main__":
    # set paths
    # dirpath = os.path.dirname(__file__)
    INPUT_PATH = "MiDaS_master/input"
    OUTPUT_PATH = "MiDaS_master/output"
    # MODEL_PATH = "model.pt"
    MODEL_PATH = "MiDaS_master/model.pt"

    # set torch options
    torch.backends.cudnn.enabled = True
    torch.backends.cudnn.benchmark = True

    # compute depth maps
    prediction = run(INPUT_PATH, OUTPUT_PATH, MODEL_PATH)
    np.savetxt('result.csv', prediction[0], delimiter=',')
