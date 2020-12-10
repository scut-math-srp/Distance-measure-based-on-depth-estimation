
#!/usr/bin/python3    #指示我们的python版本和地址 不写也没关系
# -*- coding: utf-8 -*-  #一种字符编码，Unicode的一种，这样就可以显示中文字了

"""
 ZetCode PyQt5 tutorial

 In this example, we create a simple
 window in PyQt5.

 author: Jan Bodnar    #作者
 website: zetcode.com  #作者的网站
 last edited: January 2015
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget  #导入必要的组件


if __name__ == '__main__':

    app = QApplication(sys.argv)   #每一个程序都要建立一个，相当于一个画布，其他组件可以在上面画，放置，是一个父组件 sys.argv用来表示可以用命令行运行代码

    w = QWidget()       #建立一个窗口
    w.resize(1600, 900)  #重置为大小250，150大小的窗口
    w.move(120, 50)    #移动到300，300这个桌面的坐标上
    w.setWindowTitle('MegaDepth') #设置窗口的标题
    w.show()            #显示它，如果没有这句话，前面做的工作就没法看到，只是存进了内存里

    sys.exit(app.exec_()) #关闭程序，没有这句就只能强制关闭程序了，app.exec_()，只有这个好像也可以成功，可能是需要让程序知道进程都已经释放了吧





