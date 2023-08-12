from socket import *

#Hàm để kiểm tra phương thức
def is_valid_method(method):
    if method != 'GET' and method != 'POST' and method != 'HEAD':
        return False
    return True

#Hàm định nghĩa lại request
def create_proxy_request(request):
    request_splited = request.split(' ')

    #Kiểm tra phương thức
    if not is_valid_method(request_splited[0]):
        return
    #Đếm số xuỵt
    count_slash = 0
    for i in request_splited[1]:
        if i == '/':
            count_slash += 1


    if count_slash == 1:
        target_host = request_splited[1][1:]
        request_splited[1] = request_splited[1].replace(target_host,'')
    else:
        target_host = request_splited[1][1:request_splited[1].index('/',2)]
        request_splited[1] = request_splited[1].replace('/' + target_host,'')
    
    request_splited[3] = request_splited[3].replace('127.0.0.1:31103', target_host)
    return ' '.join(request_splited), target_host