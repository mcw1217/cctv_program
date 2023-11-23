import cv2
import json
import queue
import threading
import socket, pickle, struct, datetime


class System():
  def __init__(self):
    self.current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
    self.password_list = ['1234', '0000', 'pass', 'pwd123']
    self.index = 0    # 현재 접속 시도한 사용자의 번호
    self.users = {}     # 접속한 사용자들을 저장할 딕셔너리
    self.available_indices = queue.Queue()     # 사용 가능한 인덱스
    for i in range(1, 5):  # 인덱스 1부터 4까지 사용 가능한 인덱스로 설정
      self.available_indices.put(i)
    thread = threading.Thread(target=self.tcp_pro)
    thread.start()
    
  def send_data(self, client_socket, sndData):
    jsn_data = json.dumps(sndData).encode()
    client_socket.sendall(jsn_data)

  def recv_data(self, client_socket):
    jsn_data = client_socket.recv(1024).decode()
    rcvData = json.loads(jsn_data)
    return rcvData
  
  def validation(self, client_socket):
    sndData= {}
    sndData['cmd'] = 'validation'
    self.send_data(client_socket, sndData)
    
    rcvData = self.recv_data(client_socket)
    if rcvData['cmd'] == 'password':
      password = rcvData['param'][0]
      print('Verifying ...')
      if password in self.password_list:
        self.index = self.available_indices.get()  # 사용 가능한 인덱스 중 하나를 가져옴
        sndData = {}
        sndData['cmd'] = ['access', self.index]
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
        self.ret, self.frame = self.cap.read()
        
        current_time = datetime.datetime.now()        
        if current_time.minute == 0 and current_time.second ==0:
          if self.out is not None:
            self.out.release() 
          self.current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
          self.file_path = f'./video/{self.current_time}.mp4'
          self.out = cv2.VideoWriter(self.file_path, self.fourcc, self.fps, self.size) # VideoWriter 객체 생성
            
        if self.ret:
          now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
          cv2.putText(self.frame, now_time, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
          cv2.imshow('camera-recording', self.frame)
          self.out.write(self.frame)
          if cv2.waitKey(int(1000/self.fps)) != -1:
            break
        else:
          print('no file!')
          break
      self.out.release()                                       # 파일 닫기
    else:
      print("Can`t open camera!")
    self.cap.release()
    cv2.destroyAllWindows()
   
  def tcp_pro(self):
    print("Starting the server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = ('', 2023)     # host, port
    server_socket.bind(addr)
    server_socket.listen(5)
    print("Server is running!!")
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"[Client connected from: ]: {addr} ")
        if (self.validation(client_socket) != -1):
            print("Client validated")
            if self.available_indices.empty():  # 사용 가능한 인덱스가 없는 경우
                print("Maximum number of users reached")
                client_socket.close()
                continue
            self.users[self.index] = client_socket
            th1 = threading.Thread(target=self.send_frame, args=[self.users[self.index], self.index])
            th1.daemon= True
            th1.start()
        else:
            print('Client failed to connect')
            continue
      
  def send_frame(self, client_socket, index):
    while True:
      data = pickle.dumps(self.frame)
      message_size = struct.pack("L",len(data))
      try:
        client_socket.sendall(message_size + data)
      except:
        # 연결이 끊어진 경우 사용자를 제거하고 인덱스를 사용 가능한 인덱스로 반환
        del self.users[index]
        self.available_indices.put(index) 
        print(f"Client No.{index} disconnected")         
        break
                      
        
if __name__ == "__main__":
      system = System()
      system.main()