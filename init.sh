#!/bin/bash
set -x
set -e

echo "Fixing Python Requests"
ReqDir=$(pip show requests | grep Location | awk '{print $NF}')
echo "Requests path: ${ReqDir}"
/bin/sed -i 's/self.verify = verify/self.verify = False/' ${ReqDir}/requests/sessions.py

echo "Starting SSH ..."
service ssh start

echo "Starting PELDA"
/code/run.py 2>&1 | tee -a /code/server.log
