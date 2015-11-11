import socket
import struct
import json
import sys
import logging
import threading
import time
MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
BUFSIZE = 8192   
TCP_TIMEOUT=2
TCP_QUEUE_LIMIT=5

tcp_ip='127.0.0.1'
tcp_port=6667

def getPredAndSucc(ip,port):
	sender = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
	flag=True
	data={}
	data['tcp_ip']=tcp_ip
	data['tcp_port']=tcp_port
	data['type']='GET_BOTH'
	while flag:
		try:
			sender.connect((ip,int(port)))
			sender.send(json.dumps(data))
			sender.close()
			flag=False
		except:
			print "Unable to send "+ repr(data) +" to "+ip+":"+str(port)
	
	listenerSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
	listenerSocket.bind((tcp_ip,tcp_port))

	listenerSocket.listen(TCP_QUEUE_LIMIT)
	try:
		connectionSocket, addr =  listenerSocket.accept()

		data = ''
		while True:
			sen = connectionSocket.recv(BUFSIZE)
			if not sen: 
				break
			data +=sen
		print data
		# data = json.loads(data)

		# processTcpDataThread= threading.Thread(name='processTcpData', target=processTcpData,args=(data,))
		# processTcpDataThread.start()
		# processTcpData(data)
		# connectionSocket.close()	
		print"yop"
	except:

		print "exception here1"
		e = sys.exc_info()[0]
		print repr(e)

def main():
	global tcp_ip
	tcp_ip = sys.argv[1];
	print "tcp_ip is: "+tcp_ip
	
	f=True
	while f:
		ip = str(raw_input("ip: "))
		port = 6666
		getPredAndSucc(ip,port)
		c = str(raw_input("cont?"))
		if(c!='y'):
			f=False






if __name__ == '__main__':
    main()