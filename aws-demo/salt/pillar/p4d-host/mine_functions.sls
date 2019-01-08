mine_functions:
  xfs: []
  network.ip_addrs: []
  network.interfaces: []
  network.interface_ip:
{% if grains['os'] == 'Amazon' %}
    - eth0
{% else %}
    - eth1
{% endif %}