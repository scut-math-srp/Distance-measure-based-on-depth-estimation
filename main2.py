import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import windnd

from FCRN import predict
from MiDaS import run
from MegaDepth import demo

# 全局变量
width = 600     # 帆布组件的宽度
height = 450    # 帆布组件的高度
input_path = None   # 原图片路径
depth = None    # 深度值矩阵
result = False    # 生成深度图状态，若已生成深度图，则为True，可以保存


def show_image(image, canvas):
    """
    将图片加载到帆布中

    :param images: 要加载的文件路径
    :param canvas: 展示图片的帆布组件
    :return: None
    """
    image_open = Image.open(image)   # 加载图片
    image_resize = image_open.resize((width, height))   # 缩放图片
    image_tk = ImageTk.PhotoImage(image_resize)    # 利用PIL包将图片转化tkinter兼容的格式
    canvas.create_image(0, 0, anchor='nw', image=image_tk)    # 在canvas中显示图像
    canvas.image = image_tk   # 保留对图像对象的引用，使图像持续显示
    return


def show_input(images):
    """
    将拖拽的图片加载到原图帆布中

    :param images: 拖拽获得的文件列表
    :return: None
    """
    global input_path
    input_path = images[0].decode()   # 获取拖拽文件列表中第一个文件的路径（str类型）
    show_image(input_path, work_input_cv)   # 将文件加载到原图帆布中
    return


def download_weight():
    return


def unzip_weight():
    return


def select_weight(*args):
    """
    选择算法后自动绑定对应的权重选项（暂未实现权重选择功能）

    :param args: 可变参数，没啥用
    :return: None
    """
    if tool_depth_cbb1.get() == 'FCRN':
        tool_depth_cbb2['value'] = 'NYU_FCRN.ckpt'
    elif tool_depth_cbb1.get() == 'MiDaS':
        tool_depth_cbb2['value'] = 'model.pt'
    elif tool_depth_cbb1.get() == 'MegaDepth':
        tool_depth_cbb2['value'] = 'best_generalization_net_G.pth'
    tool_depth_cbb2.current(0)    # 设置初始权重选项
    return


def show_output():
    """
    运行对应算法，返回深度值矩阵，将图片保存到根目录；再将图片加载到深度图帆布中；所有功能用一个函数搞定

    :return: None
    """
    global result, depth
    if tool_depth_cbb1.get() == 'FCRN':
        depth = predict.predict(model_data_path='FCRN/NYU_FCRN.ckpt', image_path=input_path)
    elif tool_depth_cbb1.get() == 'MiDaS':
        # 函数修改中：depth, _ = run.new_run(input_path=input_path, output_path='/', model_path='MiDaS/model.pt')
        return
    elif tool_depth_cbb1.get() == 'MegaDepth':
        # 函数修改中
        return

    show_image('pred.jpg', work_output_cv)    # 将生成图加载到深度图帆布中
    result = True  # 深度图已生成，可以保存
    return


def save_output():
    """
    保存生成的深度图

    :return: None
    """
    if result:
        filename = filedialog.asksaveasfilename(defaultextension='.jpg',    # 默认文件拓展名
                                                filetypes=[('JPG', '*.jpg')],   # 设置文件类型选项
                                                initialdir='',  # 默认路径
                                                initialfile='深度估计',     # 默认文件名
                                                parent=window,  # 父对话框
                                                title='保存')
        if filename != '':  # 取消保存时返回空字符
            image = Image.open('pred.jpg')
            image.save(filename)
    else:
        messagebox.showerror('错误', '未生成深度估计图')
    return


def measure_dist():
    return


# 窗口界面
window = tk.Tk()
window.title('深度估计')

# 菜单栏 menu bar
menu = tk.Menu(window)
window.config(menu=menu)

menu_file = tk.Menu(menu)                       # 文件菜单
menu_file.add_command(label='打开')             # 打开图片
menu_file.add_command(label='保存')             # 保存图片
menu.add_cascade(label='文件', menu=menu_file)

menu_help = tk.Menu(menu)                       # 帮助菜单
menu_help.add_command(label='说明')
menu.add_cascade(label='帮助', menu=menu_help)

# 工具栏 tool bar
tool = tk.Frame(window)
tool.pack(anchor='w')

tool_depth = tk.LabelFrame(tool, text='深度估计', labelanchor='s')   # 深度估计方法框架
tool_depth.pack(side='left', fill='y')
tool_depth_lb1 = tk.Label(tool_depth, text='算法')                       # 算法
tool_depth_lb1.grid(row=1, column=1)
tool_depth_cbb1 = ttk.Combobox(tool_depth, state='readonly')
tool_depth_cbb1.grid(row=1, column=2)
tool_depth_cbb1.bind('<<ComboboxSelected>>', select_weight)           # 选择算法后自动绑定对应权重
tool_depth_cbb1['values'] = ('FCRN', 'MiDaS', 'MegaDepth')
tool_depth_lb2 = tk.Label(tool_depth, text='权重')                      # 权重
tool_depth_lb2.grid(row=2, column=1)
tool_depth_cbb2 = ttk.Combobox(tool_depth, state='readonly')
tool_depth_cbb2.grid(row=2, column=2)
tool_depth_bt = tk.Button(tool_depth, text='生成', command=show_output)
tool_depth_bt.grid(row=1, column=3, rowspan=2)

tool_dist = tk.LabelFrame(tool, text='距离测量', labelanchor='s')     # 距离测量框架
tool_dist.pack(side='left', fill='y')
tool_dist_lb1 = tk.Label(tool_dist, text='焦距')                      # 焦距
tool_dist_lb1.grid(row=1, column=1)
tool_dist_etr = tk.Entry(tool_dist)
tool_dist_etr.grid(row=1, column=2)
tool_dist_lb10 = tk.Label(tool_dist, text='(cm)')
tool_dist_lb10.grid(row=1, column=3)
tool_dist_lb2 = tk.Label(tool_dist, text='比例尺')                        # 比例尺
tool_dist_lb2.grid(row=2, column=1)
tool_dist_etr = tk.Entry(tool_dist)
tool_dist_etr.grid(row=2, column=2)

tool_visual = tk.LabelFrame(tool, text='可视化效果', labelanchor='s')    # 可视化效果
tool_visual.pack(side='left', fill='y')
tool_visual_lb = tk.Label(tool_visual, text='颜色')                       # 颜色
tool_visual_lb.grid(row=1, column=1)
tool_visual_cbb = ttk.Combobox(tool_visual)
tool_visual_cbb.grid(row=1, column=2)

# 工作区域（主界面） working area
work = tk.Frame(window)
work.pack()

work_input_cv = tk.Canvas(work, width=width, height=height, bg='white')      # 原图帆布
work_input_cv.create_text(width / 2, height / 2, text='拖拽图片到此处', fill='grey', anchor='center')
work_input_cv.pack(side='left')
windnd.hook_dropfiles(work_input_cv, func=show_input)                     # 将拖拽图片与wa_input_cv组件挂钩

work_output_cv = tk.Canvas(work, width=width, height=height, bg='white')     # 深度图帆布
work_output_cv.pack(side='right')

# 状态栏 status bar
status = tk.Frame(window)
status.pack(anchor='e')

status_message_lb1 = tk.Label(status, text='A点：')       # A点信息
status_message_lb1.pack(side='left')
status_message_lb11 = tk.Label(status, text='坐标：')
status_message_lb11.pack(side='left')
status_message_lb12 = tk.Label(status, text='深度：')
status_message_lb12.pack(side='left')

status_message_lb01 = tk.Label(status, text='  ')        # 间隔
status_message_lb01.pack(side='left')

status_message_lb2 = tk.Label(status, text='B点：')       # B点信息
status_message_lb2.pack(side='left')
status_message_lb21 = tk.Label(status, text='坐标：')
status_message_lb21.pack(side='left')
status_message_lb22 = tk.Label(status, text='深度：')
status_message_lb22.pack(side='left')

status_message_lb02 = tk.Label(status, text='  ')       # 间隔
status_message_lb02.pack(side='left')

status_message_lb3 = tk.Label(status, text='距离：')       # 距离
status_message_lb3.pack(side='left')


window.mainloop()
