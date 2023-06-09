import binascii
import Padding


class Present:
        def __init__(self,key,rounds=32):
                self.rounds = rounds
                if len(key) * 8 == 80:
                        self.roundkeys = generateRoundkeys80(string2number(key),self.rounds)
                elif len(key) * 8 == 128:
                        self.roundkeys = generateRoundkeys128(string2number(key),self.rounds)
                else:
                        raise ValueError("Key must be a 128-bit or 80-bit rawstring")

        def encrypt(self,block):
                state = string2number(block)
                for i in range (self.rounds-1):
                        state = addRoundKey(state,self.roundkeys[i])
                        state = sBoxLayer(state)
                        state = pLayer(state)
                cipher = addRoundKey(state,self.roundkeys[-1])
                return number2string_N(cipher,8)

        def decrypt(self,block):
                state = string2number(block)
                for i in range (self.rounds-1):
                        state = addRoundKey(state,self.roundkeys[-i-1])
                        state = pLayer_dec(state)
                        state = sBoxLayer_dec(state)
                decipher = addRoundKey(state,self.roundkeys[0])
                return number2string_N(decipher,8)



Sbox= [0xc,0x5,0x6,0xb,0x9,0x0,0xa,0xd,0x3,0xe,0xf,0x8,0x4,0x7,0x1,0x2]
Sbox_inv = [Sbox.index(x) for x in range(16)]
PBox = [0,16,32,48,1,17,33,49,2,18,34,50,3,19,35,51,
        4,20,36,52,5,21,37,53,6,22,38,54,7,23,39,55,
        8,24,40,56,9,25,41,57,10,26,42,58,11,27,43,59,
        12,28,44,60,13,29,45,61,14,30,46,62,15,31,47,63]
PBox_inv = [PBox.index(x) for x in range(64)]

def generateRoundkeys80(key,rounds):
        roundkeys = []
        for i in range(1,rounds+1): # (K1 ... K32)
                # rawkey: used in comments to show what happens at bitlevel
                # rawKey[0:64]
                roundkeys.append(key >>16)
                #1. Shift
                #rawKey[19:len(rawKey)]+rawKey[0:19]
                key = ((key & (2**19-1)) << 61) + (key >> 19)
                #2. SBox
                #rawKey[76:80] = S(rawKey[76:80])
                key = (Sbox[key >> 76] << 76)+(key & (2**76-1))
                #3. Salt
                #rawKey[15:20] ^ i
                key ^= i << 15
        return roundkeys

def generateRoundkeys128(key,rounds):
        roundkeys = []
        for i in range(1,rounds+1): # (K1 ... K32)
                # rawkey: used in comments to show what happens at bitlevel
                roundkeys.append(key >>64)
                #1. Shift
                key = ((key & (2**67-1)) << 61) + (key >> 67)
                #2. SBox
                key = (Sbox[key >> 124] << 124)+(Sbox[(key >> 120) & 0xF] << 120)+(key & (2**120-1))
                #3. Salt
                #rawKey[62:67] ^ i
                key ^= i << 62
        return roundkeys

def addRoundKey(state,roundkey):
        return state ^ roundkey

def sBoxLayer(state):

        output = 0
        for i in range(16):
                output += Sbox[( state >> (i*4)) & 0xF] << (i*4)
        return output

def sBoxLayer_dec(state):
        output = 0
        for i in range(16):
                output += Sbox_inv[( state >> (i*4)) & 0xF] << (i*4)
        return output

def pLayer(state):
        output = 0
        for i in range(64):
                output += ((state >> i) & 0x01) << PBox[i]
        return output

def pLayer_dec(state):
        output = 0
        for i in range(64):
                output += ((state >> i) & 0x01) << PBox_inv[i]
        return output

def string2number(i):
    val = int.from_bytes(i, byteorder='big')
   
    return val
    


def number2string_N(i, N):
    s = '%0*x' % (N*2, i)
    return binascii.unhexlify(str(s))

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
    
    
    
    
    
    
    
    
text="secret"
textLen=len(text)
k="a123456789b987654321" #hex

text = Padding.appendPadding(text,blocksize=8)

print ('Text:\t'+text)
print ('Key:\t'+k)
print ('\n----------------------------------------------\n')
key = bytes.fromhex(k)
   
 
cipher = Present(key) 
encrypted = cipher.encrypt(text.encode())
print ('Cipher:\t\t'+encrypted.hex())
decrypted = cipher.decrypt(encrypted)

print ('Decrypted:\t'+decrypted.hex())
print ('Decrypted:\t'+Padding.removePadding(decrypted.decode()))


