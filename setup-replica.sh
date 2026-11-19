#!/bin/bash
set -e

ROOT_PASS="root123"
REPL_USER="repl"
REPL_PASS="repl123"

echo ">> Criando usuário de replicação no master..."
docker exec mysql-master mysql -uroot -p"$ROOT_PASS" -e "
  CREATE USER IF NOT EXISTS '$REPL_USER'@'%' IDENTIFIED WITH mysql_native_password BY '$REPL_PASS';
  GRANT REPLICATION SLAVE ON *.* TO '$REPL_USER'@'%';
  FLUSH PRIVILEGES;"

echo ">> Capturando posição do binlog..."
STATUS=$(docker exec mysql-master mysql -uroot -p"$ROOT_PASS" -e "SHOW MASTER STATUS\G")
LOG_FILE=$(echo "$STATUS" | grep "File:" | awk '{print $2}')
LOG_POS=$(echo "$STATUS" | grep "Position:" | awk '{print $2}')
echo "   Arquivo: $LOG_FILE | Posição: $LOG_POS"

echo ">> Configurando a réplica..."
docker exec mysql-slave mysql -uroot -p"$ROOT_PASS" -e "CREATE DATABASE IF NOT EXISTS pessoas_db;"
docker exec mysql-slave mysql -uroot -p"$ROOT_PASS" -e "
  STOP REPLICA;
  CHANGE REPLICATION SOURCE TO
    SOURCE_HOST='mysql-master',
    SOURCE_USER='$REPL_USER',
    SOURCE_PASSWORD='$REPL_PASS',
    SOURCE_LOG_FILE='$LOG_FILE',
    SOURCE_LOG_POS=$LOG_POS,
    GET_SOURCE_PUBLIC_KEY=1;
  START REPLICA;"

echo ">> Pronto!"