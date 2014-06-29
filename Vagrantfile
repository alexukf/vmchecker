# -*- mode: ruby -*-
# vim: set ft=ruby :

$apt_repositories = <<SCRIPT
apt-get update
apt-get install python-flask
apt-get install python-sqlalchemy
apt-get install python-voluptuous
apt-get install python-magic
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

  config.vm.provider "virtualbox" do |vb|
      # Use VBoxManage to customize the VM. For example to change memory:
      # vb.customize ["modifyvm", :id, "--memory", "1024"]
  end
end
