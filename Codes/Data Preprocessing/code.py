def func(fName):
	print fName
	fo = open(fName, "r")
	count = 0
	for line in fo:
		line = line.strip()
		print line
		if(len(line)>0):
			splitLine= line.strip().split(" ")
			if len(splitLine)==1:
				l = [[0 for x in range(int(splitLine[0]))] for x in range(int(splitLine[0]))]
				cc = [[0 for x in range(int(splitLine[0]))] for x in range(int(splitLine[0]))]
				a = [0 for x in range(int(splitLine[0]))]
			if len(splitLine)==2:
				a[count]= float(splitLine[1])
				count = count + 1
			if len(splitLine)==3:
				l[int(splitLine[0])-1][int(splitLine[1])-1]=float(splitLine[2])
				l[int(splitLine[1])-1][int(splitLine[0])-1]=float(splitLine[2])
				cc[int(splitLine[0])-1][int(splitLine[1])-1] = a[int(splitLine[0])-1]*a[int(splitLine[1])-1]*float(splitLine[2])
				cc[int(splitLine[1])-1][int(splitLine[0])-1] = a[int(splitLine[0])-1]*a[int(splitLine[1])-1]*float(splitLine[2])

	#print l

	f = open(fName.split('.')[0]+".csv", "w")
	f2 = open(fName.split('.')[0]+"_cv.csv", "w")


	for col in l:
		for item in col:
			if item == col[-1]:
				f.write("%s" % item)
			else:
				f.write("%s," % item)
	  	f.write("\n")

	for col in cc:
		for item in col:
			if item == col[-1]:
				f2.write("%s" % item)
			else:
				f2.write("%s," % item)
	  	f2.write("\n")



files = ["port1.txt",
"port2.txt",
"port3.txt",
"port4.txt",
"port5.txt"]

for fx in files:
	func(fx)