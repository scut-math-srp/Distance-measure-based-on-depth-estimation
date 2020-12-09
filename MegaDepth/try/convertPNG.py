'''from skimage import io, img_as_float, img_as_ubyte, color
import numpy as np

path = r"C:Users\Administrator.DESKTOP-K87E7J1\Desktop\MegaDepth-master\demo_img\demo.jpg"
img = io.imread(path)
gray = color.rgb2gray(img)
rows, cols = gray.shape
labels = np.zeros([rows, cols])
for i in range(rows):
    for j in range(cols):
        if (gray[i, j] < 0.4):
            labels[i, j] = 0
        elif (gray[i, j] < 0.75):
            labels[i, j] = 1
        else:
            labels[i, j] = 2

dst = color.label2rgb(labels)
io.imshow(dst)
io.show()
'''

from skimage import io,img_as_float,img_as_ubyte,color

path = r"C:\Users\Administrator.DESKTOP-K87E7J1\Desktop\MegaDepth-master\demo_img\demo.png"

#输出原图
img = io.imread(path)
io.imshow(img)
io.show()

#输出灰度图
gray = color.gray2rgb(img)
io.imshow(gray)
io.show()

#输出rgb图
rgb=color.gray2rgb(img)
io.imshow(rgb)
io.show()
