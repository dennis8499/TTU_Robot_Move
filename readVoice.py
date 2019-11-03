# -*- coding: utf-8 -*-
import serial, sys, time
import Robot1001

#NUM_List = ['118', '134', '148', '12', '164']
NUM_List = ['134', '12', '118', '166']
ID_NUM = ''

def readUart():
	global ID_NUM
	with serial.Serial('/dev/ttyUSB0', 9600, timeout = 1) as Voice_ser:
		ID_NUM = Voice_ser.readline()   # read a '\n' terminated line
		print(ID_NUM)	
	if(ID_NUM in NUM_List):
		Move = Robot1001.Moving(ID_NUM)
		ID_NUM = ''
		readUart()
		#if(Move == True):
			#with serial.Serial(Voice_COMPORT, Voice_BAUDRATES, timeout = 1) as Voice_ser:
			#	ser.write('True')		
	else:
		readUart()

def DirectInput():
	global ID_NUM
	ID_NUM = raw_input("Please Input the target.")	
	if(ID_NUM in NUM_List):
		Move = Robot1001.Moving(ID_NUM)
		if(Move == True):
			DirectInput()
		else:
			DirectInput()
	else:
		print("The ID is not in List.")
		DirectInput()
		
def main():
	Mode = raw_input("Please input \'0\':Uart Mode or \'1\':Direct Input Mode.")
	if(Mode == '0'):
		readUart()
	elif(Mode == '1'):
		DirectInput()


if __name__ == '__main__':		
	main()
