import cv2
import asyncio
import pickle
import struct
import datetime

class System:

    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        self.file_path = f'./video/{self.current_time}.mp4'
        self.fps = 30
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.size = (int(self.width), int(self.height))
        self.out = cv2.VideoWriter(self.file_path, self.fourcc, self.fps, self.size)

    async def send_frame(self, client_writer):
        while True:
            ret, frame = self.cap.read()
            if ret:
                now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cv2.putText(frame, now_time, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                data = pickle.dumps(frame)
                message_size = struct.pack("L", len(data))
                client_writer.write(message_size + data)
                self.out.write(frame)
                await client_writer.drain()
            else:
                print('프레임이 없습니다!')
                break

    async def handle_client(self, reader, writer):
        print("클라이언트 연결됨")
        await self.send_frame(writer)
        print("클라이언트 연결 해제됨")

    async def main(self):
        server = await asyncio.start_server(
            self.handle_client, '127.0.0.1', 899)

        addr = server.sockets[0].getsockname()
        print(f'서버가 {addr} 에서 실행 중입니다.')

        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    system = System()
    asyncio.run(system.main())
