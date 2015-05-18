import math
from decimal import Decimal
import decimal
import random
import KeyGen as KeyGen
import UTF8_Convert as UTF8
import json
import sys
decimal.getcontext().prec = 1000 # es wird alles benoetigte improtiert und die Praezision der Decimals festgestellt, welche nicht zu gering sein sollte.
#Curve25519: z^2(-x^2+y^2) = z^4 - (121665/121666)*y^2*x^2
#	Prinmzahl: 2^255- 19
a = Decimal(-1)
d = Decimal(-121665/121666)
c = Decimal(1)
prim = Decimal(2**255 - 19)
def Mod(num):
	if num / prim > 1 or num / prim < -1 :
		mult = Decimal((str(Decimal(num/prim)).split('.')[0]))
		num = Decimal(num - mult * prim)
		
	else:
		mod = num	
	mod = Decimal(num)
	return mod
def YCalc(x): #Ermittlung des Punktes anhand des x-wertes und einsetzen in die Gleichung
	y = Mod(Decimal((a*x**Decimal(2)-1)/(d*x**Decimal(2)-1)))
	#y = Mod(Decimal((x**Decimal(2)/(((-d)/z**Decimal(2))*x**Decimal(2)-Decimal(1)))))
	return y
def run(num):
	if num < 0.5 and num >-0.5:
		num = Decimal(0)
	else:
		if num % 1 > 0.5:
			num = Decimal(str(num + 1).split('.')[0])
		else:
			num = Decimal(str(num).split('.')[0])
	return num



def additionMG(p,q):  #Die Addition von zwei Punkten auf der Kurve
	r = []
	if p[0] == 0 and p[1] == 1: #Spezialfall: ein punkt ist (0,0), dann ist die addition ueberfluessig
		return q
	if q[0] ==0 and q[1] == 1:
		return p
	if p!=q and p[0]!=-q[0]:
	
		X1 = Decimal(p[0])
		Y1 = Decimal(p[1])
		X2 = Decimal(q[0])
		Y2 = Decimal(q[1])	#auslesen der Koordinaten der Punkte
		Z1 = Decimal(1)
		Z2 = Decimal(1)
		C = Decimal(X1*X2)
		D = Decimal(Y1*Y2)
		E = Decimal(d*C*D)
		X3 = Decimal((1-E)*((X1+Y1)*(X2+Y2)-C-D))
		Z3 = Decimal(1-E**2)
		Xr = Mod(Decimal(X3/Z3))
		#Xr = Mod(Decimal((X1*Y2+X2*Y1)/(1+d*X1*X2*Y1*Y2)))
		#Yr = Mod(Decimal((1+E)*(D-a*C)))#Mod(Decimal((Y1*Y2-a*X1*X2)/(1-d*X1*X2*Y1*Y2)))
		Yr = YCalc(Xr)#Mod(Decimal(Yr/Z3))	
		#Die Formeln erschliesst sich mit einigem aufwand aus der geometrischen Definition
		#der Addition. Dazu kann ich diese Seite empfehlen: http://en.wikipedia.org/wiki/Montgomery_curve. Etwas ungenauer findet sich das auch in 
		#theoretischen Ausarbeitung
		r.append(Xr)
		r.append(Yr)
		#r.append(Zr)
		return r
	if p[0] == -q[0] and p[1] == q[1]: #Spezialfall: Die punkte sind identisch, wenn man einen an der X-Achse spiegelt: Ergebnis (0,0)
		Xr = Decimal(0)
		Yr = Decimal(1)
		r.append(Xr)
		r.append(Yr)
		return r
	if p == q:  #Die Difinition von der Verdopplung eines Punktes ist ein bisschen anders als die normale Addition, deswegen dieser Spezialfall.
		x = Decimal(p[0])
		y = Decimal(p[1])
		B = Decimal((X1+Y1)**2)
		C = Decimal(X1**2)
		D = Decimal(Y1**2)
		E = Decimal(a*C)
		F = Decimal(E+D)
		X3 = Mod(Decimal((B-C-D)*(F-2)))
		Z3 = Mod(Decimal(F**2-2*F))
		Xr = Mod(Decimal(X3/Z3))
		Yr = YCalc(Xr)
		r.append(Xr)
		r.append(Yr)
		return r
		#Im eigentlichen gibt es den Operator der multiplikation auf Elliptischen Kurven nicht, deswegen wird hier
	#rekrusiv das "doubling and add" - verfahren genutzt.
def multiplikation(p,n): #p ist der punkt n ist der Skalarfaktor
	if n % 2 == 0 and n != 0: #Wenn der Faktor grade ist kann der erste Schritt gemacht werden, indem der Punkte verdoppelt wird.
		r = []
		X1 = Decimal(p[0])
		Y1 = Decimal(p[1])
		B = Decimal((X1+Y1)**2)
		C = Decimal(X1**2)
		D = Decimal(Y1**2)
		E = Decimal(a*C)
		F = Decimal(E+D)
		X3 = Mod(Decimal((B-C-D)*(F-2)))
		Z3 = Mod(Decimal(F**2-2*F))
		Xr = Mod(Decimal(X3/Z3))
		Yr = YCalc(Xr)
		r.append(Xr)
		r.append(Yr)
		r = multiplikation(r,n/2)
		#Hier passiert die Rekrusion, also der Selbstaufruf mit neuen Parametern. Da eine Verdopplung schon stattfand
		#wird das Ergebnis, der neue Punkt, mit der Haelfte des urspruenglichen Faktors in die Funktion gegeben. Waere der Faktor n = 8 wuerde dieser
		#Schritt 3 mal Passieren, da das neue n beim 4. mal 1 ist.
		return r
	if n == 0: #Spezialfall: der Faktor ist 0. 
		r = []
		r.append(0)
		r.append(1)
		return r
	if n % 2 == 1 and n != 1:
		zwischenwert = multiplikation(p,n-1)
		#		Rekrusion: Beispiel: n = 5. Beim ersten durchlauf kommt er in diese Abfrage und schickt den Punkt mit n = 4 in die Funktion.
#		Darauf wird 2 mal die Verdopplung durchgefuehrt und das Ergebnis mit p addiert: p * 5 = p*2*2 + p.
		r = additionMG(p,zwischenwert)
		return r
	if n == 1: #Hier kommt die Funktion schliesslich hin bei n = 2^x. Wenn der Faktor schliesslich 1 ist, ist das Erbegnis p.
		return p
def SplitBlocks(einString,Splitter):
	
	block=list()
	for i in range(0,len(einString),Splitter): #Teile in Ner Bloecke
		dump=''
		for j in range(i,i+Splitter):
			dump+=einString[j]
		block.append(dump)
	return block
def Padding(string,laenge): #Erweitere auf laenge Stellen mit vorangestellten 0
	
	while(len(string)%laenge!=0):
		string='0' + string 
	return string

def ElGamal(text, pubkey):
	
	m = UTF8.UTFConvert(text) #Wandle Text in Zahl um
	Splitter = len(str(prim)) - 1
	m = Padding(m,Splitter)
	mArray = SplitBlocks(m,Splitter)
	CipherArray = []
	for Wert in mArray:
		m = int(Wert) #Wandle Text in Zahl um
		k = random.randint(0,prim) #Waehle zufaelligen Kofaktot
		P = [Decimal(9),Decimal(YCalc(9))] #Erzeugerpunkt
		c = multiplikation(pubkey,k)[0] #multipliziert kofaktor mit dem Oeffentlichen Schluessel, welcher ein Punkt ist. Die X-Koordniate reicht aus.
		C = multiplikation(P,k) #Erster Teil des Ciphers. Das Produkt des Erzeugerpunktes und des Kofaktors 
		d = Mod(Decimal(c * m)) #Zweiter Teil des Ciphers. Produkt der Nachricht und der x-Koordinate des PubKey-Produktes.
		output = str(C[0]) + 'v' + str(C[1])  + 'u' + str(d) #Erstelle den Output
		CipherArray.append(output)
	return CipherArray

def ElGamalDecrypt(cipher, key):
	EndString = ''
	for Wert in cipher:
		cipherPart = Wert
		C = [0,0]
		C[0] = Decimal(cipherPart.split('v')[0])
		zwischenwert = cipherPart.split('v')[1]
		C[1] = Decimal(zwischenwert.split('u')[0])
		d =  Decimal(zwischenwert.split('u')[1]) #Cipher wird gesplittet
		c1 = multiplikation(C,key)[0] #Es wird C mit dem Wert Multipliziert und die X-Koordinate ausgelesen.
		Num = Mod(Decimal(d/c1))
		"""m wird ermittelt. Da das ergebnis aufgrund der Langen Decimalzahlen bei einer Praezision von 1000 immer sehr knapp unter dem eigentlichen 
		m (differenz der werte ueblicherweise bei e-900) ist und die Rundenfunktion des flaots zu ungenau ist bei prec = 1000 wird 1 dazu addiert und dann
		der rest hinter dem Komma, also .9999999... angeschnitten."""
		if Num % 1 > 0.5:
			NewNum = str(Num + 1).split('.')[0]
		if Num % 1 < 0.5:
			NewNum = str(Num).split('.')[0]
		EndString += NewNum
	Output = UTF8.UTFdeConvert(int(EndString)) #die Zahl wird wieder in einen Text gewandelt.
	return Output

def KeyGenerator(password):  #die Schluessel werden generiert
	P = [Decimal(9),Decimal(YCalc(9))]
	Privat = int(KeyGen.KeyGen(password),16)
	Public = multiplikation(P,Privat)
	return Privat, Public

#w = KeyGenerator('DasistderKeyderMichmalkann')
#print(1)
#c = ElGamal('Das ist ein ewig langer text, mit Kommata punkten und vielem anderen, nur umlaute kommen nicht vor, dennoch ist dieser Text sehr lang und jetzt kann ich jetzt auf hoeren',w[1])
#print('ultEnd -e')
#print(c)
#print('start -d ult')
#t = ElGamalDecrypt(c,w[0])
#print(t)
#print(t - 34545734545683456567468345645756896778456458567346)

#q = [Decimal(37525684500),Decimal(YCalc(37525684500))]
##print(q)
##print()
#p = [Decimal(4565),Decimal(YCalc(4565))]
##print(p)
##print()
#R = additionMG(p,q)
#print(R)
##R = multiplikation(p,2)
##print(R)
##print()
##print(YCalc(R[0]))
##print()
##print(R[1] - YCalc(R[0]))
##R = [Decimal(0),Decimal(1)]
#p = [Decimal(-4565),Decimal(YCalc(4565))]
#q1 = (additionMG(R,p))
#print()
#print(q1[0])



