#!/bin/bash

PROJECT_DIR="/home/kali/CLionProjects/Zookws"

# assert root
if id | grep -qv uid=0; then
  echo "Must be root"
  exit 1
fi
# Folders
JAIL="/var/okws/run"
ZOOBAR="$JAIL/zoobar"
MEDIA="$ZOOBAR/media"
TEMPLATES="$ZOOBAR/templates"
DB="$ZOOBAR/db"
AUTH_SVC="$JAIL/authsvc"
# Files to copy
files=(zookd zookhttp index.html zookd-exstack zookhttp-exstack favicon.ico)
# Database tables
db_tables=(person transfer)
# Services
svcs=(authsvc)

# Create JAIL if not exists
if [ ! -d "$JAIL" ]; then
  printf "[1/16] Creating JAIL \n"
  mkdir -p "$JAIL"
else
  printf "[1/16] JAIL already exists \n"
fi

# create services
printf "[2/16] create services \n"
for svc in "${svcs[@]}"; do
  rm -f "$JAIL/$svc"
  mkdir -p "$JAIL/$svc"
done

# copy files
printf "[3/16] copy files \n"
for file in "${files[@]}"; do
  rm -f "$JAIL/$file"
  cp "$PROJECT_DIR/$file" "$JAIL/$file"
done

# copy zoobar folder
printf "[4/16] copy zoobar folder \n"
rm -rf "$JAIL/zoobar"
cp -r "$PROJECT_DIR/zoobar" "$JAIL"

# create db tables
printf "[5/16] create db tables - "
for table in "${db_tables[@]}"; do
    printf " $table,"
    python "$ZOOBAR/zoodb.py" "init-$table"
    chmod -R  775 "$DB/$table"
done
printf "\n"

# Copy system dependencies
if [ ! -d "$JAIL/usr/bin" ]; then
  printf "[6/16] copying /usr/bin \n"
  mkdir -p "$JAIL/usr/bin"
  cp "/usr/bin/env" "$JAIL/usr/bin/env"
  cp "/usr/bin/openssl" "$JAIL/usr/bin/openssl"
  cp --archive --preserve=links,mode "/usr/bin/python3.10" "$JAIL/usr/bin/python3.10"
  cp --archive --preserve=links,mode "/usr/bin/python3" "$JAIL/usr/bin/python3"
  #cp "/usr/bin/zsh" "$JAIL/usr/bin/zsh"
else
  printf "[6/16] /usr/bin already exists \n"
fi

if [ ! -d "$JAIL/usr/lib/x86_64-linux-gnu" ]; then
  printf "[7/16] copying /usr/lib/x86_64-linux-gnu \n"
  mkdir -p  "$JAIL/usr/lib/x86_64-linux-gnu"
  cp --archive --preserve=links,mode "/usr/lib/x86_64-linux-gnu/libsqlite3.so.0" "$JAIL/usr/lib/x86_64-linux-gnu/libsqlite3.so.0"
else
  printf "[7/16] /usr/lib/x86_64-linux-gnu already exists \n"
fi

# Copy python 3.10 dependencies
if [ ! -d "$JAIL/usr/lib/python3.10" ]; then
  printf "[8/16] copying /usr/lib/python3.10 \n"
  cp -r "/usr/lib/python3.10" "$JAIL/usr/lib"
else
  printf "[8/16] /usr/lib/python3.10 already exists \n"
fi

# Copy python 3.10 usr/local/lib dependencies
if [ ! -d "$JAIL/usr/local/lib/python3.10" ]; then
  printf "[9/16] copying /usr/local/lib/python3.10 \n"
  mkdir -p "$JAIL/usr/local/lib"
  cp -r "/usr/local/lib/python3.10" "$JAIL/usr/local/lib"
else
  printf "[9/16] /usr/local/lib/python3.10 already exists \n"
fi

# Copy python 3 dependencies
if [ ! -d "$JAIL/usr/lib/python3" ]; then
  printf "[10/16] copying /usr/lib/python3 \n"
  cp -r "/usr/lib/python3" "$JAIL/usr/lib"
else
  printf "[10/16] /usr/lib/python3 already exists \n"
fi

# Copy list of python dependencies
if [ ! -e "$JAIL/requirements.txt" ]; then
  printf "[11/16] copying requirements.txt \n"
  cp "requirements.txt" "$JAIL/requirements.txt"
else
  printf "[11/16] requirements.txt already exists \n"
fi

# Check if dependencies have changed
deps_diff=$(diff "requirements.txt" "$JAIL/requirements.txt")
if [ ! -z "$deps_diff" ]; then
  printf "[12/16] dependencies have changed \n"
  cp -r "/usr/local/lib/python3.10" "$JAIL/usr/local/lib"
  cp -r "/usr/lib/python3.10" "$JAIL/usr/lib"
  cp -r "/usr/lib/python3" "$JAIL/usr/lib"
  cp "requirements.txt" "$JAIL/requirements.txt"
else
  printf "[12/16] dependencies have not changed \n"
fi

if [ ! -d "$JAIL/lib64" ]; then
  printf "[13/16] copying /lib64 \n"
  mkdir -p "$JAIL/lib64"
  cp --archive --preserve=links,mode "/lib64/ld-linux-x86-64.so.2" "$JAIL/lib64/ld-linux-x86-64.so.2"
else
  printf "[13/16] /lib64 already exists \n"
fi

if [ ! -d "$JAIL/lib/x86_64-linux-gnu" ]; then
  printf "[14/16] copying /lib/x86_64-linux-gnu \n"
  mkdir -p "$JAIL/lib/x86_64-linux-gnu"
  cp -r --archive --preserve=links,mode "/lib/x86_64-linux-gnu" "$JAIL/lib"
else
  printf "[14/16] /lib/x86_64-linux-gnu already exists \n"
fi

if [ ! -d "$JAIL/etc" ]; then
  printf "[15/16] copying /etc \n"
  mkdir -p "$JAIL/etc"
  cp --archive --preserve=links,mode "/etc/ld.so.cache" "$JAIL/etc/ld.so.cache"
  cp --archive --preserve=links,mode "/etc/localtime" "$JAIL/etc/localtime"
else
  printf "[15/16] /etc already exists \n"
fi

printf "[16/16] set permissions and ownerships \n"
chmod 777 "$JAIL/authsvc"
chmod 777 "$JAIL/zookd"
chmod 777 "$JAIL/zookhttp"

#chmod 775 "$DB" && chown 0:600 "$DB"s
#chmod a+rwx "$AUTH_PATH"
#chmod -R 660 "$DB/person" && chown -R 0:600 "$DB/person" && chmod 750 "$DB/person"
#chmod -R 660 "$DB/transfer" && chown -R 0:600 "$DB/transfer"  && chmod 750 "$DB/transfer"
#chmod -R 660 "$DB/cred" && chown -R 700:700 "$DB/cred"  && chmod 750 "$DB/cred"
#chmod -R 660 "$MEDIA" && chown -R 0:600 "$MEDIA" && chmod 750 "$MEDIA"
#chmod -R 660 "$TEMPLATES" && chown -R 0:600 "$TEMPLATES" && chmod 750 "$TEMPLATES"
#find "$ZOOBAR" -maxdepth 1 -name "*.py" -exec chown 0:0 {} \; -exec chmod 774 {} \;
#find "$ZOOBAR" -maxdepth 1 -name "*.cgi" -exec chown 0:600 {} \; -exec chmod 774 {} \;



echo "FINISHED"

exit 0