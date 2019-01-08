p4:
  broker:
    base_install: True
    config:
      perforce-broker-ssl:
        path:   /etc/perforce/p4broker-ssl.conf
        source: salt://p4/broker/files/master_broker-ssl.conf.jinja
      perforce-broker:
        path:   /etc/perforce/p4broker.conf
        source: salt://p4/broker/files/master_broker.conf.jinja
    certs:
      p4ssldir:
        path:     /etc/perforce/sslkeys
        user:     perforce
        group:    perforce
        mode:     700
  p4dctl:
    config:
      main:
        source: salt://p4/p4dctl/files/master_p4dctl_main.jinja
    services:
      running:
        - broker-ssl
        - broker
