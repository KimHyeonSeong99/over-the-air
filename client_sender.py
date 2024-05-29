import someip
import os

target_list = []

global update_firmware_path, latest_version, file_list
update_firmware_path = '/home/avees/OTA/tmp/'
latest_version = dict()
file_list = dict()

def check_new_firmware():
    diff = []
    remove_dict_list =[]
    now_file_list = os.listdir(update_firmware_path)
    for firmware in now_file_list:
        if firmware not in file_list:
            diff.append(firmware)
            file_list[firmware] = dict()
            file_list[firmware]['FileName'] = firmware.split('-')[-1]
            file_list[firmware]['Target'] = firmware.split('-')[0]
            file_list[firmware]['Version'] = firmware.split('-')[1]
            if file_list[firmware]['Target'] not in target_list:
                target_list.append(file_list[firmware]['Target'])
            try:
                if float(file_list[firmware]['Version']) >= float(latest_version[file_list[firmware]['Target']]):
                    latest_version[file_list[firmware]['Target']] = file_list[firmware]['Version']            
                else:
                    remove_list.append(firmware)
            except:
                latest_version[file_list[firmware]['Target']] = file_list[firmware]['Version']

    for file in file_list:
        if file not in now_file_list:
            remove_dict_list.append(file)

    for file in remove_dict_list:
        del(file_list[file])
    
    if diff:
        remove_list=[]
        for firmware in diff:
            try:
                if float(file_list[firmware]['Version']) >= float(latest_version[file_list[firmware]['Target']]):
                    latest_version[file_list[firmware]['Target']] = file_list[firmware]['Version']            
                else:
                    remove_list.append(firmware)
            except:
                latest_version[file_list[firmware]['Target']] = file_list[firmware]['Version']
        for firmware in remove_list:
            diff.remove(firmware)

    if diff:
        print('='*30)
        for target in target_list:
            print('latest', target,'Version:',latest_version[target])
            print('='*30)
        print("need to update about: ", diff)
    return diff

# vSomeIP 통신 설정
while True:
     
    publish_list = []
    publish_list = check_new_firmware()

    if publish_list:
        for FileName in publish_list:
            app = someip.Application(0x1234)  # 이 값은 서비스 ID로 실제 사용하는 ID로 대체해야 합니다.
                
            # 파일 전송 실행
            file_path = update_firmware_path + FileName  # 전송할 파일 경로
            service_id = 0x5678  # 수신측에서 사용하는 서비스 ID

            # 파일을 열고 내용을 읽음
            with open(file_path, 'rb') as file:
                    file_data = file.read()               
                # 데이터를 패킷으로 분할하여 전송
            chunk_size = 1024  # 한 번에 전송할 데이터의 크기
            num_chunks = (len(file_data) + chunk_size - 1) // chunk_size  # 파일을 패킷으로 나눔

            message = someip.Packet(0xFFFF, service_id, someip.MsgType.NOTIFY, someip.ReturnCode.E_OK, FileName)
            app.send_message(message)

            for i in range(num_chunks):
                chunk_data = file_data[i * chunk_size: (i + 1) * chunk_size]
                message = someip.Packet(0xFFFF, service_id, someip.MsgType.NOTIFY, someip.ReturnCode.E_OK, chunk_data)
                app.send_message(message)