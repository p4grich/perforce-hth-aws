{% from 'docker/map.jinja' import docker with context %}

{% for image_name, image in docker.get('container', {}).items() %}

docker_image_{{ image_name }}:
  dockerng.running:
    - name:       {{ image.name }}
    - image:      {{ image.image }}
  {% for key, value in image.get('options', {}).items() %}
    - {{ key }}:  {{ value }}
  {% endfor %}
    - require:
      - pip:      docker-py
      - service:  {{ docker.service.name }}

{% endfor %}
