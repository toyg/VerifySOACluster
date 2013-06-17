rem SET VARIABLES
set SCRIPT_HOME=%~dp0
set SCRIPT=%SCRIPT_HOME%\scripts\verifyTargets.py
set PROPS_FILE=%SCRIPT_HOME%\verifyTargets.properties
FOR /F "tokens=1* delims==" %%P IN (%PROPS_FILE%) DO (set %%P=%%Q)

rem add necessary java classes
SET CLASSPATH=%CLASSPATH%;%MW_HOME%\oracle_common\modules;%MW_HOME%\oracle_common\modules\oracle.xdk_11.1.0

set RUN_COMMAND=%MW_HOME%\oracle_common\common\bin\wlst.cmd
set RUN_ARGS=-loadProperties %PROPS_FILE% %SCRIPT%

%RUN_COMMAND% %RUN_ARGS%
