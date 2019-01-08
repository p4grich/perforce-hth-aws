{% from 'runit/map.jinja' import runit with context %}

{% for service_name, service in runit.get('services', {}).items() %}

  {%- if service == None -%}
  {%- set service = {} -%}
  {%- endif -%}

  {% set enabled = service.get('enabled', False) %}

  {% if enabled %}

runit_service_{{ service_name }}_symlink:
  file.symlink:
    - name:       {{ runit.enabled_dir }}/{{ service_name }}
    - target:     {{ runit.available_dir }}/{{ service_name }}
    - user:       {{ service.get('user',  'root') }}
    - group:      {{ service.get('group', 'root') }}
    - force:      True
    - mode:       770
    - require:
      - file:     runit_service_{{ service_name }}_dir

runit_service_{{ service_name }}_service:
  service.running:
    - name:       {{ service_name }}
    - provider:   runit
    - require:
      - file:     runit_service_{{ service_name }}_symlink
      - service:  {{ runit.service.name }}
    - watch:
      - file:     runit_service_{{ service_name }}_run_file

# TODO: Fix and re-enable.
# runit_service_{{ service_name }}_log_service:
  # service.running:
    # - name:       {{ service_name }}/log
    # - provider:   runit
    # - require:
      # - file:     runit_service_{{ service_name }}_symlink
    # - watch:
      # - file:     runit_service_{{ service_name }}_log_run_file
      # - file:     runit_service_{{ service_name }}_log_config_file

runit-service-{{ service_name }}-reload:
  module.wait:
    - name:       runit.reload
    - m_name:     {{ service_name }}

runit-service-{{ service_name }}-restart:
  module.wait:
    - name:       runit.restart
    - m_name:     {{ service_name }}

  {% else %}

runit_service_{{ service_name }}_symlink:
  file.absent:
    - name:       {{ runit.enabled_dir }}/{{ service_name }}

  {% endif %} # endif enabled
{% endfor %} # endfor service_name, service
