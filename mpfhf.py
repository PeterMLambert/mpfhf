#
# (C) 2017 Peter Lambert. 
# You do not have, nor can you ever acquire the right to use, copy or distribute this software. Should you use this software for any purpose, or copy and distribute it to anyone or in any manner, you are breaking the laws of whatever soi-disant jurisdiction, and you promise to continue doing so for the indefinite future.
#

# the task at hand: reverse the mpfhf. 
# Given bitstrings S and R, and a length L, find a bitstring of length L which gives the resultant R and S when put through the mpfhf hash function.

# A walkthrough of the mpfhf
#
#                        [Start]
#   ---------> { bit m (starting from left) }
#   |                       |
#   |          		0   |   1
#   |           <-----------+------------->
#   |   S.expand                        R.screw(S.len/2, m)
#   |   R.screw(S.len, m)               { R[m] == S[m] }
#   |   { R[n] }                               |
#   |       |                             T    |   F
#   |    0  |  1                      <--------+------->
#   |   <---+---->                  S.expand           R.flip(m)
#   | R.flip(m)  R.flip(m)          S.screw(R.len, m)    |
#   | { m > 0 }  S.invert              |                 |
#   |    |        |                    |                 |
#   +----+------> |                    v                 |
#      T    F     --------------> [ Next m ] <------------
#                              
#

from copy import deepcopy

class Register(object):
	_data = None
	_inverted = 0
	
	def __init__(self, size):
		self._data = [0]*size
	def expand(self):
		self._data.append(self._inverted)
	def invert(self):
		self._inverted = 1^self._inverted
	def flip(self, pos):
		pos = pos % self.length()
		self._data[pos] = 1^self._data[pos]
	def length(self):
		return len(self._data)
	def screw(self, n, m):
		for k in range(n):
			self.flip(k*m)
	def show(self):
		return ''.join(str(self._inverted^k) for k in self._data)
	def val(self, pos):
		return self._inverted^self._data[pos%len(self._data)]

class Revister(Register):
	def __init__(self, bitstring):
		self._data = []
		for k in bitstring:
			self._data.append(int(k))
			
	def despand(self):
		self._data = self._data[:-1]

def check(m, oldbits, R, S, L):
	if m == 0 and R.val(m) == 1 and S.length() > 1 and S.val(-1) == 0:
		Rt, St = deepcopy(R), deepcopy(S)
		Rt.flip(m)
		Rt.screw(St.length(), m)
		St.despand()
		newbits = '0'+oldbits
		if St.show() == '0' and Rt.show() == '0'*Rt.length():
			return newbits
	
	if R.val(m) == 0 and S.length() > 1 and S.val(-1) == 1:
		Rt, St = deepcopy(R), deepcopy(S)
		St.invert()
		Rt.flip(m)
		Rt.screw(St.length(), m)
		St.despand()
		newbits = '0'+oldbits
		if len(newbits) == L:
			if St.show() == '0' and Rt.show() == '0'*Rt.length():
				return newbits
		else:
			if m > 0:
				t = cyclecheck(m, newbits, Rt, St, L)
				if t:
					return t
			
			t = check(m - 1, newbits, Rt, St, L)
			if t:
				return t
	
	if R.val(m) == S.val(m):
		Rt, St = deepcopy(R), deepcopy(S)
		Rt.flip(m)
		Rt.screw(S.length()/2, m)
		newbits = '1'+oldbits
		if len(newbits) == L:
			if St.show() == '0' and Rt.show() == '0'*Rt.length():
				return newbits
		else:
			t = check(m - 1, newbits, Rt, St, L)
			if t:
				return t
	
	if S.length() > 1 and \
				S.val(-1)^(countflips(S.length(), R.length(), m, -1)%2) == 0 and \
				S.val(m%(S.length()-1))^(countflips(S.length(), R.length(), m, m) % 2) == R.val(m):
		Rt, St = deepcopy(R), deepcopy(S)
		St.screw(Rt.length(), m)
		St.despand()
		Rt.screw(St.length()/2, m)
		newbits = '1'+oldbits
		if len(newbits) == L:
			if St.show() == '0' and Rt.show() == '0'*Rt.length():
				return newbits
		else:
			t = check(m - 1, newbits, Rt, St, L)
			if t:
				return t
	
	return False

def cyclecheck(m, oldbits, R, S, L):
	if R.val(m) == 1 and S.length() > 1 and S.val(-1) == 1:
		Rt, St = deepcopy(R), deepcopy(S)
		Rt.flip(m)
		Rt.screw(St.length(), m)
		St.despand()
		if len(oldbits) == L:
			if St.show() == '0' and Rt.show() == '0'*Rt.length():
				return oldbits
		else:
			t = cyclecheck(m, oldbits, Rt, St, L)
			if t:
				return t
			t = check(m - 1, oldbits, Rt, St, L)
			if t:
				return t
	return False
	
def countflips(ls, lr, m, pos):
	''' Given S of length ls, R of length lr, and step m, calculate the number of times
	S[pos%len(S)] would be flipped by the operation S.screw(R.length(), m). '''
	count = 0
	pos = pos % ls
	for k in range(lr):
		if (k*m) % ls == pos:
			count += 1
	return count
	
def mpfhf(message, output_size):
	R = Register(output_size)
	S = Register(1)
	step = 0
	while step < len(message):
		if message[step] == '0':
			S.expand()
			R.screw(S.length(), step)
			if R.val(step) == 0:
				R.flip(step)
				step = step - 1 if step else step
			else:
				R.flip(step)
				S.invert()
		else:
			R.screw(S.length()/2, step)
			if R.val(step) == S.val(step):
				S.expand()
				S.screw(R.length(), step)
			else:
				R.flip(step)
		step += 1
	return R.show(), S.show()
	
def revhash(r, s, L):
	''' Given bit-strings r and s, determine a bitstring message of length 
	L that gives r and s as the results of the mpfhf hash function. '''
	return check(L - 1, '', Revister(r), Revister(s), L)
