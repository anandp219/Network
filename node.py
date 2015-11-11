#!/usr/bin/python
from socket import *
import sys,os
import commands
HOST_IP=commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]
PORT=5001
path = os.path.dirname(os.path.realpath(__file__))+"/share"
address=HOST_IP+":"+str(PORT)
node_id=hash(address)%1024
dirs = os.listdir( path )
for file in dirs:
	print hash(file)%1024
print "node_id=" + str(node_id)
try:	
	clientSocket = socket(AF_INET, SOCK_STREAM)
	clientSocket.bind(('',PORT))
	print "Client has started and waiting for connections on the port number " + str(PORT)
except:
	print "Error in creating the socket"
	sys.exit()
while True:
	i=1
