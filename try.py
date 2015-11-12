import socket
tcp_ip = "127.0.0.3"
tcp_port = 6669
listenerSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)   
listenerSocket.bind((tcp_ip,tcp_port))
listenerSocket.listen(2)
listenerSocket.close()