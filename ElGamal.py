#-*-coding: utf-8-*-
import sys
import math
from decimal import Decimal
import decimal
import random
import KeyGen as KeyGen
import UTF8_Convert as UTF8
import json
import os
from os import path
decimal.getcontext().prec = 1000 # es wird alles benoetigte improtiert und die Praezision der Decimals festgestellt, welche nicht zu gering sein sollte.
#Curve25519: y^2=x^3+486662x^2+x
#	Prinmzahl: 2^255- 19
a = Decimal(486662) #Die Montomerykurve wird mit Primzahl definiert
b = 1
prim = Decimal(2**255 - 19)
def Mod(num):
	if num / prim > 1 or num / prim < -1 :
		mult = Decimal((str(Decimal(num/prim)).split('.')[0]))
		num = Decimal(num - mult * prim)
		
	
	mod = Decimal(num)
	return mod
def YCalc(x): #Ermittlung des Punktes anhand des x-wertes und einsetzen in die Gleichung
	y = Mod(Decimal((x**3+ a * x**2 + x)**Decimal(0.5)))
	return y
def additionMG(p,q): #Die Addition von zwei Punkten auf der Kurve
	r = []
	if p[0] == 0 and p[1] == 0: #Spezialfall: ein punkt ist (0,0), dann ist die addition ueberfluessig
		return q
	if q[0] ==0 and q[1] == 0:
		return p
	if p!=q and p[1]!=-q[1]:
		x1 = Decimal(p[0])
		y1 = Decimal(p[1])
		x2 = Decimal(q[0])
		y2 = Decimal(q[1]) #auslesen der Koordinaten der Punkte
		Xr = Mod(Decimal((x2*y1-x1*y2)**2/(x1*x2*(x2-x1)**2)))
		Yr = Mod(Decimal((((2*x1 + x2 + a)*(y2 - y1)) / (x2 - x1)) - ((y2 - y1)**3 / (x2 - x1)**3) - y1))
		#Die Formeln erschliesst sich mit einigem aufwand aus der geometrischen Definition
		#der Addition. Dazu kann ich diese Seite empfehlen: http://en.wikipedia.org/wiki/Montgomery_curve. Etwas ungenauer findet sich das auch in 
		#theoretischen Ausarbeitung
		r.append(Xr)
		r.append(Yr)
		return r
	if p[0] == q[0] and p[1] == -q[1]: #Spezialfall: Die punkte sind identisch, wenn man einen an der X-Achse spiegelt: Ergebnis (0,0)
		Xr = Decimal(0)
		Yr = Decimal(0)
		r.append(Xr)
		r.append(Yr)
		return r
	if p == q: #Die Difinition von der Verdopplung eines Punktes ist ein bisschen anders als die normale Addition, deswegen dieser Spezialfall.
		x = Decimal(p[0])
		y = Decimal(p[1])
		l = Decimal((3*x**2 + 2 * a * x + 1)/(2*y))
		Xr = Mod(Decimal(b * l**2 - a - 2*x))
		Yr = Mod(Decimal((x*3 + a )*l - l**3 - y))		
		r.append(Xr)
		r.append(Yr)
		return r
	#Im eigentlichen gibt es den Operator der multiplikation auf Elliptischen Kurven nicht, deswegen wird hier
	#rekrusiv das "doubling and add" - verfahren genutzt.
def multiplikation(p,n): #p ist der punkt n ist der Skalarfaktor
	if n % 2 == 0 and n != 0: #Wenn der Faktor grade ist kann der erste Schritt gemacht werden, indem der Punkte verdoppelt wird.
		r = []
		x = Decimal(p[0])
		y = Decimal(p[1])
		l = Decimal((3*x**2 + 2 * a * x + 1)/(2 * y * b))
		Xr = Mod(Decimal(b * l**2 - a - 2*x))
		Yr = Mod(Decimal((x*3 + a )*l - b * l**3 - y))	
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
		r.append(0)
		return r
	if n % 2 == 1 and n != 1:
		zwischenwert = multiplikation(p,n-1)
#		Rekrusion: Beispiel: n = 5. Beim ersten durchlauf kommt er in diese Abfrage und schickt den Punkt mit n = 4 in die Funktion.
#		Darauf wird 2 mal die Verdopplung durchgefuehrt und das Ergebnis mit p addiert: p * 5 = p*2*2 + p.
		r = additionMG(p,zwischenwert)
		return r
	if n == 1: #Hier kommt sie Funktion schliesslich hin bei n = 2^x. Wenn der Faktor schliesslich 1 ist, ist das Erbegnis p.
		return p

def Padding(string,laenge): #Erweitere auf laenge Stellen mit vorangestellten 0
	while(len(string)%laenge!=0):
		string='0' + string 
	return string

def SplitBlocks(inString,Splitter):
	block = list()
	if len(inString) % Splitter != 0:
		NewLen = Splitter*int(str(len(inString)/Splitter).split('.')[0]) 
		einString = inString[0:NewLen] 
		dump2 = inString[NewLen:len(inString)+1]
	else:
		einString = inString

	for i in range(0,len(einString),Splitter): #Teile in Ner Bloecke
		dump=''
		for j in range(i,i+Splitter):
			dump+=einString[j]
		block.append(dump)
	if len(inString) % Splitter != 0:
		block.append(dump2)
	return block
def Stringsplitter(String):
	array = []
	String = String.split('[')[1]
	String = String.split(']')[0]
	count = 0
	for char in String:
		if char == ',':
			count+=1
	for i in range(0,count+1):
		wert = String.split(',')[i]
		wert = wert.split("'")[1]
		wert = wert.split("'")[0]
		array.append(wert)
	return array

def ElGamalCalc(text,PubKey):
	m = int(UTF8.UTFConvert(text)) #Wandle Text in Zahl um
	k = random.randint(0,578960446186580977117854925043439539266349923) #Waehle zufaelligen Kofaktot
	P = [Decimal(9),Decimal(YCalc(9))] #Erzeugerpunkt
	c = multiplikation(PubKey,k)[0] #multipliziert kofaktor mit dem Oeffentlichen Schluessel, welcher ein Punkt ist. Die X-Koordniate reicht aus.
	C = multiplikation(P,k) #Erster Teil des Ciphers. Das Produkt des Erzeugerpunktes und des Kofaktors 
	d = Mod(c * m) #Zweiter Teil des Ciphers. Produkt der Nachricht und der x-Koordinate des PubKey-Produktes.
	output = str(C[0]) + 'v' + str(C[1])  + 'u' + str(d) #Erstelle den Output
	return output

def ElGamalDecryptCalc(cipher,Privatkey): #Mit dem Privatkey und den Cipher wird m ermittelt
	C = [0,0]
	C[0] = Decimal(cipher.split('v')[0])
	zwischenwert = cipher.split('v')[1]
	C[1] = Decimal(zwischenwert.split('u')[0])
	zwischenwert = zwischenwert.split('l')[0]
	d =  Decimal(zwischenwert.split('u')[1]) #Cipher wird gesplittet
	c1 = multiplikation(C,Privatkey)[0] #Es wird C mit dem Wert Multipliziert und die X-Koordinate ausgelesen.
	m1 = Mod(d/c1)
	if m1 % 1 >= 0.5:
		m = str(m1 + 1).split('.')[0]
	if m1% 1 < 0.5:
		m = str(m1).split('.')[0]
	#m wird ermittelt. Da das ergebnis aufgrund der Langen Decimalzahlen bei einer Praezision von 1000 immer sehr knapp unter dem eigentlichen 
	#m (differenz der werte ueblicherweise bei e-900) ist und die Rundenfunktion des flaots zu ungenau ist bei prec = 1000 wird 1 dazu addiert und dann
	#der rest hinter dem Komma, also .9999999... angeschnitten.
	m = int(m)
	output = UTF8.UTFdeConvert(m) #die Zahl wird wieder in einen Text gewandelt.
	return output

def KeyGenerator(password): #generiert das Keypaar aus einem Passwort mit sha3
	P = [Decimal(9),Decimal(YCalc(9))] #Jan: P0 -> kurze Zahl; P1 -> lange Zahl mit Komma nach ca. 7 Stellen
	Privat = int(KeyGen.KeyGen(password),16)
	Public = (multiplikation(P,Privat))
	Public = str(Public[0]) + "lol" + str(Public[1])
	return Privat, Public


def Elgamal(text,key):
	Key0 = Decimal(key.split('lol')[0])
	Key1 = Decimal(key.split('lol')[1])
	key = [Key0,Key1]
	text = SplitBlocks(text,16)
	c = ''
	for Wert in text:
		dump = ElGamalCalc(Wert,key)
		c +=dump +'l'
	return c
def ElgamalDecrypt(cipher,key):
	array = []
	count=0
	for char in cipher:
		if char == 'l':
			count+=1
	for i in range(0,count):
		wert = cipher.split('l')[i]
		array.append(wert)
	output = ''
	cipher = array
	#cipher = Stringsplitter(cipher)
	for i in range(0,len(cipher)):
		output += ElGamalDecryptCalc(cipher[i],key) 
	return output


def handleShellParam(param, default):

	for cmdarg in sys.argv:
		if(("--" + param + "=") in cmdarg):
			return str(cmdarg.replace(("--" + param + "="), ""))
		elif(("-" + param + "=") in cmdarg):
			return str(cmdarg.replace(("-" + param + "="), ""))
		elif(("--" + param) in cmdarg):
			return str(cmdarg.replace(("--"), ""))
		elif(("-" + param) in cmdarg):
			return str(cmdarg.replace(("-"), ""))
	return default

task = handleShellParam("t", 0) 
#zur Bestimmung was gerade von dem Script verlangt wird, sonst exited er, wenn man verschluesseln will und natuerlich das Password fehlt
#Fuer KeyGen waehlen Sie bitte die 1, fue Encrypt die 2 und fuer Decrypt die 3 
password = handleShellParam("p", 0)
keyname = handleShellParam("k", 0)
PlainOrCipher = handleShellParam("poc", 0)
Key = handleShellParam("key", 0)
if task == "1":
	if password != 0 and keyname != 0 and len(password) > 15: #das mit len braucht sha3, sonst bugt das.
		keys = KeyGenerator(password)
		privat = keys[0]
		public = keys[1]
		print("Private Key: " + str(privat))
		print("Public Key: " + str(public))
		#NewKey = {"key" : {"name" : keyname, "keys" : {"privkey" : privat, "pubkey" : public}}}
	
		#with open("keys.json", 'w') as outfile:
			#json.dump(NewKey, outfile, indent = 3, sort_keys = True)
			#sys.exit(0)
	elif password == 0:
		print("Es fehlte das Passwort bei ihrer Eingabe")
		sys.exit(1)
	elif len(str(password)) < 16:
		print("Das Passwort ist zu kurz. Die laenge muss mindestens 16 Zeichen betragen")
		sys.exit(1)
	elif keyname == 0:
		print("Es fehlte der Schluesselname bei ihrer Eingabe")
		sys.exit(1)
	else:
		print ("Leere Felder mag Deep Thought nicht") #der muss so bleiben!!!
		sys.exit(1)
if task == "2":
	#try :
	#	#with open(name+".json")as f:
	#	with open(keyname) as f:
	#		Key = json.load(f)
	#		PuKey = Key["Public Key: "]
	#except OSError:
	#	print('Fehler, kein Key für diesen Namen')
		#sys.exit(1)
	print(Elgamal(PlainOrCipher, Key))
	sys.exit(0)
if task == "3":
	#try :
	#	#with open(name+".json")as f:
	#	with open(keyname) as f:
	#		Key = json.load(f)
	#		PrKey = Key["Private Key: "]
	#except OSError:
	#	print('Fehler, kein Key für diesen Namen')
		#sys.exit(1)
	PrKey = Decimal(Key)
	print(ElgamalDecrypt(PlainOrCipher, PrKey))
	sys.exit(0)
else:
	print("No task given!")
#Ja ich weiss, dass evt. manche Kommentare noch geaendert werden muessen, aber klappt das so?


