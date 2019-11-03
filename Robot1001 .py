# -*- coding: utf-8 -*-
from collections import deque, namedtuple
import serial, sys, time
import numpy as np
import re
#import Dijkstra2
import Dijkstra
#----star gaze----
ID_NUM = ""
Angle = ""
Height = ""
Gazer_X = ""
Gazer_Y = ""
before_ID = ''
#-----------------
NUM_List = ['50', '16', '80', '48', '32']
#NUM_List = ['34', '2', '18', '66']
#NUM_List = ['118', '134', '148', '12', '164']
#Command = ['w', 'a', 'd', 'x']
Degree_UpperLimit = [95, -85, 5, -175]
Degree_LowerLimit = [85, -95, -5, 175]
Command = ['s', 'a', 'd', 'z']
Direction = 0
#0 = 116 > 180 1 = 180 > 132 2 = 180 > 116 3 = 132 > 180
PointLimit = 5
#在 X = +-10 Y = +-10才算在Poing裡面
PointRangeLimit = 5
#靠近 X = +-20 Y = +-20的時候啟動到定點公式
LineLimit = 10
#若偏移這個位置則進行路經返回
graph = None
Target = '16'
time_sleep = 0.3
path = None
Rotation_Count_Limit = 1500
Rotation_Degree_limit = 2
Origin = '16'
#-----------------
star_COMPORT = '/dev/ttyUSB0'
star_BAUDRATES = 115200
star_ser = serial.Serial(star_COMPORT, star_BAUDRATES)

MEGA_COMPORT = '/dev/ttyACM0'
MEGA_BAUDRATES = 9600
MEGA_ser = serial.Serial(MEGA_COMPORT, MEGA_BAUDRATES)
send_msg = ''
#-----------------
def Calc_Data(str):
	global ID_NUM, Angle, Height, Gazer_X, Gazer_Y
	arr = str.split(',')
	ID_NUM = arr[0][1:]
	Angle = arr[1]	
	Gazer_X = arr[2]
	Gazer_Y = arr[3]
	Heigh = arr[4]
	print('ID Num',ID_NUM)
	print('Angle', int(float(Angle)))
	print('Heigh', Heigh )
	print('X', Gazer_X, 'Y', Gazer_Y)

		
def transmit_Arduino(c):
	global send_msg
	if (send_msg != c):
		send_msg = c
		MEGA_ser.write(send_msg)
		print c
		
def Moving(END):		
	str = []
	Flag = False
	Flag_Mode = 1
	Flag_Range_Offset = 1
	Flag_Range_Offset_flag1 = True
	Flag_Range_Offset_flag2 = False
	Flag_Range_Offset_flag3 = False
	Flag_Point1 = True
	Flag_Point2 = False
	Flag_END1 = True
	Flag_END2 = False
	BackFlag = False
	Flag_Path = False
	Flag_Path2 = False
	Flag_Path3 = False
	Flag_Path4 = False
	Flag_Path5 = False
	Flag_Path_Mode = 0
	degree = X = Y = 0
	Dijkstra_flag = True
	BackUpperLimit = 0
	BackLowerLimit = 0
	Rotation_Count = 0
	Rotation_Degree_Count = 0
	while True:
		#Read Rs232
		state = star_ser.read()
		if (state == '`'): # read landmark
			str = ''.join(str)
			print (str)
			if (str == 'DeadZone'):
				str = []
				continue
			
			if(len(str) != 0):
				Calc_Data(str)
				Flag = True				
				print ('\n')
				str = []
				

		elif (state == '^') or (state == '~'):
			star_ser.read()
		elif (state == '|'):
			str.append(',')
		else:
			str.append(state)	
		
		if (Flag == True):			
			global ID_NUM, Angle, Gazer_X, Gazer_Y, before_ID, send_msg, Direction, PointLimit, NUM_List, PointRangeLimit, LineLimit, graph, time_sleep, Command, path
			global Degree_UpperLimit, Degree_LowerLimit, Rotation_Degree_limit, Rotation_Count_Limit, Origin
			degree = int(float(Angle))
			X = int(float(Gazer_X))
			Y = int(float(Gazer_Y))	
			if(Flag_Mode == 1 and ID_NUM in NUM_List):
				#回歸原點					
				if(Flag_Range_Offset == 1 and X >= -PointLimit and X <= PointLimit and Y >= -PointLimit and Y <= PointLimit):
					Flag_Mode = 2
					Dijkstra_flag = True
					
				elif(Flag_Range_Offset == 1 and Flag_Range_Offset_flag1 == True and X >= -PointLimit):
					Flag_Range_Offset = 2					

				elif(Flag_Range_Offset == 1 and Flag_Range_Offset_flag1 == True and X <= -PointLimit):			
					if(degree >= Degree_LowerLimit[2] and degree <= Degree_UpperLimit[2]):
						transmit_Arduino(Command[0]) #w
						Flag_Range_Offset_flag1 = False
						Flag_Range_Offset_flag2 = False
						Flag_Range_Offset_flag3 = True
					else:
						transmit_Arduino(Command[3]) #x
						time.sleep(time_sleep)						
						if(degree >= 0 and degree <= 180):
							transmit_Arduino(Command[1]) #a
						elif(degree >= -180 and degree <= 0):
							transmit_Arduino(Command[2]) #d						
						Flag_Range_Offset_flag1 = False
						Flag_Range_Offset_flag2 = True
						Tmp_LowerLimit = Degree_LowerLimit[2]
						Tmp_UpperLimit = Degree_UpperLimit[2]
						
				elif(Flag_Range_Offset == 1 and Flag_Range_Offset_flag2 == True):
					if(degree >= Tmp_LowerLimit and degree <= Tmp_UpperLimit):						
						transmit_Arduino(Command[3]) #x
						time.sleep(time_sleep)
						transmit_Arduino(Command[0]) #w
						Rotation_Count = 0
						Rotation_Degree_Count = 0
						Flag_Range_Offset_flag2 = False
						Flag_Range_Offset_flag3 = True
						
					else:						
						Rotation_Count += 1						
						if(Rotation_Count == Rotation_Count_Limit):
							Tmp_LowerLimit -= 5
							Tmp_UpperLimit += 5
							Rotation_Degree_Count += 1
							Rotation_Count = 0
							if(Rotation_Degree_Count == Rotation_Degree_limit):
								transmit_Arduino(Command[3]) #x
								Rotation_Degree_Count = 0
								break
								
						elif(degree >= -45 and degree < -5):
							transmit_Arduino(Command[2]) #d
							
						elif(degree > 5 and degree <= 45): 		
							transmit_Arduino(Command[1]) #a
								
				elif(Flag_Range_Offset == 1 and Flag_Range_Offset_flag3 == True):
					if(X >= -PointLimit):							
						transmit_Arduino(Command[3]) #x					
						Flag_Range_Offset_flag3 = False
						Flag_Range_Offset_flag1 = True
						Flag_Range_Offset = 2
							
				elif(Flag_Range_Offset == 2 and Flag_Range_Offset_flag1 == True and X <= PointLimit):
					Flag_Range_Offset = 3	

				elif(Flag_Range_Offset == 2 and Flag_Range_Offset_flag1 == True and X >= PointLimit):	
					if(degree >= Degree_LowerLimit[3] or degree <= Degree_UpperLimit[3]):
						transmit_Arduino(Command[0]) #w
						Flag_Range_Offset_flag1 = False
						Flag_Range_Offset_flag2 = False
						Flag_Range_Offset_flag3 = True
					else:
						transmit_Arduino(Command[3]) #x
						time.sleep(time_sleep)
						if(degree >= 0 and degree <= 180):
							transmit_Arduino(Command[2]) #d
						elif(degree >= -180 and degree <= 0):
							transmit_Arduino(Command[1]) #a
						Flag_Range_Offset_flag1 = False
						Flag_Range_Offset_flag2 = True
						Tmp_LowerLimit = Degree_LowerLimit[3]
						Tmp_UpperLimit = Degree_UpperLimit[3]
						
				elif(Flag_Range_Offset == 2 and Flag_Range_Offset_flag2 == True):
					if(degree >= Tmp_LowerLimit or degree <= Tmp_UpperLimit):
						transmit_Arduino(Command[3])
						time.sleep(time_sleep)
						transmit_Arduino(Command[0])
						Rotation_Count = 0
						Rotation_Degree_Count = 0
						Flag_Range_Offset_flag2 = False
						Flag_Range_Offset_flag3 = True
						
					else:
						Rotation_Count += 1						
						if(Rotation_Count == Rotation_Count_Limit):
							Tmp_LowerLimit -= 5
							Tmp_UpperLimit += 5
							Rotation_Degree_Count += 1
							Rotation_Count = 0
							if(Rotation_Degree_Count == Rotation_Degree_limit):
								transmit_Arduino(Command[3]) #x
								Rotation_Degree_Count = 0
								break
								
						elif(degree >= 135 and degree < 175):
							transmit_Arduino(Command[2]) #d
							
						elif(degree > -175 and degree <= -135):		
							transmit_Arduino(Command[1]) #a

				elif(Flag_Range_Offset == 2 and Flag_Range_Offset_flag3 == True):		
					if(X <= PointLimit):
						transmit_Arduino(Command[3]) #x
						Flag_Range_Offset_flag3 = False
						Flag_Range_Offset_flag1 = True
						Flag_Range_Offset = 3
							
				elif(Flag_Range_Offset == 3 and Flag_Range_Offset_flag1 == True and Y >= -PointLimit):
					Flag_Range_Offset = 4				
					
				elif(Flag_Range_Offset == 3 and Flag_Range_Offset_flag1 == True and Y <= -PointLimit):
					if(degree >= Degree_LowerLimit[1] and degree <= Degree_UpperLimit[1]):
						transmit_Arduino(Command[0]) #w
						Flag_Range_Offset_flag1 = False
						Flag_Range_Offset_flag2 = False
						Flag_Range_Offset_flag3 = True
					else:
						transmit_Arduino(Command[3]) #x
						time.sleep(time_sleep)
						if(degree >= 0 and degree <= 90 or degree >= -90 and degree <= 0):
							transmit_Arduino(Command[1]) #a
						elif(degree >= 90 and degree <= 180 or degree >= -180 and degree <= -90):
							transmit_Arduino(Command[2]) #d
						Flag_Range_Offset_flag1 = False
						Flag_Range_Offset_flag2 = True
						Tmp_LowerLimit = Degree_LowerLimit[1]
						Tmp_UpperLimit = Degree_UpperLimit[1]
						
				elif(Flag_Range_Offset == 3 and Flag_Range_Offset_flag2 == True):		
					if(degree >= Tmp_LowerLimit and degree <= Tmp_UpperLimit):
						transmit_Arduino(Command[3]) #x
						time.sleep(time_sleep)
						transmit_Arduino(Command[0]) #w
						Rotation_Count = 0
						Rotation_Degree_Count = 0
						Flag_Range_Offset_flag2 = False
						Flag_Range_Offset_flag3 = True
					else:
						Rotation_Count += 1						
						if(Rotation_Count == Rotation_Count_Limit):
							Tmp_LowerLimit -= 5
							Tmp_UpperLimit += 5
							Rotation_Degree_Count += 1
							Rotation_Count = 0
							if(Rotation_Degree_Count == Rotation_Degree_limit):
								transmit_Arduino(Command[3]) #x
								Rotation_Degree_Count = 0
								break
								
						elif(degree >= -135 and degree < -95):
							transmit_Arduino(Command[2]) #d
							
						elif(degree > -85 and degree <= -45): 		
							transmit_Arduino(Command[1]) #a

	
				elif(Flag_Range_Offset == 3 and Flag_Range_Offset_flag3 == True):		
					if(Y >= -PointLimit):
						transmit_Arduino(Command[3]) #x
						Flag_Range_Offset_flag1 = True
						Flag_Range_Offset_flag3 = False
						Flag_Range_Offset = 4
							
				elif(Flag_Range_Offset == 4 and Flag_Range_Offset_flag1 == True and Y <= PointLimit):
					Flag_Range_Offset = 1
					Flag_Mode = 2
					Dijkstra_flag = True					
					
				elif(Flag_Range_Offset == 4 and Flag_Range_Offset_flag1 == True and Y >= PointLimit):
					if(degree >= Degree_LowerLimit[0] and degree <= Degree_UpperLimit[0]):
						transmit_Arduino(Command[0]) #w
						Flag_Range_Offset_flag1 = False
						Flag_Range_Offset_flag2 = False
						Flag_Range_Offset_flag3 = True
					else:
						transmit_Arduino(Command[3]) #x
						time.sleep(time_sleep)
						if(degree >= 0 and degree <= 90 or degree >= -90 and degree <= 0):
							transmit_Arduino(Command[2]) #d
						elif(degree >= 90 and degree <= 180 or degree >= -180 and degree <= -90):
							transmit_Arduino(Command[1]) #a
						Flag_Range_Offset_flag1 = False
						Flag_Range_Offset_flag2 = True
						Tmp_LowerLimit = Degree_LowerLimit[0]
						Tmp_UpperLimit = Degree_UpperLimit[0]
						
				elif(Flag_Range_Offset == 4 and Flag_Range_Offset_flag2 == True):						
					if(degree >= Tmp_LowerLimit and degree <= Tmp_UpperLimit):
						transmit_Arduino(Command[3]) #x
						time.sleep(time_sleep)
						transmit_Arduino(Command[0]) #w
						Rotation_Count = 0
						Rotation_Degree_Count = 0
						Flag_Range_Offset_flag2 = False
						Flag_Range_Offset_flag3 = True	
						
					else:
						Rotation_Count += 1						
						if(Rotation_Count == Rotation_Count_Limit):
							Tmp_LowerLimit -= 5
							Tmp_UpperLimit += 5
							Rotation_Degree_Count += 1
							Rotation_Count = 0
							if(Rotation_Degree_Count == Rotation_Degree_limit):
								transmit_Arduino(Command[3]) #x
								Rotation_Degree_Count = 0		
								break
								
						elif(degree >= 45 and degree < 85): 
							transmit_Arduino(Command[2])
						
						elif(degree > 95 and degree <= 135):
							transmit_Arduino(Command[1])

				elif(Flag_Range_Offset == 4 and Flag_Range_Offset_flag3 == True):		
					if(Y <= PointLimit):
						transmit_Arduino(Command[3]) #x
						Flag_Range_Offset_flag3 = False
						Flag_Range_Offset_flag1 = True
						Flag_Range_Offset = 1		
						Flag_Mode = 2
						Dijkstra_flag = True
						
			elif(Flag_Mode == 2 and ID_NUM in NUM_List):
				#點位方向
				if(ID_NUM == END):
					if(path != None):
						if(Flag_END1 == True):
							if(END == Origin):
								BackFlag = False
								BackUpperLimit = 95 #未定
								BackLowerLimit = 85 #未定
								transmit_Arduino(Command[3]) #x
								time.sleep(time_sleep)
								#未定
								if(degree >= 0 and degree <= 90 or degree >= -90 and degree <= 0):
									transmit_Arduino(Command[2]) #d
								elif(degree >= 90 and degree <= 180 or degree >= -180 and degree <= -90):
									transmit_Arduino(Command[1]) #a
									
							elif(path[1] == -90): 
								BackFlag = False
								BackUpperLimit = 95
								BackLowerLimit = 85
								transmit_Arduino(Command[3]) #x
								time.sleep(time_sleep)
								if(degree >= 0 and degree <= 90 or degree >= -90 and degree <= 0):
									transmit_Arduino(Command[2]) #d
								elif(degree >= 90 and degree <= 180 or degree >= -180 and degree <= -90):
									transmit_Arduino(Command[1]) #a
									
							elif(path[1] == 90):
								BackFlag = False
								BackUpperLimit = -85
								BackLowerLimit = -95
								transmit_Arduino(Command[3]) #x
								time.sleep(time_sleep)
								if(degree >= 0 and degree <= 90 or degree >= -90 and degree <= 0):
									transmit_Arduino(Command[1]) #a
								elif(degree >= 90 and degree <= 180 or degree >= -180 and degree <= -90):
									transmit_Arduino(Command[2]) #d
									
							elif(path[1] == 0): 
								BackFlag = True
								BackUpperLimit = -175
								BackLowerLimit = 175
								transmit_Arduino(Command[3]) #x
								time.sleep(time_sleep)
								if(degree >= 0 and degree <= 180):
									transmit_Arduino(Command[2]) #d
								elif(degree >= -180 and degree <= 0):
									transmit_Arduino(Command[1]) #a
									
							elif(path[1] == 180):
								BackFlag = False
								BackUpperLimit = 5
								BackLowerLimit = -5
								transmit_Arduino(Command[3]) #x
								time.sleep(time_sleep)
								if(degree >= 0 and degree <= 180):
									transmit_Arduino(Command[1]) #a
								elif(degree >= -180 and degree <= 0):
									transmit_Arduino(Command[2]) #d					
							Flag_END1 = False
							Flag_END2 = True
							
						elif(Flag_END2 == True):
							if(BackFlag == True):
								if(degree <= BackUpperLimit or degree >= BackLowerLimit):
									transmit_Arduino(Command[3]) #x
									Flag_END1 = True
									Flag_END2 = False
									break
							elif(BackFlag == False):
								if(degree >= BackLowerLimit and degree <= BackUpperLimit):
									transmit_Arduino(Command[3]) #x
									Flag_END1 = True
									Flag_END2 = False
									break
					elif(path == None):
						if(Flag_END1 == True):
							if(END == Origin):
								BackFlag = False
								BackUpperLimit = 95 #未定
								BackLowerLimit = 85 #未定
								transmit_Arduino(Command[3]) #x
								time.sleep(time_sleep)
								#未定
								if(degree >= 0 and degree <= 90 or degree >= -90 and degree <= 0):
									transmit_Arduino(Command[2]) #d
								elif(degree >= 90 and degree <= 180 or degree >= -180 and degree <= -90):
									transmit_Arduino(Command[1]) #a
								Flag_END1 = False
								Flag_END2 = True
						elif(Flag_END2 == True):
							if(BackFlag == True):
								if(degree <= BackUpperLimit or degree >= BackLowerLimit):
									transmit_Arduino(Command[3]) #x
									Flag_END1 = True
									Flag_END2 = False
									break
							elif(BackFlag == False):
								if(degree >= BackLowerLimit and degree <= BackUpperLimit):
									transmit_Arduino(Command[3]) #x
									Flag_END1 = True
									Flag_END2 = False
									break
				elif(ID_NUM != END):
					if(Dijkstra_flag == True):
						#path = Dijkstra2.makePath(ID_NUM, END)
						path = Dijkstra.makePath(ID_NUM, END)
						Flag_Point1 = True
						Dijkstra_flag = False
						Aim = path[0]	
						if(X >= -PointLimit and X <= PointLimit and Y >= -PointLimit and Y <= PointLimit):
							if(path[1] == -90): 
								Direction = 1
								UpperLimit = path[1] + 5 #-85
								LowerLimit = path[1] - 5 #-95
							elif(path[1] == 90):
								Direction = 2
								UpperLimit = path[1] + 5 #95
								LowerLimit = path[1] - 5 #85
							elif(path[1] == 0): 
								Direction = 3
								UpperLimit = path[1] + 5 #5
								LowerLimit = path[1] - 5 #-5	
							elif(path[1] == 180):
								Direction = 4
								UpperLimit = -path[1] + 5 #-175
								LowerLimit = path[1] - 5 #175	
						else:
							Flag_Mode = 1	
							Flag_Point1 = False
							
					elif(path != None and Dijkstra_flag == False):					
						if(Direction == 1 or Direction == 2 or Direction == 3):
							if(Flag_Point1 == True):	
								if (degree >= LowerLimit and degree <= UpperLimit):
									transmit_Arduino(Command[0]) #w
									Flag_Mode = 3
									Flag_Path = True	
									Flag_Point1 = False
									Flag_Point2 = False									
								else:
									transmit_Arduino(Command[3]) #x
									time.sleep(time_sleep)
									if(Direction == 1): #-90
										if((degree >= 0 and degree <= 90) or (degree >= -90 and degree <= 0)):
											transmit_Arduino(Command[1]) #a
										elif((degree >= 90 and degree <= 180) or (degree >= -180 and degree < -90)):
											transmit_Arduino(Command[2]) #d
											
									elif(Direction == 2): #90
										if((degree >= 0 and degree <= 90) or (degree >= -90 and degree <= 0)):
											transmit_Arduino(Command[2]) #d
										elif((degree >= 90 and degree <= 180) or (degree >= -180 and degree <= -90)):
											transmit_Arduino(Command[1]) #a
											
									elif(Direction == 3): #0
										if(degree >= 0 and degree <= 180):
											transmit_Arduino(Command[1]) #a
										elif(degree >= -180 and degree <= 0):
											transmit_Arduino(Command[2]) #d		
											
									Flag_Point1 = False
									Flag_Point2 = True	
									Tmp_LowerLimit = LowerLimit
									Tmp_UpperLimit = UpperLimit
									
							elif(Flag_Point2 == True):
								if (degree >= Tmp_LowerLimit and degree <= Tmp_UpperLimit):
									transmit_Arduino(Command[3]) #x
									time.sleep(time_sleep)
									transmit_Arduino(Command[0]) #w
									Flag_Mode = 3
									Rotation_Count = 0
									Rotation_Degree_Count = 0
									Flag_Path = True
									Flag_Point2 = False						
								else:
									Rotation_Count += 1						
									if(Rotation_Count == Rotation_Count_Limit):
										Tmp_LowerLimit -= 5
										Tmp_UpperLimit += 5
										Rotation_Degree_Count += 1
										Rotation_Count = 0
										if(Rotation_Degree_Count == Rotation_Degree_limit):
											transmit_Arduino(Command[3]) #x
											Rotation_Degree_Count = 0	
											break
											
									elif(degree >= LowerLimit - 50 and degree < LowerLimit):
										transmit_Arduino(Command[2]) #d
										
									elif(degree > UpperLimit and degree <= UpperLimit + 50):
										transmit_Arduino(Command[1]) #a
							
						elif(Direction == 4):
							if(Flag_Point1 == True):								
								if(degree >= LowerLimit or degree <= UpperLimit): #180
									transmit_Arduino(Command[0]) #w
									Flag_Mode = 3
									Flag_Path = True	
									Flag_Point1 = False
									Flag_Point2 = False
								else:
									transmit_Arduino(Command[3]) #x
									time.sleep(time_sleep)			
									if(degree >= 0 and degree <= 180):
										transmit_Arduino(Command[2]) #d
									elif(degree >= -180 and degree <= 0):
										transmit_Arduino(Command[1]) #a								
									Flag_Point1 = False
									Flag_Point2 = True	
									Tmp_LowerLimit = LowerLimit
									Tmp_UpperLimit = UpperLimit
									
							elif(Flag_Point2 == True):	
								if (degree >= Tmp_LowerLimit or degree <= Tmp_UpperLimit):
									transmit_Arduino(Command[3]) #x
									time.sleep(time_sleep)
									transmit_Arduino(Command[0]) #w
									Flag_Mode = 3
									Rotation_Count = 0
									Rotation_Degree_Count = 0	
									Flag_Path = True	
									Flag_Point2 = False
								else: # 175 -175
									Rotation_Count += 1						
									if(Rotation_Count == Rotation_Count_Limit):
										Tmp_LowerLimit -= 5
										Tmp_UpperLimit += 5
										Rotation_Degree_Count += 1
										Rotation_Count = 0
										if(Rotation_Degree_Count == Rotation_Degree_limit):
											transmit_Arduino(Command[3]) #x
											Rotation_Degree_Count = 0	
											break
										
									elif(degree >= LowerLimit - 50 and degree < LowerLimit):
										transmit_Arduino(Command[2]) #d
									elif(degree > UpperLimit and degree <= UpperLimit + 50):				
										transmit_Arduino(Command[1]) #a
										
			elif(Flag_Mode == 3 and ID_NUM in NUM_List):
				#路徑偏移	
				if(ID_NUM == Aim):
					if(Direction == 1 and Y >= -PointRangeLimit): #-90
						Flag_Mode = 1
						#transmit_Arduino(Command[3]) #x
					elif(Direction == 2 and Y <= PointRangeLimit): #90
						Flag_Mode = 1
						#transmit_Arduino(Command[3]) #x
					elif(Direction == 3 and X >= -PointRangeLimit): #0
						Flag_Mode = 1
						#transmit_Arduino(Command[3]) #x
					elif(Direction == 4 and X <= PointRangeLimit): #180
						Flag_Mode = 1
						#transmit_Arduino(Command[3]) #x
						
				elif(ID_NUM != Aim):				 
					if(Flag_Path == True):
						if(Direction == 1 or Direction == 2):
							if(X > LineLimit):
								print('1')
								transmit_Arduino(Command[3]) #x
								time.sleep(time_sleep)
								if(Direction == 1):
									if(degree >= 0 and degree <= 180):
										transmit_Arduino(Command[1]) #a
									elif(degree >= -180 and degree <= 0):
										transmit_Arduino(Command[2]) #d
								elif(Direction == 2):
									if(degree >= 0 and degree <= 180):
										transmit_Arduino(Command[2]) #d
									elif(degree >= -180 and degree <= 0):
										transmit_Arduino(Command[1]) #a
								Tmp_LowerLimit = Degree_LowerLimit[3]
								Tmp_UpperLimit = Degree_UpperLimit[3]	
								Flag_Path = False
								Flag_Path3 = True
								Flag_Path_Mode = 1
											
							elif(X < -LineLimit):
								print('2')
								transmit_Arduino(Command[3]) #x
								time.sleep(time_sleep)
								if(Direction == 1):
									if(degree >= 0 and degree <= 180):
										transmit_Arduino(Command[2]) #d
									elif(degree >= -180 and degree <= 0):
										transmit_Arduino(Command[1]) #a	
								elif(Direction == 2):
									if(degree >= 0 and degree <= 180):
										transmit_Arduino(Command[1]) #a
									elif(degree >= -180 and degree <= 0):
										transmit_Arduino(Command[2]) #d
								Tmp_LowerLimit = Degree_LowerLimit[2]
								Tmp_UpperLimit = Degree_UpperLimit[2]
								Flag_Path = False
								Flag_Path3 = True
								Flag_Path_Mode = 2
								
							elif(X >= -LineLimit and X <= LineLimit):
								#-90(Upper: -85, Lower: -95) 90(Upper:95, Lower:85)
								if(degree > UpperLimit + 2 and degree <= UpperLimit + 30): 
									transmit_Arduino(Command[3]) #x
									time.sleep(time_sleep)
									transmit_Arduino(Command[1]) #a
									Flag_Path = False
									Flag_Path2 = True
								elif(degree < LowerLimit - 2 and degree >= LowerLimit - 30):
									transmit_Arduino(Command[3]) #x
									time.sleep(time_sleep)
									transmit_Arduino(Command[2]) #d
									Flag_Path = False
									Flag_Path2 = True
								Tmp_LowerLimit = LowerLimit
								Tmp_UpperLimit = UpperLimit	
								
						elif(Direction == 3 or Direction == 4):
							if(Y > LineLimit):
								print('3')
								transmit_Arduino(Command[3]) #x
								time.sleep(time_sleep)
								if(Direction == 3):
									if(degree >= 0 and degree <= 90 or degree >= -90 and degree <= 0):
										transmit_Arduino(Command[2]) #d
									elif(degree >= 90 and degree <= 180 or degree >= -180 and degree <= -90):
										transmit_Arduino(Command[1]) #a
								elif(Direction == 4):
									if(degree >= 0 and degree <= 90 or degree >= -90 and degree <= 0):
										transmit_Arduino(Command[1]) #a
									elif(degree >= 90 and degree <= 180 or degree >= -180 and degree <= -90):
										transmit_Arduino(Command[2]) #d		
								Tmp_LowerLimit = Degree_LowerLimit[0]
								Tmp_UpperLimit = Degree_UpperLimit[0]
								Flag_Path = False
								Flag_Path3 = True
								Flag_Path_Mode = 1
									
							elif(Y < -LineLimit):
								print('4')
								transmit_Arduino(Command[3]) #x
								time.sleep(time_sleep)
								if(Direction == 3):
									if(degree >= 0 and degree <= 90 or degree >= -90 and degree <= 0):
										transmit_Arduino(Command[1]) #d
									elif(degree >= 90 and degree <= 180 or degree >= -180 and degree <= -90):
										transmit_Arduino(Command[2]) #a
								elif(Direction == 4):
									if(degree >= 0 and degree <= 90 or degree >= -90 and degree <= 0):
										transmit_Arduino(Command[2]) #a
									elif(degree >= 90 and degree <= 180 or degree >= -180 and degree <= -90):
										transmit_Arduino(Command[1]) #d	
								Tmp_LowerLimit = Degree_LowerLimit[1]
								Tmp_UpperLimit = Degree_UpperLimit[1]
								Flag_Path = False
								Flag_Path3 = True
								Flag_Path_Mode = 2
								
							elif(Y >= -LineLimit and Y <= LineLimit):
								#0(Upper:5, Lower:-5) 180(Upper:-175, Lower:175)
								if(degree > UpperLimit + 2 and degree <= UpperLimit + 30):
									transmit_Arduino(Command[3]) #x
									time.sleep(time_sleep)
									transmit_Arduino(Command[1]) #a
									Flag_Path = False
									Flag_Path2 = True
								elif(degree < LowerLimit - 2 and degree >= LowerLimit -30):
									transmit_Arduino(Command[3]) #x
									time.sleep(time_sleep)
									transmit_Arduino(Command[2]) #d
									Flag_Path = False
									Flag_Path2 = True
								Tmp_LowerLimit = LowerLimit
								Tmp_UpperLimit = UpperLimit
									
					elif(Flag_Path2 == True):
						if(Direction == 1 or Direction == 2 or Direction == 3):
							if(degree >= Tmp_LowerLimit and degree <= Tmp_UpperLimit):
								transmit_Arduino(Command[3]) #x
								time.sleep(time_sleep)
								transmit_Arduino(Command[0]) #w
								Rotation_Count = 0
								Rotation_Degree_Count = 0
								Flag_Path = True
								Flag_Path2 = False								
							else:
								Rotation_Count += 1						
								if(Rotation_Count == Rotation_Count_Limit):
									Tmp_LowerLimit -= 5
									Tmp_UpperLimit += 5
									Rotation_Degree_Count += 1
									Rotation_Count = 0
									if(Rotation_Degree_Count == Rotation_Degree_limit):
										transmit_Arduino(Command[3]) #x
										Rotation_Degree_Count = 0	
										break									
						elif(Direction == 4): 
							if(degree >= Tmp_LowerLimit or degree <= Tmp_UpperLimit):
								transmit_Arduino(Command[3]) #x
								time.sleep(time_sleep)
								transmit_Arduino(Command[0]) #w
								Rotation_Count = 0
								Flag_Path = True
								Flag_Path2 = False
							else:
								Rotation_Count += 1						
								if(Rotation_Count == Rotation_Count_Limit):
									Tmp_LowerLimit -= 5
									Tmp_UpperLimit += 5
									Rotation_Degree_Count += 1
									Rotation_Count = 0
									if(Rotation_Degree_Count == Rotation_Degree_limit):
										transmit_Arduino(Command[3]) #x
										Rotation_Degree_Count = 0	
										break
										
					elif(Flag_Path3 == True):
						if(Direction == 1 or Direction == 2 or Direction == 3):
							if(degree >= Tmp_LowerLimit and degree <= Tmp_UpperLimit):
								transmit_Arduino(Command[3]) #x
								time.sleep(time_sleep)
								transmit_Arduino(Command[0]) #w
								Rotation_Count = 0
								Rotation_Degree_Count = 0
								Flag_Path3 = False	
								Flag_Path4 = True															
							else:
								Rotation_Count += 1						
								if(Rotation_Count == Rotation_Count_Limit):
									Tmp_LowerLimit -= 5
									Tmp_UpperLimit += 5
									Rotation_Degree_Count += 1
									Rotation_Count = 0
									if(Rotation_Degree_Count == Rotation_Degree_limit):
										transmit_Arduino(Command[3]) #x
										Rotation_Degree_Count = 0	
										break									
						elif(Direction == 4): 
							if(degree >= Tmp_LowerLimit or degree <= Tmp_UpperLimit):
								transmit_Arduino(Command[3]) #x
								time.sleep(time_sleep)
								transmit_Arduino(Command[0]) #w
								Rotation_Count = 0
								Flag_Path3 = False	
								Flag_Path4 = True		
							else:
								Rotation_Count += 1						
								if(Rotation_Count == Rotation_Count_Limit):
									Tmp_LowerLimit -= 5
									Tmp_UpperLimit += 5
									Rotation_Degree_Count += 1
									Rotation_Count = 0
									if(Rotation_Degree_Count == Rotation_Degree_limit):
										transmit_Arduino(Command[3]) #x
										Rotation_Degree_Count = 0	
										break					
										
					elif(Flag_Path4 == True):
						if(Direction == 1 or Direction == 2):
							if(X >= -LineLimit and X <= LineLimit):
								if(Flag_Path_Mode == 1):
									transmit_Arduino(Command[3]) #x
									time.sleep(time_sleep)
									transmit_Arduino(Command[1]) #a
									Flag_Path4 = False
									Flag_Path5 = True
								elif(Flag_Path_Mode == 2):
									transmit_Arduino(Command[3]) #x
									time.sleep(time_sleep)
									transmit_Arduino(Command[2]) #d
									Flag_Path4 = False
									Flag_Path5 = True
						elif(Direction == 3 or Direction == 4):
							if(Y >= -LineLimit and Y <= LineLimit):
								if(Flag_Path_Mode == 1):
									transmit_Arduino(Command[3]) #x
									time.sleep(time_sleep)
									transmit_Arduino(Command[1]) #a
									Flag_Path4 = False
									Flag_Path5 = True
								elif(Flag_Path_Mode == 2):
									transmit_Arduino(Command[3]) #x
									time.sleep(time_sleep)
									transmit_Arduino(Command[2]) #d
									Flag_Path4 = False
									Flag_Path5 = True	
						Tmp_LowerLimit = LowerLimit
						Tmp_UpperLimit = UpperLimit
						
					elif(Flag_Path5 == True):
						if(Direction == 4):
							if(degree >= Tmp_LowerLimit or degree <= Tmp_UpperLimit):
								transmit_Arduino(Command[3]) #x
								time.sleep(time_sleep)
								transmit_Arduino(Command[0]) #w
								Rotation_Count = 0
								Rotation_Degree_Count = 0
								Flag_Path = True
								Flag_Path5 = False
							else:
								Rotation_Count += 1						
								if(Rotation_Count == Rotation_Count_Limit):
									Tmp_LowerLimit -= 5
									Tmp_UpperLimit += 5
									Rotation_Degree_Count += 1
									Rotation_Count = 0
									if(Rotation_Degree_Count == Rotation_Degree_limit):
										transmit_Arduino(Command[3]) #x
										Rotation_Degree_Count = 0	
										break			
						else:
							if(degree >= Tmp_LowerLimit and degree <= Tmp_UpperLimit):
								transmit_Arduino(Command[3]) #x
								time.sleep(time_sleep)
								transmit_Arduino(Command[0]) #w
								Rotation_Count = 0
								Rotation_Degree_Count = 0
								Flag_Path = True
								Flag_Path5 = False
							else:
								Rotation_Count += 1						
								if(Rotation_Count == Rotation_Count_Limit):
									Tmp_LowerLimit -= 5
									Tmp_UpperLimit += 5
									Rotation_Degree_Count += 1
									Rotation_Count = 0
									if(Rotation_Degree_Count == Rotation_Degree_limit):
										transmit_Arduino(Command[3]) #x
										Rotation_Degree_Count = 0	
										break			
			flag = False		


if __name__ == '__main__':		
	Moving(Target)