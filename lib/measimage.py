# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QDialog, QSizePolicy

from ui.MeasImage_ui import Ui_Dialog


class MeasImageDialog(QDialog):
    """按 ui/MeasImage.ui 显示某块板的 CS（正面）/SS（反面）板厚图。

    两张图随窗口自动缩放，滚轮缩放与拖动平移联动，双击复位。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("板厚图")
        self.ui.lblComment.setWordWrap(True)

        # 让两张图随窗口大小伸缩
        self.ui.gridLayout.setColumnStretch(0, 1)
        self.ui.gridLayout.setColumnStretch(1, 1)
        self.ui.gridLayout.setRowStretch(3, 1)
        for view in (self.ui.imgCS, self.ui.imgSS):
            view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.ui.imgCS.stateChanged.connect(self._sync_to_ss)
        self.ui.imgSS.stateChanged.connect(self._sync_to_cs)
        self.ui.imgCS.doubleClicked.connect(self._reset_views)
        self.ui.imgSS.doubleClicked.connect(self._reset_views)

    # ------------------------------------------------------------------
    def show_board(self, title, comment, cs_path, ss_path):
        self.ui.lblTitle.setText(title)
        self.ui.lblComment.setText(comment)
        self.ui.imgCS.setImage(cs_path)
        self.ui.imgSS.setImage(ss_path)
        self.setWindowTitle("板厚图 - " + title)
        self.show()
        self.raise_()
        self.activateWindow()

    # ------------------------------------------------------------------
    def _sync_to_ss(self, scale, rel_x, rel_y):
        self.ui.imgSS.apply_state(scale, rel_x, rel_y)

    def _sync_to_cs(self, scale, rel_x, rel_y):
        self.ui.imgCS.apply_state(scale, rel_x, rel_y)

    def _reset_views(self):
        self.ui.imgCS.fit()
        self.ui.imgSS.fit()
