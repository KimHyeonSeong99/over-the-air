import someip
import os

# vSomeIP 통신 설정
app = someip.Application(0x5678)  # 서비스 ID로 전송 측과 동일한 값을 사용해야 합니다.

# 파일을 수신하는 함수 정의
def receive_file(file_directory):
    # 데이터를 수신하고 파일로 저장
    file_path = file_directory + app.receive_message().payload
    with open(file_path, 'wb') as file:
        while True:
            message = app.receive_message()
            if not message:
                break
            file.write(message.payload)

# 파일 수신 실행
file_directory = '/home/sea/sea-me-hackathon-2023/Cluster/src/'  # 수신한 파일을 저장할 경로
receive_file(file_directory)
os.chdir('/home/sea/sea-me-hackathon-2023/Cluster/src/')
os.system("make -j6")


