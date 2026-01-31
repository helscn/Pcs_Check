#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from PySide6.QtCore import Signal,Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox
from ui.PointCloud_ui import Ui_MainWindow
import resources_rc
import pyqtgraph as pg
import numpy as np
import math
import re
import os


class Point(object):
    def __init__(self, x, y, z, depth=0.0, comment=''):
        self.x = x
        self.y = y
        self.z = z
        self.depth = depth
        self.comment = comment

    def __sub__(self, other):
        return math.sqrt((self.x - other.x)^2 + (self.y - other.y)^2)


class PointCloudWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("PCS背钻点云图查看程序")

        self.files={}
        self.data=[]
        self.defectsData=[]
        self.X=np.array([])
        self.Y=np.array([])
        self.Z=np.array([])

        self.load_config()
        self.init_plot()
        self.init_signals()

    def load_config(self):
        self.config = {
            "srcData":"\\\\172.29.230.15\\ProdData01\\测厚仪数据\\P2D测厚仪数据",
            "colorMap": "CET-R2"
        }

    def init_plot(self):
        self.plot = self.ui.graphWidget.addPlot(title="点云图")
        self.plot.setAspectLocked(ratio=1) # type: ignore
        self.plot.setLabel('left', 'Y坐标')
        self.plot.setLabel('bottom', 'X坐标')
        self.plot.setTitle('点云图')
        self.plot.showGrid(x=True, y=True, alpha=0.4)

        self.cmap = pg.colormap.get(self.config['colorMap'])
        self.scatter = pg.ScatterPlotItem(
                    size=8,
                    hoverable=True,
                    hoverSize=12,
                    brush=pg.mkBrush(255, 255, 255, 255),
                    pen=pg.mkPen('k', width=1),  # 添加黑色边框
                    pxMode=True
                )
        self.defects = pg.ScatterPlotItem(
                    size=15,
                    hoverable=False,
                    symbol='s',
                    brush=None,
                    pen=pg.mkPen(color='#FF66CC', width=1),  # 添加黑色边框
                    pxMode=True
                )
        self.scatter.setZValue(0)
        self.defects.setZValue(5)
        self.plot.addItem(self.scatter)
        # self.plot.addItem(self.defects)
        
        self.colorbar = pg.ColorBarItem(
            values=(0, 10),  # 初始范围为Z坐标的最小最大值
            colorMap=self.cmap,
            label='板厚 (mm)',
            limits=(0, 10),  # 设置限制范围
            rounding=0.01  # 关键：设置小的浮点数精度
        )        
        self.ui.graphWidget.addItem(self.colorbar, row=0, col=1)
        
        # 设置 ColorBar 的初始范围 - 使用正确的调用方式
        self.colorbar.setLevels(values=(0, 10))

    def init_signals(self):
        self.ui.barCode.textChanged.connect(self.on_barcode_changed)
        self.ui.showPlot.clicked.connect(self.show_plot)
        self.colorbar.sigLevelsChangeFinished.connect(self.update_colors)
        self.colorbar.sigLevelsChanged.connect(self.update_colors)


    def update_colors(self):
        low, high = self.colorbar.values
        
        # 将 Z 值归一化到 [0, 1] 范围
        
        normalized_z = (self.Z - low) / (high - low)
        normalized_z = np.clip(normalized_z, 0, 1)  # 确保在 [0, 1] 范围内
        
        # 使用颜色映射获取颜色 - 同样需要转换为0-255的整数
        colors_float = self.cmap.map(normalized_z, mode='float')
        colors_int = (np.array(colors_float) * 255).astype(np.uint8)
        
        # 更新散点的颜色
        brushes = [pg.mkBrush(color) for color in colors_int]
        self.scatter.setBrush(brushes)

    def on_barcode_changed(self):
        product = self.ui.productName.text().strip().upper()
        seek_code = self.ui.barCode.text().strip()
        if not product: return
        if not seek_code: return
        
        src_path = self.config["srcData"]
        self.ui.fileSelect.clear()
        self.files={}
        pattern = re.compile(r"^\s*([A-Za-z0-9\-]+)_(\d+)_(\d+)_(\d+)_(\d+\.?\d*mm)(_\w+)?_(\w+)\.(B\d0)$")
        for folder in os.listdir(self.config["srcData"]):
            folder_path = os.path.join(src_path, folder)
            if os.path.isdir(folder_path) and (product in folder.upper()):
                print(f'正在处理{folder}...')
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        match = pattern.match(file)
                        if match:
                            print(file)
                            pn,lot,date,barcode,thickness,_,side,process=match.groups()
                            if seek_code in barcode:
                                pretty_name = f"{pn}_{date}_{barcode}_{side}_{process}"
                                self.files[pretty_name] = os.path.join(root, file)
                                self.ui.fileSelect.addItem(pretty_name)


    def show_plot(self):
        pretty_name = self.ui.fileSelect.currentText()
        if pretty_name in self.files:
            file_path = self.files[pretty_name]
            if os.path.isfile(file_path):
                self.load_data(file_path)
                if not self.data: return
                comment=[]
                for point in self.data:
                    comment.append(point.comment)

                self.scatter.setData(x=self.X, y=self.Y, data=comment)
                self.defects.setData(x=self.X, y=self.Y)
                min_z = self.Z.min()
                max_z = self.Z.max()
                if min_z<0: min_z=0
                if max_z>10: max_z=10
                self.colorbar.setLevels(values=(min_z, max_z))
                self.update_colors()
                
                # 设置绘图范围，确保数据可见
                x_min, x_max = self.X.min(), self.X.max()
                y_min, y_max = self.Y.min(), self.Y.max()
                self.plot.setXRange(x_min, x_max)
                self.plot.setYRange(y_min, y_max)
                self.plot.setTitle(os.path.basename(file_path))

    def load_data(self, file_path):
        data=[]
        depth=0.0
        M18_pattern=r"M18Z(\d*\.?\d+)"
        pos_pattern=r"X(\-?\d*)Y(\-?\d*)\((\d*\.?\d+)\)"
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                match_pos = re.match(pos_pattern, line)
                if match_pos:
                    x = self.parsePos(match_pos.group(1))
                    y = self.parsePos(match_pos.group(2))
                    z = float(match_pos.group(3))
                    data.append(Point(x, y, z, depth, match_pos.group(0)))
                else:
                    match_M18 = re.match(M18_pattern, line)
                    if match_M18:
                        depth = float(match_M18.group(1))
        self.data=data
        self.X = np.fromiter((point.x for point in data), dtype=np.float32, count=len(data))
        self.Y = np.fromiter((point.y for point in data), dtype=np.float32, count=len(data))
        self.Z = np.fromiter((point.z for point in data), dtype=np.float32, count=len(data))

        min_z=10
        max_z=0
        for point in data:
            if point.z<min_z and point.z>0:
                min_z=point.z
            if point.z>max_z: max_z=point.z
        print(f"不计算0值 最小Z: {min_z}, 最大Z: {max_z}")

        median_z=np.median(self.Z)
        q1 = np.quantile(self.Z, 0.25)
        q3 = np.quantile(self.Z, 0.75)
        iqr = q3 - q1
        k=3.0
        while True:
            tol = k*iqr
            if median_z+tol>max_z+0.1 or median_z-tol<min_z-0.1:
                break
            k+=0.1

        ucl=median_z+tol
        lcl=median_z-tol
        print(f"最小规格Z: {lcl}, 中位数Z: {median_z}, 最大规格Z: {ucl}, k: {k},  tol: {tol}")

        return data


    def parsePos(self, s, leadingZero=True, length=3)->float:
        '''
        将文本坐标值转换为浮点数
        leadingZero: 是否为前导零格式，为False时表示为后导零格式（省略前导零）
        length: 前导零格式时表示整数的位数，后导零格式时表示小数的位数
        '''
        if type(s) is str:
            s = s.strip()
            if '.' in s:
                return float(s)
        elif type(s) in [float, int]:
            return float(s)
        else:
            raise ValueError('Invalid data type!')

        sign = 1
        if s[0:1] == "-":
            sign = -1
            s = s[1:]
        if leadingZero:
            # 前补零时 length 表示整数位数
            if len(s) < length:
                integer = s.ljust(length, '0')
                decimal = '0'
            else:
                integer = s[:length]
                decimal = s[length:]
        else:
            # 后补零时 length 表示小数位数
            if len(s) < length:
                integer = '0'
                decimal = s.rjust(length, '0')
            else:
                integer = s[:-length]
                decimal = s[-length:]
        return sign * float('{}.{}'.format(integer, decimal))


if __name__ == '__main__':
    app = QApplication([])
    win = PointCloudWindow()
    win.show()
    app.exec()