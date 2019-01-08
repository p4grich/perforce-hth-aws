{% from 'docker/map.jinja' import docker with context %}

docker_package_server:
  pkgrepo:
    - managed
    - humanname:  {{ docker.pkgrepo.humanname }}
    - name:       {{ docker.pkgrepo.name }}
{% if grains.os_family == 'Debian' %}
    - dist:       {{ docker.pkgrepo.dist }}
    - file:       {{ docker.pkgrepo.file }}
    - key_url:    {{ docker.pkgrepo.key_url }}
{% elif grains.os_family == 'RedHat' %}
    - baseurl:    {{ docker.pkgrepo.baseurl }}
    - gpgkey:     {{ docker.pkgrepo.gpgkey }}
    - gpgcheck:   {{ docker.pkgrepo.gpgcheck }}
{% endif %}
