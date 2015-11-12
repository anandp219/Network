import math
import socket
import struct
import json
import sys
import logging
import threading
import time
import os
import shutil
import random

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )


MCAST_GRP_LIST = ['224.1.1.1','224.1.1.2','224.1.1.3','224.1.1.4','224.1.1.5']
MCAST_GRP = MCAST_GRP_LIST[int((random.random())*2)]
PARENT_MCAST_GRP = '224.1.1.6'
MCAST_PORT = 5007
BUFSIZE = 8192   
TCP_TIMEOUT=2
TCP_QUEUE_LIMIT=5
tcp_ip='127.0.0.1'
tcp_port=6666
pred_candidate=[]
succ_candidate=[]
pred_ip=None
pred_id=None
pred_port=None
succ_ip=None
succ_id=None
file_port=32321
succ_port=None
own_id=None
N = 10
chord_table ={}
parent_chord_table ={}
listenerSocket=None

#todo hanldle the case when we have on;y 2 nodes
#todo handle multple ppl claiming to be my successor
def getHashedId(ip,port):
	address=ip+":"+str(port)
	return hash(address)%1024

def check_chord_table():
	time.sleep(30)
	print "MULTICAST Group", MCAST_GRP
	print "chord table ---------------------"
	for x in chord_table:
		print str(x)+" : "+repr(chord_table[x])
	print " this is the chord_table_iterator ---------------------"
	print "----------------------------------"
	print "Parent chord table ---------------------"
	for x in  parent_chord_table:
		print str(x)+" : "+repr(parent_chord_table[x])
	print " this is the chord_table_iterator ---------------------"
	print "----------------------------------"

def setPred(ip,port):
	global pred_id,pred_port,pred_ip

	print "****New Pred is "+ip+":"+str(port)
	pred_ip,pred_port = ip,int(port)
	pred_id=getHashedId(pred_ip,pred_port)

def setSucc(ip,port):
	global succ_port,succ_ip,succ_id
	print "****New Succ is "+ip+":"+str(port)

	succ_ip,succ_port = ip,int(port)
	succ_id=getHashedId(succ_ip,succ_port)

def main():
	if not os.path.exists('output'):       #if directory is not there create a new one
		os.makedirs('output')

	global tcp_ip, own_id,listenerSocket, chord_table
	tcp_ip = sys.argv[1];
	print "tcp_ip is: "+tcp_ip

	#this is the ip which identifies everyone in the overlay  network
	
	own_id = getHashedId(tcp_ip,tcp_port)
	for chord_table_iterator in range(0,N):
		temp_dict = {}
		temp_dict['tcp_ip'] = ""
		temp_dict['id'] = -1
		temp_dict['tcp_port'] = ""
		chord_table[chord_table_iterator]=temp_dict
		
		temp_dict2 = {}
		temp_dict2['tcp_ip'] = ""
		temp_dict2['id'] = -1
		temp_dict2['tcp_port'] = ""
		parent_chord_table[chord_table_iterator]=temp_dict2
		# dict = chord_table[pow(2,chord_table_iterator)]
		# chord_table[pow(2,chord_table_iterator)] = dict
	
	print "own id:"+str(own_id)
	if not os.path.exists('share/'+str(own_id)):
		os.makedirs('share/'+str(own_id))
	#should call join() here
	setPred(tcp_ip,tcp_port)
	setSucc(tcp_ip,tcp_port)

	listenerSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
	listenerSocket.bind((tcp_ip,tcp_port))

	
	tcpListenThread= threading.Thread(name='tcpListen', target=tcpListen)
	multicastListenThread = threading.Thread(name='multicastListen', target=multicastListen)
	parentmulticastListenThread = threading.Thread(name='parentmulticastListen', target=parentmulticastListen)
	# # w2 = threading.Thread(target=worker)
	# # join()
	# joinThread.start()
	# time.sleep(2)
	# multicastListenThread.start()
	# print "arg 2:"+str(sys.argv[2]) 
	# if int(sys.argv[2])==1:
	# joinThread.start()
	# join()
	# time.sleep(1)
	# multicastListen()
	multicastSend('BOTH')
	parentmulticastSThread = threading.Thread(name='parentmulticastSend', target=parentmulticastSend)

	# multicastSend('BOTH','parent')
	
	tcpListenThread.start()
	multicastListenThread.start()
	parentmulticastListenThread.start()
	parentmulticastSThread.start()
	check_chord_table()
	# else:

def parentmulticastSend():
	time.sleep(20)
	multicastSend('BOTH','parent')

def join():
	# print here
	multicastSend()
	data = tcpListen(TCP_TIMEOUT)
	if(data!=None):
		processTcpData(data)
	data = tcpListen(TCP_TIMEOUT)
	if(data!=None):
		processTcpData(data)
	print "Joined Something!"

def establishConnect(typ,ip,port):
	# typ  represents my succ/pred candidate
	global tcp_ip,tcp_port
	print 'Establishing connection with '+str(ip)+":"+str(port)+" for "+typ
	data={}
	data['tcp_ip']=tcp_ip
	data['tcp_port']=tcp_port
	
	if typ == 'PRED': 
		data['type']='SUCC'#this type says  that i am your succ
		pred_candidate.append((ip,int(port)))
	
	elif typ=='SUCC':
		data['type']='PRED'
		succ_candidate.append((ip,int(port)))

	else:	
		print "[ERROR in establishConnect] : Invalid type "+typ
		return
	
	tcpSend(data,ip,port)
	print 'Sent Establishing data to the broadcaster '+ip+":"+str(port)
	return

	# if typ=='PRED':
	# 	#send a signal to the broadcaster saying I am your successor

	# elif typ=='SUCC':
	# 	pass
	# data['type'] = 
	# json_data= json.dumps(data)

	# sender = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
	# sender.connect((ip,port))
	# sender.send(json_data)
	# sender.close()

	# print 'Sent data '+json.dumps(data)+' to '+ip+":"+str(port)+" for "+typ

	# sender = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
	# sender.bind((tcp_ip,tcp_port))
	# sender.listen(5)
 	
	# connectionSocket, addr =  sender.accept()
	# newdata = ''
	# while True:
	# 	sen = connectionSocket.recv(BUFSIZE)
	# 	if not sen: 
	# 		break
	# 	newdata +=sen
	#     # print '###'
	# # print 'recieved: '+sentence
	# connectionSocket.close()

	# # print "Data Recieved after sending invitation: "+newdata
	# newdata=json.loads(newdata)
	# # print newdata
	# # print typ
	# if newdata['message']=='ACK' and newdata['type'] == data['type'] :
	# 	if typ=='PRED':
	# 		setPred(ip,port)
	# 	else:	
	# 		setSucc(ip,port)
	# 	print "ACK recieved from "+ip+":"+str(port)
	# elif newdata['message']=='NACK':
	# 	print  '[NACK] : '+typ+ " " +ip+":"+str(port)
	# else:
	# 	print "OOPS1!"

def getDistance(first,second):
	return int((first -second+ pow(2,N))%pow(2,N))

def populateFingerTable(index,incomingId,data,distance,finger_table,flag):
	# global chord_table
	if flag == 'parent':
		for key in finger_table:
			if finger_table[key]['id']!=-1:
				if distance > finger_table[key]['distance']:
					return


	for x in range(index,-1,-1):
		if finger_table[x]['id'] !=-1 and distance > finger_table[x]['distance'] :
			break
		else:
			finger_table[x]['id'] = int(incomingId)
			finger_table[x]['tcp_port']=int(data['tcp_port'])
			finger_table[x]['tcp_ip']=data['tcp_ip']
			finger_table[x]['distance']=int(distance)
	# if data['type'] !='PING':
	# 	multicastSend('PING')
def parent_chord_implementor(incomingId,data,finger_table):
	distance = getDistance(incomingId,own_id)
	found = True
	for key in chord_table:
		if chord_table[key]['id'] != -1:
			di=getDistance(chord_table[key]['id'],own_id)
			if di < distance:
				found = False
				break
	if found:
		probableIndex = int(math.floor(math.log(distance,2)))
		if finger_table[probableIndex]['id'] == -1 :
			populateFingerTable(probableIndex,incomingId, data,distance,finger_table,'parent')
		else:
			oldDistance = finger_table[probableIndex]['distance']
			if oldDistance > distance:
				populateFingerTable(probableIndex,incomingId,data,distance,finger_table,'parent')
		
def chord_implementor(data,finger_table,flag):
	print "data is ",data
	if flag == 'parent' and data['MCAST_GRP'] == MCAST_GRP:
		return
	incomingId = getHashedId(data['tcp_ip'],data['tcp_port'])

	if flag == 'parent':
		parent_chord_implementor(incomingId,data,finger_table)
		return
	if incomingId == own_id:
		return 
	distance = getDistance(incomingId,own_id)
	print "distance is bhaiyo ",distance," with id = ",data
	probableIndex = int(math.floor(math.log(distance,2)))
	if finger_table[probableIndex]['id'] == -1 :
		populateFingerTable(probableIndex,incomingId, data,distance,finger_table,flag)
	else:
		oldDistance = finger_table[probableIndex]['distance']
		if oldDistance > distance:
			populateFingerTable(probableIndex,incomingId,data,distance,finger_table,flag)
	if data['type']!='PING':
		if flag=='parent':
			parentMulticastSendThread= threading.Thread(name='parentMulticastSend', target=multicastSend,args=('PING',flag,))
			parentMulticastSendThread.start()
		else:
			multicastSendThread= threading.Thread(name='multicastSend', target=multicastSend,args=('PING',flag,))
			multicastSendThread.start()
		# pass# multicastSend('PING')	


	# for x in range(0,N):

	## ZERO KE LIYE BANAN HAI
	# max = -1
	# max_val = {}
	# for key,value in chord_table.iteritems():
	# 	if key > max and key <= incomingId:
	# 		max = key
	# 		max_val = value
	# if max_val['id'] == -1 or incomingId < max_val['id']:
	# 	max_val['id'] = incomingId
	# 	max_val['tcp_ip'] = data['tcp_ip']
	# 	max_val['tcp_port'] = data['tcp_port']






def processRecievedMulticast(data):
	chord_implementor(data,chord_table,'own')
	#data['type'] represents the type required by the other node
	global pred_id,own_id,succ_id
	address=data['tcp_ip']+":"+str(data['tcp_port'])
	incomingId = hash(address)%1024
	print "incoming id:"+str(incomingId)
	if incomingId==own_id:
		print "Recieved Own Multicast"
	elif  pred_id < incomingId and incomingId < own_id:
		#fit for my  pred, I am candidate for his succ
		if data['type']=='BOTH' or data['type']=='SUCC':
			establishConnect('PRED',data['tcp_ip'],data['tcp_port'])

	elif own_id < incomingId and incomingId < succ_id:
		#fit for my succ
		if data['type']=='BOTH' or data['type']=='PRED':
			establishConnect('SUCC',data['tcp_ip'],data['tcp_port'])
	elif pred_id==succ_id and pred_id!=incomingId:
		if data['type']=='PRED':
			establishConnect('SUCC',data['tcp_ip'],data['tcp_port'])
		elif data['type']=='BOTH':
			establishConnect('SUCC',data['tcp_ip'],data['tcp_port'])
			# time.sleep(1)
			establishConnect('PRED',data['tcp_ip'],data['tcp_port'])
		elif data['type']=='SUCC':
			establishConnect('PRED',data['tcp_ip'],data['tcp_port'])
	elif data['type'] == 'BOTH':
		print data
		sendData={}
		sendData['type']='SEND_BOTH'
		sendData['tcp_ip']=tcp_ip
		sendData['tcp_port']=tcp_port
		sendData['succ_ip']=succ_ip
		sendData['pred_ip']=pred_ip

 		tcpSendThread= threading.Thread(name='tcpSend', target=tcpSend,args=(sendData,data['tcp_ip'],data['tcp_port'],))
		tcpSendThread.start()
		
		# tcpSend(sendData,data['tcp_ip'],data['tcp_port'])
	else:	
		print "OOPS!"
	return
def processRecievedParentMulticast(data):
	# pass# global parent_chord_table
	chord_implementor(data,parent_chord_table,'parent')	

def parentmulticastListen():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind((PARENT_MCAST_GRP, MCAST_PORT)) 
	mreq = struct.pack("4sl", socket.inet_aton(PARENT_MCAST_GRP), socket.INADDR_ANY)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
	while True:
	  	data, sender = sock.recvfrom(BUFSIZE)
	  	while data[-1:] == '\0':
	  		data = data[:-1]
		data=  json.loads(data)
		print (str(sender) + '  ' + repr(data)) 
  		processMulticastDataThread= threading.Thread(name='processRecievedParentMulticast', target=processRecievedParentMulticast,args=(data,))
		processMulticastDataThread.start()



def multicastListen():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	
	sock.bind((MCAST_GRP, MCAST_PORT))  # use MCAST_GRP instead of '' to listen only
	                             # to MCAST_GRP, not all groups on MCAST_PORT
	mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

	sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
	print "I am listening"
	while True:
	  	data, sender = sock.recvfrom(BUFSIZE)
	  	while data[-1:] == '\0':
	  		data = data[:-1]
		data=  json.loads(data)
  		#data contains a lot of things
		print (str(sender) + '  ' + repr(data)) 
  		processMulticastDataThread= threading.Thread(name='processRecievedMulticast', target=processRecievedMulticast,args=(data,))
		processMulticastDataThread.start()
  		# processRecievedMulticast(data)

def multicastSend(messageType,flag='own'):
	global tcp_ip,tcp_port
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
	h={}
	print "multicastSend has beend done"
	h["tcp_ip"]=tcp_ip
	h["tcp_port"]=tcp_port
	h['type']=messageType
	h['MCAST_GRP']= MCAST_GRP

	# h["text"]="robot"
	json_data = json.dumps(h)
	print "json is: "+json_data
	if flag =='parent':
		sock.sendto(json_data,( PARENT_MCAST_GRP, MCAST_PORT))
	else:
		sock.sendto(json_data,( MCAST_GRP, MCAST_PORT))

	sock.close()

def sendAliveConfirmation(data):
	pass

def processTcpData(data):
	global succ_candidate,pred_candidate
	print "***"
	print   repr(data)
	print "***"
	print "yahan pe desh ea"
	if 'type' in data:
		messageType=data['type']
		if messageType == 'PRED':
			address=data['tcp_ip']+":"+str(data['tcp_port'])
			incomingId = hash(address)%1024
			print "sds incoming id:"+str(incomingId),succ_id
			if (incomingId > pred_id and incomingId < own_id ) or pred_id == own_id or (own_id < pred_id and incomingId < own_id) or (incomingId > pred_id and own_id < pred_id):
				setPred(data['tcp_ip'],data['tcp_port'])
				
				sendData={}
				sendData['type']='ACK_'+messageType
				# sendData['type']='ACK_PRED'
				# sendData['message']=messageType
				sendData['tcp_ip']=tcp_ip
				sendData['tcp_port']=tcp_port
				
				tcpSend(sendData,data['tcp_ip'],data['tcp_port'])
				print 'sent ACK for the PRED req from '+data['tcp_ip']+":"+str(data['tcp_port'])

		elif messageType=='SUCC':

			address=data['tcp_ip']+":"+str(data['tcp_port'])
			incomingId = hash(address)%1024
			print "incoming id: sdsdsd "+str(incomingId),succ_id
			if (incomingId < succ_id and incomingId > own_id) or succ_id==own_id or (incomingId > own_id and succ_id < incomingId) or (incomingId < succ_id and succ_id < own_id ):
				setSucc(data['tcp_ip'],data['tcp_port']) 

				sendData={}
				sendData['type']='ACK_'+messageType
				#sendData['type']=messageType
				sendData['tcp_ip']=tcp_ip
				sendData['tcp_port']=tcp_port

				tcpSend(sendData,data['tcp_ip'],data['tcp_port'])
				print 'sent ACK for the SUCC req from '+data['tcp_ip']+":"+str(data['tcp_port'])
			else:
				print "This cannot become my successor"

		elif messageType=='IS_ALIVE':
			sendAliveConfirmation(data)
		
		elif messageType=='ACK_PRED':
			print "hggh hgh "
			if (data['tcp_ip'],int(data['tcp_port'])) in succ_candidate:
				succ_candidate[:]  = []
				address=data['tcp_ip']+":"+str(data['tcp_port'])
				incomingId = hash(address)%1024
				if (incomingId < succ_id and incomingId > own_id) or succ_id==own_id or (incomingId > own_id and succ_id < incomingId) or (incomingId < succ_id and succ_id < own_id):
					setSucc(data['tcp_ip'],data['tcp_port'])
					print "Succ sdhs ACK recieved from "+data['tcp_ip']+":"+str(data['tcp_port'])	

		elif messageType=='ACK_SUCC':
			print "jhhh  hjh "
			if (data['tcp_ip'],int(data['tcp_port'])) in pred_candidate:
				pred_candidate[:] = []
				address=data['tcp_ip']+":"+str(data['tcp_port'])
				incomingId = hash(address)%1024
				if (incomingId > pred_id and incomingId < own_id ) or pred_id == own_id or (own_id < pred_id and incomingId < own_id) or (incomingId > pred_id and own_id < pred_id):
					setPred(data['tcp_ip'],data['tcp_port'])
					print "Pred ACK djs recieved from "+data['tcp_ip']+":"+str(data['tcp_port'])	

		elif messageType=='GET_BOTH':
				sendData={}
				sendData['type']='SEND_BOTH'
				sendData['tcp_ip']=tcp_ip
				sendData['tcp_port']=tcp_port
				sendData['succ_ip']=succ_ip
				sendData['pred_ip']=pred_ip
				tcpSend(sendData,data['tcp_ip'],data['tcp_port'])


		elif messageType=='UPLOAD_FILE':
				file_name=data['file']
				path="share/"+str(own_id)+"/"+file_name
				print path
				print data
				sendData='NACK_FILE'
				if os.path.isfile(path):
					print "file is there "
					sendData='NACK_FILE'
					tcpSend(sendData,data['tcp_ip'],data['tcp_port'])
				else:
					sendData='ACK_FILE'
					port_me=tcpFileSend(sendData,data['tcp_ip'],data['tcp_port'])
					print port_me
					f = open('share/'+str(own_id)+"/"+data['file'],'wb')
					s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
					#s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
					s.bind((tcp_ip, (port_me+1)))
					print "finally bind"
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
		elif messageType == 'PUT_CHORD':
			file_id = data['file_id']
			dest_id = own_id
			dest_key = -1
			if file_id >= own_id:
				for key in chord_table:
					if chord_table[key]['id'] != - 1 and chord_table[key]['id'] <= file_id:
						dest_id = chord_table[key]['id']
						dest_key = key			
					else:
						break
			else:
				dest_id = -1
				dest_key = -1
				for key in chord_table:
					if chord_table[key]['id'] != - 1 and chord_table[key]['id'] < own_id and \
					chord_table[key]['id'] <= file_id:
						if chord_table[key]['id'] > dest_id :
							dest_id = chord_table[key]['id']
							dest_key = key
				if dest_id == -1:
					max = -1
					for key in chord_table:
						if chord_table[key]['id'] > max  and chord_table[key]['id'] > own_id:
							dest_id = chord_table[key]['id']
							dest_key = key
				if dest_id == -1:
					dest_id = own_id
			if file_id != own_id and dest_id == -1:
				temp_id = -1
				temp_key = -1
				if file_id >= own_id:
					for key in chord_table:
						if parent_chord_table[key]['id'] != - 1 and \
						parent_chord_table[key]['id'] <= file_id:
							temp_id = parent_chord_table[key]['id']
							temp_key = key			
						else:
							break
				else:
					temp_id = -1
					temp_key = -1
					for key in parent_chord_table:
						if parent_chord_table[key]['id'] != - 1 and parent_chord_table[key]['id'] < own_id and \
						parent_chord_table[key]['id'] <= file_id:
							if parent_chord_table[key]['id'] > temp_id :
								temp_id = parent_chord_table[key]['id']
								temp_key = key
					if temp_id == -1:
						max = -1
						for key in parent_chord_table:
							if parent_chord_table[key]['id'] > max  and \
							parent_chord_table[key]['id'] > own_id:
								temp_id = parent_chord_table[key]['id']
								temp_key = key
					if temp_id == -1:
						temp_id = own_id
				dest_id = temp_id
				dest_key = temp_key


			print dest_id,dest_key,"----------++++++++++++++++ss"
			if dest_id == own_id :
				print "File will be downloaded here ",dest_id
				file_name=data['file_name']
				path="share/"+str(own_id)+"/"+file_name
				print path
				print data
				sendData='NACK_FILE'
				if os.path.isfile(path):
					print "file is there "
					sendData='NACK_FILE'
					tcpSend(sendData,data['file_src_ip'],data['file_src_port'])
				else:
					sendData='ACK_FILE'
					port_me=tcpFileSend(sendData,data['file_src_ip'],data['file_src_port'])
					print port_me
					f = open('share/'+str(own_id)+"/"+data['file_name'],'wb')
					s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
					#s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
					s.bind((tcp_ip, (port_me+1)))
					print "finally bind"
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
					s.close()
		elif messageType == 'GET_CHORD':
			file_id = data['file_id']
			dest_id = own_id
			dest_key = -1
			if file_id >= own_id:
				for key in chord_table:
					if chord_table[key]['id'] != - 1 and chord_table[key]['id'] <= file_id:
						dest_id = chord_table[key]['id']
						dest_key = key			
					else:
						break
			else:
				dest_id = -1
				dest_key = -1
				for key in chord_table:
					if chord_table[key]['id'] != - 1 and chord_table[key]['id'] < own_id and \
					chord_table[key]['id'] <= file_id:
						if chord_table[key]['id'] > dest_id :
							dest_id = chord_table[key]['id']
							dest_key = key
				if dest_id == -1:
					max = -1
					for key in chord_table:
						if chord_table[key]['id'] > max  and chord_table[key]['id'] > own_id:
							dest_id = chord_table[key]['id']
							dest_key = key
				if dest_id == -1:
					dest_id = own_id


			print dest_id,dest_key,"----------++++++++++++++++ss"
			if dest_id == own_id :
				print "File will be uploaded from here ",dest_id
				file_name=data['file_name']
				path="share/"+str(own_id)+"/"+file_name
				print path
				print data
				sendData='NACK_FILE'
				if not os.path.isfile(path):
					print "file is not there "
					sendData='NACK_FILE'
					tcpSend(sendData,data['file_src_ip'],data['file_src_port'])
				else:
					sendData='ACK_FILE'
					port_me=tcpFileSend(sendData,data['file_src_ip'],data['file_src_port'])
					print port_me
					
					s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
					#s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
					s.bind((tcp_ip, (port_me+1)))
					print "finally bind"
					flag=True
					while flag:
						try:
							s.connect((data['file_src_ip'],data['file_src_port']))
							flag=False
						except:
							pass
					f = open('share/'+str(own_id)+"/"+data['file_name'],'rb')
					l = f.read(1024)
					while (l):
						s.send(l)
						l = f.read(1024)
					f.close()
					print "Done Sending"
					s.shutdown(socket.SHUT_WR)
					s.close()
					print "file has be sent"
	
			else:
				print "file download has been forwarded to ",dest_id
				sender = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
				flag = True
				while flag:
					try:
						sender.connect((chord_table[dest_key]['tcp_ip'],chord_table[dest_key]['tcp_port']))
						sender.send(json.dumps(data))
						sender.close()
						flag=False
					except:
						print "Unable to send "+ repr(data) +" to "+str(dest_id)+":"
			


		elif messageType=='DOWNLOAD_FILE':
				file_name=data['file']
				path="share/"+str(own_id)+"/"+file_name
				print path
				print data
				sendData='NACK_FILE'
				if not os.path.isfile(path):
					print "file is not there "
					sendData='NACK_FILE'
					tcpSend(sendData,data['tcp_ip'],data['tcp_port'])
				else:
					sendData='ACK_FILE'
					port_me=tcpFileSend(sendData,data['tcp_ip'],data['tcp_port'])
					print port_me
					
					s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
					#s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
					s.bind((tcp_ip, (port_me+1)))
					print "finally bind"
					flag=True
					while flag:
						try:
							s.connect((data['tcp_ip'],data['tcp_port']))
							flag=False
						except:
							pass
					f = open('share/'+str(own_id)+"/"+data['file'],'rb')
					l = f.read(1024)
					while (l):
						s.send(l)
						l = f.read(1024)
					f.close()
					print "Done Sending"
					s.shutdown(socket.SHUT_WR)
					s.close()
					print "file has be sent"

					# s.listen(5)
					# c, addr = s.accept()
					# print 'Got connection from', addr
					# print "Receiving..."
					# l = c.recv(1024)
					# while (l):
					# 	print "Receiving..."
					# 	f.write(l)
					# 	l = c.recv(1024)
					# f.close()
					# print "Done Receiving"
					# c.close()        





		elif messageType == 'SEND_BOTH':
			print data
			print "Listening here"
			pred=hash(data['pred_ip']+":"+str(data['tcp_port']))%1024
			incom=hash(data['tcp_ip']+":"+str(data['tcp_port']))%1024
			suc=hash(data['succ_ip']+":"+str(data['tcp_port']))%1024
			own=hash(tcp_ip+":"+str(data['tcp_port']))%1024
			if ( own < incom and own > pred ) or (own > pred and pred > incom) or pred == incom or ( own < incom and incom < pred ):
				establishConnect('SUCC',data['tcp_ip'],data['tcp_port'])
			if ( suc < incom and own < suc ) or (own < suc and suc > incom) or suc == incom or ( incom > suc and own > incom ):
				establishConnect('PRED',data['tcp_ip'],data['tcp_port'])



		else:
			print"[ERROR in processTcpData']: Unsupported messageType"

	else:
		print "'type' key is missing'"

def tcpListen(timeout=None):
	#ever running function
	global tcp_ip,tcp_port,listenerSocket
	listenerSocket.listen(TCP_QUEUE_LIMIT)

	# listener = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
	# listener.bind((tcp_ip,tcp_port))
	# listener.listen(TCP_QUEUE_LIMIT)

	if(timeout==None):
		#this is a general case
		while True:
			try:
				connectionSocket, addr =  listenerSocket.accept()

				data = ''
				while True:
					sen = connectionSocket.recv(BUFSIZE)
					if not sen: 
						break
					data +=sen
				
				data = json.loads(data)
				print data 
				print "THis is the tcp data i have been jear"
				processTcpDataThread= threading.Thread(name='processTcpData', target=processTcpData,args=(data,))
				processTcpDataThread.start()
				# processTcpData(data)
				# connectionSocket.close()	
				print"yop"
			except:

				print "exception here1"
				e = sys.exc_info()[0]
				print repr(e)
	else:
		listenerSocket.settimeout(timeout)
		try:
			connectionSocket, addr =  listenerSocket.accept()
			data = ''
			while True:
				sen = connectionSocket.recv(BUFSIZE)
				if not sen: 
					break
				data +=sen
			
			# connectionSocket.close()	
			data = json.loads(data)
			listenerSocket.close()
			return data
		except:
			print "exception here2"
			e = sys.exc_info()[0]
			print repr(e)
			listenerSocket.close()
			return None

def tcpSend(data,ip,port):
	#data should only   contain
	sender = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
	flag=True
	while flag:
		try:
			sender.connect((ip,int(port)))
			sender.send(json.dumps(data))
			sender.close()
			flag=False
		except:
			print "Unable to send "+ repr(data) +" to "+ip+":"+str(port)


def tcpFileSend(data,ip,port):
	#data should only   contain
	sender = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
	sender.bind((tcp_ip,0))
	port_me=""
	print "sdsd yahan se file " + str(port_me)
	flag=True
	while flag:
		try:
			sender.connect((ip,int(port)))
			sender.send(json.dumps(data))
			port_me=sender.getsockname()[1]
			sender.shutdown(socket.SHUT_WR)
			sender.close()
			flag=False
		except:
			print "Unable to send "+ repr(data) +" to "+ip+":"+str(port)
	
	
	#
	sender.close()
	print "sender has been closed"
	print "Sender has already been closed"
	return port_me


if __name__ == '__main__':
    main()
