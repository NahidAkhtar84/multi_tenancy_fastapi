

## Run Locally with Docker
Run from inside project directory where `docker-compose.yaml` is located.
Use `--build` option if build is required before run.
```
docker-compose up --build
```
Individual container service can be run separately if needed. 
Just make sure `pgdb` is up and running before `server`
```
docker-compose up pgdb
docker-compose up --build server
```

## Run Locally with Uvicorn

Make sure installed Python version is at least **3.10**


First ensure postgres db is up and running locally. <br>
Make sure db related environment variables are updated in `.env`

To run the FastAPI enabled backend server:
```
uvicorn app.main:app --reload
```
You can **also** run postgres db with docker and backend with uvicorn locally
```
docker-compose up pgdb
```
In that case make sure to set `POSTGRES_SERVER=0.0.0.0` in `.env`


## Deploy in Development (AWS)

### Setup AWS Services
- AWS ec2 instance launch, keypair generate, security group setup
- Install docker and other tools in EC2 machine
- Create ECR repository
- Create `ats-backend` folder in ec2 instance:

### Build and Push to ECR
Make sure `VERSION_TAG` in `.env.dev` is updated. <br>
To build the docker image and push to ecr docker registry
```
sh script-build-and-push.sh
```

### Run in AWS EC2
#### ssh to ec2 instance

- if aws ec2 instance host 'ats' configured in local `.ssh/config`
	```
	ssh ats
	```
	otherwise
	```
	ssh -i ~/.ssh/ats.pem ec2-user@ec2-3-110-37-143.ap-south-1.compute.amazonaws.com
	```
#### Inside the ec2 instance

- to check if docker daemon is running/active?
	```
	systemctl is-active docker
	```
- to start docker daemon
	```
	sudo service docker start
	```
- remove already running ATS container (if needed)
	```
	docker ps
	docker rm <ATS CONTAINER ID>
	```
- pull the ATS docker image and run (using scrpt)
	```
	cd ats
	sh script-pull-and-run.sh
	```

## Check / Test

### Check in API endpoints in Browser
Use ec2 instance's public ip with port: [http://3.110.37.143/:8000/](http://3.110.37.143/:8000/)

### Check log [TBD]
...

### Inspect Inside Docker
Bash like inspecting inside docker container
```
docker exec -it <container id or name> bash
```

### Alembic 

#### To automatically generate revision
```
docker-compose run --rm server alembic revision --autogenerate -m "<alembic message>";
```
#### To upgrade head
```
docker-compose run --rm server alembic upgrade head;
```

#### To downgrade to previous head
```
docker-compose run --rm server alembic downgrade -1;
```

#### To downgrade to specific head
```
docker-compose run --rm server alembic downgrade <target-revision>;
```

#### If it is needed to upgrade multiple heads:
Dont use ```upgrade heads``` instead you should merge the heads and then run upgrade head.

#### To merge heads:
```
docker-compose run --rm server alembic merge heads -m "<message>";
```
Now run upgrade head command.

### Data Seed
To populate database and create initial user pass environment value ```DATA_SEED=1``` otherwise ```DATA_SEED=0```


### DB Backup &  Restore

#### Backup a postgres db running in docker
```commandline
docker exec -i <container-id> bash -c "PGPASSWORD=postgres pg_dump --username postgres postgres" > ~/ats-backend/db-backup/dump_ats_dev_$(date +%y-%m-%d_%H-%M).sql
```

#### Restore a postgres db running in docker
```commandline
docker exec -i <container-id> bash -c "PGPASSWORD=postgres psql --username postgres postgres" < ~/ats-backend/db-backup/dump_ats_dev_2023-12-31_23-59.sql
```


