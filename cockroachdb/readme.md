### Введение

Данный docker-compose.yaml содержит запуск в защищенном режиме, подробнее о запуске:
[https://p.yakunin.dev/posts/2023/Feb/09/cockroachdb-docker-install/](https://p.yakunin.dev/posts/2023/Feb/09/cockroachdb-docker-install/)

### Запуск в незащищенном режиме (insecure)

После запуска необходимо зайти в первый контейнер и выполнить инициализацию кластера. 

```shell
>>> docker exec -it cdb01 sh

cockroach init --insecure --host=cdb01:26257

Out:
Cluster successfully initialized
```

После этого можно подключаться к базе, так же для теста можно создать базу, таблицу и запись.

```shell
cockroach sql --insecure
```
```sql
CREATE DATABASE bank;
CREATE TABLE bank.accounts (id INT PRIMARY KEY, balance DECIMAL);
INSERT INTO bank.accounts VALUES (1, 1000.50);
SELECT * FROM bank.accounts;
```

### Запуск в боевом режиме (SSL secure)

Необходимо сгенерировать сертификаты:

```shell
>>> docker exec -it cdb01 sh

cockroach cert create-ca --certs-dir=/certs --ca-key=/certs/ca.key
cockroach cert create-node cdb01 cdb02 cdb03 --certs-dir=/certs --ca-key=/certs/ca.key 
```

Для входа в консоль, необходимо создать пользователя, так же назначим ему права на базу и таблицы.

```shell
>>> docker exec -it cdb01 sh

cockroach sql --certs-dir=/certs --host=cdb01
```
```sql
CREATE USER craig WITH PASSWORD 'cockroach';
GRANT ALL ON DATABASE bank TO craig WITH GRANT OPTION;
GRANT ALL ON TABLE bank.* TO craig;
SHOW GRANTS ON TABLE bank.accounts;
```
