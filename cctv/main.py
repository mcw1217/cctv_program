import cv2
import json
import threading
import socket ,datetime,sys,time,os
from flask import Flask, Response
app = Flask(__name__)


class System():
  def __init__(self):
    self.current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
    self.password_list = ['1234', '0000', 'pass', 'pwd123']
    self.save_video_func = False
    thread = threading.Thread(target=self.tcp_pro)
    thread.start()
    
  def send_data(self, client_socket, sndData):
    jsn_data = json.dumps(sndData).encode()
    client_socket.sendall(jsn_data)

  def recv_data(self, client_socket):
    try:
      jsn_data = client_socket.recv(1024).decode()
      rcvData = json.loads(jsn_data)
      return rcvData
    except:pass
  
  def validation(self, client_socket):
    sndData= {}
    sndData['cmd'] = 'validation'
    self.send_data(client_socket, sndData)
    
    rcvData = self.recv_data(client_socket)
    if rcvData['cmd'] == 'password':
      password = rcvData['param'][0]
      print('Verifying ...')
      if password in self.password_list:
        sndData = {}
        sndData['cmd'] = 'access'
        self.send_data(client_socket, sndData)
        print('\nAccess Success!\n')
        return 1
      else:
        sndData = {}
        sndData['cmd'] = 'deny'
        self.send_data(client_socket, sndData)
        print('\nAccess Denied!\n')
        return -1
    return -1
  
   
  def main(self):
    self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if self.cap.isOpened:
      self.file_path = f'./video/{self.current_time}.mp4'
      self.fps = 30
      self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')            # 인코딩 포맷 문자
      self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
      self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
      self.size = (int(self.width), int (self.height))                   # 프레임 크기
      
      self.out = cv2.VideoWriter(self.file_path, self.fourcc, self.fps, self.size) # VideoWriter 객체 생성
      while True:
        try:
          self.ret, self.frame = self.cap.read()
          
          #정각마다 영상 저장
          current_time = datetime.datetime.now()        
          if current_time.minute == 0 and current_time.second ==0:
            if self.out is not None:
              self.out.release() 
            self.current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
            self.file_path = f'./video/{self.current_time}.mp4'
            self.out = cv2.VideoWriter(self.file_path, self.fourcc, self.fps, self.size) # VideoWriter 객체 생성
            
          #클라이언트가 영상 목록을 불러오려고 하면 현재 영상을 저장하고, 새로운 영상을 녹화          
          if self.save_video_func:
            if self.out is not None:
              self.out.release() 
            self.current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
            self.file_path = f'./video/{self.current_time}.mp4'
            self.out = cv2.VideoWriter(self.file_path, self.fourcc, self.fps, self.size) # VideoWriter 객체 생성
            self.save_video_func = False
            
          
          if self.ret:
            now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cv2.putText(self.frame, now_time, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            # cv2.imshow('camera-recording', self.frame)
            self.out.write(self.frame)
            if cv2.waitKey(int(1000/self.fps)) != -1:
              break
          else:
            print('no file!')
            break
        except:
          print("오류발생")
          self.out.release()
          break
      self.out.release()                                       # 파일 닫기
    else:
      print("Can`t open camera!")
    self.out.release()   
    self.cap.release()
    cv2.destroyAllWindows()
    sys.exit()
        
  def tcp_pro(self):
    print("Starting the server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = ('', 2023)     # host, port
    server_socket.bind(addr)
    server_socket.listen(5)
    print("Server is running!!")
    users=[]
    while True:
      client_socket, addr = server_socket.accept()
      print(f"[Client connected from: ]: {addr} ")
      if (self.validation(client_socket) != -1):
        print("Client validated")
        users.append(client_socket)
        if users:
          sndData= {}
          sndData['cmd'] = 'url'
          sndData['para'] = "http://wolsv.kro.kr:2022/video_feed"
          self.send_data(users[0],sndData)
          th1 = threading.Thread(target=self.open_video, args=[users[0]])
          th1.daemon = True
          th1.start()
          del users[0]
      else:
        print('Client failed to connect')
        continue
      
  def open_video(self, client_socket):
    self.client_socket = client_socket
    while True:
      try:
        recvd = self.recv_data(self.client_socket)
        if recvd['cmd'] == 'open_video':
          self.save_video_func = True
          video_dic_path = os.path.join(os.getcwd(), 'video')
          video_files = [f for f in os.listdir(video_dic_path)]
          self.send_data(self.client_socket, video_files)
        if recvd['cmd'] == 'download':
          threading.Thread(target=self.send_video, args=[recvd['para']]).start()
          
      except:
        print("Disconnect: ", self.client_socket.getsockname())
        break
      
  def send_video(self,path):
    self.real_path = os.path.join(os.path.join(os.getcwd(),'video'),path)
    data_transferred = 0
    
    with open(self.real_path,'rb') as video_file:
      data = video_file.read(1024)
      while data:
        data_transferred += self.client_socket.send(data)
        data = video_file.read(1024)
    print("전송완료")
    print(data_transferred)
        
def generate_frames():
    while True:
      frame = system.frame
      ret, buffer = cv2.imencode('.jpg',frame)
      if not ret:
        break

      frame = buffer.tobytes()
      yield (b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
          
        
        
        
if __name__ == "__main__":
      system = System()
      threading.Thread(target=app.run,args=['0.0.0.0',2022]).start()
      threading.Thread(target=system.main()).start()