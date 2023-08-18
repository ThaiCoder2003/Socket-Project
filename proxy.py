from socket import *
from zlib import *
import os
from datetime import datetime

def config():
    config={}

    config["cache_time"]=900
    config["whitelist"]=["oosc.online", "example.com", "google.com", "bing.com", "testphp.vulnweb.com/login.php", "vbsca.ca/login/login.asp", "vbsca.ca/login", "vbsca.ca/login/LoginsAndPermissions3.htm"]
    config["time_in"]=8
    config["time_out"]=20

    return config

def TimeLimit():
    currentDateAndTime = datetime.now()
    float=currentDateAndTime.hour+currentDateAndTime.minute/60
    return (float>=config_info['time_in'] and float<=config_info['time_out'])

config_info=config()

cache_time=config_info["cache_time"]
whitelist=config_info["whitelist"]
time_in=config_info["time_in"]
time_out=config_info["time_out"]

# Hàm kiểm tra whitelist
def isWhite(input_str):
    return input_str in whitelist

#Hàm để kiểm tra phương thức
def is_valid_method(method):
    if method != 'GET' and method != 'POST' and method != 'HEAD':
        return False
    return True

#Hàm định nghĩa lại request
def create_proxy_request(request, target_host):
    request_splited = request.split(' ')

    #Kiểm tra phương thức
    if not is_valid_method(request_splited[0]):
        return
    #Đếm số xuỵt
    count_slash = 0
    for i in request_splited[1]:
        if i == '/':
            count_slash += 1

    #Kiểm tra xem có phải là gửi request lần 2 không
    if request.find('same-origin') == -1:
        if count_slash == 1:
            target_host = request_splited[1][1:]
            request_splited[1] = request_splited[1].replace(target_host,'')
        else:
            target_host = request_splited[1][1:request_splited[1].index('/',2)]
            request_splited[1] = request_splited[1].replace('/' + target_host,'')
    else:
        if count_slash == 1:
            request_splited[1] = request_splited[1].replace(target_host,'')
        else:
            request_splited[1] = request_splited[1].replace('/' + target_host,'')
    
    request_splited[3] = request_splited[3].replace('127.0.0.1:31103', target_host)
    return ' '.join(request_splited), target_host

def isImage(request, response):
    response_splited = response.split(b'\r\n')
    
    if response_splited[1].find(b'image') != -1:
        request_splited = request.split()
        path_img = request_splited[1].split('/')
        img_name = path_img[-1]
        extension = img_name.split('.')[1]
        if extension == 'png':
            return response.find(b'\x89')
        elif extension == 'jpg' or extension == 'jpeg':
            return response.find(b'\xff\xd8')
        # elif response.find(b'\x00\x00\x01\x00') != -1:
        #     return 'ico', response.find(b'\x00\x00\x01\x00')
    return None

def saveCache(request, response, target_host):
    idx = isImage(request, response)
    if idx == None:
        pass
    else:
        #Tạo path cho ảnh
        request_splited = request.split()
        path_img = request_splited[1].split('/')
        img_name = path_img[-1]
        img_name = target_host+'/'+img_name
        #Lưu ảnh nếu chưa tồn tại
        if not os.path.exists(img_name):
            os.makedirs(target_host, exist_ok = True)
            with open(img_name, 'wb') as f:
                # Tiến hành ghi dữ liệu vào tệp ảnh
                f.write(response[idx:])

def load_cache(request, target_host, tcpClientSock):
    #Điều tra request
    request_splited = request.split()
    http_ver = request_splited[2].split('\r\n')[0]
    path_img = request_splited[1].split('/')
    img_name = path_img[-1]
    img_name = target_host+'/'+img_name
    

    if img_name.find('png') != -1 or img_name.find('jpg') != -1 or img_name.find('jpeg') != -1:
        extension = img_name.split('.')[-1]
        if os.path.exists(img_name):
            #Lấy ảnh từ cache
            with open(img_name, 'rb') as f:
                img = f.read()
            #Gửi ảnh từ proxy
            response = http_ver.encode() + b'200 OK\r\nContent_type: image/' + extension.encode() + b'\r\n\r\n' + img
            print(f'RESPONSE:\n{response}')
            tcpClientSock.send(response)
            print(f'Tải ảnh {img_name} thành công')
            return True
    return False

def check_forbidden(request):
    request_splited = request.split()
    #test phương thức
    method = is_valid_method(request_splited[0])
    #test white list
    temp = request_splited[1].split('/')
    white = isWhite(temp[1])
    #test time
    time = TimeLimit()

    if request.find('same-origin') != -1:
        return True

    if method and white and time:
        return True
    return False

def send_forbidden(request, tcpClientSock):
    request_splited = request.split()
    http_ver = request_splited[2].split('\r\n')[0]
    with open('403/403.html', 'rb') as f_html:
        html = f_html.read()
    response = http_ver.encode() + b' 200 OK\r\nContent-Type: text/html\r\n\r\n' + html

    tcpClientSock.sendall(response)