{% from 'docker/map.jinja' import docker with context %}

docker_service:
  service.running:
    - name:     {{ docker.service.name }}
    - enable:   {{ docker.service.enable }}
    - require:
{% if grains['os'] == 'Amazon' %}
      - pkg:    docker
{% else %}
      - pkg:    {{ docker.package.name }}
{% endif %}

docker-service-reload:
  module.wait:
    - name:     service.reload
    - m_name:   {{ docker.service.name }}

docker-service-restart:
  module.wait:
    - name:     service.restart
    - m_name:   {{ docker.service.name }}
