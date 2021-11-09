# -*- coding:utf-8 -*-
'''
Author: Jonah Liu
Date: 2021-08-20 09:50:46
LastEditTime: 2021-11-09 09:58:26
LastEditors: Jonah Liu
Description: AUTOLAB control need pythonnet and AUTOALB SDK 1.1 first
'''


'''
MIT License

Copyright (c) 2021 Jonah Liu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''


import sys
import time
from math import log10,floor
import clr

def CMDLOG(ISLOG,CONTENT,INTENT='\n'):
    if ISLOG:
        sys.stdout.write("%s[%s] %s"%(INTENT,time.asctime(),CONTENT))
    else:
        pass


def appendSuffixToFilename(filename,suffix):
    if not len(filename) == 0:
        dotAt = filename.rfind('.')
        baseName = filename[0:dotAt]
        extName = filename[dotAt:]
        return baseName+suffix+extName
    else:
        return filename

class AUTOLAB():
    
    def __init__(self,sdk=R"C:\Program Files\Metrohm Autolab\autolabsdk\EcoChemie.Autolab.Sdk",
                 adx=R"C:\Program Files\Metrohm Autolab\autolabsdk\Hardware Setup Files\Adk.x"):
        self.setSDKandADX(sdk,adx)
        self.autolab = None

    def __del__(self):
        if self.autolab == None:
            return
        elif self.autolab.AutolabConnection.IsConnected:
            self.autolab.Disconnect()
    
    def disconnectAutolab(self):
        try:
            self.autolab.Disconnect()
        except:
            print("[ERROR] Cannot unlinke AUTOLAB, this might caused by unusual shut down of AUTOLAB.")
            print("\n-----------------------\n Try to restart AUTOALB manually \n-----------------------")
    
    def setSDKandADX(self,sdk,adx):
        self.Adx = adx
        self.sdk = sdk
        
        if clr.FindAssembly(self.sdk):
            clr.AddReference(self.sdk)
        else:
            print("[ERROR] Cannot find %s.dll"%self.sdk)
            print("[ERROR] Reload function setSDKandADX(adk,adx) with necessary files")
    
    def isMeasuring(self):
        return self.pcd.IsMeasuring
 
    def connectToAutolab(self,
                         hdw=R"C:\Program Files\Metrohm Autolab\autolabsdk\Hardware Setup Files\PGSTAT302N\HardwareSetup.FRA32M.xml"):
        # please ensure that has firstly call self.setSDKandADX()
        from EcoChemie.Autolab.Sdk import Instrument
        self.autolab = Instrument()
        self.autolab.AutolabConnection.EmbeddedExeFileToStart = self.Adx
        self.autolab.set_HardwareSetupFile(hdw)
        try:
            self.autolab.Connect()
        except:
            print("[ERROR] Configuration file is not valid? \n This might also results from previously unreleased link by other software")
            self.disconnectAutolab()
        return self.autolab.AutolabConnection.IsConnected
        
    def measure(self,procedure):
#        start = time.clock()
        self.pcd = self.autolab.LoadProcedure(procedure)
        
        if self.autolab.AutolabConnection.IsConnected:
            try:
                CMDLOG(self.CMD,"[INFO] Trying to start measuring file \n\t%s....\n\r"%procedure)

                self.pcd.Measure()

                # CMDLOG
                if self.CMD:
                    CMDLOG(self.CMD,"[INFO] Measurement Start Successfully.\n",'\t')
                    start = time.clock()
                    while(self.pcd.IsMeasuring):
                        time.sleep(0.08) # to prevent fake death 80 ms
                        CMDLOG(self.CMD,"[INFO] Still measuring... using %.1f s."%(time.clock()-start),'\r\t')
                    
                    CMDLOG(self.CMD,"[INFO] Measurement Finished!",'\n\t')
            except:
                self.disconnectAutolab()
        else:
            try:
                self.connectToAutolab(self.autolab.get_HardwareSetupFile())
                self.measure(procedure)
            except:
                print("[ERROR] We must descipt our equipment(such as PGSTAT302N\HardwareSetup.FRA32M.xml) first.\n find it in SDK folder")   
    
    def save(self):
        self.saveAs(self.pcd.get_FileName())
    
    def saveAs(self,saveName):
        if not len(saveName) == 0:
            saveto = appendSuffixToFilename(saveName,time.strftime("_%Y%m%d-%H%M%S"))
            CMDLOG(self.CMD,"[INFO] Save File to %s\n\n"%saveto)
            self.pcd.SaveAs(saveto)
        else:
            print("[WARNING]You should give me a NAME to save this file.\n otherwise, please use save() instead of saveAs()")

    def setCellOn(self,On=True):
        self.autolab.Ei.set_CellOnOff(On)
        while self.autolab.Ei.get_CurrentOverload() :
            self.autolab.Ei.set_CurrentRange(self.autolab.Ei.CurrentRange + 1)
    
    def setMode(self,Mode='Potentialstatic'):
        if 'Galvanostatic' == Mode:
            self.autolab.Ei.set_Mode(1)#Ei.EIMode.Galvanostatic=0
        elif 'Potentialstatic' == Mode:
            self.autolab.Ei.set_Mode(0)#Ei.EIMode.Potentiostatic=1
        else:
            CMDLOG(self.CMD,"Wrong workstation mode, Options: Potentialstatic/Galvanostatic, PotentialStatic for default.")
            self.autolab.Ei.set_Mode(0)#Potentialstatic for default
    
    def setPotential(self,potential):
        self.setMode('Potentialstatic')
        self.autolab.Ei.set_Setpoint(potential)
        if self.autolab.Ei.get_CurrentOverload() :
            self.autolab.Ei.set_CurrentRange(self.autolab.Ei.Current + 1)
            
        return self.autolab.Ei.PotentialApplied
    
    def setCurrentRange(self,EstimateCurrentInAmpere = 1E-6):
        currentLevel = floor(log10(EstimateCurrentInAmpere))
        self.autolab.Ei.set_CurrentRange(currentLevel)
        
        return self.autolab.Ei.CurrentRange
        
    def wait(self,QuietTime=5):
        time.sleep(QuietTime)
    #TODO:
    # def EIS(self,EISProc=R"E:\LSh\PicoView 1.14\scripts\STEP0-FRA.nox"):
    #     self.measure(EISProc)
            
'''
                                                    __----~~~~~~~~~~~------___
                                   .  .   ~~//====......          __--~ ~~
                   -.            \_|//     |||\\  ~~~~~~::::... /~
                ___-==_       _-~o~  \/    |||  \\            _/~~-
        __---~~~.==~||\=_    -_--~/_-~|-   |\\   \\        _/~
    _-~~     .=~    |  \\-_    '-~7  /-   /  ||    \      /
  .~       .~       |   \\ -_    /  /-   /   ||      \   /
 /  ____  /         |     \\ ~-_/  /|- _/   .||       \ /
 |~~    ~~|--~~~~--_ \     ~==-/   | \~--===~~        .\
          '         ~-|      /|    |-~\~~       __--~~
                      |-~~-_/ |    |   ~\_   _-~            /\
                           /  \     \__   \/~                \__
                       _--~ _/ | .-~~____--~-/                  ~~==.
                      ((->/~   '.|||' -_|    ~~-/ ,              . _||
                                 -_     ~\      ~~---l__i__i__i--~~_/
                                 _-~-__   ~)  \--______________--~~
                               //.-~~~-~_--~- |-------~~~~~~~~
                                      //.-~~~--\
                      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

                              神兽保佑            永无BUG
'''
     