{% from 'docker/map.jinja' import docker with context %}

{% for network_name, network in docker.get('network', {}).items() %}

docker_network_{{ network_name }}:
  dockerng.network_present:
    - name:   {{ network.get('name', network_name) }}
    - containers:
  {% for container in network.get('containers', []) %}
      - {{ container }}
  {% endfor %}

{% endfor %}
