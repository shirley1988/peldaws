#!/bin/bash
set -e

echo "Starting SSH ..."
service ssh start

/code/run.py >> /code/server.log 2>&1
