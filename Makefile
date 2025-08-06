build-dev: docker-build-dev
build-test: docker-build-test
build-prod: docker-build-prod
down: docker-stop
pull: docker-pull
# build the image
build-version: docker-build-version
build-latest: docker-build-latest
# tag the image
tag-version: docker-tag-version
tag-latest: docker-tag-latest
# push the image to the registry
push-version: docker-push-version
push-latest: docker-push-latest
# start the pytest
pytest-all: pytest-auth pytest-user pytest-post pytest-follow
# alembic python database
alembic-init: python-alembic-init
alembic-first: python-alembic-first-migration
alembic-next: python-alembic-second-migration
alembic-downgrade: python-alembic-downgrading

docker-build-dev:
	docker compose -f 'docker-compose.yml' up -d --build

docker-build-test:
	docker compose -f 'docker-compose.test.yml' up -d --build

docker-build-prod:
	docker compose -f 'docker-compose.prd.yml' up -d --build

docker-pull:
	docker compose pull

docker-stop:
	docker compose down

docker-build-version:
	docker build -t val-api:2.0.X -f Dockerfile .

docker-build-latest:
	docker build -t val-api:latest -f Dockerfile .

docker-tag-version:
	docker tag val-api:2.0.X evanhs/val-api:2.0.X

docker-tag-latest:
	docker tag val-api:latest evanhs/val-api:latest

docker-push-version:
	docker push evanhs/val-api:2.0.X

docker-push-latest:
	docker push evanhs/val-api:latest

pytest-auth:
	pytest .\app\tests\auth.py

pytest-user:
	pytest .\app\tests\user.py

pytest-post:
	pytest .\app\tests\post.py

pytest-follow:
	pytest .\app\tests\follow.py

python-alembic-init:
	alembic init --template pyproject alembic

python-alembic-first-migration:
	alembic upgrade head

python-alembic-second-migration:
	alembic revision -m "Add a column"

python-alembic-downgrading:
	alembic downgrade base
