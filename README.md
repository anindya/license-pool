# license-pool
Practical Computer Security Project under Prof. Kevin Chen

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 
See deployment for notes on how to deploy the project on a live system.

### Prerequisites

```
virtualbox + vagrant
```
OR
```
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

3. Go to the project root directory (it's synced with `/vagrant` in the VM)

    ```sh
    cd /vagrant
    ```

4. Spin up example Flask app and Postgres database instance with docker-compose

    ```sh
    cd /vagrant/AuthSrvr
    docker-compose up
    ```

5. Test the endpoints with POSTMAN or curl from your host machine

    ```sh
    # create a new licenses
    curl -H "Content-Type: application/json" \
    -X POST \
    -d '{"username":"tester","used_by":null,"is_available":true,"private_key_path":"keys/private_tester_1.pem","public_key_path":"keys/public_tester_1.pem","last_issued":null}' \
    http://192.168.33.10:5000/licenses

    # update a licenses
    curl -H "Content-Type: application/json" \
    -X POST \
    -d '{"username":"tester","used_by":"12d8c6885151","is_available":false,"private_key_path":"keys/private_tester_1.pem","public_key_path":"keys/public_tester_1.pem","last_issued":"2021-03-24 04:05:06"}' \
    http://192.168.33.10:5000/licenses/1

    # list all licenses
    curl -X GET http://192.168.33.10:5000/licenses        
    ```

6. Build image and spin up the example containerized app (also a Flask server)

    ```sh
    cd /vagrant/App
    docker build -t app:1.0 . 
    docker run --rm -p 9090:9090 --name app app:1.0
    ```

7. Test the endpoints with POSTMAN or curl from your host machine

    ```sh
    # get the welcome page
    curl -X GET http://192.168.33.10:9090/

    # get a fibonacci number
    curl -X GET http://192.168.33.10:9090/fibonacci?number=10 
    ```

8. Remove the containers and/or images

    ```sh
    # list all containers
    docker container ls -a #list all containers, including stopped ones

    # remove containers
    docker rm <container name or container id> #<another container name> ...etc.

    #remove images
    docker rmi <image name>
    ```
   
9.  Exit and stop the VM

    ```sh
    exit
    vagrant halt
    ```
<!-- ## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system -->

## Acknowledgments
- The `Vagrantfile`, `Dockerfile`, `docker-compose.yml`, `config.py` and the `service` directory are based on John J. Rofrano's [nyu-devops/lab-kubernetes](https://github.com/nyu-devops/lab-kubernetes) and [nyu-devops/lab-flask-tdd](https://github.com/nyu-devops/lab-flask-tdd)
