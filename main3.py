import tkinter as tk
from init_window import Tkwindow

if __name__ == "__main__":
    # 初始化窗口
    window = tk.Tk()
    window.title('深度估计')
    window.geometry('1208x551')

    # 调用Tkwindow类 添加窗口内容
    app_window = Tkwindow(window)
    app_window()

    window.mainloop()
