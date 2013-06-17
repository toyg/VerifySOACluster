#!/bin/sh
# SET VARIABLES
SCRIPT_HOME=`dirname $0`
SCRIPT=${SCRIPT_HOME}/scripts/verifyTargets.py
PROPS_FILE=${SCRIPT_HOME}/verifyTargets.properties
. ${PROPS_FILE}

SET CLASSPATH=%CLASSPATH%:%MW_HOME%/oracle_common/modules:%MW_HOME%/oracle_common/modules/oracle.xdk_11.1.0

RUN_COMMAND=${MW_HOME}/oracle_common/common/bin/wlst.sh
RUN_ARGS="-loadProperties ${PROPS_FILE} ${SCRIPT}"

${RUN_COMMAND} ${RUN_ARGS}

