# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2021 Shuay Liu

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
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Metrohm Autolab wrapper
=======================
Full-featured wrapper for Metrohm Autolab potentiostat.

Merges v0.0.4 features (Ei direct control, loadData, CMDLOG) with
v0.1.0 generic command/parameter API and data output reading.

Compatible with pythonnet (clr) + EcoChemie.Autolab.Sdk.
Author: Shuay Liu
"""
from __future__ import print_function
import sys
import time
from math import log10, floor
import clr
import os


# =====================================================================
# Logging utility (from v0.0.4)
# =====================================================================
def CMDLOG(is_log, content, intent='\n'):
    if is_log:
        sys.stdout.write("%s[%s] %s" % (intent, time.asctime(), content))


def appendSuffixToFilename(filename, suffix):
    if not len(filename) == 0:
        dotAt = filename.rfind('.')
        baseName = filename[0:dotAt]
        extName = filename[dotAt:]
        return baseName + suffix + extName
    else:
        return filename


class AUTOLAB(object):
    """
    Full-featured wrapper for Metrohm Autolab potentiostat.
    """

    # =====================================================================
    # Common command keys (from Autolab SDK manual Appendix 6.1)
    # =====================================================================
    CMD_CV_STAIRCASE = "FHCyclicVoltammetry2"
    CMD_LSV_STAIRCASE = "FHLinearSweep"
    CMD_CV_LINEAR_SCAN = "CVLinearScanAdc164"
    CMD_CV_LINEAR_SCAN_HS = "CVLinearScanAdcHs"
    CMD_CV_GALVANOSTATIC = "FHCyclicVoltammetryGalvanostatic"
    CMD_LSV_GALVANOSTATIC = "FHLinearSweepGalvanostatic"
    CMD_RECORD_SIGNALS = "FHLevel"
    CMD_CHRONO_METHODS = "RecordLevelsContainer"
    CMD_CHRONO_HS = "HighSpeedLevelsContainer"
    CMD_CHRONO_HS_GALVANOSTATIC = "HighSpeedLevelsContainer"
    CMD_FRA_SCAN = "FIAScan"
    CMD_CORROSION_FIT = "CorrosionRateFitCommand"
    CMD_CORROSION_TAFEL = "CorrosionRateTafelSlopeCommand"
    CMD_SG_SMOOTH = "MathSmoothSavitzkyGolay"
    CMD_PEAK_SEARCH = "PeakSearchCommand"
    CMD_NESTED_PROCEDURE = "ExecCommandSequence"
    CMD_CALCULATE_SIGNAL = "MathParser"
    CMD_WINDOWER = "SignalWindowerCommand"

    # =====================================================================
    # Common CV parameter keys (from Appendix 6.2)
    # =====================================================================
    PARAM_START_VALUE = "Start value"
    PARAM_UPPER_VERTEX = "Upper vertex"
    PARAM_LOWER_VERTEX = "Lower vertex"
    PARAM_STEP = "Step"
    PARAM_INTERVAL_TIME = "Interval time"
    PARAM_NR_OF_STOP_CROSSINGS = "NrOfStopCrossings"
    PARAM_STOP_VALUE = "Stop value"
    PARAM_SCAN_RATE = "Scanrate"

    # =====================================================================
    # Common CV output parameter keys (from Appendix 6.3)
    # =====================================================================
    OUTPUT_POTENTIAL = "EI_0.CalcPotential"
    OUTPUT_CURRENT = "EI_0.CalcCurrent"
    OUTPUT_TIME = "CalcTime"
    OUTPUT_SETPOINT_APPLIED = "SetpointApplied"

    # =====================================================================
    # Constructor
    # =====================================================================
    def __init__(self, sdk=R"C:\Program Files\Metrohm Autolab\autolabsdk\EcoChemie.Autolab.Sdk",
                 adx=R"C:\Program Files\Metrohm Autolab\autolabsdk\Hardware Setup Files\Adk.x"):
        self.autolab = None
        self.pcd = None
        self.CMD = True  # v0.0.4 logging flag
        self.setSDKandADX(sdk, adx)

    def __del__(self):
        if self.autolab is None:
            return
        elif self.autolab.AutolabConnection.IsConnected:
            self.autolab.Disconnect()

    def setSDKandADX(self, sdk, adx):
        self.Adx = adx
        self.sdk = sdk
        if clr.FindAssembly(self.sdk):
            clr.AddReference(self.sdk)
            from EcoChemie.Autolab.Sdk import Instrument
            self.autolab = Instrument()
        else:
            print("[ERROR] Cannot find %s.dll" % self.sdk)
            print("[ERROR] Reload function setSDKandADX(sdk, adx) with necessary files")

    # =====================================================================
    # Connection
    # =====================================================================
    def connectToAutolab(self,
                         hdw=R"C:\Program Files\Metrohm Autolab\autolabsdk\Hardware Setup Files\PGSTAT302N\HardwareSetup.FRA32M.xml"):
        self.autolab.AutolabConnection.EmbeddedExeFileToStart = self.Adx
        self.autolab.set_HardwareSetupFile(hdw)
        try:
            self.autolab.Connect()
        except Exception as e:
            print("[ERROR] Configuration file is not valid?")
            print("This might also result from previously unreleased link by other software")
            print(str(e))
            self.disconnectAutolab()
        return self.autolab.AutolabConnection.IsConnected

    def disconnectAutolab(self):
        try:
            if self.autolab and self.autolab.AutolabConnection.IsConnected:
                self.autolab.Disconnect()
        except Exception as e:
            print("[ERROR] Cannot unlink AUTOLAB, this might be caused by unusual shutdown of AUTOLAB.")
            print("\n-----------------------\n Try to restart AUTOLAB manually \n-----------------------")
        self.autolab = None
        self.pcd = None

    def Disconnect(self):
        """Alias for backward compatibility."""
        self.disconnectAutolab()

    def isConnected(self):
        return self.autolab is not None and self.autolab.AutolabConnection.IsConnected

    # =====================================================================
    # Procedure / Measurement
    # =====================================================================
    def loadProcedure(self, procedure):
        """Load a .nox procedure file."""
        self.pcd = self.autolab.LoadProcedure(procedure)
        return self.pcd

    def measure(self, procedure=None):
        """Load and measure a procedure. If already loaded, just measure."""
        if procedure is not None:
            self.loadProcedure(procedure)
        if not self.isConnected():
            print("[ERROR] Autolab not connected. Cannot measure.")
            return False
        if self.pcd is None:
            print("[ERROR] No procedure loaded. Cannot measure.")
            return False
        try:
            CMDLOG(self.CMD, "[INFO] Trying to start measuring...\n\t%s\n\r" % str(procedure))
            self.pcd.Measure()
            if self.CMD:
                CMDLOG(self.CMD, "[INFO] Measurement started successfully.\n", '\t')
                start = time.clock()
                while self.pcd.IsMeasuring:
                    time.sleep(0.08)
                    CMDLOG(self.CMD, "[INFO] Still measuring... using %.1f s." % (time.clock() - start), '\r\t')
                CMDLOG(self.CMD, "[INFO] Measurement finished!", '\n\t')
        except Exception as e:
            print("[ERROR] Measure failed: %s" % str(e))
            self.disconnectAutolab()
            return False
        return True

    def save(self):
        """Save with auto-generated timestamp suffix."""
        if self.pcd is None:
            print("[ERROR] No procedure loaded.")
            return
        self.saveAs(self.pcd.get_FileName())

    def saveAs(self, saveName):
        if not len(saveName) == 0:
            saveto = appendSuffixToFilename(saveName, time.strftime("_%Y%m%d-%H%M%S"))
            CMDLOG(self.CMD, "[INFO] Save file to %s\n\n" % saveto)
            self.pcd.SaveAs(saveto)
        else:
            print("[WARNING] You should give me a NAME to save this file.")
            print("Otherwise, please use save() instead of saveAs()")

    def isMeasuring(self):
        if self.pcd is None:
            return False
        return self.pcd.IsMeasuring

    # =====================================================================
    # High-level EC control (direct Ei access, from v0.0.4)
    # =====================================================================
    def setCellOn(self, On=True):
        """Turn cell on/off via direct Ei control."""
        self.autolab.Ei.set_CellOnOff(On)
        while self.autolab.Ei.get_CurrentOverload():
            self.autolab.Ei.set_CurrentRange(self.autolab.Ei.CurrentRange + 1)

    def setMode(self, Mode='Potentialstatic'):
        """Set workstation mode: 'Potentialstatic' or 'Galvanostatic'."""
        if 'Galvanostatic' == Mode:
            self.autolab.Ei.set_Mode(1)
        elif 'Potentialstatic' == Mode:
            self.autolab.Ei.set_Mode(0)
        else:
            CMDLOG(self.CMD, "Wrong workstation mode. Options: Potentialstatic/Galvanostatic. Using Potentialstatic as default.")
            self.autolab.Ei.set_Mode(0)

    def setPotential(self, potential):
        """Set cell potential (V) via direct Ei control."""
        self.setMode('Potentialstatic')
        self.autolab.Ei.set_Setpoint(potential)
        if self.autolab.Ei.get_CurrentOverload():
            self.autolab.Ei.set_CurrentRange(self.autolab.Ei.Current + 1)
        return self.autolab.Ei.PotentialApplied

    def setCurrentRange(self, EstimateCurrentInAmpere=1e-6):
        """Set current range based on estimated current (A)."""
        currentLevel = floor(log10(EstimateCurrentInAmpere))
        self.autolab.Ei.set_CurrentRange(currentLevel)
        return self.autolab.Ei.CurrentRange

    def setQuietTime(self, seconds):
        """Set quiet time before measurement (s)."""
        if self.pcd is None:
            return
        try:
            self.pcd.set_QuietTime(float(seconds))
        except AttributeError:
            pass

    def wait(self, QuietTime=5):
        """Blocking wait (s)."""
        time.sleep(QuietTime)

    # =====================================================================
    # Data loading from saved .nox files (from v0.0.4)
    # =====================================================================
    @staticmethod
    def _as_list(value):
        """Convert .NET array or scalar to Python list."""
        if value is None:
            return []
        try:
            return list(value)
        except TypeError:
            return [value]

    def loadData(self, filename):
        """
        Load data from a saved .nox file.

        Returns list of rows depending on procedure type:
        - CV: [[SetpointApplied, EI_0.CalcCurrent, CalcTime, ScanNumber], ...]
        - EIS: [[Frequency, Zreal, Zimaginary, Zmodulus, -Phase], ...]
        """
        Data = None
        try:
            pcd = self.autolab.LoadProcedure(filename)
            if pcd.Commands.ContainsId('FHCyclicVoltammetry2'):
                CMDLOG(self.CMD, "It is a CV procedure DATA!\n")
                cmd = pcd.Commands['FHCyclicVoltammetry2']
                sig = cmd.Signals

                setpoint = self._as_list(sig.get_Item('SetpointApplied').ValueAsObject)
                current = self._as_list(sig.get_Item('EI_0.CalcCurrent').ValueAsObject)
                calc_time = self._as_list(sig.get_Item('CalcTime').ValueAsObject)
                scan_num = self._as_list(sig.get_Item('ScanNumber').ValueAsObject)

                # Transpose: zip turns columns into rows
                Data = [list(row) for row in zip(setpoint, current, calc_time, scan_num)]
                CMDLOG(self.CMD, "The file format is: SetpointApplied EI_0.CalcCurrent CalcTime ScanNumber\n")

            elif pcd.Commands.ContainsId('PlotsNyquist') and pcd.Commands.ContainsId('PlotsBodeModulus'):
                CMDLOG(self.CMD, "It is an EIS procedure DATA!\n")
                cmd1 = pcd.Commands['PlotsNyquist']
                cmd2 = pcd.Commands['PlotsBodeModulus']

                freq = self._as_list(cmd1.CommandParameters['Z'].ValueAsObject)
                zr = self._as_list(cmd1.CommandParameters['X'].ValueAsObject)
                zi = self._as_list(cmd1.CommandParameters['Y'].ValueAsObject)
                zmod = self._as_list(cmd2.CommandParameters['Y'].ValueAsObject)
                phase = self._as_list(cmd2.CommandParameters['Z'].ValueAsObject)

                Data = [list(row) for row in zip(freq, zr, zi, zmod, phase)]
                CMDLOG(self.CMD, "The file format is: Frequency Zreal Zimaginary Zmodulus -Phase\n")

        except Exception as e:
            print(repr(e))
        finally:
            if Data is None:
                raise Exception('LoadFailedException', Data)
            else:
                return Data

    # =====================================================================
    # Low-level Command / Parameter access (generic API, NEW in v0.1.0)
    # =====================================================================
    def getCommand(self, commandKey):
        """Get a Command from the loaded procedure by its key name."""
        if self.pcd is None:
            print("[ERROR] No procedure loaded.")
            return None
        try:
            return self.pcd.get_Command(commandKey)
        except Exception as e:
            print("[ERROR] getCommand failed: %s" % str(e))
            return None

    def getParameter(self, commandKey, paramKey):
        """Get a CommandParameter by command key and parameter key."""
        cmd = self.getCommand(commandKey)
        if cmd is None:
            return None
        try:
            return cmd.get_Parameter(paramKey)
        except Exception as e:
            print("[ERROR] getParameter failed: %s" % str(e))
            return None

    def setParameterDouble(self, commandKey, paramKey, value):
        from EcoChemie.Autolab.Sdk import CommandParameterDouble
        param = self.getParameter(commandKey, paramKey)
        if param is None:
            return False
        try:
            cp = CommandParameterDouble(param)
            cp.set_Value(float(value))
            return True
        except Exception as e:
            print("[ERROR] setParameterDouble failed: %s" % str(e))
            return False

    def setParameterDoubleList(self, commandKey, paramKey, values):
        from EcoChemie.Autolab.Sdk import CommandParameterDoubleList
        param = self.getParameter(commandKey, paramKey)
        if param is None:
            return False
        try:
            cp = CommandParameterDoubleList(param)
            cp.set_Value([float(v) for v in values])
            return True
        except Exception as e:
            print("[ERROR] setParameterDoubleList failed: %s" % str(e))
            return False

    def setParameterInt(self, commandKey, paramKey, value):
        from EcoChemie.Autolab.Sdk import CommandParameterInt
        param = self.getParameter(commandKey, paramKey)
        if param is None:
            return False
        try:
            cp = CommandParameterInt(param)
            cp.set_Value(int(value))
            return True
        except Exception as e:
            print("[ERROR] setParameterInt failed: %s" % str(e))
            return False

    def setParameterBool(self, commandKey, paramKey, value):
        from EcoChemie.Autolab.Sdk import CommandParameterBool
        param = self.getParameter(commandKey, paramKey)
        if param is None:
            return False
        try:
            cp = CommandParameterBool(param)
            cp.set_Value(bool(value))
            return True
        except Exception as e:
            print("[ERROR] setParameterBool failed: %s" % str(e))
            return False

    def getParameterDouble(self, commandKey, paramKey):
        from EcoChemie.Autolab.Sdk import CommandParameterDouble
        param = self.getParameter(commandKey, paramKey)
        if param is None:
            return None
        try:
            cp = CommandParameterDouble(param)
            return cp.get_Value()
        except Exception as e:
            print("[ERROR] getParameterDouble failed: %s" % str(e))
            return None

    def getParameterDoubleList(self, commandKey, paramKey):
        from EcoChemie.Autolab.Sdk import CommandParameterDoubleList
        param = self.getParameter(commandKey, paramKey)
        if param is None:
            return None
        try:
            cp = CommandParameterDoubleList(param)
            return list(cp.get_Value())
        except Exception as e:
            print("[ERROR] getParameterDoubleList failed: %s" % str(e))
            return None

    def getParameterInt(self, commandKey, paramKey):
        from EcoChemie.Autolab.Sdk import CommandParameterInt
        param = self.getParameter(commandKey, paramKey)
        if param is None:
            return None
        try:
            cp = CommandParameterInt(param)
            return cp.get_Value()
        except Exception as e:
            print("[ERROR] getParameterInt failed: %s" % str(e))
            return None

    def getParameterBool(self, commandKey, paramKey):
        from EcoChemie.Autolab.Sdk import CommandParameterBool
        param = self.getParameter(commandKey, paramKey)
        if param is None:
            return None
        try:
            cp = CommandParameterBool(param)
            return cp.get_Value()
        except Exception as e:
            print("[ERROR] getParameterBool failed: %s" % str(e))
            return None

    # =====================================================================
    # Convenience: CV parameter setters
    # =====================================================================
    def setCVStartValue(self, value):
        self.setParameterDouble(self.CMD_CV_STAIRCASE, self.PARAM_START_VALUE, value)

    def setCVUpperVertex(self, value):
        self.setParameterDouble(self.CMD_CV_STAIRCASE, self.PARAM_UPPER_VERTEX, value)

    def setCVLowerVertex(self, value):
        self.setParameterDouble(self.CMD_CV_STAIRCASE, self.PARAM_LOWER_VERTEX, value)

    def setCVStep(self, value):
        self.setParameterDouble(self.CMD_CV_STAIRCASE, self.PARAM_STEP, value)

    def setCVIntervalTime(self, value):
        self.setParameterDouble(self.CMD_CV_STAIRCASE, self.PARAM_INTERVAL_TIME, value)

    def setCVScanRate(self, value):
        self.setParameterDouble(self.CMD_CV_STAIRCASE, self.PARAM_SCAN_RATE, value)

    # =====================================================================
    # Data output reading (measured values, NEW in v0.1.0)
    # =====================================================================
    def getOutputDouble(self, commandKey, outputKey):
        from EcoChemie.Autolab.Sdk import CommandParameterDouble
        cmd = self.getCommand(commandKey)
        if cmd is None:
            return None
        try:
            param = cmd.get_Parameter(outputKey)
            cp = CommandParameterDouble(param)
            return cp.get_Value()
        except Exception as e:
            print("[ERROR] getOutputDouble failed: %s" % str(e))
            return None

    def getOutputDoubleList(self, commandKey, outputKey):
        from EcoChemie.Autolab.Sdk import CommandParameterDoubleList
        cmd = self.getCommand(commandKey)
        if cmd is None:
            return None
        try:
            param = cmd.get_Parameter(outputKey)
            cp = CommandParameterDoubleList(param)
            return list(cp.get_Value())
        except Exception as e:
            print("[ERROR] getOutputDoubleList failed: %s" % str(e))
            return None

    def getMeasuredPotential(self):
        return self.getOutputDoubleList(self.CMD_CV_STAIRCASE, self.OUTPUT_POTENTIAL)

    def getMeasuredCurrent(self):
        return self.getOutputDoubleList(self.CMD_CV_STAIRCASE, self.OUTPUT_CURRENT)

    def getMeasuredTime(self):
        return self.getOutputDoubleList(self.CMD_CV_STAIRCASE, self.OUTPUT_TIME)
