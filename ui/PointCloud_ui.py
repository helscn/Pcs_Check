# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PointCloud.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QPushButton, QSizePolicy,
    QSpacerItem, QStatusBar, QVBoxLayout, QWidget)

from pyqtgraph import GraphicsLayoutWidget
import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(858, 825)
        icon = QIcon()
        icon.addFile(u":/icon.ico", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_3 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_2.addWidget(self.label_3)

        self.productName = QLineEdit(self.centralwidget)
        self.productName.setObjectName(u"productName")
        self.productName.setMinimumSize(QSize(100, 0))
        self.productName.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_2.addWidget(self.productName)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.barCode = QLineEdit(self.centralwidget)
        self.barCode.setObjectName(u"barCode")
        self.barCode.setMinimumSize(QSize(100, 0))
        self.barCode.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_2.addWidget(self.barCode)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.fileSelect = QComboBox(self.centralwidget)
        self.fileSelect.setObjectName(u"fileSelect")
        self.fileSelect.setMinimumSize(QSize(350, 0))

        self.horizontalLayout_2.addWidget(self.fileSelect)

        self.showPlot = QPushButton(self.centralwidget)
        self.showPlot.setObjectName(u"showPlot")
        self.showPlot.setMinimumSize(QSize(100, 40))

        self.horizontalLayout_2.addWidget(self.showPlot)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.graphWidget = GraphicsLayoutWidget(self.centralwidget)
        self.graphWidget.setObjectName(u"graphWidget")

        self.verticalLayout.addWidget(self.graphWidget)

        self.verticalLayout.setStretch(1, 1)

        self.horizontalLayout_3.addLayout(self.verticalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u578b\u53f7\uff1a", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u5b54\u9635\u7801\uff1a", None))
        self.barCode.setText("")
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u6570\u636e\u6587\u4ef6\uff1a", None))
        self.showPlot.setText(QCoreApplication.translate("MainWindow", u"\u663e\u793a\u70b9\u4e91\u56fe", None))
    # retranslateUi

