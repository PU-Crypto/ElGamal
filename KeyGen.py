import Keccak as Keccak
myKeccak=Keccak.Keccak()


def KeyGen(string): 					#KeyGen macht aus einem Satz oder Passwort 
	s = list(string)
	einString =''
	for i in range(0,len(s)): 			
		s[i]=ord(s[i])
		dump = format(s[i],'#04x')
		dump = dump.split('x')[1]
		einString += dump

	sha3 = str(myKeccak.Keccak((128,einString),1152,448,224,True)) #dieser String wird mit Keccak (sha3) gehashed
	
	return sha3


