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

# Troubleshooting
If you get the error:
```
------
failed to solve with frontend dockerfile.v0: failed to create LLB definition: failed to authorize: rpc error: code = Unknown desc = failed to fetch anonymous token
```
This is because we are fetching the python image from artifactory
For this reason you need to set your proxy parameters in the shell where 
you are going to build the image:

```
export http_proxy="http://aproxy.corproot.net:8080"
export https_proxy="http://aproxy.corproot.net:8080"
export no_proxy="localhost,.vptt.ch,.swissptt.ch,.corproot.net,.sharedtcs.net,.swisscom.com,127.0.0.1,localhost"
export HTTP_PROXY="http://aproxy.corproot.net:8080"
export HTTPS_PROXY="http://aproxy.corproot.net:8080"
export NO_PROXY="localhost,.vptt.ch,.swissptt.ch,.corproot.net,.sharedtcs.net,.swisscom.com,127.0.0.1,locahost"
```

## How to Run
- launch your docker
- start runing the image -> a container will start executing and after it's doen
with the tests it will exit:
Exit status 0 if all went well
Exit status 1 if there where errors

## Changelog

### Version 0.1
Initial release