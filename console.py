import socket
import struct
import json
import re
import sys
import os
import logging
import threading
import time
MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
BUFSIZE = 8192   
TCP_TIMEOUT=2
TCP_QUEUE_LIMIT=5
commands =['PUT','PUT_CHORD','GET_CHORD','DELETE','GET','SEARCH']
tcp_ip='127.0.0.1'
tcp_port=8907
listen_port=6666
own_id=""
hash_index=1024



def check_succ(own_id,succ_id,file_hash):
	if (file_hash >= own_id and file_hash < succ_id  and succ_id > own_id) or succ_id ==own_id or (file_hash >= own_id and succ_id < own_id) or (file_hash < succ_id and succ_id < own_id):
		return True
	else:
		return False

def process_command(own_id,command,path,file_name):
	if command == 'PUT_CHORD':
		file_data = {}
		file_hash=hash(file_name)%hash_index
		print "File to be uploaded is "+file_name +"("+str(file_hash)+")"
		file_data['type'] = "PUT_CHORD" 
		file_data['file_name'] = file_name
		file_data['file_src_ip'] = tcp_ip
		file_data['file_src_port'] = tcp_port
		file_data['file_id'] = file_hash
		flag = True
		sender = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		while flag:
			try:
				sender.connect((tcp_ip,listen_port))
				sender.send(json.dumps(file_data))
				sender.close()
				flag=False
			except:
				print "Unable to send "+ repr(data) +" to "+dest_ip+":"+str(listen_port)
		listenerSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
		flag = True
		print "Binding....."
		while flag:
			try:
				print "Binding to ",tcp_ip
				listenerSocket.bind((tcp_ip,tcp_port))
				flag = False
			except:
				"Waiting to bind "
		print "Bind completed ..."
		listenerSocket.listen(TCP_QUEUE_LIMIT)
		connectionSocket, addr =  listenerSocket.accept()
		print addr
		data = ''
		while True:
			sen = connectionSocket.recv(BUFSIZE)
			if not sen: 
				break
			data +=sen
		data=data[1:len(data)-1]
		print addr
		connectionSocket.close()
		listenerSocket.close()
		if data == "ACK_FILE":
			s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
			s.bind((tcp_ip,tcp_port))
			port_u=addr[1]+1
			print port_u
			flag=True
			while flag:
				try:
					s.connect((addr[0],int(addr[1])+1))
					flag=False
				except:
					pass
			print "will be sending file"
			f = open(path,'rb')
			print 'Sending...'
			l = f.read(1024)
			while (l):
				s.send(l)
				l = f.read(1024)
			f.close()
			print "Done Sending"
			s.shutdown(socket.SHUT_WR)
			s.close()
			print "file will be sent" 
		elif data == "NACK_FILE":
			print "File is already there in the Destination node"
		else:
			print "File cannot be sent now"

	elif command == 'GET_CHORD':
		file_data = {}
		file_hash=hash(file_name)%hash_index
		print "File to be downloaded is "+file_name +"("+str(file_hash)+")"
		file_data['type'] = "GET_CHORD" 
		file_data['file_name'] = file_name
		file_data['file_src_ip'] = tcp_ip
		file_data['file_src_port'] = tcp_port
		file_data['file_id'] = file_hash
		flag = True
		sender = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		while flag:
			try:
				sender.connect((tcp_ip,listen_port))
				sender.send(json.dumps(file_data))
				sender.close()
				flag=False
			except:
				print "Unable to send "+ repr(data) 
		listenerSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
		flag = True
		print "Binding....."
		while flag:
			try:
				listenerSocket.bind((tcp_ip,tcp_port))
				flag = False
			except:
				"Waiting to bind "
		listenerSocket.listen(TCP_QUEUE_LIMIT)
		connectionSocket, addr =  listenerSocket.accept()
		data = ''
		while True:
			sen = connectionSocket.recv(BUFSIZE)
			if not sen: 
				break
			data +=sen
		data=data[1:len(data)-1]
		print addr
		connectionSocket.close()
		listenerSocket.close()
		if data == "ACK_FILE":
			print "will be downloading file"
			print 'downloading...'
			f = open('share/'+str(own_id)+"/"+file_name,'wb')
			s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
			s.bind((tcp_ip,tcp_port))
			s.listen(5)
			c, addr = s.accept()
			print 'Got connection from', addr
			print "Receiving..."
			l = c.recv(1024)
			while (l):
				print "Receiving..."
				f.write(l)
				l = c.recv(1024)
			f.close()
			print "Done Receiving"
			c.close()        
			s.close()
			print "file has been downloaded"
			# flag=True
			# l = f.read(1024)
			# while (l):
			# 	s.send(l)
			# 	l = f.read(1024)
			# f.close()
			# print "Done Sending"
			# s.shutdown(socket.SHUT_WR)
			# s.close()
			# print "file will be sent" 
		elif data == "NACK_FILE":
			print "File is not there in the Destination node"
		else:
			print "File cannot be downloaded now"
		

	elif command == 'PUT':
		file_hash=hash(file_name)%hash_index
		print "File to be uploaded is "+file_name +"("+str(file_hash)+")" 
		data=getPredAndSucc(tcp_ip,listen_port)
		data=json.loads(data)
		own_id=hash(data['tcp_ip']+":"+str(listen_port))%hash_index
		succ_id=hash(data['succ_ip']+":"+str(listen_port))%hash_index
		pred_id=hash(data['pred_ip']+":"+str(listen_port))%hash_index
		current_id=own_id
		print current_id,succ_id
		while not check_succ(current_id,succ_id,file_hash):
			data=getPredAndSucc(data['succ_ip'],listen_port)
			current_id=succ_id
			data=json.loads(data)
			succ_id=hash(data['succ_ip']+":"+str(listen_port))%hash_index
			pred_id=hash(data['pred_ip']+":"+str(listen_port))%hash_index
			print data['tcp_ip'] +" has forwarded to "+data['succ_ip']
			print data
			print current_id,succ_id

		print "File will be put at this location "+data['tcp_ip']+" "+str(current_id)
		dest_ip=data['tcp_ip']
		if dest_ip == tcp_ip :
			print "File has already been uploaded "
		else:
			data={}
			data['tcp_ip']=tcp_ip
			data['tcp_port']=tcp_port
			data['type']='UPLOAD_FILE'
			data['file']=file_name
			print data
			flag=True
			sender = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			while flag:
				try:
					sender.connect((dest_ip,listen_port))
					sender.send(json.dumps(data))
					sender.close()
					flag=False
				except:
					print "Unable to send "+ repr(data) +" to "+dest_ip+":"+str(listen_port)
			listenerSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
			listenerSocket.bind((tcp_ip,tcp_port))
			listenerSocket.listen(TCP_QUEUE_LIMIT)
			connectionSocket, addr =  listenerSocket.accept()
			data = ''
			while True:
				sen = connectionSocket.recv(BUFSIZE)
				if not sen: 
					break
				data +=sen
			data=data[1:len(data)-1]
			print addr
			connectionSocket.close()
			listenerSocket.close()
			if data == "ACK_FILE":
				
				s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
				s.bind((tcp_ip,tcp_port))
				port_u=addr[1]+1
				print port_u
				flag=True
				while flag:
					try:
						s.connect((addr[0],int(addr[1])+1))
						flag=False
					except:
						pass
				print "will be sending file"
				f = open(path,'rb')
				print 'Sending...'
				l = f.read(1024)
				while (l):
					s.send(l)
					l = f.read(1024)
				f.close()
				print "Done Sending"
				s.shutdown(socket.SHUT_WR)
				s.close()
				print "file will be sent" 
			elif data == "NACK_FILE":
				print "File is already there in the Destination node"
			else:
				print "File cannot be sent now"
				
	elif command == 'GET':
		file_hash=hash(file_name)%hash_index
		print "File to be downloaded is "+file_name +"("+str(file_hash)+")" 
		data=getPredAndSucc(tcp_ip,listen_port)
		data=json.loads(data)
		own_id=hash(data['tcp_ip']+":"+str(listen_port))%hash_index
		succ_id=hash(data['succ_ip']+":"+str(listen_port))%hash_index
		pred_id=hash(data['pred_ip']+":"+str(listen_port))%hash_index
		current_id=own_id
		print current_id,succ_id
		while not check_succ(current_id,succ_id,file_hash):
			data=getPredAndSucc(data['succ_ip'],listen_port)
			current_id=succ_id
			data=json.loads(data)
			succ_id=hash(data['succ_ip']+":"+str(listen_port))%hash_index
			pred_id=hash(data['pred_ip']+":"+str(listen_port))%hash_index
			print data['tcp_ip'] +" has forwarded to "+data['succ_ip']
			print data
			print current_id,succ_id

		print "File will be downloaded from this location "+data['tcp_ip']+" "+str(current_id)
		dest_ip=data['tcp_ip']
		if dest_ip == tcp_ip :
			print "File is present in the self location "
		else:
			data={}
			data['tcp_ip']=tcp_ip
			data['tcp_port']=tcp_port
			data['type']='DOWNLOAD_FILE'
			data['file']=file_name
			print data
			flag=True
			sender = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			while flag:
				try:
					sender.connect((dest_ip,listen_port))
					sender.send(json.dumps(data))
					sender.close()
					flag=False
				except:
					print "Unable to send "+ repr(data) +" to "+dest_ip+":"+str(listen_port)
			listenerSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
			listenerSocket.bind((tcp_ip,tcp_port))
			listenerSocket.listen(TCP_QUEUE_LIMIT)
			connectionSocket, addr =  listenerSocket.accept()
			data = ''
			while True:
				sen = connectionSocket.recv(BUFSIZE)
				if not sen: 
					break
				data +=sen
			data=data[1:len(data)-1]
			print addr
			connectionSocket.close()
			listenerSocket.close()
			if data == "ACK_FILE":
				print "will be downloading file"
				print 'downloading...'
				f = open('share/'+str(own_id)+"/"+file_name,'wb')
				s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
				s.bind((tcp_ip,tcp_port))
				s.listen(5)
				c, addr = s.accept()
				print 'Got connection from', addr
				print "Receiving..."
				l = c.recv(1024)
				while (l):
					print "Receiving..."
					f.write(l)
					l = c.recv(1024)
				f.close()
				print "Done Receiving"
				c.close()        
				s.close()
				print "file has been downloaded"
				# flag=True
				# l = f.read(1024)
				# while (l):
				# 	s.send(l)
				# 	l = f.read(1024)
				# f.close()
				# print "Done Sending"
				# s.shutdown(socket.SHUT_WR)
				# s.close()
				# print "file will be sent" 
			elif data == "NACK_FILE":
				print "File is not there in the Destination node"
			else:
				print "File cannot be downloaded now"
				
			

def getPredAndSucc(ip,port):
	sender = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
	flag=True
	data={}
	data['tcp_ip']=tcp_ip
	data['tcp_port']=tcp_port
	data['type']='GET_BOTH'
	while flag:
		try:
			sender.connect((ip,port))
			sender.send(json.dumps(data))
			sender.close()
			flag=False
		except:
			print "Unable to send "+ repr(data) +" to "+ip+":"+str(port)
	
	listenerSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	flag=True
	while flag:    
		try:
			listenerSocket.bind((tcp_ip,tcp_port))
			flag=False
		except:
			pass

	listenerSocket.listen(TCP_QUEUE_LIMIT)
	try:
		connectionSocket, addr =  listenerSocket.accept()

		data = ''
		while True:
			sen = connectionSocket.recv(BUFSIZE)
			if not sen: 
				break
			data +=sen
		#print"yop"
		connectionSocket.close()
		listenerSocket.close()
		return data
		# data = json.loads(data)

		# processTcpDataThread= threading.Thread(name='processTcpData', target=processTcpData,args=(data,))
		# processTcpDataThread.start()
		# processTcpData(data)
		# connectionSocket.close()	
		
	except:
		listenerSocket.close()
		print "exception here1"
		e = sys.exc_info()[0]
		print repr(e)

def main():
	global tcp_ip
	tcp_ip = sys.argv[1];
	own_id=hash(tcp_ip+":"+str(listen_port))%hash_index
	if not os.path.exists('share/'+str(own_id)):
		os.makedirs('share/'+str(own_id))
	print "tcp_ip is: "+tcp_ip+"Port number being used is "+str(tcp_port)
	#k=int(raw_input())
	f=True
	while f:
		#ip = str(raw_input("ip: "))
		c = str(raw_input(">"))
		if ( c== 'QUIT') or c=='quit':
			f=False
			break
		else:
			s=c.split(" ")
			if( len(s)>2 ):
				print "Usage: <Command> <file_name>"
				continue
			else:
				file_name=s[1]
				command=s[0].upper()
				if command not in commands:
					print "Command not found"
				path="share/"+str(own_id)+"/"+file_name
				if command == 'PUT' and not os.path.isfile(path):
					print "file not found"
					continue
				else:
					#print os.stat(path)
					process_command(own_id,command,path,file_name)

		# if(c!='y'):
		# 	f=False

if __name__ == '__main__':
    main()