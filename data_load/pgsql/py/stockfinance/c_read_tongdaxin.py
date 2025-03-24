#通达信自动启动下载盘后数据和财务数据
# -*- coding: utf-8 -*-
import subprocess,pyautogui
from time import sleep

pyautogui.PAUSE=1
pyautogui.FAILSAFE=True
k=input('下载完自动关机(默认否，关机_1):')
cc=str(pyautogui.size().width)+'*'+str(pyautogui.size().height)
print(cc)
tdxpt={'buzou':['0免费','1确定','2系统','3盘后数据','4选择日期','5下载','6关闭','7系统','8专业数据','9财务数据','10股票数据','11关闭'],
          '1440*900':[(858,488),(1000,520),(38,10),(90,260),(420,320),(900,626),(1000,626),(38,10),(90,282),(680,600),(1050,600),(1050,646)],
          '1920*1080':[(1100,568),(1200,600),(38,10),(90,242),(703,414),(1120,700),(1200,700),(38,10),(100,263),(930,670),(1240,670),(1244,716)],
          '1366*768':[(820,420),(925,450),(38,10),(85,240),(425,265),(850,548),(928,548),(38,10),(90,260),(664,520),(977,520),(968,564)]}
jc={'buzou':['0下载盘后数据关闭前','1财务数据包前while','2财务数据包前if','3股票数据包前while','4股票数据包前if'],
       '1440*900':[[1005,625,128], [464,600,240],[697,597,128],[832,600,240],[1061,597,128]],
       '1920*1080':[[1205,700,128],[748,674,240],[940,673,128],[1063,674,240],[1253,674,128]],
    '1366*768':[[928,549,128], [471,523,240],[664,522,128],[786,523,240],[976,522,128]]}
try:
    try:
        subprocess.Popen(r'D:\new_tdx\TdxW.exe')  # hp
    except:
        subprocess.Popen(r'E:\Program Files (x86)\new_tdx\TdxW.exe')  # aoc
    
    sleep(3)
    pyautogui.click(tdxpt[cc][0],button='left') #免费
    sleep(0.25)
    pyautogui.click(tdxpt[cc][1]) #确定
    sleep(8)
##下载盘后数据
    pyautogui.click(tdxpt[cc][2]) #系统
    sleep(0.25)
    pyautogui.click(tdxpt[cc][3]) #盘后数据下载
    sleep(0.25)
    pyautogui.click(tdxpt[cc][4]) #选择日期范围
    sleep(0.25)
    pyautogui.click(tdxpt[cc][5]) #开始下载
    sleep(0.25)  # 下面关闭为灰色，等待
    while pyautogui.pixelMatchesColor(jc[cc][0][0],jc[cc][0][1],(jc[cc][0][2],jc[cc][0][2],jc[cc][0][2])): sleep(3)
    pyautogui.click(tdxpt[cc][6]) #关闭
    sleep(0.25)
##下载专业财务数据
    pyautogui.click(tdxpt[cc][7]) #系统
    sleep(0.25)
    pyautogui.click(tdxpt[cc][8]) #专业数据下载
    sleep(8)  #下面没冒号等待，下载为灰色跳出
    while pyautogui.pixelMatchesColor(jc[cc][1][0],jc[cc][1][1],(jc[cc][1][2],jc[cc][1][2],jc[cc][1][2])):
        if pyautogui.pixelMatchesColor(jc[cc][2][0],jc[cc][2][1],(jc[cc][2][2],jc[cc][2][2],jc[cc][2][2])): break
        sleep(3)
    pyautogui.click(tdxpt[cc][9]) #财务数据包
    sleep(0.25)  #下面没冒号等待，下载为灰色跳出
    while pyautogui.pixelMatchesColor(jc[cc][3][0],jc[cc][3][1],(jc[cc][3][2],jc[cc][3][2],jc[cc][3][2])):
        if pyautogui.pixelMatchesColor(jc[cc][4][0],jc[cc][4][1],(jc[cc][4][2],jc[cc][4][2],jc[cc][4][2])):break
        sleep(3)
    pyautogui.click(tdxpt[cc][10]) #股票数据包
    sleep(0.25)
    while pyautogui.pixelMatchesColor(jc[cc][4][0],jc[cc][4][1],(jc[cc][4][2],jc[cc][4][2],jc[cc][4][2])): sleep(3)
    pyautogui.click(tdxpt[cc][11]) #关闭
    print('_____OK_____')
    if k=='1':subprocess.Popen(r'shutdown.exe /s /t 30')  #30秒关机
except:
    print('X 错误：核查 TDX 所在目录')


