# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.scope = :box
  end

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "centos6-min"
  config.vm.provider "virtualbox" do |v|
    v.memory = 1024
    v.cpus = 2
  end

  config.vm.define :saltmaster do |salt|
    salt.vm.network :private_network, ip: "192.168.44.101"
    salt.vm.hostname = 'salt-master'
    # salt.vm.provision "shell", inline: "systemctl disable firewalld && systemctl stop firewalld"
    salt.vm.provision "shell", inline: "sh /vagrant/setup/init.sh --ip 192.168.44.101 --id master --password d3l1c10u5 --swarmurl https://192.168.44.101:8443"
    # salt.vm.synced_folder "salt/states", "/srv/salt"
    # salt.vm.synced_folder "salt/pillar", "/srv/pillar"

    # expose the http and p4d ports
    salt.vm.network "forwarded_port", guest: 80, host: 8080
    salt.vm.network "forwarded_port", guest: 443, host: 8443
    salt.vm.network "forwarded_port", guest: 1666, host: 8666
    salt.vm.network "forwarded_port", guest: 1667, host: 8667
    salt.vm.network "forwarded_port", guest: 9000, host: 9000
  end

  # test minion 
  config.vm.define :p4dhost do |salt|
    salt.vm.provider "virtualbox" do | v |
        # make 2 disks for metadata and archive data
        (1..2).each do |i| 
          file = "p4disk#{i}.vdi"
          v.customize ['createhd', '--filename', file, '--size', 50 * 1024] unless File.exist? file
          v.customize ['storageattach', :id, '--storagectl', 'SATA Controller', '--port', i, '--device', 0, '--type', 'hdd', '--medium', file]
        end

      end

    salt.vm.network :private_network, ip: "192.168.44.201"
    salt.vm.hostname = "p4d-host"
    # salt.vm.provision "shell", inline: "systemctl disable firewalld && systemctl stop firewalld"
    salt.vm.provision "shell", inline: "sh /vagrant/setup/init.sh --ip 192.168.44.101 --id p4d-host"
  end

  # test minion 
  config.vm.define :apphost do |salt|
    salt.vm.network :private_network, ip: "192.168.44.51"
    salt.vm.hostname = "app-host"
    # salt.vm.provision "shell", inline: "systemctl disable firewalld && systemctl stop firewalld"
    salt.vm.provision "shell", inline: "sh /vagrant/setup/init.sh --ip 192.168.44.101 --id app-host"
  end

end
