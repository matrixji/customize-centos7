IMAGE=customize-centos7

all: build

docker_image:
	docker build -q -t $(IMAGE) .

ut: docker_image
	docker run --rm -v$(shell pwd):/src -e PYTHONPATH=/src/scripts/python-libs $(IMAGE) \
		python3 -m pytest /src

lint: docker_image
	docker run --rm -v$(shell pwd):/src -e PYTHONPATH=/src/scripts/python-libs $(IMAGE) \
		python3 -m pylint --rcfile /src/pylintrc /src/scripts/build.py /src/scripts/python-libs/

build: docker_image
	docker run --rm -v$(shell pwd):/src -e PYTHONPATH=/src/scripts/python-libs $(IMAGE) \
		python3 /src/scripts/build.py build /src

.PHONY: docker_image

