#!/bin/bash
#if [ "$UID" -eq 0 ]; then
#    echo "Updating jail files"
#    /bin/sh -c "./setup.sh; echo \$?"
#fi
pgrep process_name1 process_name2 process_name3 | xargs kill
current_dir=$(pwd)
echo "Activating virtual environment"
source /var/okws/run/venv/bin/activate
echo "Running zookld in a new terminal"
x-terminal-emulator -e "bash -c 'cd $current_dir/; sudo ./zookld 8080 $@; read'"
kill $(pgrep zookld) $(pgrep zookd) $(pgrep zookhttp)
