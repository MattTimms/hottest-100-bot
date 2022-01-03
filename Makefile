REPO=hottest100

build:
	DOCKER_BUILDKIT=1 docker build . \
		-t $(REPO):latest \
