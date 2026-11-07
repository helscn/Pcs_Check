# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MeasImage.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout,
    QWidget)

from lib.imageview import ZoomImageView

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(857, 634)
        self.horizontalLayout = QHBoxLayout(Dialog)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.line_2 = QFrame(Dialog)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_3.addWidget(self.line_2)

        self.lblTitle = QLabel(Dialog)
        self.lblTitle.setObjectName(u"lblTitle")
        self.lblTitle.setMinimumSize(QSize(0, 30))
        self.lblTitle.setMaximumSize(QSize(16777215, 30))
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.lblTitle.setFont(font)
        self.lblTitle.setFrameShape(QFrame.NoFrame)
        self.lblTitle.setAlignment(Qt.AlignBottom|Qt.AlignHCenter)

        self.verticalLayout_3.addWidget(self.lblTitle)

        self.lblComment = QLabel(Dialog)
        self.lblComment.setObjectName(u"lblComment")
        self.lblComment.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.lblComment)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.imgCS = ZoomImageView(Dialog)
        self.imgCS.setObjectName(u"imgCS")
        self.imgCS.setMinimumSize(QSize(200, 200))
        self.imgCS.setFrameShape(QFrame.Box)

        self.gridLayout.addWidget(self.imgCS, 3, 0, 1, 1)

        self.imgSS = ZoomImageView(Dialog)
        self.imgSS.setObjectName(u"imgSS")
        self.imgSS.setMinimumSize(QSize(200, 200))
        self.imgSS.setFrameShape(QFrame.Box)

        self.gridLayout.addWidget(self.imgSS, 3, 1, 1, 1)

        self.label_5 = QLabel(Dialog)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMaximumSize(QSize(16777215, 25))
        self.label_5.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label_5, 2, 0, 1, 1)

        self.label_6 = QLabel(Dialog)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMaximumSize(QSize(16777215, 25))
        self.label_6.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label_6, 2, 1, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout)

        self.verticalLayout_3.setStretch(3, 1)

        self.horizontalLayout.addLayout(self.verticalLayout_3)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.lblTitle.setText(QCoreApplication.translate("Dialog", u"\u677f\u539a\u56fe\u7247", None))
        self.lblComment.setText("")
        self.label_5.setText(QCoreApplication.translate("Dialog", u"\u6b63\u9762", None))
        self.label_6.setText(QCoreApplication.translate("Dialog", u"\u53cd\u9762", None))
    # retranslateUi

