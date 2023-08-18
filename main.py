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
while True:
    
    print('Proxy server is listening on', ADDR)
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)
    
    
    #Lấy request từ web client
    request_data = tcpCliSock.recv(65536).decode('utf-8')
    request_data, target_host = create_proxy_request(request_data, target_host)
    print(f'REQUEST:\n{request_data}\n')


    #Mở socket đến Server
    target_socket = socket(AF_INET, SOCK_STREAM)
    target_socket.connect((target_host, TARGET_PORT))
    
    #Gửi request đến Server
    target_socket.send(request_data.encode())

    if not load_cache(request_data, target_host, tcpCliSock):
        response_data = target_socket.recv(65536)
        saveCache(request_data, response_data, target_host)

        tcpCliSock.send(response_data)
        print(f'RESPONSE:\n{response_data}\n')
    
    target_socket.close()
    tcpCliSock.close()
    
tcpSerSock.close()
