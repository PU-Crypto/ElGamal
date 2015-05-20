def Padding(string,laenge): #Erweitere auf laenge Stellen mit vorangestellten 0
	while(len(string)%laenge!=0):
		string='0' + string 
	return string

def SplitBlocks(einString,Splitter):
	block=list()
	for i in range(0,len(einString),Splitter): #Teile in Ner Bloecke
		dump=''
		for j in range(i,i+Splitter):
			dump+=einString[j]
		block.append(dump)
	return block


def UTFConvert(plain): #Wandle Test in utf-8 um und erstelle CBC kompatible Bloecke, die 8 Stellen lang sind
    s=list(plain)
    for i in range(0,len(s)):
        s[i]=ord(s[i])

    einString =''
    for i in range(0,len(s)): #erstelle einen string mit dualzahlen
        dump = str(s[i])
        dump = Padding(dump,4)
        einString += dump


   

    
    return einString
    




def UTFdeConvert(einString): #Array mit jeweils acht stellen die 0 oder 1 sind
    

    einString = str(int(einString)) #Entferne fuehrende 0
    einString = Padding(einString,4) #Erweitere wieder auf 11er Bloecke
    
    block = SplitBlocks(einString,4) #Trenne in 11er Bloecke


    output = ''
    for wert in block:
        wert = int(wert,10) #Erstelle aus der Dualzahl eine Dezimalzahl
        wert = chr(wert) #Erhalte den utf-8 Gegenwert zu dieser Zahl
        output += wert #Haenge die einzelnen Zeichen an den Output

    return output
