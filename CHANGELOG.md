# Changelog

All notable changes to `pymetrohmautolab` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-23

### Added

#### Generic Command / Parameter API
- `getCommand(commandKey)` — retrieve any `Command` object from a loaded procedure by its key name
- `getParameter(commandKey, paramKey)` — retrieve any `CommandParameter` object
- `setParameterDouble(commandKey, paramKey, value)` — set double-type parameters
- `setParameterDoubleList(commandKey, paramKey, values)` — set double-list-type parameters
- `setParameterInt(commandKey, paramKey, value)` — set int-type parameters
- `setParameterBool(commandKey, paramKey, value)` — set bool-type parameters
- `getParameterDouble(commandKey, paramKey)` — get double-type parameter value
- `getParameterDoubleList(commandKey, paramKey)` — get double-list-type parameter value
- `getParameterInt(commandKey, paramKey)` — get int-type parameter value
- `getParameterBool(commandKey, paramKey)` — get bool-type parameter value

#### Data Output Reading
- `getOutputDouble(commandKey, outputKey)` — read output double values from measured procedures
- `getOutputDoubleList(commandKey, outputKey)` — read output double-list values (e.g., time series)
- `getMeasuredPotential()` — convenience wrapper to read potential from CV staircase
- `getMeasuredCurrent()` — convenience wrapper to read current from CV staircase
- `getMeasuredTime()` — convenience wrapper to read time from CV staircase

#### CV Convenience Methods
- `setCVStartValue(value)` — set CV start potential
- `setCVUpperVertex(value)` — set CV upper vertex potential
- `setCVLowerVertex(value)` — set CV lower vertex potential
- `setCVStep(value)` — set CV step potential
- `setCVIntervalTime(value)` — set CV interval time
- `setCVScanRate(value)` — set CV scan rate

#### Command & Parameter Key Constants
- `CMD_CV_STAIRCASE`, `CMD_LSV_STAIRCASE`, `CMD_FRA_SCAN`, `CMD_RECORD_SIGNALS`, etc.
- `PARAM_START_VALUE`, `PARAM_UPPER_VERTEX`, `PARAM_SCAN_RATE`, etc.
- `OUTPUT_POTENTIAL`, `OUTPUT_CURRENT`, `OUTPUT_TIME`, etc.

#### Connection & State
- `isConnected()` — explicit connection state check
- `loadProcedure(path)` — separate loading from measurement for multi-step workflows
- `setQuietTime(seconds)` — set quiet time before measurement

### Changed
- `measure()` now supports real-time progress logging with `CMD` flag and `time.clock()`
- `saveAs()` handles filenames without extension correctly
- `disconnectAutolab()` now properly nulls `self.autolab` and `self.pcd` to prevent stale references
- `__del__` now calls `disconnectAutolab()` for safer cleanup
- Default SDK paths updated to match common Metrohm Autolab SDK installation locations
- `setSDKandADX()` now imports `Instrument` and sets `self.autolab` immediately (matching v0.0.4 behavior)
- `measure()` now accepts `procedure=None` (useful when procedure already loaded)
- `setCurrentRange()` now uses `log10` estimation with current overload protection

### Fixed
- `disconnectAutolab()` no longer throws if called twice or when connection was never established
- `saveAs()` crash on filenames without extension
- `measure()` now returns `False` on failure instead of `None`
- `setCellOn()` now includes current overload protection loop
- `setPotential()` now correctly calls `setMode('Potentialstatic')` first and handles overload

### Preserved from v0.0.4
- `CMDLOG(is_log, content, intent)` — global logging utility
- `CMD` flag — instance-level logging toggle
- `setMode('Potentialstatic'/'Galvanostatic')` — direct `autolab.Ei` mode control
- `setCellOn(On)` — direct `autolab.Ei.set_CellOnOff()` with overload protection
- `setPotential(potential)` — direct `autolab.Ei.set_Setpoint()` with mode switch and overload
- `setCurrentRange(EstimateCurrentInAmpere)` — `log10`-based current range estimation
- `loadData(filename)` — extract CV / EIS data from saved `.nox` files into numpy arrays
- `appendSuffixToFilename(filename, suffix)` — utility for timestamped filenames

## [0.0.4] - 2022-01-07

### Added
- Initial release
- `AUTOLAB` class with basic connection, measurement, and EC control
- `connectToAutolab(hdw)`, `disconnectAutolab()`, `measure(procedure)`, `saveAs(name)`
- `setPotential(potential)`, `setCurrentRange(current_range)`, `setCellOn(on)`, `setMode(mode)`
- `wait(seconds)`, `isMeasuring()`
- `loadData(filename)` — CV and EIS data extraction from saved `.nox` files
- `CMDLOG(is_log, content, intent)` — logging utility
- `appendSuffixToFilename(filename, suffix)` — filename utility
- `numpy` dependency for data extraction
