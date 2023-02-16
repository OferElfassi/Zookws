#!/bin/bash

if id | grep -qv uid=0; then
  echo "Must be root"
  exit 1
fi

JAIL="/var/okws/run"
ZOOBAR="/var/okws/run/zoobar"
MEDIA="/var/okws/run/zoobar/media"
TEMPLATES="/var/okws/run/zoobar/templates"
DB="/var/okws/run/zoobar/db"
AUTH_PATH="/var/okws/run/authsvc"
VENV_PATH="/var/okws/run/venv"

SHARED_ID=1000
declare -A ZOOKD=( ["uid"]=500 ["gid"]=500)
declare -A ZOOKHTTP=( ["uid"]=600 ["gid"]=600)
declare -A AUTHSVC=( ["uid"]=700 ["gid"]=700)
declare -A BANKSVC=( ["uid"]=800 ["gid"]=700)

# Create JAIL if not exists
if [ ! -d "$JAIL" ]; then
  printf "Creating JAIL \n"
  mkdir -p "$JAIL"
fi

cp "requirements.txt" "$JAIL/requirements.txt"
cp "index.html" "$JAIL/index.html"
cp "favicon.ico" "$JAIL/favicon.ico"

# Executables list
files=(zookd zookhttp)

# Database tables list
db_tables=(person transfer)

# copy Executables
printf "copy executables \n"
for file in "${files[@]}"; do
  rm -f "$JAIL/$file"
  cp "$file" "$JAIL/$file"
done

printf "copy user env \n"
mkdir -p "$JAIL/usr/bin"
cp "/usr/bin/env" "$JAIL/usr/bin/env"

# copy zoobar folder
printf "copy zoobar folder \n"
rm -rf "$JAIL/zoobar"
cp -r "zoobar" "$JAIL"

# create db tables if not exists
for table in "${db_tables[@]}"; do
  if [ ! -d "$ZOOBAR/db/$table" ]; then
    printf "create db table  \n" $table
    python "$ZOOBAR/zoodb.py" "init-$table"
  fi
done

# Copy system dependencies
printf "copy system dependencies \n"
# Copy system dependencies
for file in *; do
  if [ -x "$file" ] && [ ! -d "$file" ]; then
    # Get the dependencies of the executable
    while read -r line; do
      # Extract the path of the dependency
      path=$(echo "$line" | awk '/\/.* / { print  }')
      if [ -n "$path" ]; then
         substring=${path#*/}
         result=${substring%% *}
         if [ ! -f "$JAIL/$result" ]; then
            # Create the parent directories if they don't exist
            parent_dir=$(dirname "$JAIL/${result#/}")
            mkdir -p "$parent_dir"
            # Copy the file
            cp --archive --preserve=links,mode "/$result" "$JAIL/$result"
#            cp "/$result" "$JAIL/$result"
            echo " "
         fi
      fi
    done < <(ldd "$file" 2>/dev/null)
  fi
done


printf "set permissions and ownerships \n"

chmod 775 "$DB" && chown 0:600 "$DB"
chmod -R 660 "$DB/person" && chown -R 0:600 "$DB/person" && chmod 750 "$DB/person"
chmod -R 660 "$DB/transfer" && chown -R 0:600 "$DB/transfer"  && chmod 750 "$DB/transfer"
chmod -R 660 "$MEDIA" && chown -R 0:600 "$MEDIA" && chmod 750 "$MEDIA"
chmod -R 660 "$TEMPLATES" && chown -R 0:600 "$TEMPLATES" && chmod 750 "$TEMPLATES"
find "$ZOOBAR" -maxdepth 1 -name "*.py" -exec chown 0:600 {} \; -exec chmod 774 {} \;
find "$ZOOBAR" -maxdepth 1 -name "*.cgi" -exec chown 600:600 {} \; -exec chmod 774 {} \;



if [ -d "$ZOOBAR/__pycache__" ]; then
  printf "remove __pycache__ \n"
  rm -rf "$ZOOBAR/__pycache__"
fi

if [ ! -d "$VENV_PATH" ]; then
  printf "Creating virtualenv \n"
  virtualenv -p="/usr/bin/python3" "$VENV_PATH"
  source "$VENV_PATH/bin/activate"
  x-terminal-emulator -e "bash -c 'cd $JAIL/; pip install -r requirements.txt $@; read'"
fi


echo "FINISHED"

exit 0