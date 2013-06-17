rem SET VARIABLES
set SCRIPT_HOME=%~dp0
set SCRIPT=%SCRIPT_HOME%\scripts\verifyTargets.py
set PROPS_FILE=%SCRIPT_HOME%\verifyTargets.properties
FOR /F "tokens=1* delims==" %%P IN (%PROPS_FILE%) DO (set %%P=%%Q)

set RUN_COMMAND=%MW_HOME%\oracle_common\common\bin\wlst.cmd
set RUN_ARGS=-loadProperties %PROPS_FILE% %SCRIPT%

%RUN_COMMAND% %RUN_ARGS%
