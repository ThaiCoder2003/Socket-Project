from socket import *
from zlib import *
import os

from important.file_config import config
from important.time_constraint import TimeLimit
config_info=config()

cache_time=config_info["cache_time"]
whitelist=config_info["whitelist"]
time_in=config_info["time_in"]
time_out=config_info["time_out"]



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

def unzip(response):
    idx = response.find(b'\x1f')
    if idx != -1:
        gzip = response[idx:]
        response = response[:idx] + decompress(gzip, MAX_WBITS | 16)
    return response

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
        request_splited = request.split()
        path_img = request_splited[1].split('/')
        img_name = path_img[-1]
        img_name = target_host+'/'+img_name
        if not os.path.exists(img_name):
            os.makedirs(target_host, exist_ok = True)
            with open(img_name, 'wb') as f:
                # Tiến hành ghi dữ liệu vào tệp ảnh
                f.write(response[idx:])

def load_cache(request, target_host, tcpClientSock):
    request_splited = request.split()
    http_ver = request_splited[2].split('\r\n')[0]
    path_img = request_splited[1].split('/')
    img_name = path_img[-1]
    img_name = target_host+'/'+img_name
    

    if img_name.find('png') != -1 or img_name.find('jpg') != -1 or img_name.find('jpeg') != -1:
        extension = img_name.split('.')[-1]
        if os.path.exists(img_name):
            with open(img_name, 'rb') as f:
                img = f.read()
            response = http_ver.encode() + b'200 OK\r\nContent_type: image/' + extension.encode() + b'\r\n\r\n' + img
            print(f'RESPONSE:\n{response}')
            tcpClientSock.send(response)
            return True
    return False