hello-world:
	echo "hello world"

docker-build:
	docker build -t dofuseye-bot .

docker-run:
	docker run -d dofuseye-bot

publish-heroku:
	heroku container:push worker --app=dofuseye-bot
	heroku container:release worker --app=dofuseye-bot
