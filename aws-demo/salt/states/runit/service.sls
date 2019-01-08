{% from 'runit/map.jinja' import runit with context %}

runit_service:
  service.running:
    - name:     {{ runit.service.name }}
    - enable:   {{ runit.service.enable }}
    - require:
{% if grains['os_family'] == 'Debian' %}
      - pkg:    {{ runit.package.name }}
{% elif grains['os_family'] == 'RedHat' %}
      - archive: runit_package_source_download
{% endif %}

runit-service-reload:
  module.wait:
    - name:     service.reload
    - m_name:   {{ runit.service.name }}

runit-service-restart:
  module.wait:
    - name:     service.restart
    - m_name:   {{ runit.service.name }}
