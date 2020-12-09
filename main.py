import tkinter as tk
import windnd
from PIL import Image, ImageTk
from tkinter import messagebox, ttk
from tkinter.filedialog import askopenfilename
import matplotlib.pyplot as plt
import math
import cv2
import numpy as np
import requests
import os
import zipfile

from FCRN_master import predict
from MiDaS_master import run
from MegaDepth import demo

# 窗口
window = tk.Toplevel()
window.title('深度估计')

# 定义canvas的height和width
width = 400
height = 300

# 输入部分
# “输入”标签
label_in = tk.Label(window, text='输入')
label_in.grid(row=1, column=1)
# 帆布
canvas_in = tk.Canvas(window, bg='white', width=width, height=height)
canvas_in.create_text(200, 150, text='拖拽图片到此处', fill='grey', anchor='center')
canvas_in.grid(row=2, column=1, rowspan=2)
# 初始化全局变量
"""image_in：输入图片；   depth：深度图；  rec：点"""
filepath, image_in, depth, rec_red, line_red, rec_red2 = None, None, None, None, None, None
"""起点横、纵坐标"""
start_x, start_y = 0, 0
"""调整系数"""
alter_dep_para = 1
alter_plain_para = 1
"""距离"""
text_dis, plain_dis, dep_dis, max_dep_dis = None, None, None, None
"""记录序号"""
record_index = 1


def show_input(file):
    global filepath, image_in
    for item in file:
        filepath = ''.join(item.decode('gbk'))
    image_open = Image.open(filepath)
    image_resize = image_open.resize((width, height))
    image = ImageTk.PhotoImage(image_resize)
    canvas_in.create_image(0, 0, anchor='nw', image=image)
    canvas_in.image = image
    image_in = image_open


windnd.hook_dropfiles(window, func=show_input)


'''输入：下载网址，保存文件路径'''


def download_weight(url, path):
    name = url.split('/')[-1]                   # 获取文件名
    response = requests.get(url, stream=True)   # 请求链接后保存到变量respone中，设置为流读取（适用于大文件下载）
    chunk_size = 1024                           # 每次下载数据块大小
    content_size = int(response.headers['content-length'])  # 下载文件大小

    download_window = tk.Tk()                   # 下载窗口初始化
    download_window.title('权重下载')
    label_download = tk.Label(download_window, text='下载进度：')
    label_download.grid(row=1, column=1)
    canvas_download = tk.Canvas(download_window, width=600, height=16, bg='white')
    canvas_download.grid(row=1, column=2)
    fill_line = canvas_download.create_rectangle(1.5, 1.5, 0, 23, width=0, fill='green')    # 进度条
    raise_data = 600/(content_size/chunk_size)  # 进度条增量大小
    with open(path+'/'+str(name), 'wb') as f:   # 将下载的数据写入文件
        n = 0
        for chunk in response.iter_content(chunk_size=chunk_size):  # 以1024个字节为一个数据块进行读取
            if chunk:                           # 如果chunk不为空
                f.write(chunk)
                n = n + raise_data
                canvas_download.coords(fill_line, (0, 0, n, 60))    # 更新进度条
                download_window.update()


'''输入：压缩包路径，解压路径'''


def unzip_weight(zip_src, dst_dir):
    weight_zip = zipfile.ZipFile(zip_src, 'r')
    for file in weight_zip.namelist():  # 获取压缩包里所有文件
        weight_zip.extract(file, dst_dir)   # 循环解压文件到指定目录


def show_output():
    model = askopenfilename()
    global filepath, depth, max_dep_dis, save
    if para.get() == 'A':
        if not os.path.exists('FCRN_master/NYU_FCRN.ckpt.data-00000-of-00001'):  # 如果参数文件不存在
            messagebox.showinfo('提示', '第一次使用需要下载相关权重文件，点击确定开始下载')
            download_weight('http://campar.in.tum.de/files/rupprecht/depthpred/NYU_FCRN-checkpoint.zip',
                            'FCRN_master')
            unzip_weight('FCRN_master/NYU_FCRN-checkpoint.zip', 'FCRN_master')
            os.remove('FCRN_master/NYU_FCRN-checkpoint.zip')
        predict.predict(model_data_path=model, image_path=filepath)

    elif para.get() == 'B':
        image_in_path = 'MiDaS_master/input/' + filepath.split('\\')[-1]  # 将图片保存到MiDas_master/input文件夹
        image_in.save(image_in_path)
        # depth, image_result = run.new_run(image_in_path, 'MiDaS_master/output', 'MiDaS_master/model.pt')
        depth, image_result = run.new_run(image_in_path, 'MiDaS_master/output', model)
        max_dep_dis = depth.max() - depth.min()
        plt.imsave('pred.jpg', image_result)

    elif para.get() == 'C':
        image_in_path = 'MegaDepth/demo_img/demo.jpg'
        image_in.save(image_in_path)                     # 将图片保存到指定文件夹
        demo.run()
        image_result = Image.open('MegaDepth/demo_img/demo1.jpg')
        plt.imsave('pred.jpg', image_result)

    else:
        messagebox.showwarning('警告', '请选择参数')
        return

    image_open = Image.open('pred.jpg')
    image_resize = image_open.resize((width, height))
    image = ImageTk.PhotoImage(image_resize)
    canvas_out.create_image(0, 0, anchor='nw', image=image)
    canvas_out.image = image
    save = True     # 表示可保存生成图片
    img_range = cv2.imread('pred.jpg', 0)  # 读取图像
    img_range.resize((image_in.size[0], image_in.size[1]))  # 将图像放缩为输入框内的大小
    depth = np.copy(img_range)  # 获得灰度值


def save_output():
    if save:
        filename = filedialog.asksaveasfilename(defaultextension='.jpg',        # 默认文件扩展名
                                                filetypes=[('JPG', '*.jpg')],   # 设置文件类型下拉菜单里的选项
                                                initialdir='',                  # 对话框中默认的路径
                                                initialfile='深度估计',         # 对话框中初始化显示的文件名
                                                parent=window,
                                                title='另存为')
        if filename != '':
            im = Image.open('pred.jpg')
            im.save(filename)
    else:
        messagebox.showerror('错误', '未生成输出')


# 参数部分
# “参数”标签
label_para = tk.Label(window, text='参数')
label_para.grid(row=1, column=2)
# 单选框架
frame_para = tk.Frame(window)
frame_para.grid(row=2, column=2)
"""# 复选框
check_para = tk.IntVar()
check_pick = tk.Checkbutton(window, text='选择第二点', variable=check_para, height=2, width=20, onvalue=0, offvalue=1)
check_pick.grid(row=4, column=2)"""
# 单选按钮
para = tk.StringVar()
radiobutton1 = tk.Radiobutton(frame_para, text='FCRN', variable=para, value='A')
radiobutton1.pack(anchor='w')
radiobutton2 = tk.Radiobutton(frame_para, text='MiDaS', variable=para, value='B')
radiobutton2.pack(anchor='w')
radiobutton3 = tk.Radiobutton(frame_para, text='MegaDepth', variable=para, value='C')
radiobutton3.pack(anchor='w')
# 焦距输入
label_focal = tk.Label(master=frame_para, text='焦距/mm')
label_focal.pack(pady=10)
entry_focal = tk.Entry(master=frame_para, width=10)
entry_focal.pack()
# “确认”按钮
button_para = tk.Button(master=frame_para, text='选择参数', command=show_output)
button_para.pack(pady=20)
# 按钮框架
frame_button = tk.Frame(window)
frame_button.grid(row=3, column=2)
# “保存”按钮
button_save = tk.Button(frame_button, text='保存图片', command=save_output)
button_save.grid(row=2, column=1)
# 调整系数
label_plain_alter = tk.Label(master=frame_para, text='平面系数：' + str(alter_plain_para))
label_plain_alter.pack(pady=0)
label_dep_alter = tk.Label(master=frame_para, text='深度系数：' + str(alter_dep_para))
label_dep_alter.pack(pady=0)


def check_num1(b):
    """检测输入是否为数字"""
    lst = list(entry_plain_alter.get())
    for i in range(len(lst)):
        if lst[i] not in ".0123456789":
            entry_plain_alter.delete(i, i + 1)
    if lst.count('.') == 2:
        entry_plain_alter.delete(len(lst) - 1, len(lst))


def check_num2(a):
    """检测输入是否为数字"""
    lst = list(entry_alter.get())
    for i in range(len(lst)):
        if lst[i] not in ".0123456789":
            entry_alter.delete(i, i + 1)
    if lst.count('.') == 2:
        entry_alter.delete(len(lst) - 1, len(lst))


# 调整框架
frame_alter = tk.Frame(window)
frame_alter.grid(row=4, column=2)
# 调整距离
label_alter_depth = tk.Label(master=frame_alter, text='调整平面距离为(cm)：')
label_alter_depth.grid(row=1, column=1)
entry_plain_alter = tk.Entry(master=frame_alter, width=10)
entry_plain_alter.bind('<KeyRelease>', check_num1)
entry_plain_alter.grid(row=1, column=2)

label_alter_depth = tk.Label(master=frame_alter, text='调整距离为(cm)：')
label_alter_depth.grid(row=3, column=1)
entry_alter = tk.Entry(master=frame_alter, width=10)
entry_alter.bind('<KeyRelease>', check_num2)
entry_alter.grid(row=3, column=2)

# 输出部分
# “输出”标签
label_out = tk.Label(window, text='输出')
label_out.grid(row=1, column=3)
# 帆布
canvas_out = tk.Canvas(window, bg='white', width=width, height=height)
canvas_out.grid(row=2, column=3, rowspan=2)

# 选点部分
# 第一点
frame_point1 = tk.Frame(window)
label_axis1 = tk.Label(frame_point1, text='坐标：')
label_axis1.grid(row=1, column=1)
label_axis_content1 = tk.Label(frame_point1, text='')
label_axis_content1.grid(row=1, column=2)
frame_point1.grid(row=4, column=1)

label_depth1 = tk.Label(frame_point1, text='深度：')
label_depth1.grid(row=2, column=1)
label_depth_content1 = tk.Label(frame_point1, text='')
label_depth_content1.grid(row=2, column=2)

# 第二点
frame_point2 = tk.Frame(window)
label_axis2 = tk.Label(frame_point2, text='坐标：')
label_axis2.grid(row=1, column=1)
label_axis_content2 = tk.Label(frame_point2, text='')
label_axis_content2.grid(row=1, column=2)
frame_point2.grid(row=4, column=3)

label_depth2 = tk.Label(frame_point2, text='深度：')
label_depth2.grid(row=2, column=1)
label_depth_content2 = tk.Label(frame_point2, text='')
label_depth_content2.grid(row=2, column=2)


def click(event):
    """点击canvas_in，得到所选点的信息"""
    global rec_red, start_x, start_y
    try:
        start_x, start_y = event.x, event.y
        x = round(event.x * image_in.size[0] / width)
        y = round(event.y * image_in.size[1] / height)
        """限定x，y的范围"""
        x = max(x, 0)
        x = min(x, image_in.size[0] - 1)
        y = max(y, 0)
        y = min(y, image_in.size[1] - 1)
    except:
        return

    try:
        canvas_in.delete(rec_red, rec_red2, line_red)
        canvas_in.delete(text_dis)
    except:
        return
    rec_red = canvas_in.create_rectangle(event.x - 2, event.y - 2, event.x + 2, event.y + 2, outline='red',
                                         fill='red')
    label_axis_content1.config(text='({0}, {1})'.format(x, y))
    if depth is not None:
        label_depth_content1.config(text='{0}'.format(depth[y, x]))
    else:
        return


def move(event):
    """移动canvas_in，得到所选点的信息"""
    global line_red, start_x, start_y, rec_red2, text_dis
    try:
        x1 = round(start_x * image_in.size[0] / width)
        y1 = round(start_y * image_in.size[1] / height)
        x2 = round(event.x * image_in.size[0] / width)
        y2 = round(event.y * image_in.size[1] / height)
        """限定x，y的范围"""
        x1 = min(max(x1, 0), image_in.size[0] - 1)
        y1 = min(max(y1, 0), image_in.size[1] - 1)
        x2 = min(max(x2, 0), image_in.size[0] - 1)
        y2 = min(max(y2, 0), image_in.size[1] - 1)
    except:
        return

    try:
        canvas_in.delete(line_red)
        canvas_in.delete(rec_red2)
        canvas_in.delete(text_dis)
    except:
        return
    line_red = canvas_in.create_line(start_x, start_y, event.x, event.y, fill='red', width=2)
    rec_red2 = canvas_in.create_rectangle(event.x - 2, event.y - 2, event.x + 2, event.y + 2, outline='red',
                                          fill='red')
    label_axis_content2.config(text='({0}, {1})'.format(x2, y2))
    if depth is not None:
        label_depth_content2.config(text='{0}'.format(depth[y2, x2]))
        text_x = (start_x + event.x) // 2
        text_y = (start_y + event.y) // 2 - 5
        str_dis = get_dis(x1, y1, x2, y2)
        text_dis = canvas_in.create_text(text_x, text_y, text=str_dis, fill='red',
                                         font=('Helvetica', '20', 'bold'))     # 显示距离
    else:
        return
    return


def release(event):
    global start_x, start_y, record_index
    try:
        x1 = round(start_x * image_in.size[0] / width)
        y1 = round(start_y * image_in.size[1] / height)
        x2 = round(event.x * image_in.size[0] / width)
        y2 = round(event.y * image_in.size[1] / height)
        """限定x，y的范围"""
        x1 = min(max(x1, 0), image_in.size[0] - 1)
        y1 = min(max(y1, 0), image_in.size[1] - 1)
        x2 = min(max(x2, 0), image_in.size[0] - 1)
        y2 = min(max(y2, 0), image_in.size[1] - 1)
    except:
        return

    if depth is not None:
        str_dis = get_dis(x1, y1, x2, y2)
        tree_view.insert('', 0, values=(str(record_index), '(' + str(x1) + ', ' + str(y1) + ')', '(' + str(x2)
                                                   + ', ' + str(y2) + ')', str_dis))
        record_index += 1
    else:
        return


def get_dis(x1, y1, x2, y2):
    """计算距离"""
    global alter_dep_para, alter_plain_para, plain_dis, dep_dis
    plain_dis = (x1 - x2)**2 + (y1 - y2)**2
    dep_dis = abs(depth[y2, x2] - depth[y1, x1])
    dis = math.sqrt(plain_dis * alter_plain_para + dep_dis * alter_dep_para)   # 平面距离乘参数 + 深度差乘参数
    if dis < 100:
        str_dis = str(round(dis, 2)) + 'cm'
    else:
        str_dis = str(round(dis / 100, 2)) + 'm'

    return str_dis


def alter_plain_dis():
    """修改平面距离"""
    global alter_plain_para, plain_dis, dep_dis, max_dep_dis
    get_plain_dis = entry_plain_alter.get()
    if get_plain_dis and plain_dis:
        get_plain_dis = float(get_plain_dis)
        if math.sqrt(dep_dis) / max_dep_dis < 0.02:
            alter_plain_para = (get_plain_dis**2) / plain_dis
            label_plain_alter.config(text='平面系数：' + str(alter_plain_para))
        else:
            messagebox.showwarning('限制', '请选择同一平面上的两点进行调整')


def alter_dis():
    """修改距离"""
    global alter_dep_para, alter_plain_para, plain_dis, dep_dis
    get_real_dis = entry_alter.get()
    if get_real_dis and dep_dis:
        get_real_dis = float(get_real_dis)
        alter_dep_para = max((get_real_dis**2 - plain_dis * alter_plain_para) / dep_dis, 0)
        label_dep_alter.config(text='深度系数：' + str(alter_dep_para))


# 测距部分
# 调整距离按钮
button_para = tk.Button(master=frame_alter, text='确认调整', command=alter_plain_dis)
button_para.grid(row=2, column=2)
button_para = tk.Button(master=frame_alter, text='确认调整', command=alter_dis)
button_para.grid(row=4, column=2)

# 测距记录
record_frame = tk.Frame(window)
record_frame.grid(row=5, column=1, columnspan=3)
sbar = tk.Scrollbar(record_frame)
tree_view = ttk.Treeview(record_frame, height=6)
sbar.pack(side=tk.RIGHT, fill=tk.Y)
tree_view.pack(pady=10, side=tk.LEFT, fill=tk.Y)
sbar.config(command=tree_view.yview)
tree_view.config(yscrollcommand=sbar.set)

# 数据列的定义
tree_view["columns"] = ("#0", "one", "two", "three")
tree_view.column("#0", width=50, minwidth=50, stretch=tk.NO)
tree_view.column("one", width=200, minwidth=200, stretch=tk.NO)
tree_view.column("two", width=200, minwidth=200, stretch=tk.NO)
tree_view.column("three", width=150, minwidth=150, stretch=tk.NO)

tree_view.heading("#0", text="序号", anchor='center')
tree_view.heading("one", text="第一点坐标", anchor='center')
tree_view.heading("two", text="第二点坐标", anchor='center')
tree_view.heading("three", text="距离", anchor='center')

canvas_in.bind('<Button-1>', click)
canvas_in.bind("<B1-Motion>", move)
canvas_in.bind("<ButtonRelease-1>", release)

window.mainloop()
