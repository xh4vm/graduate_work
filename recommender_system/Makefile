# define standard colors
ifneq (,$(findstring xterm,${TERM}))
	BLACK        := $(shell printf "\033[30m")
	RED          := $(shell printf "\033[91m")
	GREEN        := $(shell printf "\033[92m")
	YELLOW       := $(shell printf "\033[33m")
	BLUE         := $(shell printf "\033[94m")
	PURPLE       := $(shell printf "\033[95m")
	ORANGE       := $(shell printf "\033[93m")
	WHITE        := $(shell printf "\033[97m")
	RESET        := $(shell printf "\033[00m")
else
	BLACK        := ""
	RED          := ""
	GREEN        := ""
	YELLOW       := ""
	BLUE         := ""
	PURPLE       := ""
	ORANGE       := ""
	WHITE        := ""
	RESET        := ""
endif

define log
	@echo ""
	@echo "${WHITE}----------------------------------------${RESET}"
	@echo "${BLUE}[+] $(1)${RESET}"
	@echo "${WHITE}----------------------------------------${RESET}"
endef

.PHONY: interactive build recom services
recom: create-venv poetry-install-build-recom build-dockers-recom

.PHONY: interactive build clickhouse research
ch-research: create-venv poetry-install-clickhouse build-dockers-ch

.PHONY: clean all docker images and pyc-files
clean-all: clean-pyc clean-all-dockers

.PHONY: run pre-commit all files
pre-commit: create-venv pip-install-pre-commit pre-commit-files

.PHONY: create venv
create-venv:
	$(call log,Create venv)
	python3 -m venv venv

.PHONY: install requirements-build to venv
pip-install-build:
	$(call log,Pip installing packages)
	./venv/bin/pip3 install -r requirements-build.txt

.PHONY: potery install build to venv
poetry-install-build-recom:
	$(call log,Poetry installing packages)
	poetry install --only build

.PHONY: install requirements-pre-commit to venv
pip-install-pre-commit:
	$(call log,Pip installing packages)
	./venv/bin/pip3 install -r requirements-pre-commit.txt

.PHONY: potery install pre-commit to venv
poetry-pre-commit-build:
	$(call log,Poetry installing packages)
	poetry install --only pre-commit

.PHONY: potery install clickhouse research to venv
poetry-install-clickhouse:
	$(call log,Poetry installing packages)
	poetry install --only clickhouse

.PHONY: interactive build docker services
build-dockers:
	$(call log,Build containers)
	docker-compose --profile dev up --build

.PHONY: interactive build docker recom services 
build-dockers-recom:
	$(call log,Build recom containers)
	docker-compose --profile dev_recom up --build

.PHONY: run pre-commit all files
pre-commit-files:
	$(call log,Run pre commit functions)
	source venv/bin/activate; ./venv/bin/pre-commit run --all-files

.PHONY: clean-pyc
clean-pyc:
	$(call log,Run cleaning pyc and pyo files recursively)
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

.PHONY: clean all docker images
clean-all-dockers:
	$(call log,Run stop remove and cleaning memory)
	T=$$(docker ps -q); docker stop $$T; docker rm $$T; docker container prune -f

.PHONY: interactive build docker clickhouse services
build-dockers-ch:
	docker-compose --profile clickhouse up --build

.PHONY: upgrade clickhouse's database schema
ch-db-upgrade:
	source venv/bin/activate; ./venv/bin/python3 backend/clickhouse/src/db_upgrade.py

.PHONY: load fake-data into clickhouse
ch-load:
	source venv/bin/activate; ./venv/bin/python3 backend/clickhouse/src/load_data.py

.PHONY: execute queries for clickhouse
ch-benchmark:
	source venv/bin/activate; ./venv/bin/python3 backend/clickhouse/src/benchmarks.py

.PHONY: run mongo containers
mongo: run_containers

.PHONY: interactive build mongo cluster
mongo_cfg: config_cluster create_recommendations_coll


.PHONY: run install dependencies in spark cluster
spark_dep: spark_install_dependencies


.PHONY: run docker mongodb containers
run_containers:
	$(call log,Run containers)
	docker-compose -f docker-compose_mongodb.yml --profile mongo up

.PHONY: configure the cluster
config_cluster:
	$(call log,Configure the cluster)
	docker exec -it mongocfg1 bash -c 'echo "rs.initiate({_id: \"mongors1conf\", configsvr: true, members: [{_id: 0, host: \"mongocfg1\"}, {_id: 1, host: \"mongocfg2\"}, {_id: 2, host: \"mongocfg3\"}]})" | mongosh'
	sleep 2
	docker exec -it mongors1n1 bash -c 'echo "rs.initiate({_id: \"mongors1\", members: [{_id: 0, host: \"mongors1n1\"}, {_id: 1, host: \"mongors1n2\"}, {_id: 2, host: \"mongors1n3\"}]})" | mongosh'
	sleep 10
	docker exec -it mongos1 bash -c 'echo "sh.addShard(\"mongors1/mongors1n1\")" | mongosh'
	sleep 2
	docker exec -it mongors2n1 bash -c 'echo "rs.initiate({_id: \"mongors2\", members: [{_id: 0, host: \"mongors2n1\"}, {_id: 1, host: \"mongors2n2\"}, {_id: 2, host: \"mongors2n3\"}]})" | mongosh'
	sleep 10
	docker exec -it mongos1 bash -c 'echo "sh.addShard(\"mongors2/mongors2n1\")" | mongosh'

.PHONY: create database
create_mongo_db:
	$(call log,Create database)
	docker exec -it mongors1n1 bash -c 'echo "use recommender" | mongosh'
	docker exec -it mongos1 bash -c 'echo "sh.enableSharding(\"movies\")" | mongosh'


.PHONY: create recommendations collections with index
create_recommendations_coll:
	$(call log,Create collections)
	export PYTHONPATH=${PWD}; \
poetry run python src/db/receiver/mongodb/create_collections.py


.PHONY: install dependencies
spark_install_dependencies:
	$(call log,Install dependencies)
	docker exec -it spark-master bash -c 'pip install -r /work/requirements.txt'
	docker exec -it spark-worker01 bash -c 'pip install -r /work/requirements.txt'
	docker exec -it spark-worker02 bash -c 'pip install -r /work/requirements.txt'
	docker exec -it spark-worker03 bash -c 'pip install -r /work/requirements.txt'


.PHONY: get params for recommendations model
params_recom:
	export PYTHONPATH=${PWD}; src/train_model.py

.PHONY: make recommendations
make_recom:
	export PYTHONPATH=${PWD}; src/recommender.py'
