### VerySecureFTPdaemon (vsftpd)

Good old ftp server. To work, you will need to fill out a file .env, enter your username and password to connect on server. You can also generate certificates using letsencrypt or use your own.

Before starting, you need to create a vsfptd.log file, these are docker requirements, because if the file is not created you will get an error, docker will think it is a directory.

Please note that in this configuration, passive mode is also enabled. Edit main configuration file src/vsftpd.conf, you must specify the real ip address.

Also define the directories to be used, edit volumes in docker-compose.yaml.

### Start

```
> vi .env # setup username and password
> touch vsftpd.log
> docker compose up --build --detach
```
