Docker-based integration tests using pytest
=====

# Description
This docker image starts with a simple python image.
On top ot was been added the pytest library.
It will also be added the traffic generators and the kafka consumers.

For pytest you can find more infromation: [pytest](http://doc.pytest.org/) 

In the future we will need a  [docker-compose](https://docs.docker.com/compose/).
There we will specify all necessary containers in a `docker-compose.yml` file and and
`pytest-docker` will spin them up for the duration of our tests.

# Build of the python-nat-pytest
You can use the following command:
```
docker build -f ./Dockerfile_pytest -t python-nat-pytest .
```

## How to Run
- launch your docker
- start runing the image -> a container will start executing and after it's doen
with the tests it will exit:
Exit status 0 if all went well
Exit status 1 if there where errors

## Changelog

### Version 0.1
Initla release