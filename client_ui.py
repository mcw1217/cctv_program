# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'client.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

import typing
from PyQt5.QtCore import QObject
import cv2
import pickle
import struct
import json
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget

class FrameThread(QThread):
    def __init__(self, client_socket, videoWindow):
        super().__init__()
        self.client_socket = client_socket
        self.videoWindow = videoWindow
        self.isRunning = True
    def stop(self):
        self.isRunning = False
    def run(self):
        data = b""
        payload_size = struct.calcsize("L")
        while True:  
            try:
                while len(data) < payload_size:
                    data += self.client_socket.recv(4096)

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("L",packed_msg_size)[0]

                while len(data) < msg_size:
                    data += self.client_socket.recv(4096)

                # 이미지 데이터를 디코딩하여 표시
                frame_data = data[:msg_size]
                data = data[msg_size:]
                frame = pickle.loads(frame_data)

                # VideoThread 인스턴스에 이미지 데이터 전달
                self.videoWindow.videoThread.set_frame(frame)

            except:
                print('connection failed')
                break
        self.isRunning = False
        self.finished.emit()
        
class VideoThread(QThread):
    frameReady = pyqtSignal(QImage)

    def __init__(self, videoWindow):
        super().__init__()
        self.videoWindow = videoWindow
        self.frame = None

    def set_frame(self, frame):
        self.frame = frame

    def convert_to_qimage(self, frame):
        # OpenCV BGR 이미지를 RGB로 변환
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # QImage 객체로 변환
        image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        return image

    def run(self):
        while True:
            if self.frame is not None:
                qimage = self.convert_to_qimage(self.frame)  
                self.frameReady.emit(qimage)  # frameReady 시그널 발생
                self.frame = None
            

class VideoWindow(QMainWindow):
    def __init__(self, index, client_id):
        super().__init__()
        self.index = index
        self.client_id = client_id
        self.setWindowTitle(f"Client {client_id}")
        self.labels = [QLabel() for _ in range(4)]
        # 2*2 배치의 그리드 레이아웃
        layout = QGridLayout()
        for i, label in enumerate(self.labels):
            layout.addWidget(label, i // 2, i % 2)
            self.show_black_screen(i)
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        centralWidget.setLayout(layout)
        
        # VideoThread 인스턴스 생성
        self.videoThread = VideoThread(self)
        self.videoThread.start()
        self.videoThread.frameReady.connect(self.update_frame)
        
    def update_frame(self, qimage):
        # client_id 표시
        painter = QPainter()
        painter.begin(qimage)
        painter.setPen(QColor('white'))
        painter.setFont(QFont('Arial', 10))
        # 오른쪽 하단에 표시
        painter.drawText(qimage.rect().adjusted(0, 0, -10, -10), Qt.AlignRight | Qt.AlignBottom, str(self.client_id))
        painter.end()
        # 라벨에 이미지 표시
        self.labels[self.index-1].setPixmap(QPixmap.fromImage(qimage))
        # QLabel 크기에 맞춰 이미지 크기 조절
        self.labels[self.index-1].setScaledContents(True)
        
    def show_black_screen(self, index):
        # 검은색 QImage 객체 생성
        image = QImage(640, 480, QImage.Format_RGB888)
        image.fill(QColor('black'))
        # QPainter 객체 생성
        painter = QPainter()
        painter.begin(image)
        painter.setPen(QColor('white'))
        painter.setFont(QFont('Arial', 30))
        painter.drawText(image.rect(), Qt.AlignCenter, str(index+1))
        painter.end()
        # QLabel에 표시
        self.labels[index].setPixmap(QPixmap.fromImage(image))   

class MainWindow(object):
    def setupUi(self, MainWindow):
        self.move(300, 300)
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(70, 170, 141, 61))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 40, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.AccessButton = QtWidgets.QPushButton(self.centralwidget)
        self.AccessButton.setGeometry(QtCore.QRect(560, 220, 171, 81))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.AccessButton.setFont(font)
        self.AccessButton.setObjectName("AccessButton")
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(70, 230, 141, 61))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 40, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(16)
        self.label_2.setFont(font)
        self.label_2.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.verticalLayoutWidget_3 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(70, 290, 141, 61))
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_3.setContentsMargins(0, 0, 40, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(16)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_3.addWidget(self.label_3)
        self.verticalLayoutWidget_4 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_4.setGeometry(QtCore.QRect(210, 170, 301, 61))
        self.verticalLayoutWidget_4.setObjectName("verticalLayoutWidget_4")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_4)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.InputIP = QtWidgets.QLineEdit(self.verticalLayoutWidget_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.InputIP.sizePolicy().hasHeightForWidth())
        self.InputIP.setSizePolicy(sizePolicy)
        self.InputIP.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.InputIP.setText("")
        self.InputIP.setObjectName("InputIP")
        self.verticalLayout_4.addWidget(self.InputIP)
        self.verticalLayoutWidget_5 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_5.setGeometry(QtCore.QRect(210, 230, 301, 61))
        self.verticalLayoutWidget_5.setObjectName("verticalLayoutWidget_5")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_5)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.InputPort = QtWidgets.QLineEdit(self.verticalLayoutWidget_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.InputPort.sizePolicy().hasHeightForWidth())
        self.InputPort.setSizePolicy(sizePolicy)
        self.InputPort.setObjectName("InputPort")
        self.verticalLayout_5.addWidget(self.InputPort)
        self.verticalLayoutWidget_6 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_6.setGeometry(QtCore.QRect(210, 290, 301, 61))
        self.verticalLayoutWidget_6.setObjectName("verticalLayoutWidget_6")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_6)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.InputPassword = QtWidgets.QLineEdit(self.verticalLayoutWidget_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.InputPassword.sizePolicy().hasHeightForWidth())
        self.InputPassword.setSizePolicy(sizePolicy)
        self.InputPassword.setObjectName("InputPassword")
        # 패스워드 Masking 
        self.InputPassword.setEchoMode(QLineEdit.Password)

        self.verticalLayout_6.addWidget(self.InputPassword)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def Button_Click(self):
        # print("Button Clicked")
        print(self.InputIP.text())
        print(self.InputPort.text())
        print(self.InputPassword.text())
        
    def retranslateUi(self, MainWindow):
        # IP 주소를 위한 정규 표현식
        ip_regex = QRegExp("^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$")
        ip_validator = QRegExpValidator(ip_regex, self)
        # 포트 번호를 위한 정규 표현식
        port_regex = QRegExp("^\\d{1,10}$")
        port_validator = QRegExpValidator(port_regex, self)
        
        _translate = QtCore.QCoreApplication.translate
        # MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "IP : "))
        self.AccessButton.setToolTip(_translate("MainWindow", "Trying to connect"))
        self.AccessButton.setText(_translate("MainWindow", "Login"))
        #버튼클릭 호출 추가
        self.AccessButton.clicked.connect(self.Button_Click)  
        self.label_2.setText(_translate("MainWindow", "Port :"))
        self.label_3.setText(_translate("MainWindow", "Password :"))
        self.InputPort.setToolTip(_translate("MainWindow", "Enter the port number to connect.."))
        self.InputPort.setPlaceholderText(_translate("MainWindow", "Insert the port number"))
        self.InputPort.setStyleSheet("QLineEdit { padding-left: 15px; }")
        self.InputPort.setValidator(port_validator)
        self.InputIP.setToolTip(_translate("MainWindow", "Enter the IP to connect.."))
        self.InputIP.setPlaceholderText(_translate("MainWindow", "Insert the IP"))
        self.InputIP.setStyleSheet("QLineEdit { padding-left: 15px; }")
        self.InputIP.setValidator(ip_validator)
        self.InputPassword.setToolTip(_translate("MainWindow", "Enter your password.."))
        self.InputPassword.setPlaceholderText(_translate("MainWindow", "Insert your password"))
        self.InputPassword.setStyleSheet("QLineEdit { padding-left: 15px; }")


# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     MainWindow = QtWidgets.QMainWindow()
#     ui = MainWindow()
#     ui.setupUi(MainWindow)
#     MainWindow.show()
#     sys.exit(app.exec_())

