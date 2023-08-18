from proxy import *
from socket import *


IP = '127.0.0.1'
PORT = 31103
ADDR = (IP, PORT)
TARGET_PORT = 80 #http: 80


#Mở socket tại proxy
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
tcpSerSock.bind(ADDR)
i = 0
target_host = ''
tcpSerSock.listen()
run = True
while run:
    try:
        print('Proxy server is listening on', ADDR)
        print('Ready to serve...')
        tcpCliSock, addr = tcpSerSock.accept()
        print('Received a connection from:', addr)
        
        #Lấy request từ web client
        request_data = tcpCliSock.recv(65536).decode('utf-8')

        if not check_forbidden(request_data):
            send_forbidden(request_data, tcpCliSock)
            tcpCliSock.close()
        else:
            #Điều chỉnh lại request
            request_data, target_host = create_proxy_request(request_data, target_host)

            #Mở socket đến Server
            target_socket = socket(AF_INET, SOCK_STREAM)
            target_socket.connect((target_host, TARGET_PORT))
            
            #Duyệt trong cache nếu không có cache thì sẽ gửi đến server
            if not load_cache(request_data, target_host, tcpCliSock):
                #Gửi request đến Server
                target_socket.send(request_data.encode())
                response_data = target_socket.recv(65536)
                #lưu cache
                saveCache(request_data, response_data, target_host)
                tcpCliSock.send(response_data)
            
            target_socket.close()
            tcpCliSock.close()
    except KeyboardInterrupt:
        tcpSerSock.close()
        print('CLOSE')
        run = False
