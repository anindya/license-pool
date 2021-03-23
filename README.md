# license-pool
Practical Computer Security Project under Prof. Kevin Chen
# Project Title

One Paragraph of project description goes here

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 
See deployment for notes on how to deploy the project on a live system.

### Prerequisites

```
virtualbox + vagrant
OR
docker
```

### Installing

1. (optional) Spin up and access the VM

    ```sh
    $ vagrant up
    $ vagrant ssh
    ```

2. Test docker installation

    ```sh
    docker run hello-world
    ```

3. Build Docker image for the Flask App

    ```sh
    docker build -t flaskapp:1.0 .
    ```

4. Spin up a Flask App Container

    ```sh
    docker run -p 8080:8080 flaskapp:1.0
    ```

5. Open `http://localhost:8080/` or `http://192.168.33.10:8080/`(if using vagrant VM) in a browser on your host machine. You should see the front page of the Flask App.

6. Use `ctrl+c` to stop the container, run `docker container ps -a` to see all the containers (including stopped ones), and then use `docker rm <container_name or container_id>` to remove the container.

7. Spin up multiple containers with docker-compose

    ```sh
    docker-compose up -d  # run as deamon
    ```

8. Test the endpoints with POSTMAN or curl from your host machine

    ```sh
    curl -X POST http://192.168.33.10:8080/counters/test  # create a new counter called test
    curl -X PUT http://192.168.33.10:8080/counters/test   # increment the count by 1
    curl -X GET http://192.168.33.10:8080/counters        # list all counters
    ```

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Acknowledgments
- The `Vagrantfile`, `Dockerfile`, `docker-compose.yml`, and the `service` directory are based on John J. Rofrano's [nyu-devops/lab-kubernetes](https://github.com/nyu-devops/lab-kubernetes)
