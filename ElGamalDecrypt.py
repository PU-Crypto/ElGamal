import math
from decimal import Decimal
import decimal

import KeyGen as KeyGen
import UTF8_Convert as UTF8
decimal.getcontext().prec = 1000 # es wird alles benoetigte improtiert und die Praezision der Decimals festgestellt, welche nicht zu gering sein sollte.
"""Curve25519: y^2=x^3+486662x^2+x
	Prinmzahl: 2^255- 19"""
a = 486662 #Die Montomerykurve wird mit Primzahl definiert
b = 1
prim = Decimal(2**255 - 19)
def YCalc(x): #Ermittlung des Punktes anhand des x-wertes und einsetzen in die Gleichung
	y = Decimal(((x**3+ 486662 * x**2 + x)/1)**Decimal(0.5))
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
		Xr = Decimal(b*(x2*y1-x1*y2)**2/(x1*x2*(x2-x1)**2))
		Yr = Decimal((((2*x1 + x2 + a)*(y2 - y1)) / (x2 - x1)) - b*((y2 - y1)**3 / (x2 - x1)**3) - y1)
		"""Die Formeln erschliesst sich mit einigem aufwand aus der geometrischen Definition
		der Addition. Dazu kann ich diese Seite empfehlen: http://en.wikipedia.org/wiki/Montgomery_curve. Etwas ungenauer findet sich das auch in 
		theoretischen Ausarbeitung"""  
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
		l = Decimal((3*x**2 + 2 * a * x + 1)/(2*y* b))
		Xr = Decimal(b * l**2 - a - 2*x)
		Yr = Decimal((x*3 + a )*l - b *l**3 - y)		
		r.append(Xr)
		r.append(Yr)
		return r
def multiplikation(p,n): #p ist der punkt n ist der Skalarfaktor
"""Im eigentlichen gibt es den Operator der multiplikation auf Elliptischen Kurven nicht, deswegen wird hier
rekrusiv das "doubling and add" - verfahren genutzt."""
	if n % 2 == 0 and n != 0: #Wenn der Faktor grade ist kann der erste Schritt gemacht werden, indem der Punkte verdoppelt wird.
		r = []
		x = Decimal(p[0])
		y = Decimal(p[1])
		l = Decimal((3*x**2 + 2 * a * x + 1)/(2 * y * b))
		Xr = Decimal(b * l**2 - a - 2*x)
		Yr = Decimal((x*3 + a )*l - b * l**3 - y)	
		r.append(Xr)
		r.append(Yr)
		r = multiplikation(r,n/2) 
		"""Hier passiert die Rekrusion, also der Selbstaufruf mit neuen Parametern. Da eine Verdopplung schon stattfand
		wird das Ergebnis, der neue Punkt, mit der Haelfte des urspruenglichen Faktors in die Funktion gegeben. Waere der Faktor n = 8 wuerde dieser
		Schritt 3 mal Passieren, da das neue n beim 4. mal 1 ist.""" 
		return r
	if n == 0: #Spezialfall: der Faktor ist 0. 
		r = []
		r.append(0)
		r.append(0)
		return r
	if n % 2 == 1 and n != 1:
		zwischenwert = multiplikation(p,n-1)
		"""Rekrusion: Beispiel: n = 5. Beim ersten durchlauf kommt er in diese Abfrage und schickt den Punkt mit n = 4 in die Funktion.
		Darauf wird 2 mal die Verdopplung durchgefuehrt und das Ergebnis mit p addiert: p * 5 = p*2*2 + p."""
		r = additionMG(p,zwischenwert)
		return r
	if n == 1: #Hier kommt die Funktion schliesslich hin bei n = 2^x. Wenn der Faktor schliesslich 1 ist, ist das Erbegnis p.
		return p

def ElGamalDecrypt(cipher,Privatkey): #Mit dem Privatkey und den Cipher wird m ermittelt
	C = [0,0]
	C[0] = Decimal(cipher.split('v')[0])
	zwischenwert = cipher.split('v')[1]
	C[1] = Decimal(zwischenwert.split('u')[0])
	d =  Decimal(zwischenwert.split('u')[1]) #Cipher wird gesplittet
	c1 = multiplikation(C,Privatkey)[0] #Es wird C mit dem Wert Multipliziert und die X-Koordinate ausgelesen.
	m1 = str(d/c1 % prim + 1) 
	"""m wird ermittelt. Da das ergebnis aufgrund der Langen Decimalzahlen bei einer Praezision von 1000 immer sehr knapp unter dem eigentlichen 
	m (differenz der werte ueblicherweise bei e-900) ist und die Rundenfunktion des flaots zu ungenau ist bei prec = 1000 wird 1 dazu addiert und dann
	der rest hinter dem Komma, also .9999999... angeschnitten."""
	m1 = m1.split('.')
	m1 = int(m1[0])
	output = UTF8.UTFdeConvert(m1) #die Zahl wird wieder in einen Text gewandelt.
	return output


