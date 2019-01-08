{% from 'haproxy/map.jinja' import haproxy with context %}

haproxy_config_file:
  file.managed:
    - name:     {{ haproxy.config_file.path }}
    - user:     {{ haproxy.config_file.user }}
    - group:    {{ haproxy.config_file.group }}
    - mode:     {{ haproxy.config_file.mode }}
{% if haproxy.config_file.manage %}
    - source:   {{ haproxy.config_file.source }}
{% endif %}
    - template: jinja
    - context:
      config:   {{ haproxy.config }}
    - require:
      - pkg:    {{ haproxy.package.name }}
    - watch_in:
      - module: haproxy-service-reload
