#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from PySide6.QtCore import Signal, Qt, QEvent, QObject
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QMainWindow, QComboBox, QMessageBox
from ui.PointCloud_ui import Ui_MainWindow
from lib.measimage import MeasImageDialog
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
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


class CheckableComboBox(QObject):
    """为已有的 QComboBox 增加复选（checkbox）多选能力。

    列表项带勾选框，勾选/取消勾选不会关闭弹出列表；
    下拉框的文本框显示当前已选数量（只选一个时显示该项名称）。
    """

    DEFAULT_HINT = "请选择数据文件（可多选）"

    selectionChanged = Signal()

    def __init__(self, combo):
        super().__init__()
        self.combo = combo
        self.model = QStandardItemModel(combo)

        combo.setModel(self.model)
        combo.setInsertPolicy(QComboBox.NoInsert)
        combo.setMaxVisibleItems(20)
        # 用只读的可编辑框显示摘要：可编辑时下拉框显示的才是我们的摘要文本，
        # 而不是当前选中项的名称
        combo.setEditable(True)
        self.lineEdit = combo.lineEdit()
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setPlaceholderText(self.DEFAULT_HINT)
        # 文件名后缀（C/S/S1...）在末尾，中间省略才能看清
        combo.view().setTextElideMode(Qt.ElideMiddle)

        # 事件过滤器必须挂在被过滤控件上，随控件一起销毁，
        # 否则程序退出时会崩溃
        self.viewport = combo.view().viewport()
        self.setParent(self.viewport)
        self.viewport.installEventFilter(self)
        self.lineEdit.installEventFilter(self)

        self.model.itemChanged.connect(self._on_item_changed)
        combo.currentIndexChanged.connect(self._on_current_index_changed)

    def addItem(self, text, userData=None):
        item = QStandardItem(text)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        item.setToolTip(text)
        if userData is not None:
            item.setData(userData, Qt.UserRole)
        self.model.appendRow(item)
        return item

    def clear(self):
        self.model.blockSignals(True)
        self.model.clear()
        self.model.blockSignals(False)
        self.combo.setCurrentIndex(-1)
        self.lineEdit.clear()

    def count(self):
        return self.model.rowCount()

    def item(self, row):
        return self.model.item(row)

    def checkedItems(self):
        names = []
        for row in range(self.model.rowCount()):
            item = self.model.item(row)
            if item is not None and item.checkState() == Qt.Checked:
                names.append(item.text())
        return names

    def checkFirst(self):
        if self.model.rowCount() > 0:
            self.model.item(0).setCheckState(Qt.Checked)

    def refreshText(self):
        names = self.checkedItems()
        if not names:
            self.lineEdit.clear()
        elif len(names) == 1:
            self.lineEdit.setText(names[0])
        else:
            self.lineEdit.setText("已选 {} 项".format(len(names)))

    def _on_item_changed(self, _item):
        self.refreshText()
        self.selectionChanged.emit()

    def _on_current_index_changed(self, _index):
        # 展开列表时 QComboBox 会把当前项名称写进文本框，
        # 这里恢复成“已选 N 项”的摘要
        self.refreshText()

    def eventFilter(self, obj, event):
        if obj is self.lineEdit and event.type() == QEvent.MouseButtonPress:
            # 点击文本框的任意位置都展开复选列表
            self.combo.showPopup()
            return True
        if obj is self.viewport and event.type() == QEvent.MouseButtonRelease:
            index = self.combo.view().indexAt(event.pos())
            if index.isValid():
                item = self.model.itemFromIndex(index)
                if item is not None and (item.flags() & Qt.ItemIsUserCheckable):
                    if item.checkState() == Qt.Checked:
                        item.setCheckState(Qt.Unchecked)
                    else:
                        item.setCheckState(Qt.Checked)
                # 吞掉鼠标释放事件，弹出列表保持打开，方便连续勾选
                return True
        return super().eventFilter(obj, event)


class DecimalAxisItem(pg.AxisItem):
    """坐标轴刻度带小数显示（默认 pyqtgraph 会取整）。"""

    def tickStrings(self, values, scale, spacing):
        if spacing < 0.001:
            decimals = 5
        elif spacing < 0.01:
            decimals = 4
        elif spacing < 0.1:
            decimals = 3
        elif spacing < 1:
            decimals = 2
        else:
            decimals = 1
        strings = []
        for value in values:
            value = value * scale
            if abs(value) < 1e-12:
                value = 0.0
            strings.append("{0:.{1}f}".format(value, decimals))
        return strings


class PointCloudWindow(QMainWindow):
    # 文件名示例：
    #  Q22130675A8_000015963995_20261107112147_1596399509_3.9mm_S3.csv
    # 文件名前可能有空格，保持原来的匹配规则（只把扩展名由 .B?0 改为 .csv）
    FILE_PATTERN = re.compile(
        r"^\s*([A-Za-z0-9\-]+)_(\d+)_(\d+)_(\d+)_(\d+\.?\d*mm)(_\w+)?_(\w+)\.csv$",
        re.IGNORECASE)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("PCS背钻点云图查看程序")

        self.files = {}
        self.imageDialog = None
        self.data = []
        self.X = np.array([])
        self.Y = np.array([])
        self.Z = np.array([])

        self.load_config()
        self.init_file_select()
        self.init_plot()
        self.init_signals()

    def load_config(self):
        self.config = {
            "srcData": "\\\\172.29.230.15\\ProdData01\\测厚仪数据\\P2D测厚仪数据",
            "srcImage": "\\\\172.21.244.15\\p2dpcs\\PCBImages\\HeightImage",
            "colorMap": "CET-R2"
        }

    def init_file_select(self):
        # 原来的下拉框升级为可复选：可同时勾选多个数据文件
        self.fileSelect = CheckableComboBox(self.ui.fileSelect)
        self.ui.fileSelect.setToolTip("可勾选多个数据文件，叠加显示在同一张点云图中")

    def init_plot(self):
        self.plot = self.ui.graphWidget.addPlot(title="点云图")
        self.plot.setAxisItems({
            'bottom': DecimalAxisItem('bottom'),
            'left': DecimalAxisItem('left'),
        })
        self.plot.setAspectLocked(ratio=1)  # type: ignore
        self.plot.setLabel('left', 'Y坐标')
        self.plot.setLabel('bottom', 'X坐标')
        self.plot.setTitle('点云图')
        self.plot.showGrid(x=True, y=True, alpha=0.4)

        self.cmap = pg.colormap.get(self.config['colorMap'])
        self.scatter = pg.ScatterPlotItem(
                    size=8,
                    hoverable=True,
                    hoverSize=12,
                    tip=self.format_tip,
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
        self.ui.pushButton.clicked.connect(self.show_image)
        self.colorbar.sigLevelsChangeFinished.connect(self.update_colors)
        self.colorbar.sigLevelsChanged.connect(self.update_colors)

    def closeEvent(self, event):
        # 关闭窗口时先摘掉下拉列表的事件过滤器，避免退出时弹出列表
        # 还开着导致 Qt 在析构阶段访问已释放的对象
        try:
            self.fileSelect.viewport.removeEventFilter(self.fileSelect)
            self.fileSelect.lineEdit.removeEventFilter(self.fileSelect)
        except RuntimeError:
            pass
        super().closeEvent(event)

    def update_colors(self):
        if len(self.Z) == 0:
            return
        low, high = self.colorbar.values
        if high <= low:
            return

        # 将 Z 值归一化到 [0, 1] 范围

        normalized_z = (self.Z - low) / (high - low)
        normalized_z = np.clip(normalized_z, 0, 1)  # 确保在 [0, 1] 范围内

        # 使用颜色映射获取颜色 - 同样需要转换为0-255的整数
        colors_float = self.cmap.map(normalized_z, mode='float')
        colors_int = (np.array(colors_float) * 255).astype(np.uint8)

        # 更新散点的颜色
        brushes = [pg.mkBrush(color) for color in colors_int]
        self.scatter.setBrush(brushes)

    def format_tip(self, x=None, y=None, data=None):
        """悬浮提示：坐标保留 3 位小数，data 为 板厚mm(背钻流程和刀序)。"""
        tip = "x: {0:.3f}\ny: {1:.3f}".format(x, y)
        if data:
            tip += "\n{}".format(data)
        return tip

    def on_barcode_changed(self):
        product = self.ui.productName.text().strip().upper()
        seek_code = self.ui.barCode.text().strip()
        if not product: return
        if not seek_code: return

        src_path = self.config["srcData"]
        self.fileSelect.clear()
        self.files = {}
        entries = []
        for folder in sorted(os.listdir(self.config["srcData"])):
            folder_path = os.path.join(src_path, folder)
            if not (os.path.isdir(folder_path) and (product in folder.upper())):
                continue
            pointcloud_path = os.path.join(folder_path, "PointCloud")
            if not os.path.isdir(pointcloud_path):
                continue
            print(f'正在处理{folder}...')
            for root, _, files in os.walk(pointcloud_path):
                for file in files:
                    match = self.FILE_PATTERN.match(file)
                    if not match:
                        continue
                    pn, lot, date, barcode, _thickness, _, side = match.groups()
                    if seek_code in barcode:
                        entries.append((date, side, pn, lot, barcode, os.path.join(root, file)))

        # 同一时间点的量测按 C/S/S1 排序，新的量测排在前面
        entries.sort(key=lambda item: item[1])
        entries.sort(key=lambda item: item[0], reverse=True)
        for _date, side, pn, lot, barcode, file_path in entries:
            pretty_name = f"{pn}_{_date}_{barcode}_{side}"
            if pretty_name in self.files:
                pretty_name = f"{pretty_name}_{lot}"
            self.files[pretty_name] = file_path
            self.fileSelect.addItem(pretty_name)

        if self.fileSelect.count() > 0:
            # 默认勾选最新的一条，和原来下拉框默认选中第一项的习惯保持一致
            self.fileSelect.checkFirst()
        self.fileSelect.refreshText()

    def show_plot(self):
        pretty_names = self.fileSelect.checkedItems()
        if not pretty_names:
            QMessageBox.information(self, "提示", "请先勾选要显示的数据文件")
            return

        data = []
        loaded_paths = []
        for pretty_name in pretty_names:
            file_path = self.files.get(pretty_name)
            if not file_path or not os.path.isfile(file_path):
                continue
            file_data = self.load_data(file_path)
            if file_data:
                data.extend(file_data)
                loaded_paths.append(file_path)
        if not data:
            return

        self.data = data
        self.X = np.fromiter((point.x for point in data), dtype=np.float64, count=len(data))
        self.Y = np.fromiter((point.y for point in data), dtype=np.float64, count=len(data))
        self.Z = np.fromiter((point.z for point in data), dtype=np.float64, count=len(data))

        comment = [self.format_comment(point) for point in data]
        self.scatter.setData(x=self.X, y=self.Y, data=comment)
        self.defects.setData(x=self.X, y=self.Y)

        min_z = self.Z.min()
        max_z = self.Z.max()
        if min_z < 0: min_z = 0
        if max_z > 10: max_z = 10
        if max_z - min_z < 1e-6:
            max_z = min_z + 0.01
        self.colorbar.setLevels(values=(min_z, max_z))
        self.update_colors()

        # 设置绘图范围，确保数据可见
        x_min, x_max = self.X.min(), self.X.max()
        y_min, y_max = self.Y.min(), self.Y.max()
        self.plot.setXRange(x_min, x_max, padding=0.02)
        self.plot.setYRange(y_min, y_max, padding=0.02)

        if len(loaded_paths) == 1:
            title = os.path.basename(loaded_paths[0]).strip()
        else:
            title = "{} 个数据文件 - {} 等".format(
                len(loaded_paths), os.path.basename(loaded_paths[0]).strip())
        self.plot.setTitle(title)

    def format_comment(self, point):
        """悬浮提示里的 data：板厚mm(背钻流程和刀序)，如 3.912mm(B30/T02)。"""
        if point.comment:
            return "{0:.3f}mm({1})".format(point.z, point.comment)
        return "{0:.3f}mm".format(point.z)

    def parse_file_name(self, file_name):
        """把数据文件名拆成 型号/工单/时间/二维码/板厚 等信息。"""
        match = self.FILE_PATTERN.match(file_name)
        if not match:
            return None
        pn, lot, date, barcode, thickness, _, side = match.groups()
        return {
            "pn": pn,
            "lot": lot,
            "date": date,
            "barcode": barcode,
            "thickness": thickness,
            "side": side,
            # 图片文件名就是数据文件名去掉流程/面次后缀
            "base": f"{pn}_{lot}_{date}_{barcode}_{thickness}",
        }

    def image_folder(self, info):
        """图片目录：{型号}_{工单}。混板时在型号相同的目录里再找一次。"""
        root = self.config["srcImage"]
        folder = os.path.join(root, f"{info['pn']}_{info['lot']}")
        if os.path.isdir(folder):
            return folder
        try:
            entries = os.listdir(root)
        except OSError:
            return None
        for name in entries:
            if not name.startswith(info["pn"] + "_"):
                continue
            candidate = os.path.join(root, name)
            if not os.path.isdir(candidate):
                continue
            try:
                for file_name in os.listdir(candidate):
                    if file_name.startswith(info["base"]):
                        return candidate
            except OSError:
                continue
        return None

    @staticmethod
    def image_date(file_name):
        """从图片/数据文件名里取量测时间（第 3 段）。"""
        if not file_name:
            return None
        parts = os.path.basename(file_name).strip().split("_")
        if len(parts) >= 3 and parts[2].isdigit():
            return parts[2]
        return None

    @staticmethod
    def _date_value(text):
        try:
            return int(text)
        except (TypeError, ValueError):
            return None

    def find_image(self, folder, info, suffix):
        """先按完整文件名匹配，找不到时按二维码匹配量测时间最接近的一张。"""
        if not folder:
            return None
        path = os.path.join(folder, info["base"] + suffix)
        if os.path.isfile(path):
            return path

        try:
            names = [n for n in os.listdir(folder)
                     if n.lower().endswith(suffix.lower())
                     and info["barcode"] and info["barcode"] in n]
        except OSError:
            return None
        if not names:
            return None

        target = self._date_value(info["date"])
        if target is not None:
            def distance(name):
                value = self._date_value(self.image_date(name))
                return abs(value - target) if value is not None else target
            names.sort(key=distance)
        return os.path.join(folder, names[0])

    def show_image(self):
        """点击【显示板厚图】：按第一个勾选的数据文件显示该板的 CS/SS 图片。"""
        names = self.fileSelect.checkedItems()
        if not names:
            QMessageBox.information(self, "提示", "请先勾选要查看板厚图的数据文件")
            return

        infos = []
        for name in names:
            file_path = self.files.get(name)
            if not file_path:
                continue
            info = self.parse_file_name(os.path.basename(file_path))
            if info:
                infos.append(info)
        if not infos:
            QMessageBox.warning(self, "提示", "无法解析所选数据文件名")
            return

        info = infos[0]
        folder = self.image_folder(info)
        cs_path = self.find_image(folder, info, "_CS.png")
        ss_path = self.find_image(folder, info, "_SS.png")

        title = "{}  {}".format(info["pn"], info["lot"])
        comment = "{} | 二维码 {} | 板厚 {}".format(
            info["date"], info["barcode"], info["thickness"])
        if not cs_path and not ss_path:
            comment += "（未找到图片）"
        image_date = self.image_date(cs_path or ss_path)
        if image_date and image_date != info["date"]:
            comment += "（图片量测时间 {}）".format(image_date)
        bases = {item["base"] for item in infos}
        if len(bases) > 1:
            comment += "（勾选了 {} 组不同量测，显示第一组）".format(len(bases))
        elif len(names) > 1:
            comment += "（{} 个数据文件共用同一组图片）".format(len(names))
        comment += "\n滚轮缩放（两图联动）· 按住左键拖动平移 · 双击复位"

        if self.imageDialog is None:
            self.imageDialog = MeasImageDialog(self)
        self.imageDialog.show_board(title, comment, cs_path, ss_path)

    def load_data(self, file_path):
        """读取 PointCloud 下的 csv 点云数据。

        列：X坐标, Y坐标, 量测板厚, 背钻流程和刀序（如 B30/T02）
        """
        data = []
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(',')
                if len(parts) < 4:
                    continue
                try:
                    x = float(parts[0])
                    y = float(parts[1])
                    z = float(parts[2])
                except ValueError:
                    # 跳过表头等非数据行
                    continue
                process = parts[3].strip()
                data.append(Point(x, y, z, 0.0, process))
        return data

    def print_stats(self):
        if len(self.Z) == 0:
            return
        min_z = 10
        max_z = 0
        for z in self.Z:
            if min_z > z > 0:
                min_z = z
            if z > max_z:
                max_z = z

        median_z = float(np.median(self.Z))
        q1 = float(np.quantile(self.Z, 0.25))
        q3 = float(np.quantile(self.Z, 0.75))
        iqr = q3 - q1
        tol = 0.0
        k = 3.0
        if iqr > 0:
            while k <= 20.0:
                tol = k * iqr
                if median_z + tol > max_z + 0.1 or median_z - tol < min_z - 0.1:
                    break
                k += 0.1

        ucl = median_z + tol
        lcl = median_z - tol


if __name__ == '__main__':
    app = QApplication([])
    win = PointCloudWindow()
    win.show()
    app.exec()
