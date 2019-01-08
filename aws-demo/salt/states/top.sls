base:
  '*':
    - docker
    - users

  'master':
    - ssc
    - haproxy
    - p4.broker
    - p4.p4dctl

  'p4d-host':
    - disks
    - p4.server
    - p4python
    - p4.p4dctl
    - p4.client
    - perlmods
    - p4.checkpoint

  'app-host': []
