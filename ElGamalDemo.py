import math
from decimal import Decimal
import decimal
import random
import KeyGen as KeyGen
import UTF8_Convert as UTF8
decimal.getcontext().prec = 1000
"""Curve25519: y^2=x^3+486662x^2+x
	Prinmzahl: 2^255- 19"""
a = 486662
b = 1
prim = Decimal(2**255 - 19)

def YCalc(x):
	y = Decimal(((x**3+ 486662 * x**2 + x)/1)**Decimal(0.5))
	return y

def XCalc(y):
	r = 0
	i = 0
	while r != y:
		r = YCalc(i)
		i +=1
		print(i)
	return i

def additionMG(p,q): 
	r = []
	if p[0] == 0 and p[1] == 0:
		return q
	if q[0] ==0 and q[1] == 0:
		return p
	if p!=q and p[1]!=-q[1]:
		x1 = Decimal(p[0])
		y1 = Decimal(p[1])
		x2 = Decimal(q[0])
		y2 = Decimal(q[1])
		Xr = Decimal(b*(x2*y1-x1*y2)**2/(x1*x2*(x2-x1)**2))
		Yr = Decimal((((2*x1 + x2 + a)*(y2 - y1)) / (x2 - x1)) - b*((y2 - y1)**3 / (x2 - x1)**3) - y1)
		r.append(Xr)
		r.append(Yr)
		return r
	if p[0] == q[0] and p[1] == -q[1]:
		Xr = Decimal(0)
		Yr = Decimal(0)
		r.append(Xr)
		r.append(Yr)
		return r
	if p == q:
		x = Decimal(p[0])
		y = Decimal(p[1])
		l = Decimal((3*x**2 + 2 * a * x + 1)/(2*y* b))
		Xr = Decimal(b * l**2 - a - 2*x)
		Yr = Decimal((x*3 + a )*l - b *l**3 - y)		
		r.append(Xr)
		r.append(Yr)
		return r
def multiplikation(p,n):
	if n % 2 == 0 and n != 0:
		r = []
		x = Decimal(p[0])
		y = Decimal(p[1])
		l = Decimal((3*x**2 + 2 * a * x + 1)/(2 * y * b))
		Xr = Decimal(b * l**2 - a - 2*x)
		Yr = Decimal((x*3 + a )*l - b * l**3 - y)	
		r.append(Xr)
		r.append(Yr)
		r = multiplikation(r,n/2)
		return r
	if n == 0:
		r = []
		r.append(0)
		r.append(0)
		return r
	if n % 2 == 1 and n != 1:
		zwischenwert = multiplikation(p,n-1)
		r = additionMG(p,zwischenwert)
		return r
	if n == 1:
		return p
x = int(KeyGen.KeyGen('das ist das passwort, welches zu kurz ist, du lappen, anscheinen sei er immernoch zu kurz. ich meine jetzt ernsthaft?'),16)

def ElGamal(text,Key):
	m = int(UTF8.UTFConvert(text))
	print(type(m))
	k = random.randint(0,100)
	P = [Decimal(3),Decimal(YCalc(3))]

	Y = multiplikation(P,x)

	c = multiplikation(Y,k)[0]
	Px = 3
	C = multiplikation(P,k)
	d = c * m % prim
	output = str(C[0]) + 'v' + str(C[1])  + 'u' + str(d)
	return output

print(ElGamal('das ist der text','das ist das passwort, welches zu kurz ist, du lappen, anscheinen sei er immernoch zu kurz. ich meine jetzt ernsthaft?'))
	

def KeyGenerator(password):
	P = [Decimal(3),Decimal(YCalc(3))]
	Privat = int(KeyGen.KeyGen(password),16)
	Public = multiplikation(P,Privat)
	return Privat, Public
print(KeyGenerator('das ist mein geiles password'))