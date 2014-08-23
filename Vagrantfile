# -*- mode: ruby -*-
# vim: set ft=ruby :

$packages = <<SCRIPT
apt-get update

apt-get install -y zsh
chsh -s /bin/zsh {,vagrant}

apt-get install -y python-pip
apt-get install -y python-paramiko python-ldap python-magic

apt-get install -y python-dev libffi-dev libgit2-dev
pip install flask
pip install sqlalchemy
pip install voluptuous
pip install cffi
pip install requests
pip install click
pip install pygit2==0.19.0

apt-get install -y git
apt-get install -y acl
apt-get install -y apache2 libapache2-mod-python
SCRIPT

VAGRANTFILE_API_VERSION = "2"

unless Vagrant.has_plugin?("vagrant-omnibus")
    raise "Omnibus plugin not installed"
end

VAGRANTFILE_BOX_NAME = "trusty-x86_64"
VAGRANTFILE_BOX_URL  = "https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = VAGRANTFILE_BOX_NAME
  config.vm.box_url = VAGRANTFILE_BOX_URL

  config.vm.network :forwarded_port, host: 5000, guest: 5000
  config.vm.network :forwarded_port, host: 8080, guest: 80

  config.vm.provider "virtualbox" do |vb|
      # Use VBoxManage to customize the VM. For example to change memory:
      # vb.customize ["modifyvm", :id, "--memory", "1024"]
  end

  config.vm.provision "shell", inline: $packages
end
