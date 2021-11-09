<!--
 * @Author: Jonah Liu
 * @Date: 2021-09-15 18:25:11
 * @LastEditTime: 2021-11-09 10:02:30
 * @LastEditors: Jonah Liu
 * @Description: 
-->
# Metrohm AUTOLAB control package

This is a **unofficial** control package to Metrohm-AUTOALB. 
This package contains a main pacakge named ```AUTOALB()```

## class structure and implemented functions:
```python
class AUTOLAB():
    
    def __init__(self,
                 sdk=R"C:\Program Files\Metrohm Autolab\autolabsdk\EcoChemie.Autolab.Sdk",
                 adx=R"C:\Program Files\Metrohm Autolab\autolabsdk\Hardware Setup Files\Adk.x"):
 
    def disconnectAutolab(self):
    def setSDKandADX(self,sdk,adx):
 
    def isMeasuring(self):
    def connectToAutolab(self,
                         hdw=R"C:\Program Files\Metrohm Autolab\autolabsdk\Hardware Setup Files\PGSTAT302N\HardwareSetup.FRA32M.xml"):
    def measure(self,procedure):
    def save(self):
    def saveAs(self,saveName):
        
    def setCellOn(self,On=True):
    def setMode(self,Mode='Potentialstatic'):   
    def setPotential(self,potential):   
    def setCurrentRange(self,EstimateCurrentInAmpere = 1E-6):
    def wait(self,QuietTime=5):

```


## how to use it:
- Step 0,
  install the requirement softerware,

    ```bash
    pip install pythonnet
    pip install pyMetrohmAUTOLAB
    ```
  
    And AUTOALB SDK v1.11 
    You can download it [here](https://www.metrohm-autolab.com/Products/Echem/Software/SDK)
- Step 1, import this package

    ```python
    import Metrohm.AUTOLAB as EC
    ```

- Step 2, tell Python where your instrument located

    ```python
    # tell the codes where your SDK install first
    hdw=R'C:\Program Files\Metrohm Autolab\autolabsdk\Hardware Setup Files\PGSTAT302N\HardwareSetup.FRA32M.xml',
    sdk=R"C:\Program Files\Metrohm Autolab\autolabsdk\EcoChemie.Autolab.Sdk"
    adx=R"C:\Program Files\Metrohm Autolab\autolabsdk\Hardware Setup Files\Adk.x"
    ```

- Setp 3, initialise the AUTOLAB class(C's bad habbit)

    ```python
    # initializing the class first
    autolab = EC.AUTOLAB(sdk=sdk,adx=adx)

    autolab.CMD = True # optional: Enable CMDLOG or not, it's good if you want to trace the code
    ```

- Step 4, Have fun with it

    ```python
    try:
        if autolab.connectToAutolab(hdw): # first we need to connect to our instrument
            print("Connecting to AUTOLAB successfully....")
            # do measurement
            autolab.measure(R"*.nox file path") # it will take times till measrement finish
            autolab.saveAs(R"save file name")
            `
    except:
        print("Connecting to AUTOLAB FAIL....")
        return
    ```

- *Optional* Step 5, delete the instance

    It is a good habit, but not always necessary.

    ```python
    # it is a good habit to del the instance after script
    del autolab
    ```

