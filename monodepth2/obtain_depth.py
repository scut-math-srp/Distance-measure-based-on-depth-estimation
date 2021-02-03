import os
import PIL.Image as pil
import torch
from torchvision import transforms
import cv2

from . import networks
from .utils import download_model_if_doesnt_exist
from .layers import disp_to_depth

from matplotlib import pyplot as plt


def get_depth(image_path):
        model_name = "mono+stereo_1024x320"
        # DOWNLOAD MODEL
        download_model_if_doesnt_exist(model_name) # If you wanna download weights in code, refer to this.
        model_folder = os.path.dirname(os.path.abspath(__file__)) + '/models'
        encoder_path = os.path.join(model_folder, model_name, "encoder.pth")
        depth_decoder_path = os.path.join(model_folder, model_name, "depth.pth")

        # LOADING PRETRAINED MODEL
        encoder = networks.ResnetEncoder(18, False)
        depth_decoder = networks.DepthDecoder(num_ch_enc=encoder.num_ch_enc, scales=range(4))

        loaded_dict_enc = torch.load(encoder_path, map_location='cpu')
        filtered_dict_enc = {k: v for k, v in loaded_dict_enc.items() if k in encoder.state_dict()}
        encoder.load_state_dict(filtered_dict_enc)

        loaded_dict = torch.load(depth_decoder_path, map_location='cpu')
        depth_decoder.load_state_dict(loaded_dict)

        encoder.eval()
        depth_decoder.eval()
        # LOADING IMAGE
        input_image = pil.open(image_path).convert('RGB')
        original_width, original_height = input_image.size
        # print("original size: (%s, %s)"%(original_width, original_height))

        feed_height = loaded_dict_enc['height']
        feed_width = loaded_dict_enc['width']
        input_image_resized = input_image.resize((feed_width, feed_height), pil.LANCZOS)

        input_image_pytorch = transforms.ToTensor()(input_image_resized).unsqueeze(0)

        # PREDICTING DEPTH
        with torch.no_grad():
            features = encoder(input_image_pytorch)
            outputs = depth_decoder(features)

        disp = outputs[("disp", 0)] # disparity
        # use bilinear interpolate to recover to the original size
        disp_resized = torch.nn.functional.interpolate(disp, (original_height, original_width), mode="bilinear", align_corners=False)
        disp_resized_np = disp_resized.squeeze().cpu().numpy()
        # transform disparity to depth
        scaled_disp, depth_map = disp_to_depth(disp_resized_np, 0.1, 1000)
        # print(depth_map.shape)
        # print(type(depth_map))
        
        # plot depth map
        # cv2.namedWindow("depth_map", 0)
        # cv2.imshow("depth_map", depth_map)

        return depth_map


if __name__ == "__main__":
    image_path = '../data/QQ20210119210629.jpg'
    get_depth(image_path)