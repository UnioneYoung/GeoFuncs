#!/usr/bin/env python
# coding: utf-8

"""==========================================================
用来解析NDK格式的天然地震数据中的震源机制解数据，并根据需要导出可直接用
    于GMT绘制震源机制解的文件
输入：(<NDKfileName>,<needOut>)
    NDKfileName(String)：需要用来解析的DNK格式文件的路径，类型为String
    needOut(Boolean):True则输出可直接用于GMT绘制震源机制解的文件，
        位置为当前文件夹，文件名为"GMTinput_CMT_Smdz.txt"
返回：包含所有事件Dictionary的List
=============================================================
Dictionary中的Key：
    catalog
    data
    time
    lantitude
    longitude
    depth
    index
    CMTname
    Mrr,Mtt,Mpp,Mrp,Mtp,Mrp:六个地震矩张量分量的系数
    power:地震矩张量每个分量的指数，
        即实际矩张量为 系数e指数，e.g. Mrr=7.8，power=24，则实际矩张量为7.8e24
    MxxStdErr:各个矩张量分量的标准误差
    newLantitude/Longitude:
============================================================="""
def analyzeNDK(NDKfileName,needOut):
    outputFileName='GMTinput_CMT_Smdz.txt'
    eventsList=[]
    singleEvent={}
    inputFile=open(NDKfileName)#打开目标文件
    lines=inputFile.readlines()
    numOfLines=len(lines)
    if numOfLines%5==0:
        numOfEvents=int(numOfLines/5)
        print("读到"+str(numOfLines)+"行，"+str(numOfEvents)+"个事件\n正在解析数据...")
    else:
        print("文件格式不正确：行数不正确!")
        return eventsList
    for index in range(numOfLines):
        if (index%5)==0:
            thisLine=lines[index].split()
            singleEvent['catalog']=thisLine[0]
            singleEvent['date']=thisLine[1]
            singleEvent['time']=thisLine[2]
            singleEvent['lantitude']=thisLine[3]
            singleEvent['longitude']=thisLine[4]
            singleEvent['depth']=thisLine[5]
            singleEvent['index']=thisLine[6]
        elif (index%5)==1:
            thisLine=lines[index].split()
            singleEvent['CMTname']=thisLine[0]
        elif (index%5)==3:
            thisLine=lines[index].split()
            singleEvent['power']=thisLine[0]
            singleEvent['Mrr']=thisLine[1]
            singleEvent['MrrStdErr']=thisLine[2]
            singleEvent['Mtt']=thisLine[3]
            singleEvent['MttStdErr']=thisLine[4]
            singleEvent['Mpp']=thisLine[5]
            singleEvent['MppStdErr']=thisLine[6]
            singleEvent['Mrt']=thisLine[7]
            singleEvent['MrtStdErr']=thisLine[8]
            singleEvent['Mrp']=thisLine[9]
            singleEvent['MrpStdErr']=thisLine[10]
            singleEvent['Mtp']=thisLine[11]
            singleEvent['MtpStdErr']=thisLine[12]
        elif (index%5)==4:
            
            #每个事件的最后一行完成录入后需要针对整个事件的dictionary做如下操作
            #这些操作是eventList共有的：
            singleEvent['newLantitude']="X"#默认不改变位置
            singleEvent['newLongitude']="Y"#默认不改变位置
            singleEvent['dateForm']="%Y/%m/%d"#日期格式
            singleEvent['timeForm']="%H:%M:%S"#时间格式
            eventsList.append(singleEvent)#将dictionary添加到List中
            singleEvent={}#初始化dictionary
    inputFile.close()
    #删除相同的事件
    deletedItem=DictionaryListDeleteRepeat(eventsList,
                                        ['date','time','lantitude','longitude','depth'],['CMTname'])
    print("删除了"+str(deletedItem)+"个相同事件，输出"+str(numOfEvents-deletedItem)+"个事件")
    
    #输出
    if needOut is True:
        print("正在写文件...")
        outputFile=open(outputFileName,'w')
        for singleEvent in eventsList:
            outputFile.write(singleEvent['longitude']+" "+singleEvent['lantitude']+" "+
                singleEvent['depth']+" "+singleEvent['Mrr']+" "+singleEvent['Mtt']
                +" "+singleEvent['Mpp']+" "+singleEvent['Mrt']+" "+singleEvent['Mrp']
                +" "+singleEvent['Mtp']+" "+singleEvent['power']+" "+singleEvent['newLantitude']
                +" "+singleEvent['newLongitude']+"\n")
        outputFile.close()
    else:
        print("不需要写文件")
        
    print("NDK解析完成！")
    return eventsList



"""=============================================================================
用来写可以直接输入CMT进行计算的txt文件
输入：
    dictionaryList(List):为包含需要输出数据的dictionaryList
    outputFileName(String):为输出文件路径
    itemList(List):为需要依次输出的数据的名称
============================================================================="""
def writeCMTinputTxt(dictionaryList,outputFileName,itemList):
    outputFile=open(outputFileName,'w')
    index=0
    for singleEvent in dictionaryList:
        for item in itemList:
            index+=1
            outputFile.write(singleEvent[item])
            if(index<len(itemList)):
                outputFile.write(" ")
            else:
                outputFile.write("\n")
        index=0

        #outputFile.write(singleEvent['longitude']+" "+singleEvent['lantitude']+" "+singleEvent['depth']+" "+singleEvent['Mrr']+" "+singleEvent['Mtt']+" "+singleEvent['Mpp']+" "+singleEvent['Mrt']+" "+singleEvent['Mrp']+" "+singleEvent['Mtp']+" "+singleEvent['power']+" "+singleEvent['newLantitude']+" "+singleEvent['newLongitude']+"\n")
        #outputFile.write(singleEvent['CMTname']+" "+singleEvent['longitude']+" "+singleEvent['lantitude']+" "+singleEvent['depth']+" "+singleEvent['Mrr']+" "+singleEvent['Mtt']+" "+singleEvent['Mpp']+" "+singleEvent['Mrt']+" "+singleEvent['Mrp']+" "+singleEvent['Mtp']+" "+singleEvent['power']+" "+singleEvent['newLantitude']+" "+singleEvent['newLongitude']+"\n")
    outputFile.close()




"""==========================================================
用来将距离太近而导致重叠的元素通过设置newX和newY参数来分开
输入：(<eventList>,<mapSize>,<latitudeSection>,<componentSize>)
    eventList(List):
    mapSize(String):
    lantitudeSection(float):
    componentSize(String):
返回：修改了坐标的元素个数
=============================================================
gap:组件半径对应的地理距离，两个事件对应的地理距离小于gap则需要转换坐标
============================================================="""
def operateNewXY(eventsList,mapSize,latiduteSection,componentSize):
    changedNumber=0
    if len(eventsList)<2:
        print("函数'operateNewXY'没有进行运算:eventsList至少需要2个事件才能运算")
        return changedNumber
    else:
        gap=6371*(lengthUnitTo_p(componentSize)*float(latiduteSection)/lengthUnitTo_p(mapSize))/2
        for i in range(len(eventsList)):
            for j in range(i):
                #地理距离小于gap（km）则需要转换新坐标
                if getGeoDistance(eventsList[i]['longitude'],eventsList[i]['lantitude'],
                                  eventsList[j]['longitude'],eventsList[j]['lantitude'])<=gap:
                    #
                    print("+1")
                    #


"""===========================================================================================================

==========================================================================================================="""

def lengthUnitTo_p(len_str):#将non p单位转换为p
    if len_str[-1]=="i":
        return float(len_str[:-1])*72
    elif len_str[-1]=="c":
        return float(len_str[:-1])*(72/2.54)
    elif len_str[-1]=="p":
        return float(len_str[:-1])
    else:
        print("长度格式有误")
        return 0.0






def getSectionByDate(eventList, start, form_start, isEqOK_start, end, form_end, isEqOK_end):
    import datetime
    isBiggerLeft=False#满足左限
    isBiggerRight=False#满足右限
    outputList=[]
    for singleEvent in eventList:
        try: 
            if isEqOK_start:
                if datetime.datetime.strptime(singleEvent['date'],singleEvent['dateForm'])>=datetime.datetime.strptime(start,form_start):
                    if isEqOK_end:
                        if datetime.datetime.strptime(singleEvent['date'],singleEvent['dateForm'])<=datetime.datetime.strptime(end,form_end):
                            outputList.append(singleEvent)
                    else:
                        if datetime.datetime.strptime(singleEvent['date'],singleEvent['dateForm'])<datetime.datetime.strptime(end,form_end):
                            outputList.append(singleEvent)
            else:
                if datetime.datetime.strptime(singleEvent['date'],singleEvent['dateForm'])>datetime.datetime.strptime(start,form_start):
                    if isEqOK_end:
                        if datetime.datetime.strptime(singleEvent['date'],singleEvent['dateForm'])<=datetime.datetime.strptime(end,form_end):
                            outputList.append(singleEvent)
                    else:
                        if datetime.datetime.strptime(singleEvent['date'],singleEvent['dateForm'])<datetime.datetime.strptime(end,form_end):
                            outputList.append(singleEvent)
        except:
            pass    
    print("Date:"+start+" to "+end+" has "+str(len(outputList))+"item(s)")
    return outputList
    





def getGeoDistance(lng1,lat1,lng2,lat2):
    import math
    lng1, lat1, lng2, lat2 = map(math.radians, [float(lng1), float(lat1), float(lng2), float(lat2)]) # 经纬度转换成弧度
    dlon=lng2-lng1
    dlat=lat2-lat1
    a=math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2 
    distance=2*math.asin(math.sqrt(a))*6371*1000 # 地球平均半径，6371km
    distance=round(distance/1000,3)
    return distance





def DictionaryListDeleteRepeat(dictionaryList, keyList_all, keyList_exist):
    flg=0
    deletFlg=len(keyList_all)
    deletList=[]
    if len(dictionaryList)<2:
        print("函数'DictionaryListDeleteRepeat'没有进行运算:dictionaryList至少需要2个事件才能运算")
        return deletedItem
    for i in range(len(dictionaryList)):
        for j in range(i):
            for item2 in keyList_exist:
                if dictionaryList[i][item2]==dictionaryList[j][item2]:
                    deletList.append(i)
            for item1 in keyList_all:
                if dictionaryList[i][item1]==dictionaryList[j][item1]:
                    flg=flg+1
                else:
                    break
            if flg==deletFlg:
                deletList.append(i)
            flg=0
    for k in range(len(deletList)):
        del(dictionaryList[deletList[k]-k])
    return len(deletList)





def changeCMTname(uncheckList):
    for item in uncheckList:
        name=item['CMTname']
        if(len(name)>=13):
            if name[0]=='C':
                item['CMTname']=name[1:]
    return uncheckList


