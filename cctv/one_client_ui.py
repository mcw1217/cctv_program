# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'client.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

import typing
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget
import threading

class LiveVideoWindow(QMainWindow):
    def __init__(self, client_id, go_home_callback):
        super().__init__()
        self.setWindowTitle(f"Client {client_id}")
        self.image_label = QLabel(self)
        self.setCentralWidget(self.image_label)
        self.go_home_func = go_home_callback

        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)
        home_menu = menu_bar.addMenu('Home')

        go_home_action = QAction('Go Home', self)
        go_home_action.triggered.connect(self.go_home)
        home_menu.addAction(go_home_action)

    def update_frame(self, frame):
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(image)
        self.image_label.setPixmap(pixmap)

    def go_home(self):
        print('Going home...')
        self.close()
        self.go_home_func()
class DownloadableItem(QWidget):
    def __init__(self, item_text,download_func):
        super(DownloadableItem, self).__init__()
        self.download_func = download_func
        # 리스트 항목에 대한 위젯 구성
        layout = QVBoxLayout()

        self.label = QLabel(item_text)
        self.download_button = QPushButton('다운로드')
        self.download_button.clicked.connect(self.download)

        layout.addWidget(self.label)
        layout.addWidget(self.download_button)

        self.setLayout(layout)

    def download(self):
        # 다운로드 버튼이 눌렸을 때 수행할 동작 정의
        threading.Thread(target=self.download_func,args=[self.label.text(),self.download_button]).start()
        
            
class SavedVideoWindow(QMainWindow):
    def __init__(self,recD,go_home_callback,download_func):
        super().__init__()
        self.recD = recD
        self.go_home_func = go_home_callback
        self.download_func = download_func
        self.download_items = []
        self.initUI()
        

    def initUI(self):
        
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Home")
        
        home_action = QAction("go_home",self)
        home_action.triggered.connect(self.go_home)
        file_menu.addAction(home_action)
        
        
        # QListWidget을 부모로 하는 QListWidget 객체 생성
        self.list_widget = QListWidget(self)
        
        for item_text in self.recD:
            item_widget = DownloadableItem(item_text,self.download_func)
            list_item = QListWidgetItem(self.list_widget)
            list_item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, item_widget)
            self.download_items.append(item_widget)


        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        
        central_widget= QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.center()

        # 윈도우 설정
        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle('저장된 영상 목록')
    
        
    def en_bu(self):
        for item in self.download_items:
            item.setEnabled(True)
       
        
    
    def dis_bu(self):
        for item in self.download_items:
            item.setEnabled(False)
    
    def center(self):
        # 창을 화면 중앙에 위치시키는 메서드
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def go_home(self):
        print('Going home...')
        self.close()
        self.go_home_func()
             
        
    

class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        vbox = QVBoxLayout()
        self.LiveVideoButton = QPushButton('Live')
        vbox.addWidget(self.LiveVideoButton)
        vbox.addStretch(1)

        self.SavedVideoButton = QPushButton('Recorded')
        vbox.addWidget(self.SavedVideoButton)
        vbox.addStretch(1)
        widget = QWidget()
        widget.setLayout(vbox)

        self.setCentralWidget(widget)

class LoginWindow(object):        
    def setupUi(self, MainWindow):  
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 550)
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
        self.LoginButton = QtWidgets.QPushButton(self.centralwidget)
        self.LoginButton.setGeometry(QtCore.QRect(560, 220, 171, 81))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.LoginButton.setFont(font)
        self.LoginButton.setObjectName("LoginButton")
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
        
    def retranslateUi(self, MainWindow):
        # IP 주소를 위한 정규 표현식
        ip_regex = QRegExp("^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$")
        ip_validator = QRegExpValidator(ip_regex, self)
        # 포트 번호를 위한 정규 표현식
        port_regex = QRegExp("^\\d{1,10}$")
        port_validator = QRegExpValidator(port_regex, self)
        
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("MainWindow", "IP : "))
        self.LoginButton.setToolTip(_translate("MainWindow", "Trying to connect"))
        self.LoginButton.setText(_translate("MainWindow", "Login"))
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


