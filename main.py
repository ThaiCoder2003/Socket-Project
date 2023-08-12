from proxy import *
from socket import *
from gzip import *

IP = '127.0.0.1'
PORT = 31103
ADDR = (IP, PORT)
TARGET_PORT = 80 #http: 80


#Mở socket tại proxy
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
tcpSerSock.bind(ADDR)
tcpSerSock.listen()

print('Proxy server is listening on', ADDR)


while True:
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)

    #Lấy request từ web client
    request_data = tcpCliSock.recv(4096).decode('utf-8')
    request_data, target_host = create_proxy_request(request_data)
    print(f'REQUEST:\n{request_data}')

    #Mở socket đến Server
    target_socket = socket(AF_INET, SOCK_STREAM)
    target_socket.connect((target_host, TARGET_PORT))
    
    #Gửi request đến Server
    target_socket.send(request_data.encode())
    #Nhận response từ server
    try:
        response_data = target_socket.recv(4096).decode('utf-8')
        tcpCliSock.send(response_data.encode())
    except:
        response_data = target_socket.recv(4096)
        tcpCliSock.send(response_data)
    #Gửi response cho web client
    tcpCliSock.send(response_data.encode())
    print(f'RESPONSE:\n{response_data}')
    
    target_socket.close()
    tcpCliSock.close()
    
tcpSerSock.close()
