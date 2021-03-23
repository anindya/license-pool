# -*- mode: ruby -*-
# vi: set ft=ruby :

######################################################################
# WARNING: You will need the following plugin:
######################################################################
# vagrant plugin install vagrant-docker-compose
if Vagrant.plugins_enabled?
  unless Vagrant.has_plugin?('vagrant-docker-compose')
    puts 'Plugin missing.'
    system('vagrant plugin install vagrant-docker-compose')
    puts 'Dependencies installed, please try the command again.'
    exit
  end
end

######################################################################
# Dev Environment
######################################################################
Vagrant.configure(2) do |config|
  config.vm.box = "bento/ubuntu-20.04"
  # config.vm.hostname = "vagrant"

  # config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 5000, host: 5000, host_ip: "127.0.0.1"
  config.vm.network "forwarded_port", guest: 5432, host: 5432, host_ip: "127.0.0.1"

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  config.vm.network "private_network", ip: "192.168.33.10"
  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Mac users can comment this next line out but
  # Windows users need to change the permission of files and directories
  config.vm.synced_folder ".", "/vagrant", mount_options: ["dmode=755,fmode=644"]

  ############################################################
  # Configure Vagrant to use VirtualBox:
  ############################################################
  config.vm.provider "virtualbox" do |vb|
    # Customize the amount of memory on the VM:
    vb.memory = "2048"
    vb.cpus = 2

    # Fixes some DNS issues on some networks
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
  end

  ############################################################
  # Copy some host files to configure VM like the host
  ############################################################
  # # Copy your .gitconfig file so that your git credentials are correct
  # if File.exists?(File.expand_path("~/.gitconfig"))
  #   config.vm.provision "file", source: "~/.gitconfig", destination: "~/.gitconfig"
  # end

  ############################################################
  # Install common libraries
  ############################################################
  config.vm.provision "shell", inline: <<-SHELL
    # Update and install common packages
    apt-get update && sudo apt-get install -y unzip git tree wget jq gettext bash-completion moreutils
  SHELL

  ############################################################
  # Create a Python 3 environment for development work
  ############################################################
  config.vm.provision "shell", inline: <<-SHELL
    # Install
    apt-get update && apt-get install -y build-essential python3-dev python3-pip python3-venv apt-transport-https
    apt-get upgrade python3
    # Check versions to prove that everything is installed
    python3 --version
    # # Create a Python3 Virtual Environment and Activate it in .profile
    # sudo -H -u vagrant sh -c 'python3 -m venv ~/venv'
    # sudo -H -u vagrant sh -c 'echo ". ~/venv/bin/activate" >> ~/.profile'
    # sudo -H -u vagrant sh -c '. ~/venv/bin/activate && pip install -U pip && pip install wheel && cd /vagrant && pip install -r requirements.txt'

    # Install app dependencies
    cd /vagrant
    pip3 install -r requirements.txt

  SHELL

  ############################################################
  # Provision Docker with Vagrant
  ############################################################
  config.vm.provision "docker" do |d|
    # d.pull_images "alpine"
    d.pull_images "python:3.8-slim"
    # d.pull_images "redis:6-alpine"
    # d.run "redis:6-alpine",
    #   args: "--restart=always -d --name redis -p 6379:6379 -v redis:/data"
  end

  ############################################################
  # Add Docker compose
  ############################################################
  config.vm.provision :docker_compose
  # config.vm.provision :docker_compose,
  #   yml: "/vagrant/docker-compose.yml",
  #   rebuild: true,
  #   run: "always"

end
