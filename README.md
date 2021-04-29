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

1. (optional) Spin up and access the VM. (NOTE: when you spin up the VM for the first time, it might not finish all the provisioning process, just provision it again.)

    ```sh
    $ vagrant up
    $ vagrant ssh

    # provision the VM again if needed.
    $ vagrant up --provision    
    ```
    **NOTE: the project root directory is synced with `/vagrant` in the VM**

2. Test docker installation

    ```sh
    docker run hello-world
    ```

3. Spin up the Authorizing Server with docker-compose

    ```sh
    cd /vagrant/AuthSrvr
    docker-compose up
    ```

4. Test the endpoints with POSTMAN or curl from your host machine (NOTE: replace `localhost` with `192.168.33.10` if you're using vagrant VM.)

    ```sh
    # list all licenses
    curl -X GET http://localhost:5000/licenses        
    ```

5. Build image and spin up the example containerized app (also a Flask server). When the container is spun up, you should see the license printed out.

    ```sh
    cd /vagrant/dist
    # If you want to run the unobfuscated code, use cd /vagrant/App
    docker build -t app:1.0 . 
    docker run --rm -p 9090:9090 --name app app:1.0

    # If you successfully get a license:
    {"message":"OK","public_key":"ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCpHX+NnnL1++9iynu8iU8b/tBIGfaZafsIzmpvCvB3QVP+sxsoK8gLFGdmiPk4D18kOn/CZ98B9AysOC22kJjBN/w8gOtya+yDgwoMSBlpIbskKhlbz4s5to5yQyFME7UWU9D3wmRtl0pIR1aU3c9YqqL13NXGfS5OJxrvUzJPvKLowQ8cnac5OqQzI82/k3Wl/ZQOLZtHGQcfbX/Fe8UJDWL5SDJ/cxFkzhtwxwfkJw8BoS2T/hVY2LUB/59AmzgGDMTMhsk4A7QMLboqE7LZJ76Znr2GBiP3orjNdVLqN4l9ClW/PSDMDPaRrKCeibbAaDqN4WEuke5Fe+tVpyst","status":200}
    ```

6. Test the endpoints with POSTMAN or curl from your host machine. (NOTE: replace `localhost` with `192.168.33.10` if you're using vagrant VM.)

    ```sh
    # get the welcome page
    curl -X GET http://localhost:9090/

    # get a fibonacci number
    curl -X GET http://localhost:9090/fibonacci?number=10 
    ```

7. Stop the App with `ctrl+c` and you should see the log for revoking license:

   ```sh
   {"message":"Revoked"}
   License has been revoked on this server.
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

## (Optional) How to rebuild obfuscated package
If you changed code in `App/`, **Inside the vagrant VM**, run
```sh
   cd /vagrant
   pip3 install pyarmor
   export PATH=$PATH:/home/vagrant/.local/bin
   bash App/obfuscate.sh
```
The new obfuscated package will be in `dist/`.