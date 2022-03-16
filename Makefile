hello-world:
	echo "hello world"

docker-build:
	docker build -t dofuseye-bot .

docker-run:
	docker run -d dofuseye-bot

publish-heroku:
	heroku container:push worker
	heroku container:release worker
