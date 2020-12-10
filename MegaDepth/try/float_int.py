from skimage import io, img_as_float, img_as_ubyte

if __name__ == '__main__':
    path = r"E:\PythonProjects\python_common\skimage\images\lena.jpg"
    img = io.imread(path)
    print('img type name = {}'.format(img.dtype.name))
    """1 、unit8 to float"""
    unit8_float = img_as_float(img)
    print('float_img type name = {}'.format(unit8_float.dtype.name))
    """2、float to unit8"""
    float_unit8 = img_as_ubyte(unit8_float)
    print('float_unit8 type name = {}'.format(float_unit8.dtype.name))

