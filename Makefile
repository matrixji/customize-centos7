IMAGE=customize-centos7

all: build

docker_image:
	sudo docker build  -t $(IMAGE) \
		--build-arg http_proxy=$(http_proxy) \
		--build-arg https_proxy=$(https_proxy) \
		--build-arg no_proxy=$(no_proxy) \
		dockers/build

ut: docker_image
	docker run --rm -v$(shell pwd):/src \
		-e PYTHONPATH=/src/scripts/python-libs \
		-e http_proxy=$(http_proxy) \
		-e https_proxy=$(https_proxy) \
		-e no_proxy=$(no_proxy) \
		$(IMAGE) \
		python3 -m pytest /src

lint: docker_image
	docker run --rm -v$(shell pwd):/src \
		-e PYTHONPATH=/src/scripts/python-libs \
		-e http_proxy=$(http_proxy) \
		-e https_proxy=$(https_proxy) \
		-e no_proxy=$(no_proxy) \
		$(IMAGE) \
		python3 -m pylint --rcfile /src/pylintrc /src/scripts/build.py /src/scripts/python-libs/

build: docker_image
	docker run --rm -v$(shell pwd):/src \
		-e PYTHONPATH=/src/scripts/python-libs \
		-e http_proxy=$(http_proxy) \
		-e https_proxy=$(https_proxy) \
		-e no_proxy=$(no_proxy) \
		$(IMAGE) \
		python3 /src/scripts/build.py build /src


clean:
	rm -fr *.iso build

.PHONY: docker_image clean

