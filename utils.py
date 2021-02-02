import math


def get_depth(algorithm, image_path):
    """
    根据选择的算法和图片的路径，计算并返回深度值矩阵，保存深度图

    :param algorithm:   选择的算法名称
    :param image_path:  要估计深度的图片路径
    :return depth:  深度估计矩阵
    """
    if algorithm == 'FCRN':
        from FCRN.obtain_depth import get_depth

    elif algorithm == 'MiDaS':
        from MiDaS.obtain_depth import get_depth

    elif algorithm == 'MegaDepth':
        from MegaDepth.obtain_depth import get_depth

    elif algorithm == 'Monodepth2':
        from monodepth2.obtain_depth import get_depth

    depth_map = get_depth(image_path)   # 返回深度矩阵，保存深度图
    return depth_map


def check_num(entry):
    """
    检测输入是否为数字
    """
    lst = list(entry.get())
    for i in range(len(lst)):
        if lst[i] not in ".0123456789":
            entry.delete(i, i + 1)
    if lst.count('.') == 2:
        entry.delete(len(lst) - 1, len(lst))


class Line:
    """
    用于选点时的事件及计算
    """

    def __init__(self, width, height):
        """

        :param width:  画布canvas宽度
        :param height:  画布canvas高度
        """
        self.width = width
        self.height = height
        self.image_width = 0
        self.image_height = 0
        self.canvas = None
        self.depth = None

        self.start_point = None  # 画出选中的第一点
        self.line = None  # 画出两点间的连线
        self.end_point = None  # 画出选中的第二点
        self.text_dis = None  # 距离信息

        self.start_canvas_x, self.start_canvas_y = 0, 0  # 选中第一点在canvas中的x, y坐标
        self.start_x, self.start_y = 0, 0  # 选中第一点的x, y坐标
        self.text_x, self.text_y = 0, 0  # 距离信息所在点的坐标

        # 初始化焦距等参数
        self.dx = 36
        self.dy = 24
        self.focal_length = 4.5

        self.dis_para = 1  # 比例尺参数
        self.dis = 0  # 距离

    def get_canvas(self, canvas):
        self.canvas = canvas

    def get_image_size(self, image):
        self.image_width = image.size[0]
        self.image_height = image.size[1]

    def get_depth(self, depth):
        self.depth = depth

    def set_range(self, x, y):
        """
        将canvas中选中点的坐标转化成在原图中的坐标
        :param x: 选中点的x坐标
        :param y: 选中点的y坐标
        :return x_pro, y_pro: 返回还原后的坐标
        """
        x_pro = round(x * self.image_width / self.width)
        y_pro = round(y * self.image_height / self.height)
        x_pro = min(max(x_pro, 0), self.image_width - 1)
        y_pro = min(max(y_pro, 0), self.image_height - 1)

        return x_pro, y_pro

    def update_focal(self, focal_entry):
        """
        检测输入焦距是否合法，并更新焦距
        :param focal_entry: 焦距文本框中输入的焦距
        :return:
        """
        check_num(focal_entry)
        focal = float(focal_entry.get())
        self.focal_length = focal

    def click(self, event, window):
        """
        点击cavans事件
        :param window: tk窗口
        :param event:
        :return:
        """
        self.start_x, self.start_y = self.set_range(event.x, event.y)

        self.canvas.delete(self.start_point, self.line, self.end_point, self.text_dis)
        self.start_point = self.canvas.create_rectangle(event.x - 2, event.y - 2, event.x + 2, event.y + 2,
                                                        outline='red',
                                                        fill='red')
        self.start_canvas_x, self.start_canvas_y = event.x, event.y

        # 更改状态栏
        if self.depth is not None:
            window.status_message_lb1_ord.config(text='({0}, {1})'.format(self.start_x, self.start_y))
            window.status_message_lb1_dep.config(text='{0}'.format(self.depth[self.start_y, self.start_x]))

        return

    def move(self, event, window):
        """
        移动鼠标事件
        :param window: tk窗口
        :param event:
        :return:
        """
        self.canvas.delete(self.line, self.end_point)
        self.line = self.canvas.create_line(self.start_canvas_x, self.start_canvas_y, event.x, event.y, fill='red',
                                            width=2)
        self.end_point = self.canvas.create_rectangle(event.x - 2, event.y - 2, event.x + 2, event.y + 2, outline='red',
                                                      fill='red')
        return

    def release(self, event, window):
        """
        canvas中松开鼠标事件
        :param window: tk窗口
        :param event:
        :return:
        """
        end_x, end_y = self.set_range(event.x, event.y)
        if self.depth is not None:
            str_dis = self.get_dis(self.start_x, self.start_y, end_x, end_y)
            self.text_x = (self.start_canvas_x + event.x) // 2
            self.text_y = (self.start_canvas_y + event.y) // 2 - 5
            self.text_dis = self.canvas.create_text(self.text_x, self.text_y, text=str_dis, fill='red',
                                                    font=('Helvetica', '20', 'bold'))

            # 更改状态栏
            window.status_message_lb2_ord.config(text='({0}, {1})'.format(end_x, end_y))
            window.status_message_lb2_dep.config(text='{0}'.format(self.depth[end_y, end_x]))
            window.status_message_dis.config(text='{0}'.format(str_dis))
        else:
            return

    def get_dis(self, u1, v1, u2, v2):
        """
        计算距离
        :param u1: 第一点的x坐标
        :param v1: 第一点的y坐标
        :param u2: 第二点的x坐标
        :param v2: 第二点y的坐标
        :return str_dis: 估计距离的字符串
        """

        u0, v0 = 0.5 * self.image_width, 0.5 * self.image_height
        z1, z2 = self.depth[v1, u1], self.depth[v2, u2]
        x1 = ((u1 - u0) * self.dx * z1) / self.focal_length
        y1 = ((v1 - v0) * self.dy * z1) / self.focal_length
        x2 = ((u2 - u0) * self.dx * z2) / self.focal_length
        y2 = ((v2 - v0) * self.dy * z2) / self.focal_length

        self.dis = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2) * self.dis_para
        str_dis = str(round(self.dis, 2)) + 'mm'

        return str_dis

    def alter_dis(self, str_dis):
        """

        :param str_dis: 输入的修正坐标值
        :return dis_para: 返回更改后的比例尺，在窗口中修正
        """
        if str_dis:
            self.canvas.delete(self.text_dis)
            self.text_dis = self.canvas.create_text(self.text_x, self.text_y, text=str_dis + 'mm', fill='red',
                                                    font=('Helvetica', '20', 'bold'))
            new_dis = float(str_dis)
            self.dis_para *= (new_dis / self.dis)
            self.dis = new_dis
            return self.dis_para
        return
