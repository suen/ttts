import os,hashlib,random,Crypto.PublicKey.RSA,copy
 
class User:
	def __init__(self,name):
		self.name = name
		self.RSAsize = 2048
		self.RSAKey = Crypto.PublicKey.RSA.generate(self.RSAsize, os.urandom)
	def getSizeKey (self):
		return self.RSAsize

	#we remove the secret key before returning it
	def getRSAKeySecure(self):
		secureKey = copy.copy(self.RSAKey)
		secureKey.d = 0
		return secureKey

	def getRSAKey(self):
		return self.RSAKey

	def getPrivateKey(self):
		return self.RSAKey.d

	def getN(self):
		return self.RSAKey.n

	def getPublicKey(self):
		return self.RSAKey.e

	def getName(self):
		self.name

	def printUser(self):
		print "info %s; n : %s, public key : %s, private key : %s" % (self.getName(),self.getN(), self.getPublicKey(), self.getPrivateKey())
	
class Ring:
    def __init__(self,publicKeys,lengthKey):
        self.publicKeys = publicKeys
	# 1 << lengthKey -1 = 2**(lengthKey-1) = q = 2**(b)-1 = max value on lengthKey bits
        self.lengthKey, self.numberPublicKeys,self.maxModuli = lengthKey, len(publicKeys),(1<<lengthKey)-1
 
    def getIndexCurrentSigner(self, signerKey):
	indexCurrentSigner = -1
	for index in range(0,self.numberPublicKeys):
		self.publicKeys[index].n
		if self.publicKeys[index].n == signerKey.n and self.publicKeys[index].e == signerKey.e:
			indexCurrentSigner = index
	if indexCurrentSigner == -1:
		raise Exception("signeur is not in the group")
	return indexCurrentSigner


    def getGroup(self):
	return self.publicKeys
    def sign(self,message,signerKey):
	#transorm string message to hexadecimal
        self.permutedMessage = self.permut(message)
        #generate a empty array that will contain a random value for each key
	x = [None]*self.numberPublicKeys
	y = [None]*self.numberPublicKeys
	#find index currentSigner, else raise a exception
	indexCurrentSigner = self.getIndexCurrentSigner(signerKey)
	#random seed for glue value
	u =random.randint(0,self.maxModuli)
	#v = glue value 
	z = v = self.E(u) 
	#begin combining function C, C_k,v = y_indexCurrentSigner ?
	#l'ordre est important
        for i in  range(indexCurrentSigner+1,self.numberPublicKeys) +range(0,indexCurrentSigner):
		#random x_i pick
        	x[i] = random.randint(0,self.maxModuli)
		y[i] = self.g(x[i],self.publicKeys[i].e,self.publicKeys[i].n)
		#or
            	v = self.E(v^y[i])
		#when we go to the last member
		if (i+1)%self.numberPublicKeys == 0: z = v
        #the current signer use his private key to sign it
	x[indexCurrentSigner] = self.g(v^u,signerKey.d,signerKey.n)
	#end combining function
	#concat c and s
        return [z,] + x
 
    def verify(self,message,ringSignature):
    	#key k
	self.permutedMessage = self.permut(message)
	#regenerate the ringSignature from the z output rignSignature[0] from the random value in the rign signature 
        y = map(lambda i:self.g(ringSignature[i+1],self.publicKeys[i].e,self.publicKeys[i].n),range(len(ringSignature)-1))
        return reduce(lambda x,i:self.E(x^y[i]),range(self.numberPublicKeys),ringSignature[0]) == ringSignature[0]
    #return the symetric key k, other version can be done with hash of all the public key as well
    def permut(self,message):
	#hashlib return hashed version of the message done by sha1 algo
	#hexdigest return the string of this version
	#int(string,16) convert the string to hexadecimal value
        return int(hashlib.sha1('%s'%message).hexdigest(),16)
    #generate concat x and the permuted message, then hash it to a hexadecimal form
    
    def E(self,x): 
        return int(hashlib.sha1('%s%s'%(x,self.permutedMessage)).hexdigest(),16)
    def RSA_TrapDoor(self,x,e,n):
	return  pow(x,e,n) 
    #extended trap door permutation to a common domain, domain = 2**b
    def g(self,x,e,n):
	#x = q*n + r
        q,r = x//n,x%n
	#(2**b)-1 , if we had chosen 2**b, m can be pick
	##maxModuli = (1<<self.lengthKey)-1 	
        return q*n + self.RSA_TrapDoor(r,e,n) if (q+1)*n <= self.maxModuli else x

