#This program will read the frames assuming the file is a nice
#mp3, where the file starts with a frame header

import sys
import os
import binascii

def checkSync(data):
	#Here we care about the first 11 bits
	# 1111 1111 1110 0000 0000 0000 0000 0000
	# = 0xff e0 00 00

	# We only care about the first two bytes
	byte1 = data[0]
	byte2 = data[1]
	maskedres1 = byte1 & 0xff
	maskedres2 = byte2 & 0xe0

	if maskedres1 == 0xff and maskedres2 == 0xe0:
		return True
	else:
		return False

def getVersion(data):
	#Here we care about the 12th and 13th bits
	# 0000 0000 0001 1000 0000 0000 0000 0000
	# = 0x00 18 00 00

	#We only care about the second byte
	byte2 = data[1]
	maskedres = byte2 & 0x18

	if maskedres == 0x00: #00 (2.5)
		ver = 2.5
	elif maskedres == 0x08: #01 (reserved)
		ver = None
	elif maskedres == 0x10: #10 (2)
		ver = 2
	elif maskedres == 0x18: #11 (1)
		ver = 1
	else:
		ver = None
	
	return ver

def getLayer(data):
	#Here we care about the 14th and 15th bits
	# 0000 0000 0000 0110 0000 0000 0000 0000
	# = 0x00 06 00 00

	#We only care about the second byte
	byte2 = data[1]
	maskedres = byte2 & 0x06

	if maskedres == 0x00: #00 (reserved)
		layer = None
	elif maskedres == 0x02: #01 (Layer III)
		layer = 3
	elif maskedres == 0x04: #10 (Layer II)
		layer = 2
	elif maskedres == 0x06: #11 (Layer I)
		layer = 1
	else:
		layer = None

	return layer

def getProtection(data):
	#Here we care about the 16th bit (end of second byte)
	# 0000 0000 0000 0001 0000 0000 0000 0000
	# = 0x00 01 00 00

	byte2 = data[1]
	maskedres = byte2 & 0x01
	
	if maskedres == 0x00: #0
		protected = True
	elif maskedres == 0x01: #1
		protected = False
	else:
		protected = None

	return protected

def getBitrate(data, version, layer):
	#Here we care about the 17th-20th bits
	# 0000 0000 0000 0000 1111 0000 0000 0000
	# = 0x00 00 f0 00

	byte3 = data[2]
	maskedres = byte3 & 0xf0

	# These values are pulled from the standard
	if maskedres == 0x00: #0000
		bitrate = "free" # the bitrate can be anything

	elif maskedres == 0x10: #0001
		if version == 1 or layer == 1:
			bitrate = 32
		else:
			bitrate = 8

	elif  maskedres == 0x20: #0010
		if version == 1 and layer == 1:
			bitrate = 64
		elif version == 1 and layer == 2:
			bitrate = 48
		elif version == 1 and layer == 3:
			bitrate = 40
		elif version == 2 and layer == 1:
			bitrate = 48
		else:
			bitrate = 16

	elif maskedres == 0x30: #0011
		if version == 1 and layer == 1:
			bitrate = 96
		elif version == 1 and layer == 2:
			bitrate = 56
		elif version == 1 and layer == 3:
			bitrate = 48
		elif version == 2 and layer == 1:
			bitrate = 56
		else:
			bitrate = 24

	elif maskedres == 0x40: #0100
		if version == 1 and layer == 1:
			bitrate = 128
		elif version == 1 and layer == 2:
			bitrate = 64
		elif version == 1 and layer == 3:
			bitrate = 56
		elif version == 2 and layer == 1:
			bitrate = 64
		else:
			bitrate = 32

	elif maskedres == 0x50: #0101
		if version == 1 and layer == 1:
			bitrate = 160
		elif version == 1 and layer == 2:
			bitrate = 80
		elif version == 1 and layer == 3:
			bitrate = 64
		elif version == 2 and layer == 1:
			bitrate = 80
		else:
			bitrate = 40

	elif maskedres == 0x60: #0110
		if version == 1 and layer == 1:
			bitrate = 192
		elif version == 1 and layer == 2:
			bitrate = 96
		elif version == 1 and layer == 3:
			bitrate = 80
		elif version == 2 and layer == 1:
			bitrate = 96
		else:
			bitrate = 48

	elif maskedres == 0x70: #0111
		if version == 1 and layer == 1:
			bitrate = 224
		elif version == 1 and layer == 2:
			bitrate = 112
		elif version == 1 and layer == 3:
			bitrate = 96
		elif version == 2 and layer == 1:
			bitrate = 112
		else:
			bitrate = 56

	elif maskedres == 0x80: #1000
		if version == 1 and layer == 1:
			bitrate = 256
		elif version == 1 and layer == 2:
			bitrate = 128
		elif version == 1 and layer == 3:
			bitrate = 112
		elif version == 2 and layer == 1:
			bitrate = 128
		else:
			bitrate = 64

	elif maskedres == 0x90: #1001
		if version == 1 and layer == 1:
			bitrate = 288
		elif version == 1 and layer == 2:
			bitrate = 160
		elif version == 1 and layer == 3:
			bitrate = 128
		elif version == 2 and layer == 1:
			bitrate = 144
		else:
			bitrate = 80

	elif maskedres == 0xa0: #1010
		if version == 1 and layer == 1:
			bitrate = 320
		elif version == 1 and layer == 2:
			bitrate = 192
		elif version == 1 and layer == 3:
			bitrate = 160
		elif version == 2 and layer == 1:
			bitrate = 160
		else:
			bitrate = 96

	elif maskedres == 0xb0: #1011
		if version == 1 and layer == 1:
			bitrate = 352
		elif version == 1 and layer == 2:
			bitrate = 224
		elif version == 1 and layer == 3:
			bitrate = 192
		elif version == 2 and layer == 1:
			bitrate = 176
		else:
			bitrate = 112

	elif maskedres == 0xc0: #1100
		if version == 1 and layer == 1:
			bitrate = 384
		elif version == 1 and layer == 2:
			bitrate = 256
		elif version == 1 and layer == 3:
			bitrate = 224
		elif version == 2 and layer == 1:
			bitrate = 192
		else:
			bitrate = 128

	elif maskedres == 0xd0: #1101
		if version == 1 and layer == 1:
			bitrate = 416
		elif version == 1 and layer == 2:
			bitrate = 320
		elif version == 1 and layer == 3:
			bitrate = 256
		elif version == 2 and layer == 1:
			bitrate = 224
		else:
			bitrate = 144

	elif maskedres == 0xe0: #1110
		if version == 1 and layer == 1:
			bitrate = 448
		elif version == 1 and layer == 2:
			bitrate = 384
		elif version == 1 and layer == 3:
			bitrate = 320
		elif version == 2 and layer == 1:
			bitrate = 256
		else:
			bitrate = 160

	elif maskedres == 0xf0: #1111
		bitrate = None #this is not an acceptable value for bitrate

	return bitrate

def getSampleRate(data, version):
	#Here we care about the 21st and 22nd bits
	# 0000 0000 0000 0000 0000 1100 0000 0000
	# = 0x00 00 0c 00

	#Here we only care about the 3rd byte
	byte3 = data[2]
	maskedres = byte3 & 0x0c

	if maskedres == 0x00: #00
		if version == 1:
			samplerate = 44100
		elif version == 2:
			samplerate = 22050
		elif version == 2.5:
			samplerate = 11025
		else:
			samplerate = None
	elif maskedres == 0x04: #01
		if version == 1:
			samplerate = 48000
		elif version == 2:
			samplerate = 24000
		elif version == 2.5:
			samplerate = 12000
		else:
			samplerate = None
	elif maskedres == 0x08: #10
		if version == 1:
			samplerate = 32000
		elif version == 2:
			samplerate = 16000
		elif version == 2.5:
			samplerate = 8000
		else:
			samplerate = None
	elif maskedres == 0x0c: #11
		samplerate = None
	else:
		samplerate = None

	return samplerate

def getPadding(data):
	#Here we care about the 23rd bit
	# 0000 0000 0000 0000 0000 0010 0000 0000

	byte3 = data[2]
	maskedres = byte3 & 0x02

	if maskedres == 0x00: #0
		padding = 0
	elif maskedres == 0x02: #1
		padding = 1
	else:
		padding = None

	return padding

def getPrivate(data):
	#Here we care about the 24th bit
	# 0000 0000 0000 0000 0000 0001 0000 0000

	byte3 = data[2]
	maskedres = byte3 & 0x01

	if maskedres == 0x00: #0
		private = 0
	elif maskedres == 0x01: #1
		private = 1
	else:
		private = None

	return private

	return

def setPrivate(data, pvalue):
	#Here we care about the 24th bit
	# 0000 0000 0000 0000 0000 0001 0000 0000
	return

def getMode(data, bitrate, layer):
	#Here we care about the 25-26th bit
	# 0000 0000 0000 0000 0000 0000 1100 0000

	byte4 = data[3]
	maskedres = byte4 & 0xc0

	#handle special cases for layer 2
	if maskedres == 0x00: #00
		mode = "Stereo"
	elif maskedres == 0x40: #01
		mode = "Joint Stereo"
	elif maskedres == 0x80: #10
		mode = "Dual Channel"
	elif maskedres == 0xc0: #11
		mode = "Single Channel"
	
	# Account for bad Mode combinations
	if layer == 2:
		if(bitrate == 32 or bitrate == 48 or bitrate == 56 or bitrate == 80):
			if mode != "Single Channel":
				mode = None
		elif(bitrate == 224 or bitrate == 256 or bitrate==320 or bitrate==384):
			if mode == "Single Channel":
				mode = None

	return mode

def getCopyright(data):
	#Here we care about the 33rd bit
	# 0000 0000 0000 0000 0000 0000 0000 1000

	byte4 = data[3]
	maskedres = byte4 & 0x08

	if maskedres == 0x00: #0
		copyright = 0
	elif maskedres == 0x08: #1
		copyright = 1
	else:
		copyright = None

	return copyright

def setCopyright(data, value):
	#Here we care about the 33rd bit
	# 0000 0000 0000 0000 0000 0000 0000 1000
	return

def getOriginal(data):
	#Here we care about the 34th bit
	# 0000 0000 0000 0000 0000 0000 0000 0100

	byte4 = data[3]
	maskedres = byte4 & 0x04

	if maskedres == 0x00: #0
		original = 0
	elif maskedres == 0x04: #1
		original = 1
	else:
		original = None

	return original

def setOriginal(data, value):
	#Here we care about the 34th bit
	# 0000 0000 0000 0000 0000 0000 0000 0100
	return	

def getFrameSize(bitrate, samplerate, padding, layer):
	if layer == 1:
		size = (12 * bitrate / samplerate + padding) * 4
	elif(layer==2 || layer==3):
		size = 144 * bitrate / samplerate + padding
	else:
		size = None

	return size

def getHeaderData(data):
	#Sync (11 bits)
	#Check to ensure we have a string of 11 1's
	if(checkSync(data)):
		print("Sync successful")
	else:
		print("Bad sync, header is invalid, exiting...")
		return False

	#MPEG Version (2 bits)
	ver = getVersion(data)
	if ver is None:
		print("Invalid Version, header is invalid, exiting...")
		return False
	else:
		print("MPEG Version: " + str(ver))	

	#Layer Description (2 bit)
	layer = getLayer(data)
	if layer is None:
		print("Invalid Layer, header is invalid.")
		return False
	else:
		print("Layer: " + str(layer))

	#Protection Bit (1 bit)
	protected =getProtection(data)
	if(protected is None):
		return False
	if(protected):
		print("CRC protected, 16bit CRC follows header")
	else:
		print("Not protected.")

	#Bitrate (value based on Version and Layer) (4 bits)
	#will return bitrate in kbps
	bitrate = getBitrate(data, ver, layer)
	if(bitrate is not None):
		if bitrate == "free":
			print("Free format. Constant bitrate lower than allowable max")
		else:
			print("Bitrate: " + str(bitrate) + " kbps")
	else:
		print("Invalid bitrate value, header is invalid")
		return False

	#Sampling rate frequency (based on Version) (2 bits)
	samplerate = getSampleRate(data, ver)
	if(samplerate is not None):
		print("Sample rate: " + str(samplerate) + " Hz")
	else:
		print("Sample rate malformated, header is invalid.")
		return False

	#Padding (1 bit)
	padding = getPadding(data)
	if(padding is not None):
		print("Padding bit: " + str(padding))
	else:
		print("Something went wrong reading padding bit")
		return False

	#Private Bit (1 bit, can be used by us)
	private = getPrivate(data)
	print("Private bit: " + str(private))

	#Channel Mode (2 bits)
	mode = getMode(data, bitrate, layer)
	if(mode is not None):
		print("Mode is: " + mode)
	else:
		print("Bad mode, invalid frame header, exiting...")
		return False


	#Mode extension (2 bits) - I don't care about this

	#Copyright (1 bit)
	copyright = getCopyright(data)
	if(copyright is not None):
		print("copyright bit: " + str(copyright))
	else:
		print("Something went wrong reading padding bit")
		return False

	#Original/Copy (1 bit)
	original = getOriginal(data)
	if(original is not None):
		print("original bit: " + str(original))
	else:
		print("Something went wrong reading padding bit")
		return False

	#Emphasis (2 bits)


	framesize = getFrameSize(bitrate, samplerate, padding, layer)
	if(framesize is not None):
		print("Frame size in bytes: " + framesize)
	else:
		print("Something went wrong while calculating framesize.")
		return False

	return True

#def printAsBinary(byte):
#	print(bin(int(binascii.hexlify(byte), 16))[2:].zfill(8))

try:
	filename = sys.argv[1]
except:
	print("No filename specified, quitting")
	sys.exit(0)

f = open(filename, 'rb')
## read the first 4 bytes
##for i in range(0,4):
data = f.read(4)
##printAsBinary(data)

for byte in data:
	print(bin(byte))

header = getHeaderData(data)

if(header):
	print("Header read properly!")
else:
	print("One or more fields were invalid.")

##print(str(binascii.unhexlify(data))