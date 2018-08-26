#!/bin/bash
set -e

echo "Starting SSH ..."
service ssh start

/code/run.py
