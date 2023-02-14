### Подготовка системы

Для корректной работы кластера на каждой из нод необходимо увеличить количество используемых файлов в системе,
увеличить лимит. Мы будем предпологать что Docker уже установлен в вашей системе. Если не изменить лимит 
файлов в системе, то вы получите ошибку вида: `Soft rlimits for open file descriptors too low`, стоит 
следовать рекомендациям установки. Увеличиваем лимит для пользователя от которого будет запущен процесс. 
Поумолчанию mongodb. Редактируем файл `/etc/security/limits.conf` и добавляем в конец следующие строки:

```bash
>>> vi /etc/security/limits.conf

@mongodb    soft    nproc   unlimited
@mongodb    hard    nproc   unlimited
@mongodb    soft    nofile  64000
@mongodb    hard    nofile  64000
```

Мы запускаем кластер в docker, при этом на одном хосте, но так как docker имеет свое пространство имен, ему для работы
не нужны DNS записи, но если вы запускаете кластер на отдельных хостах и вне контейнера или даже в нем, но на каждую
новую ноду выделяется отдельный хост, то вы должны либо иметь DNS запись, либо, указать их явно:

>Для корректной работы кластера необходимо иметь DNS запись для каждой ноды, рекомендуется использовать реальные 
DNS записи, для выпуска доверенных сертификатов через Let'sEncrypt. В этой статье не будет рассмотрен этот процесс. 
Пути решения: использование собственного/локального DNS сервера, либо использование файлов `/etc/hosts` каждой ноды с 
внесением соотвествующей записи. Для простоты примера, я буду использовать файл `host`, по этому вношу в него записи 
следующего вида:
> ```
 >vi /etc/hosts
 >10.200.2.2    mongodb-server-1
 >10.200.2.3    mongodb-server-2
 >10.200.2.4    mongodb-server-3
> ```

В данном документе рассматривается решение из 2х активных нод master/slave и одной arbiter ноды, как указано в 
официальной документации использование арбитра строго рекомендуется в работе кластера, он имеет больший "вес" при 
установлении кворума голосов, но, тем не менее, на нем не хранятся данные. Он выступает только арбитром. Репликация 
по факту происходит только между нодами master/slave. В роли арбитра у нас будет выступать mongodb3.orion.y

### Генерация SSL сертификатов.

Для авторизации между нодами нам будет необходимо сгенерировать 3 сертифката сервера и 1 клиента для подключения 
администратора или использования его для конечного пользователя/программы. Для начала нам необходим корневой сертификат 
и его ключ. Корневой сертификат будет валидировать выпущенные им сертификаты и доверять им. Генерируем корневой 
сертификат, в процессе генерации будет предложено ввести ключевую фразу для ключа, рекомендую сделать её как можно 
сложнее. При выпуске самого сертификата необходимо заполнить соответствующие поля, после CN (Common Name) в случае 
с корневым сертификатом заполняем RootCA, в качестве инструмента для генерации будем использовать openssl:

```bash
>>> echo "00" > ca.srl
>>> openssl genrsa -out ca.key -aes256 8192

Generating RSA private key, 8192 bit long modulus (2 primes)
............................................................................................+++
............................................
e is 65537 (0x010001)
Enter pass phrase for ca.key:
Verifying - Enter pass phrase for ca.key:

>>> openssl req -x509 -new -extensions v3_ca -key ca.orion.y.key -days 3650 \
-subj "/C=RU/ST=Russia/L=Moscow/O=Yakunin V. Vasily/OU=IT Dept./CN=Root CA" -out ca.crt

Enter pass phrase for ca.key:
>>> cat ca.crt > ca.pem
```

Теперь мы можем сгенерировать серверные сертификаты, сначала генерируется ключ, затем сам сертификат, 
внимание в поле CN (Common Name) необходимо указать доменное имя ноды, в данном случае mongodb-server-1:

```bash
>>> openssl req -nodes -newkey rsa:4096 -sha256 -keyout mongodb-server-1.key \
 -subj "/C=RU/ST=Russia/L=Moscow/O=Yakunin V. Vasily/OU=IT Dept./CN=mongodb-server-1" \
 -addext "subjectAltName = DNS.1:mongodb-server-1, IP.1:10.200.2.2" -out mongodb-server-1.csr
 
Generating a RSA private key
..............................................................................++++
............................................................................++++
writing new private key to 'mongodb-server-1.key'
-----

>>> openssl x509 -req -extfile <(printf "subjectAltName=DNS.1:mongodb-server-1,IP.1:10.200.2.2") \
 -in mongodb-server-1.csr -CA ca.crt -CAkey ca.key -out mongodb-server-1.crt
 
Signature ok
subject=C = RU, ST = Russia, O = MongoDB, OU = MongoDB, CN = mongodb-server-1
Getting CA Private Key
Enter pass phrase for ca.key:
```

Необходимо повторить генерацию сертификатов до необходимого количества нод, например 2 арбитра 3 ноды и т.д., 
число всегда должно быть нечетным, что бы избежать split brain. В завершении необходимо сгенерировать клиентский 
сертификат, он потребуется для подключения конечных пользователей/программ к кластеру.

```bash
>>> openssl req -new -nodes -newkey rsa:4096 -sha256 -keyout client.key \
 -subj "/C=RU/ST=Russia/L=Moscow/O=Yakunin V. Vasily/OU=IT Dept./CN=client" \
 -addext "subjectAltName = DNS:client, DNS:localhost" \
 -addext "keyUsage=keyEncipherment,dataEncipherment" \
 -addext "extendedKeyUsage=serverAuth" -out client.csr
 
Generating a RSA private key
..........................................++++
...++++
writing new private key to 'client.key'
-----

>>> openssl x509 -req -extfile <(printf "subjectAltName=DNS.1:client,DNS.2:localhost") \
 -in client.csr -CA ca.crt -CAkey ca.key -out client.crt
 
Signature ok
subject=C = RU, ST = Russia, O = MongoDB, OU = MongoDB, CN = client
Getting CA Private Key
Enter pass phrase for ca.key:
```

Таким образом после генерации всех сертификатов, должно получится 1 корневой сертификат и его ключ, 3 ключа и 
сертификата для серверов/нод и один клиентский ключ/сертификат.

### Подготовка Dockerfile и создание образа.

Вы можете использовать официальный образ MongoDB на docker hub, и я рекомендую вам использовать только официальные
образы, но в качестве примера, я создаю свой.

```dockerfile
>>> vi Dockerfile

FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get upgrade -y && apt install wget gnupg gnupg2  gnupg1 netcat -y && \
    wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add - && \
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list && \
    apt-get update && apt-get install -y mongodb-org && apt-get purge wget gnupg gnupg2  gnupg1 -y && \
    mkdir /home/mongodb &&  mkdir /etc/ssl/mongodb/ && mkdir /data && \
    chown -R mongodb:mongodb /data && chown -R mongodb:mongodb /home/mongodb/ && \
    rm -rf /var/cache/apt

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT /entrypoint.sh
CMD ["tail", "-f", "/var/log/mongodb/mongod.log"]
```

Так же необходимо создать файлы entrypoint.sh который будет отвечать за запуск демона внутри Docker-контейнера, 
и конфигурационный файл для MongoDB, для каждой ноды необходимо указать свое DNS имя хоста. 
Напоминание: конфигурационный файл mongod.conf имеет синтаксис yml и чувствителен к табуляции, 
используйте принцип 2х пробелов для замены табуляции.

```bash
>>> vi entrypoint.sh

#!/usr/bin/bash
chown -R mongodb:mongodb /data
chown -R mongodb:mongodb /etc/ssl
su - mongodb -s /bin/bash -c '/usr/bin/mongod --config /etc/mongod.conf'

```

```yaml
>>>  vi mongod.conf

storage:
  dbPath: /data
  journal:
    enabled: true

systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log

net:
  tls:
    mode: requireTLS
    certificateKeyFile: /etc/ssl/mongodb-server-1.pem
    CAFile: /etc/ssl/ca.pem

net:
  port: 27017
  bindIpAll: true
  ipv6: false

processManagement:
  timeZoneInfo: /usr/share/zoneinfo

security:
  authorization: enabled
  clusterAuthMode: x509

net:
  tls:
    clusterFile: /etc/ssl/mongodb-server-1.pem
    clusterCAFile: /etc/ssl/ca.pem

replication:
  replSetName: "rs0"

```

### Конфигурация docker-compose

```yaml
>>> cat docker-compose.yml

version: "3.8"
services:
  mongodb-server-1:
    image: mongodb-server:latest
    container_name: mongodb-server-1
    hostname: mongodb-server-1
    restart: always
    build: ./src
    volumes:
      - ./data/1:/data
      - ./src/mongod_node_1.conf:/etc/mongod.conf
      - ./src/ssl:/etc/ssl
      - ./mongod.log:/var/log/mongodb/mongod.log

    healthcheck:
      test: ["CMD", "nc", "-zvw3", "mongodb-server-1", "27017"]
      interval: 60s
      timeout: 3s
      retries: 3
      start_period: 5s

  mongodb-server-2:
    image: mongodb-server:latest
    container_name: mongodb-server-2
    hostname: mongodb-server-2
    restart: always
    build: ./src
    volumes:
      - ./data/2:/data
      - ./src/mongod_node_2.conf:/etc/mongod.conf
      - ./src/ssl:/etc/ssl

    healthcheck:
      test: ["CMD", "nc", "-zvw3", "mongodb-server-2", "27017"]
      interval: 60s
      timeout: 3s
      retries: 3
      start_period: 5s

  mongodb-server-3:
    image: mongodb-server:latest
    container_name: mongodb-server-3
    hostname: mongodb-server-3
    restart: always
    build: ./src
    volumes:
      - ./data/3:/data
      - ./src/mongod_node_3.conf:/etc/mongod.conf
      - ./src/ssl:/etc/ssl

    healthcheck:
      test: ["CMD", "nc", "-zvw3", "mongodb-server-3", "27017"]
      interval: 60s
      timeout: 3s
      retries: 3
      start_period: 5s
```

### Пользователи и репликация

Производить все дальнейшие действия предполагается на первом узле реплики. Заходим в контейнер и выполняем подключение:

```bash
>>> docker exec -it mongodb-server-1 bash
>>> mongosh --tls --tlsCAFile /etc/ssl/ca.pem --tlsCertificateKeyFile /etc/ssl/client.pem --authenticationMechanism MONGODB-X509 --host mongodb-server-1

Current Mongosh Log ID:	63eb9d884ba95f84e21247f3
Connecting to:		mongodb://mongodb-server-1:27017
Using MongoDB:		6.0.4
Using Mongosh:		1.7.1

For mongosh info see: https://docs.mongodb.com/mongodb-shell/

rs0 [direct: primary] test>
```
Далее необходимо создать все узлы репликации, мы используем схему master - arbiter - slave, сначала инициализируем 
реплику, далее добавляем узлы к реплике.

```bash
> rs.initiate(
{
  _id: "rs0",
  members: [
    { _id: 0, host: "mongodb-server-1" }
  ]
})

> db.adminCommand({
  "setDefaultRWConcern" : 1,
  "defaultWriteConcern" : {
    "w" : 2
  }
})

> rs.add('mongodb-server-2')
> rs.addArb('mongodb-server-3')
```

Необязательно, но очень желательно выполнить приоритет узлов в кластере. Как описано в документации, узел имеющий 
приоритет 0 не будет получать голоса, а значит мы отдадим его арбитру. Остальной вес распределяется от большего к 
меньшему, то есть узел с "весом" 2 будет иметь приоритет на 1 и т.д., по этому первому узлу мы выставляем приоритет 2, 
второму 1. Тогда первый узел после восстановления снова примет значение primary. Это более логично чем оставлять новый 
мастер на втором узле. Подключение конечных точек происходит не к конкретному узлу, а именно к имени реплики, 
то есть rs0. Так же обратите внимание на поля _id при расставлении приоритетов, получите вывод rs.status(), 
проверьте _id каждой ноды, далее можно выставлять приоритет нод.

```bash
> cfg = rs.conf()
> cfg.members[0].priority = 2
> cfg.members[1].priority = 1
> cfg.members[2].priority = 0
> rs.reconfig(cfg)
```

После чего можно проверить статус репликации (из вывода убрана часть информации для удобства чтения):

```bash
> rs.status()

{
  set: 'rs0',
  date: ISODate("2023-02-14T14:46:29.726Z"),
  myState: 1,
  term: Long("4"),
  syncSourceHost: '',
  syncSourceId: -1,
  heartbeatIntervalMillis: Long("2000"),
  majorityVoteCount: 2,
  writeMajorityCount: 2,
  votingMembersCount: 3,
  writableVotingMembersCount: 2,
  optimes: {
    lastCommittedOpTime: { ts: Timestamp({ t: 1676385987, i: 1 }), t: Long("4") },
    lastCommittedWallTime: ISODate("2023-02-14T14:46:27.827Z"),
    readConcernMajorityOpTime: { ts: Timestamp({ t: 1676385987, i: 1 }), t: Long("4") },
    appliedOpTime: { ts: Timestamp({ t: 1676385987, i: 1 }), t: Long("4") },
    durableOpTime: { ts: Timestamp({ t: 1676385987, i: 1 }), t: Long("4") },
    lastAppliedWallTime: ISODate("2023-02-14T14:46:27.827Z"),
    lastDurableWallTime: ISODate("2023-02-14T14:46:27.827Z")
  },
  lastStableRecoveryTimestamp: Timestamp({ t: 1676385927, i: 1 }),
  electionCandidateMetrics: {
    lastElectionReason: 'electionTimeout',
    lastElectionDate: ISODate("2023-02-14T14:11:47.716Z"),
    electionTerm: Long("4"),
    lastCommittedOpTimeAtElection: { ts: Timestamp({ t: 0, i: 0 }), t: Long("-1") },
    lastSeenOpTimeAtElection: { ts: Timestamp({ t: 1676383892, i: 1 }), t: Long("3") },
    numVotesNeeded: 2,
    priorityAtElection: 2,
    electionTimeoutMillis: Long("10000"),
    numCatchUpOps: Long("0"),
    newTermStartDate: ISODate("2023-02-14T14:11:47.744Z"),
    wMajorityWriteAvailabilityDate: ISODate("2023-02-14T14:11:48.729Z")
  },
  members: [
    {
      _id: 0,
      name: 'mongodb-server-1:27017',
      health: 1,
      state: 1,
      stateStr: 'PRIMARY',
      uptime: 2093,
      optime: { ts: Timestamp({ t: 1676385987, i: 1 }), t: Long("4") },
      optimeDate: ISODate("2023-02-14T14:46:27.000Z"),
      lastAppliedWallTime: ISODate("2023-02-14T14:46:27.827Z"),
      lastDurableWallTime: ISODate("2023-02-14T14:46:27.827Z"),
      syncSourceHost: '',
      syncSourceId: -1,
      infoMessage: '',
      electionTime: Timestamp({ t: 1676383907, i: 1 }),
      electionDate: ISODate("2023-02-14T14:11:47.000Z"),
      configVersion: 5,
      configTerm: 4,
      self: true,
      lastHeartbeatMessage: ''
    },
    {
      _id: 1,
      name: 'mongodb-server-2:27017',
      health: 1,
      state: 2,
      stateStr: 'SECONDARY',
      uptime: 2091,
      optime: { ts: Timestamp({ t: 1676385987, i: 1 }), t: Long("4") },
      optimeDurable: { ts: Timestamp({ t: 1676385987, i: 1 }), t: Long("4") },
      optimeDate: ISODate("2023-02-14T14:46:27.000Z"),
      optimeDurableDate: ISODate("2023-02-14T14:46:27.000Z"),
      lastAppliedWallTime: ISODate("2023-02-14T14:46:27.827Z"),
      lastDurableWallTime: ISODate("2023-02-14T14:46:27.827Z"),
      lastHeartbeat: ISODate("2023-02-14T14:46:28.564Z"),
      lastHeartbeatRecv: ISODate("2023-02-14T14:46:29.611Z"),
      pingMs: Long("0"),
      lastHeartbeatMessage: '',
      syncSourceHost: 'mongodb-server-1:27017',
      syncSourceId: 0,
      infoMessage: '',
      configVersion: 5,
      configTerm: 4
    },
    {
      _id: 2,
      name: 'mongodb-server-3:27017',
      health: 1,
      state: 7,
      stateStr: 'ARBITER',
      uptime: 2092,
      lastHeartbeat: ISODate("2023-02-14T14:46:28.565Z"),
      lastHeartbeatRecv: ISODate("2023-02-14T14:46:28.562Z"),
      pingMs: Long("0"),
      lastHeartbeatMessage: '',
      syncSourceHost: '',
      syncSourceId: -1,
      infoMessage: '',
      configVersion: 5,
      configTerm: 4
    }
  ],
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1676385987, i: 1 }),
    signature: {
      hash: Binary(Buffer.from("0000000000000000000000000000000000000000", "hex"), 0),
      keyId: Long("0")
    }
  },
  operationTime: Timestamp({ t: 1676385987, i: 1 })
}

```

Таким образом кластер настроен. Репликация происходит. Можно создавать необходимые базы данных и подключать клиентов.
Для подключения к серверам мы используем корневой сертификат и сертификат клиента, (ca.pem | client.pem), 
после подключения к первому узлу реплики создадим пользователя от которого далее будем работать с базами данных.

```bash
> use admin
> db.createUser(
  {
    user: "yakunin",
    pwd: "strong_password_here",
    roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
  }
)
Successfully added user: {
	"user" : "yakunin",
	"roles" : [
		{
			"role" : "userAdminAnyDatabase",
			"db" : "admin"
		}
	]
}
```

### Работа с базой данных

```bash
# Содание базы данных:
> use mydb

# Добавление данных в коллекцию:
> db.myCollection.insert({"name": "john", "age" : 22, "location": "colombo"})

# Вывод данных:
> db.myCollection.find().pretty()

# Удаление коллекции:
> db.myCollection.remove({});

# Удаление базы данных:
> use mydb
> db.dropDatabase();
```

### Импорт/Экспорт данных и резервное копирование.

Что бы возможно было использовать сертификат авторизации кластера для импорта/экспорта внестите следующую 
переменную окружения:

```bash
>>> export GODEBUG="x509ignoreCN=0"
```

Так же можно выпустить отдельный сертификат для импорта и экспорта данных. Если мы будем использовать сертификаты 
сервера, то в логах можно увидеть следующие строки:

```bash
Client isn't a mongod or mongos, but is connecting with a certificate with cluster membership
```

Что выполнить экспорт данных в json файл, достаточно сделать следующее:

```bash
>>> mongoexport --uri="mongodb://mongodb-server-1/?replicaSet=rs0&ssl=true" \
    --ssl --sslCAFile ca.pem --sslPEMKeyFile client.pem --authenticationMechanism MONGODB-X509 \
    -d mydb -c mydb -o output.json
```

Необходимо обратить внимание, что мы подключаемся ко всем узлам кластера и к конкретной реплике на них, это важно. 
Далее, мы используем в качестве аутентификации механизм авторизации кластера `--authenticationMechanism MONGODB-X509`, 
далее указываем базу и коллекцию. Получить коллекцию можно через функцию: `use mydb; db.getCollectionNames()`, 
после чего указываем выходной формат файла. После успешного экспорта можно stdout будет следующим:

```bash
2021-11-03T15:49:39.241+0300	connected to: mongodb://mongodb-server-1/?replicaSet=rs0&ssl=true
2021-11-03T15:49:39.247+0300	exported 1 record
```

```bash
>>> cat output.json 

{"_id":{"$oid":"6180e14ea6e26bd08976e37d"},"name":"john","age":22.0,"location":"colombo"}
```

Если необходимо подключение от конкретного пользователя, то сначала необходимо создать его и далее назначить ему права 
на базу данных, например:

```bash
> db.grantRolesToUser(
   "yakunin",
   [ "readWrite" , { role: "readWrite", db: "mydb" } ],
   { w: "majority" , wtimeout: 4000 }
)
```

Таким образом мы дали права на чтение/запись. Теперь можно экспортировать данных от конкретного пользователя, 
но необходимо внести соответствующие ключи в строку экспорта.

```bash
>>> mongoexport --uri="mongodb://mongodb-server-1/?replicaSet=rs0&ssl=true" --ssl --sslCAFile ca.pem \
    --sslPEMKeyFile client.pem --authenticationMechanism SCRAM-SHA-1 \
    --username yakunin --password="password" --authenticationDatabase admin \
    --db mydb --collection mydb --out output.json
```

Необходимо обратить внимание, что изменился механизм авторизации, а так же добавились ключи имени пользователя, 
пароля и базы аутентификации в которую заведен пользователь. Так же доступны инструменты резервного копирования и 
восстановления **mongodump/mongorestore**, для создания копии базы данных используем mongodump:

```bash
>>> mkdir mongodb-backup
>>> mongodump --uri="mongodb://mongodb-server-1/?replicaSet=rs0&ssl=true" \
    --ssl --sslCAFile ca.pem --sslPEMKeyFile client.pem --authenticationMechanism MONGODB-X509 \
    -d mydb -o /root/mongodb-backup/ --gzip

2021-11-03T16:00:21.297+0300	writing mydb.mydb to /root/mongodb-backup/mydb/mydb.bson.gz
2021-11-03T16:00:21.300+0300	done dumping mydb.mydb (1 document)
```

Для восстановления копии базы:

```bash
>>> mongorestore --uri="mongodb://mongodb-server-1/?replicaSet=rs0&ssl=true" \
    --ssl --sslCAFile ca.pem --sslPEMKeyFile client.pem --authenticationMechanism MONGODB-X509 \
    --db mydb --dir /root/mongodb-backup/mydb/ --gzip

2021-11-03T16:07:21.251+0300	building a list of collections to restore from /root/mongodb-backup/mydb dir
2021-11-03T16:07:21.252+0300	reading metadata for mydb.mydb from /root/mongodb-backup/mydb/mydb.metadata.json.gz
2021-11-03T16:07:21.257+0300	restoring mydb.mydb from /root/mongodb-backup/mydb/mydb.bson.gz
2021-11-03T16:07:21.270+0300	finished restoring mydb.mydb (1 document, 0 failures)
2021-11-03T16:07:21.270+0300	no indexes to restore for collection mydb.mydb
2021-11-03T16:07:21.270+0300	1 document(s) restored successfully. 0 document(s) failed to restore.
```

### Ссылки и дополнения

- [https://docs.mongodb.com/manual/tutorial/deploy-replica-set/](https://docs.mongodb.com/manual/tutorial/deploy-replica-set/)
- [https://www.mongodb.com/docs/manual/tutorial/configure-ssl/](https://www.mongodb.com/docs/manual/tutorial/configure-ssl/)
- [https://www.openssl.org/docs/manpages.html](https://www.openssl.org/docs/manpages.html)
- [https://docs.docker.com/engine/install/ubuntu/](https://docs.docker.com/engine/install/ubuntu/)
