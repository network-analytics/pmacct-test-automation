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
Use the command:
```
docker run -i --log-driver=none -a stdin -a stdout -a stderr --name pytest_img -p 8000:8000 python-nat-pytest

```
Alternative:
- Start your Docker desktop appliaction
- locate the image
- press the **Run** button
- go to Containers/apps
- locate the last container that run
- select by single clicking
there you can see the output of the container after it run

This container will run the tests and then will exit.
Exit status 0 if all passt through well
Exit status 1 if there where errors during the tests (it fails a test on purposse at the moment)

## Changelog

### Version 0.1
Initial release