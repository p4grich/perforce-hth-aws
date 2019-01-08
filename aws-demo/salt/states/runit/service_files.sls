{% from 'runit/map.jinja' import runit with context %}

{% for service_name, service in runit.get('services', {}).items() %}

  {%- if service == None -%}
  {%- set service = {} -%}
  {%- endif -%}

  {%- set service_user  = service.get('user',   'root') %}
  {%- set service_group = service.get('group',  'root') %}

runit_service_{{ service_name }}_dir:
  file.directory:
    - name:   {{ runit.available_dir }}/{{ service_name }}
    - user:   {{ service_user }}
    - group:  {{ service_group }}
    - mode:   770
    - require:
      - file:   runit_service_available_dir

runit_service_{{ service_name }}_run_file:
  file.managed:
    - name:   {{ runit.available_dir }}/{{ service_name}}/run
    - user:   {{ service_user }}
    - group:  {{ service_group }}
    - source: {{ service.get('run_file', '') }}
    - mode:   770
    - template: jinja
    - context:
        service_name: {{ service_name }}}
    - require:
      - file:   runit_service_{{ service_name }}_dir

{% if service.get('down_file', false) %}
runit_service_{{ service_name }}_down_file:
  file.managed:
    - name:   {{ runit.available_dir }}/{{ service_name }}/down
    - user:   {{ service_user }}
    - group:  {{ service_group }}
    - source: {{ service.get('down_file', '') }}
    - mode:   770
    - require:
      - file:   runit_service_{{ service_name }}_dir
{% endif %}

runit_service_{{ service_name }}_log_dir:
  file.directory:
    - name:   {{ runit.available_dir }}/{{ service_name }}/log
    - user:   {{ service_user }}
    - group:  {{ service_group }}
    - mode:   770
    - require:
      - file:   runit_service_{{ service_name }}_dir

runit_service_{{ service_name }}_log_run_file:
  file.managed:
    - name:   {{ runit.available_dir }}/{{ service_name}}/log/run
    - user:   {{ service_user }}
    - group:  {{ service_group }}
    - source: {{ service.get('log_run_file', '') }}
    - mode:   770
    - template: jinja
    - require:
      - file:   runit_service_{{ service_name }}_log_dir

runit_service_{{ service_name }}_log_config_file:
  file.managed:
    - name:     {{ runit.available_dir }}/{{ service_name}}/log/config
    - user:     {{ service_user }}
    - group:    {{ service_group }}
    - source:   {{ service.get('log_config_file', 'salt://runit/files/default_log_config') }}
    - mode:     770
    - require:
      - file:     runit_service_{{ service_name }}_log_dir

  {% for service_control_dir  in ['supervise', 'log/supervise'] %}

runit_service_{{ service_name }}_supervise_dir_{{ service_control_dir }}:
  file.directory:
    - name:     {{ runit.available_dir }}/{{ service_name }}/{{ service_control_dir }}
    - user:     {{ service_user }}
    - group:    {{ service_group }}
    - mode:     770
    - require:
      - file:   runit_service_{{ service_name }}_dir

  {% endfor %} # endfor service_control_dir

  {% for service_control_file in ['supervise/ok', 'supervise/control', 'log/supervise/ok', 'log/supervise/control'] %}

runit_service_{{ service_name }}_supervise_file_{{ service_control_file}}:
  file.mknod:
    - name:     {{ runit.available_dir }}/{{ service_name }}/{{ service_control_file }}
    - ntype:    p
    - user:     {{ service_user }}
    - group:    {{ service_group }}
    - mode:     770
    - require:
      - file:   runit_service_{{ service_name }}_dir

  {% endfor %} # endfor service_control_file

{% endfor %} # endfor service_name, service
