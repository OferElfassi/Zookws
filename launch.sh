#!/bin/bash

PROJECT_DIR="/home/kali/CLionProjects/Zookws"

port=${1:-8080}
full_setup=${2:-0}

# assert root
if id | grep -qv uid=0; then
  echo "Must be root"
  exit 1
fi

# kill zookld if running
echo "Killing zookld"
sudo kill -9 $(pgrep zookld)
wait $!


if [ $full_setup = 1 ]; then
  # Clean up
  echo "Cleaning up"
  make clean -C "$PROJECT_DIR"
  wait $!
  # Build
  echo "Building"
  make -C "$PROJECT_DIR"
  wait $!
  # setup JAIL
  echo "Setting up JAIL"
  "$PROJECT_DIR"/setup.sh
  wait $!
fi

# launch
echo "Launching on port $port"
"$PROJECT_DIR"/zookld $port

