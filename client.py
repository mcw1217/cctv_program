import os
import sys
import cv2
import json
import time
import threading
import socket,struct,pickle
from client_ui import MainWindow, VideoWindow, VideoThread, FrameThread
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

def send_data(sock, sndData):
  jsn_data = json.dumps(sndData).encode()
  sock.sendall(jsn_data)

def recv_data(sock):
  jsn_data = sock.recv(1024).decode()
  rcvData = json.loads(jsn_data)
  return rcvData

  
class ClientWindow(QMainWindow, MainWindow):
  def __init__(self, client_id):
    super().__init__()
    self.setWindowTitle(f"Client {client_id}")
    self.setupUi(self)
    self.show()
    self.client_socket = None
    self.videoWindow = None
    self.frameThread = None  
    self.AccessButton.clicked.connect(self.connect_to_server)

  def connect_to_server(self):
    ip = self.InputIP.text()
    port = int(self.InputPort.text())
    password = self.InputPassword.text()
    addr = (ip, port)
    self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try :
      print('try to connect to server...')
      self.client_socket.connect(addr)
      print('connected to server')
    except:
      print('connection failed')
      QMessageBox.warning(self, 'Connection Failed', 'Please check your input and try again.')
      self.InputIP.clear()
      self.InputPort.clear()
      self.InputPassword.clear()
      return
    self.start(password)  
    print('disconnect from server') 
    return

  def start(self, password): 
    rcvData = recv_data(self.client_socket)
    if rcvData['cmd'] == 'validation':
      sndData = {}
      sndData['cmd'] = 'password'
      sndData['param'] = [password]
      send_data(self.client_socket, sndData)
      print('Verifying ...')
      rcvData = recv_data(self.client_socket)
      if rcvData['cmd'][0] == 'access':
        print('\nAccess Success!\n')
        index = rcvData['cmd'][1]
        # main window close
        self.close()
        self.videoWindow = VideoWindow(index, client_id)
        self.videoWindow.show()
        self.frameThread = FrameThread(self.client_socket, self.videoWindow)  
        self.frameThread.start()
        self.frameThread.finished.connect(self.on_frameThread_finished)
      elif rcvData['cmd'] == 'deny':
        print('\nAccess Denied!\n')
        QMessageBox.warning(None, 'Connection Failed', 'Please check your password and try again.')
      else:
        print('\nAccess Error!\n')

  def on_frameThread_finished(self):
    print('frameThread finished')
    loop = QEventLoop()  
    self.frameThread.finished.connect(loop.quit)  
    loop.exec_()  
    
  def closeEvent(self, event):
    if self.frameThread is not None:  
        # self.frameThread.stop()
        self.frameThread.wait()
    event.accept()

client_id = os.getpid()
print(f"Client ID: {client_id}")
app=QApplication([])
mytest=ClientWindow(client_id)
QApplication.processEvents()
sys.exit(app.exec_())


