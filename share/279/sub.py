import time
start_time = time.time()


def subset(y,lis):
	if len(y)==1:
		l=[]
		l.append(y[0])
		lis.append(l)
		return
	subset(y[1:],lis)
	for i in range (0,len(lis)):
		x=lis[i]
		l=[]
		if(type(x)==list):
			for j in range(0,len(x)):
				l.append(x[j])
		else:
			l.append(x)
		l.append(y[0])
		lis.append(l)
	l=[]
	l.append(y[0])
	lis.append(l)

y=raw_input().split(" ")
for i in range(0,len(y)):
	y[i]=int(y[i])
lis=[]
subset(y,lis)
lis.append("empty")
lis.sort()
print len(lis)

print("--- %s seconds ---" % (time.time() - start_time))



