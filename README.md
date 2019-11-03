# TTU_Robot_Move
 大同大學_產學合作_大同機器人(行走部分)
1. 所需設備
	1. TX2 or Raspberry Pi
	2. Stargazer室內定位感測器
	3. Arduino + 馬達(機器人行走組件)
2. 程式功能
    1. 到達LandMark時回歸中心點
	2. 透過Dijkstra演算法找出下個LandMark的方向
	3. 行走過程中做角度偏移修正以及路徑偏移修正
3. 各程式功用
	1. readVoice.py:經過語音問答後，將目標點透過Uart方式傳給行走程式
	2. Robot1001.py:獲得目標點後，就不斷執行(2. 程式功能)三項功能，直到到達目標為止
	3. Dijkstra..py:將獲得的目標點與目前所在座標，進行路經規劃，並列出途中的每一個座標點與行走方向的角度
	