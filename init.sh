#!/bin/bash
set -x
set -e

echo "Starting SSH ..."
service ssh start

echo "Starting PELDA"
/code/run.py 2>&1 | tee -a /code/server.log
