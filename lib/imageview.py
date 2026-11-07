# -*- coding: utf-8 -*-

import os

from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsPixmapItem)


class ZoomImageView(QGraphicsView):
    """显示单张图片，滚轮以鼠标为中心缩放，按住左键拖动平移，双击复位。

    stateChanged 会发出当前缩放比例和视口中心在图片上的相对位置（0~1），
    便于让两个视图联动缩放/平移。
    """

    stateChanged = Signal(float, float, float)
    doubleClicked = Signal()

    MIN_SCALE = 0.02
    MAX_SCALE = 30.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self.pixmap_item = QGraphicsPixmapItem()
        self.pixmap_item.setTransformationMode(Qt.SmoothTransformation)
        self._scene.addItem(self.pixmap_item)
        self._text_item = None

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setBackgroundBrush(QColor("#101010"))
        self.setFrameShape(QGraphicsView.Box)
        self.setMinimumSize(200, 200)

        self._has_image = False
        self._user_zoomed = False
        self._last_state = None

    # ------------------------------------------------------------------
    def setImage(self, path):
        """加载图片，返回是否成功。path 为空或不存在时显示“无图片”。"""
        pixmap = QPixmap()
        if path and os.path.isfile(path):
            pixmap.load(path)

        self._clear_scene()
        self._last_state = None
        if pixmap.isNull():
            self._has_image = False
            self._scene.setSceneRect(QRectF(0, 0, 400, 400))
            self._text_item = self._scene.addText("无图片")
            self._text_item.setDefaultTextColor(QColor("#BBBBBB"))
            rect = self._text_item.boundingRect()
            self._text_item.setPos(200 - rect.width() / 2, 200 - rect.height() / 2)
            self.fit()
            return False

        self.pixmap_item.setPixmap(pixmap)
        self.pixmap_item.setPos(0, 0)
        self._scene.setSceneRect(QRectF(pixmap.rect()))
        self._has_image = True
        self.fit()
        return True

    def _clear_scene(self):
        if self._text_item is not None:
            self._scene.removeItem(self._text_item)
            self._text_item = None
        self.pixmap_item.setPixmap(QPixmap())

    # ------------------------------------------------------------------
    def fit(self):
        """按窗口大小完整显示图片。"""
        self.resetTransform()
        if self._has_image:
            self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)
        elif not self._scene.sceneRect().isEmpty():
            self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)
        self._user_zoomed = False
        self._last_state = None

    def view_state(self):
        """返回 (缩放比例, 中心相对X, 中心相对Y)；无图片时返回 None。"""
        if not self._has_image:
            return None
        scale = self.transform().m11()
        center = self.mapToScene(self.viewport().rect().center())
        pixmap = self.pixmap_item.pixmap()
        width = max(pixmap.width(), 1)
        height = max(pixmap.height(), 1)
        return scale, center.x() / width, center.y() / height

    def apply_state(self, scale, rel_x, rel_y):
        """套用另一个视图的缩放比例和相对中心，实现联动。"""
        if not self._has_image:
            return
        pixmap = self.pixmap_item.pixmap()
        width = max(pixmap.width(), 1)
        height = max(pixmap.height(), 1)
        scale = min(max(scale, self.MIN_SCALE), self.MAX_SCALE)

        self.resetTransform()
        self.scale(scale, scale)
        self.centerOn(rel_x * width, rel_y * height)
        self._user_zoomed = True

    # ------------------------------------------------------------------
    def wheelEvent(self, event):
        if not self._has_image:
            super().wheelEvent(event)
            return
        delta = event.angleDelta().y()
        if delta == 0:
            return
        current = self.transform().m11()
        factor = 1.2 ** (delta / 120.0)
        target = min(max(current * factor, self.MIN_SCALE), self.MAX_SCALE)
        factor = target / current
        if abs(factor - 1.0) < 1e-9:
            return
        self.scale(factor, factor)
        self._user_zoomed = True
        self._emit_state()
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self._user_zoomed:
            self.fit()

    def mousePressEvent(self, event):
        if self._has_image and event.button() == Qt.LeftButton:
            # 拖动平移后不要因为窗口变化而重新自适应
            self._user_zoomed = True
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if event.buttons() & Qt.LeftButton:
            self._emit_state()

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        self.fit()
        self.doubleClicked.emit()

    # ------------------------------------------------------------------
    def _emit_state(self):
        state = self.view_state()
        if state is None:
            return
        if self._last_state is not None:
            last = self._last_state
            if (abs(last[0] - state[0]) < 1e-6
                    and abs(last[1] - state[1]) < 1e-6
                    and abs(last[2] - state[2]) < 1e-6):
                return
        self._last_state = state
        self.stateChanged.emit(*state)
