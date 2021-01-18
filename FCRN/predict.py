import numpy as np
import tensorflow as tf
from matplotlib import pyplot as plt
from PIL import Image

from FCRN_master import models


def predict(model_data_path, image_path):
    # Default input size
    height = 228
    width = 304
    channels = 3
    batch_size = 1

    # Read image
    img = Image.open(image_path)
    img = img.resize([width, height], Image.ANTIALIAS)
    img = np.array(img).astype('float32')
    img = np.expand_dims(np.asarray(img), axis=0)

    # Create a placeholder for the input image
    input_node = tf.placeholder(tf.float32, shape=(None, height, width, channels))

    # Construct the network
    net = models.ResNet50UpProj({'data': input_node}, batch_size, 1, False)

    with tf.Session() as sess:
        tf.get_variable_scope().reuse_variables()
        # Load the converted parameters

        # Use to load from ckpt file
        saver = tf.train.Saver()
        saver.restore(sess, model_data_path)

        # Use to load from npy file
        # net.load(model_data_path, sess)

        # Evaluate the network for the given image
        pred = sess.run(net.get_output(), feed_dict={input_node: img})

        # Plot result
        fig = plt.figure()
        # 可修改colormap，cmap=plt.cm.jet
        ii = plt.imshow(pred[0, :, :, 0], interpolation='nearest', cmap=plt.cm.jet)
        # 去掉坐标轴
        plt.axis('off')
        # 去掉图像边缘
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1)
        # 保存生成图片
        plt.savefig('pred.jpg')
        return pred
