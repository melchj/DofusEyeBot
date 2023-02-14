hello-world:
	echo "hello world"

docker-build:
	docker build -t dofuseye-bot .

docker-run:
	docker run --name dofuseye-bot -d dofuseye-bot
