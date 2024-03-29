import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import windnd
import matplotlib.pyplot as plt

from utils import get_depth, Line, check_num


class Tkwindow:
    """
    窗口类，用于生成主窗口，拖动并显示图片，选择算法参数等功能
    """
    def __init__(self, root):
        self.root = root    # 父窗口
        self.width = 600    # 帆布组件的宽度
        self.height = 450   # 帆布组件的高度
        self.input_path = None  # 原图片路径
        self.depth = None   # 深度值矩阵
        self.result = False     # 生成深度图状态，若已生成深度图，则为True，可以保存
        self.resize_id = None
        self.line = None        # 初始化用于utils计算的类
        self.algorithm = {
            'FCRN': 'NYU_FCRN.ckpt',
            'MiDaS': 'model.pt',
            'MegaDepth': 'best_generalization_net_G.pth',
            'monodepth2': 'mono+stereo_1024x320'}    # 算法对应的权重
        self.cmaps = [
            ('Perceptually Uniform Sequential', [
                'viridis', 'plasma', 'inferno', 'magma', 'cividis']),
            ('Sequential', [
                'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
                'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']),
            ('Sequential (2)', [
                'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
                'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
                'hot', 'afmhot', 'gist_heat', 'copper']),
            ('Diverging', [
                'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
                'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']),
            ('Cyclic', [
                'twilight', 'twilight_shifted', 'hsv']),
            ('Qualitative', [
                'Pastel1', 'Pastel2', 'Paired', 'Accent',
                'Dark2', 'Set1', 'Set2', 'Set3',
                'tab10', 'tab20', 'tab20b', 'tab20c']),
            ('Miscellaneous', [
                'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
                'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
                'gist_rainbow', 'rainbow', 'jet', 'turbo', 'nipy_spectral',
                'gist_ncar'])]  # 深度图颜色选项

        # 菜单栏 menu bar
        self.menu = tk.Menu(root)
        root.config(menu=self.menu)

        # 工具栏 tool bar
        self.tool = tk.Frame(root)

        self.tool_depth = tk.LabelFrame(self.tool, text='深度估计', labelanchor='s')   # 深度估计方法框架
        self.tool_depth_cbb1 = ttk.Combobox(self.tool_depth, state='readonly')
        self.tool_depth_cbb2 = ttk.Combobox(self.tool_depth, state='readonly')

        self.tool_dist = tk.LabelFrame(self.tool, text='距离测量', labelanchor='s')  # 距离测量框架
        self.tool_dist_etr = tk.Entry(self.tool_dist)   # 输入焦距
        self.tool_dist_lb3 = tk.Label(self.tool_dist, text='1')     # 比例尺信息

        self.tool_dist_alter = tk.LabelFrame(self.tool, text='距离修改', labelanchor='s')  # 距离修正框架

        self.tool_visual = tk.LabelFrame(self.tool, text='可视化效果', labelanchor='s')  # 可视化效果框架
        self.tool_visual_cbb = ttk.Combobox(self.tool_visual)

        # 工作区域（主界面） working area
        self.work = tk.Frame(root)
        self.work_output_cv = tk.Canvas(self.work, width=self.width, height=self.height, bg='white')  # 深度图帆布
        self.work_input_cv = tk.Canvas(self.work, width=self.width, height=self.height, bg='white')  # 原图帆布

        # 状态栏 status bar
        self.status = tk.Frame(root)
        self.status_message_lb1_ord = tk.Label(self.status, text='')  # A点坐标值
        self.status_message_lb1_dep = tk.Label(self.status, text='')  # A点深度值
        self.status_message_lb2_ord = tk.Label(self.status, text='')  # B点坐标值
        self.status_message_lb2_dep = tk.Label(self.status, text='')  # B点深度值
        self.status_message_dis = tk.Label(self.status, text='')    # 距离值

    def init_menu(self):
        """
        初始化菜单栏
        """
        menu_file = tk.Menu(self.menu)  # 文件菜单
        menu_file.add_command(label='打开', command=self.open_input)  # 打开图片
        menu_file.add_command(label='保存', command=self.save_output)  # 保存图片
        self.menu.add_cascade(label='文件', menu=menu_file)

        menu_help = tk.Menu(self.menu)  # 帮助菜单
        menu_help.add_command(label='说明')
        self.menu.add_cascade(label='帮助', menu=menu_help)

    def init_toolbar(self):
        """
        初始化工具栏
        """
        self.tool.pack(anchor='w')

        # 深度估计框架
        self.tool_depth.pack(side='left', fill='y')

        tool_depth_lb1 = tk.Label(self.tool_depth, text='算法')   # 算法
        tool_depth_lb1.grid(row=1, column=1)
        self.tool_depth_cbb1.grid(row=1, column=2)
        self.tool_depth_cbb1.bind('<<ComboboxSelected>>', self.select_weight)   # 选择算法后自动绑定对应权重
        self.tool_depth_cbb1['values'] = list(self.algorithm.keys())

        tool_depth_lb2 = tk.Label(self.tool_depth, text='权重')   # 权重
        tool_depth_lb2.grid(row=2, column=1)
        self.tool_depth_cbb2.grid(row=2, column=2)
        tool_depth_bt = tk.Button(self.tool_depth, text='生成', command=self.show_output)
        tool_depth_bt.grid(row=1, column=3, rowspan=2)

        # 距离测量框架
        self.tool_dist.pack(side='left', fill='y')

        tool_dist_lb1 = tk.Label(self.tool_dist, text='焦距')     # 焦距
        tool_dist_lb1.grid(row=1, column=1)
        self.tool_dist_etr.grid(row=1, column=2)    # 输入焦距信息
        self.tool_dist_etr.bind('<KeyRelease>', lambda event: self.line.update_focal(self.tool_dist_etr))   # 检测是否为数字
        tool_dist_lb10 = tk.Label(self.tool_dist, text='(mm)')
        tool_dist_lb10.grid(row=1, column=3)
        tool_dist_lb2 = tk.Label(self.tool_dist, text='比例尺')    # 比例尺
        tool_dist_lb2.grid(row=2, column=1)
        self.tool_dist_lb3.grid(row=2, column=2)    # 比例尺信息
        # tool_dist_etr = tk.Entry(self.tool_dist, text='1')
        # tool_dist_etr.grid(row=2, column=2)

        # 距离修正框架
        self.tool_dist_alter.pack(side='left', fill='y')    # 修正距离

        tool_dist_alter_lb1 = tk.Label(self.tool_dist_alter, text='修正为')
        tool_dist_alter_lb1.grid(row=1, column=1)
        tool_dist_alter_etr = tk.Entry(self.tool_dist_alter)  # 输入修正后的距离
        tool_dist_alter_etr.grid(row=1, column=2)
        tool_dist_alter_etr.bind('<KeyRelease>', lambda event: check_num(tool_dist_alter_etr))  # 检测是否为数字
        tool_dist_alter_lb2 = tk.Label(self.tool_dist_alter, text='(mm)')
        tool_dist_alter_lb2.grid(row=1, column=3)
        tool_dist_bt = tk.Button(self.tool_dist_alter, text='修改',
                                 command=lambda: self.alter_dis(tool_dist_alter_etr.get()))    # 确认修改按钮
        tool_dist_bt.grid(row=2, column=2)

        # 可视化框架
        self.tool_visual.pack(side='left', fill='y')

        tool_visual_lb = tk.Label(self.tool_visual, text='颜色')  # 颜色
        tool_visual_lb.grid(row=1, column=1)
        self.tool_visual_cbb.grid(row=1, column=2)
        self.tool_visual_cbb.bind('<<ComboboxSelected>>', self.visual)
        self.tool_visual_cbb.bind('<Return>', self.visual)
        cmaps_list = []
        for _, cmap_list in self.cmaps:
            cmaps_list = cmaps_list+cmap_list
        self.tool_visual_cbb['values'] = cmaps_list
        self.tool_visual_cbb.current(0)

        tool_visual_lb = tk.Label(self.tool_visual, text='方向')  # 方向
        tool_visual_lb.grid(row=2, column=1)
        tool_visual_br = tk.Button(self.tool_visual, text='顺时针转动', command=self.br)
        tool_visual_br.grid(row=2, column=2)

    def init_work(self):
        """
        初始化工作区域
        """
        self.work.pack()

        self.work_input_cv.text = self.work_input_cv.create_text(self.width / 2, self.height / 2,
                                                                 text='拖拽图片到此处', fill='grey', anchor='center')
        self.work_input_cv.pack(side='left')

        # 点击并移动鼠标， 测量距离
        self.work_input_cv.bind('<Button-1>', lambda event: self.line.click(event, self))
        self.work_input_cv.bind("<B1-Motion>", lambda event: self.line.move(event, self))
        self.work_input_cv.bind("<ButtonRelease-1>", lambda event: self.line.release(event, self))

        windnd.hook_dropfiles(self.work_input_cv, func=self.drag_input)  # 将拖拽图片与wa_input_cv组件挂钩

        self.work_output_cv.pack(side='right')

        self.root.bind('<Configure>', self.resize_canvas)  # 窗口属性改变时修改帆布大小

    def init_status_bar(self):
        """
        初始化状态栏
        """
        self.status.pack(anchor='e')
        status_message_lb1 = tk.Label(self.status, text='A点：')  # A点信息
        status_message_lb1.pack(side='left')
        status_message_lb11 = tk.Label(self.status, text='坐标：')
        status_message_lb11.pack(side='left')
        self.status_message_lb1_ord.pack(side='left')
        status_message_lb12 = tk.Label(self.status, text='深度：')
        status_message_lb12.pack(side='left')
        self.status_message_lb1_dep.pack(side='left')

        status_message_lb01 = tk.Label(self.status, text='  ')  # 间隔
        status_message_lb01.pack(side='left')

        status_message_lb2 = tk.Label(self.status, text='B点：')  # B点信息
        status_message_lb2.pack(side='left')
        status_message_lb21 = tk.Label(self.status, text='坐标：')
        status_message_lb21.pack(side='left')
        self.status_message_lb2_ord.pack(side='left')
        status_message_lb22 = tk.Label(self.status, text='深度：')
        status_message_lb22.pack(side='left')
        self.status_message_lb2_dep.pack(side='left')

        status_message_lb02 = tk.Label(self.status, text='  ')  # 间隔
        status_message_lb02.pack(side='left')

        status_message_lb3 = tk.Label(self.status, text='距离：')  # 距离
        status_message_lb3.pack(side='left')
        self.status_message_dis.pack(side='left')

    def resize_canvas(self, *args):
        try:
            self.root.after_cancel(self.resize_id)
        except:
            pass
        self.resize_id = self.root.after(500, self.resize_canvas1)
        return

    def resize_canvas1(self, *args):
        """
        拖拽窗口时改变帆布大小
        """
        self.width = int((self.root.winfo_width() - 8) / 2)    # 帆布边框默认宽度为2个像素
        self.height = int((self.root.winfo_height() - 97))
        if self.width / self.height < 4 / 3:
            self.height = int(self.width * 3 / 4)
        else:
            self.width = int(self.height * 4 / 3)
        self.work_input_cv.config(width=self.width, height=self.height)
        self.work_output_cv.config(width=self.width, height=self.height)
        self.work_input_cv.coords(self.work_input_cv.text, self.width / 2, self.height / 2)
        if self.input_path:
            self.show_image(self.input_path, self.work_input_cv)
        if self.result:
            self.show_image('pred.jpg', self.work_output_cv)
        return

    def drag_input(self, images):
        """
        将拖拽的图片加载到原图帆布中

        :param images: 拖拽获得的文件列表
        :return: None
        """
        self.input_path = images[0].decode()                    # 获取拖拽文件列表中第一个文件的路径（str类型）
        self.init_line()                                        # 根据图片更新line
        self.show_image(self.input_path, self.work_input_cv)    # 将文件加载到原图帆布中
        return

    def init_line(self):
        """更新line"""
        self.line = Line(self.width, self.height, self.input_path)  # 用于使用utils中的算法
        self.line.get_canvas(self.work_input_cv)
        self.tool_dist_etr.delete(0, tk.END)
        self.tool_dist_etr.insert(0, str(self.line.focal_length))
        self.tool_dist_lb3.config(text='1')

    def open_input(self):
        """
        打开图片并加载到帆布中
        """
        self.input_path = filedialog.askopenfilename(
            parent=self.root,   # 父窗口
            title='打开',     # 对话框标题
            initialdir='',  # 默认路径
            initialfile='',     # 默认文件名
            filetypes=[],     # 设置文件类型选项
            defaultextension='.jpg',    # 默认文件拓展名
            multiple=False)
        try:
            self.show_image(self.input_path, self.work_input_cv)    # 将文件加载到原图帆布中
        except:
            messagebox.showerror('错误', '无法识别的文件格式')
        return

    def show_image(self, image, canvas):
        """
        将图片加载到帆布中

        :param image: 要加载的文件路径
        :param canvas: 展示图片的帆布组件
        :return: None
        """
        image_open = Image.open(image)      # 加载图片
        image_resize = image_open.resize((self.width, self.height))   # 缩放图片
        image_tk = ImageTk.PhotoImage(image_resize)    # 利用PIL包将图片转化tkinter兼容的格式
        canvas.create_image(0, 0, anchor='nw', image=image_tk)    # 在canvas中显示图像
        canvas.image = image_tk   # 保留对图像对象的引用，使图像持续显示

        self.line.get_image_size(image_open)    # 存储图片信息，用于Line类

        return

    def select_weight(self, *args):
        """
        选择算法后自动绑定对应的权重选项（暂未实现权重选择功能）
        """
        self.tool_depth_cbb2['values'] = self.algorithm[self.tool_depth_cbb1.get()]
        self.tool_depth_cbb2.current(0)  # 设置初始权重选项
        return

    def show_output(self):
        """
        运行对应算法，返回深度值矩阵，将图片保存到根目录；再将图片加载到深度图帆布中；所有功能用一个函数搞定

        :return: None
        """
        self.depth = get_depth(self.tool_depth_cbb1.get(), self.input_path)
        self.line.get_depth(self.depth)   # 将深度矩阵传入Line类

        plt.imsave('pred.jpg', self.depth)  # 保存深度图片
        self.show_image('pred.jpg', self.work_output_cv)  # 将生成图加载到深度图帆布中
        self.result = True  # 深度图已生成，可以保存
        return

    def save_output(self):
        """
        保存生成深度图
        """
        if self.result:
            save_path = filedialog.asksaveasfilename(
                defaultextension='.jpg',    # 默认文件拓展名
                filetypes=[('JPG', '*.jpg')],   # 设置文件类型选项，目前仅支持jpg格式输出
                initialdir='',  # 默认路径
                initialfile='深度估计',     # 默认文件名
                parent=self.root,    # 父对话框
                title='保存')     # 对话框标题
            if save_path != '':  # 取消保存时返回空字符
                image = Image.open('pred.jpg')
                image.save(save_path)   # 一种比较“投机”的保存方式
        else:
            messagebox.showerror('错误', '未生成深度估计图')
        return

    def alter_dis(self, str_dis):
        """
        修正距离

        :param str_dis: 输入框中的输入的距离
        :return:
        """
        dis_para = self.line.alter_dis(str_dis)
        self.tool_dist_lb3.config(text=str(dis_para))
        return

    def visual(self, *args):
        """
        图片可视化效果
        """
        if self.result:
            try:
                plt.imsave('pred.jpg', self.depth, cmap=self.tool_visual_cbb.get())
                self.show_image('pred.jpg', self.work_output_cv)
            except:
                messagebox.showerror('错误', '指定的颜色映射不存在')
        else:
            messagebox.showerror('错误', '未生成深度估计图')
        return

    def br(self):
        '''
        对方向错误的图片进行转动
        '''
        # 工作区左侧
        im = Image.open(self.input_path)
        out = im.transpose(Image.ROTATE_270)                  # 进行旋转270
        out.save(self.input_path)
        self.show_image(self.input_path, self.work_input_cv)    # 将文件加载到原图帆布中
        # 工作区右侧
        im = Image.open('pred.jpg')
        out = im.transpose(Image.ROTATE_270)  # 进行旋转270
        out.save('pred.jpg')
        self.show_image('pred.jpg', self.work_output_cv)
        return

    def __call__(self):
        self.init_menu()
        self.init_toolbar()
        self.init_work()
        self.init_status_bar()
