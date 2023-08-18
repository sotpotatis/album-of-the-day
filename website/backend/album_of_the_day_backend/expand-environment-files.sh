#!/usr/bin/bash
#expand-environment-files.sh
#When using the Dockerfile with for example a CI/CD-tool,
#you can store the content of secret files (wallet files for Oracle Cloud)
#and configuration files inside environment variables.
#This script expands the content of those variables - which should be the
#file contents Base64-encoded (using the base64 Linux CLI as a baseline).
#Note that environment variables will not be expanded to files if the target file
#already exists.
echo "Expanding environment files if needed..."
ls
mkdir -p album_of_the_day_backend/.wallet/ #Will not throw error if the directory exists => no check needed!
#Expand cwallet.ora
if test -f "album_of_the_day_backend/.wallet/cwallet.sso";then
  echo "cwallet.sso already exists. It will not be expanded from environment variables."
else
   echo "Expanding cwallet.sso file from environment variables..."
  touch album_of_the_day_backend/.wallet/cwallet.sso
  base64 -d "$ORACLE_WALLET_FILE_CONTENTS" >> album_of_the_day_backend/.wallet/cwallet.sso
fi
#Expand sqlnet.ora file
if test -f "album_of_the_day_backend/.wallet/sqlnet.ora";then
  echo "sqlnet.ora already exists. It will not be expanded from environment variables."
else
  echo "Expanding sqlnet.ora file from environment variables..."
  touch album_of_the_day_backend/.wallet/sqlnet.ora
  base64 -d "$ORACLE_SQLNET_FILE_CONTENTS" >> album_of_the_day_backend/.wallet/sqlnet.ora
fi
#Expand tnsnames.ora file
if test -f "album_of_the_day_backend/.wallet/tnsnames.ora";then
  echo "tnsnames.ora already exists. It will not be expanded from environment variables."
else
  echo "Expanding tnsnames.ora file from environment variables..."
  touch album_of_the_day_backend/.wallet/tnsnames.ora
  base64 -d "$ORACLE_TNSNAMES_FILE_CONTENTS" >> album_of_the_day_backend/.wallet/tnsnames.ora
fi
#Done with those, now let's do the Toml config file for the task runner!
#Expand task runner config file
if test -f "album_of_the_day_backend/website/tasks/systemd/task_runner/config.toml";then
  echo "tnsnames.ora already exists. It will not be expanded from environment variables."
else
  echo "Expanding config.toml file from environment variables..."
  touch album_of_the_day_backend/website/tasks/systemd/task_runner/config.toml
  base64 -d "$TASK_RUNNER_CONFIG_FILE_CONTENTS" >> album_of_the_day_backend/website/tasks/systemd/task_runner/config.toml
fi