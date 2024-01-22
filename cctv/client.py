import os
import sys
import cv2
import json
import threading
import socket,struct,pickle
import datetime
from one_client_ui import LoginWindow, LiveVideoWindow, SavedVideoWindow, HomeWindow,DownloadableItem
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

on_play = False

class System():
  def __init__(self, liveVideoWindow=None, savedVideoWindow=None) :
    self.client_socket = None
    self.live_window = liveVideoWindow
    self.saved_window = savedVideoWindow
    
  def send_data(self, sock, sndData):
    jsn_data = json.dumps(sndData).encode()
    sock.sendall(jsn_data)

  def recv_data(self, sock):
    jsn_data = sock.recv(1024).decode()
    rcvData = json.loads(jsn_data)
    return rcvData 
  
  def connect_to_server(self, ClientLoginWindow):
    self.ClientLoginWindow = ClientLoginWindow
    ip = ClientLoginWindow.InputIP.text()
    port = int(ClientLoginWindow.InputPort.text())
    password = ClientLoginWindow.InputPassword.text()
    print(f"IP: {ip}, Port: {port}, Password: {password}")
    addr = (ip, port)
    # 서버 설정
    self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try :
      print('try to connect to server...')
      self.client_socket.connect(addr)  # 서버 IP 주소를 실제 서버의 IP로 변경
      print('connected to server')
      self.validation(password)
    except:
      print('connection failed')
      QMessageBox.warning(self.ClientLoginWindow, 'Connection Failed', 'Please check your input and try again.')
      self.ClientLoginWindow.InputIP.clear()
      self.ClientLoginWindow.InputPort.clear()
      self.ClientLoginWindow.InputPassword.clear()
      return
            
  def validation(self, password):
    client_socket = self.client_socket
    rcvData = self.recv_data(client_socket)
    if rcvData['cmd'] == 'validation':
      sndData = {}
      sndData['cmd'] = 'password'
      sndData['param'] = [password]
      self.send_data(client_socket, sndData)
      print('Verifying ...')
      
      rcvData = self.recv_data(client_socket)
      if rcvData['cmd'] == 'access':
        print('\nAccess Success!\n')
        # main window close
        self.ClientLoginWindow.close()
        self.HomeWindow = ClientHomeWindow(client_id, self)
        self.HomeWindow.show()
        rcvData = self.recv_data(client_socket)
        self.rtsp_url = rcvData["para"]
      
      elif rcvData['cmd'] == 'deny':
        print('\nAccess Denied!\n')
        QMessageBox.warning(None, 'Connection Failed', 'Please check your password and try again.')
        return
      else:
        print('\nAccess Error!\n')
        return
    
  def send_frame(self,rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)
    
    while on_play:
      ret, frame = cap.read()
      if not ret:
        print("no frame")
        break
      self.live_window.update_frame(frame)


class ClientLoginWindow(QMainWindow, LoginWindow):
  def __init__(self, client_id, system):
    super().__init__()
    self.system = system
    self.setWindowTitle(f"Client {client_id}")
    self.setupUi(self)
    self.move(300, 300)
    
    # 버튼 클릭 시 connect_to_server 함수 호출
    self.LoginButton.clicked.connect(lambda:self.system.connect_to_server(self))
  
class ClientHomeWindow(HomeWindow):
  def __init__(self, client_id, system):
    super().__init__()    
    self.client_id = client_id
    self.system = system
    
    # 버튼 클릭 시 특정 함수 호출
    self.LiveVideoButton.clicked.connect(self.play_liveVideo)
    self.SavedVideoButton.clicked.connect(self.play_savedVideo)
    
  def go_home(self):
    global on_play
    self.show()
    on_play = False    
    
  def play_liveVideo(self):
    global on_play
    on_play = True
    print('play live video')
    self.close()
    # live video play
    self.LiveWindow = LiveVideoWindow(self.client_id, self.go_home)
    self.system.live_window = self.LiveWindow
    threading.Thread(target=self.system.send_frame,args=[self.system.rtsp_url]).start()
    self.LiveWindow.show()
    
  def play_savedVideo(self):
    print('play saved video')
    self.close()
    self.sndData = {}
    self.sndData['cmd'] = 'open_video'
    self.system.send_data(self.system.client_socket,self.sndData)
    recD = self.system.recv_data(self.system.client_socket)
    self.SavedWindow = SavedVideoWindow(recD,self.go_home,self.download_func)
    self.SavedWindow.show()
    # saved video play
    
  def download_func(self,file_path,download_button):
    self.SavedWindow.dis_bu()
    self.file_path = file_path
    self.sndData={}
    self.sndData['cmd'] = 'download'
    self.sndData['para'] = self.file_path
    self.system.send_data(self.system.client_socket,self.sndData)
    
    data = self.system.client_socket.recv(1024)
    
    self.real_path = os.path.join(os.getcwd(),self.file_path)
    with open(self.real_path,'wb') as rec_file:
      try:
        while True:
          rec_file.write(data)
          if len(data) < 1024:  #데이터가 1024씩 받는데 마지막에 1024보다 작은 데이터가 들어오면 마지막 데이터이기때문에 파일 다운로드를 종료
            break
          data = self.system.client_socket.recv(1024)
          
      except Exception as ex:
        print(ex)
    self.SavedWindow.en_bu()
    print("다운로드 완료")
    
    


if __name__ == "__main__":
  client_id = os.getpid()
  print(f"Client ID: {client_id}")
  app=QApplication([])
  ClientLoginWindow = ClientLoginWindow(client_id, System())
  ClientLoginWindow.show()
  QApplication.processEvents()
  sys.exit(app.exec_())


