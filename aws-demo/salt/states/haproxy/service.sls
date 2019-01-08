{% from 'haproxy/map.jinja' import haproxy with context %}

haproxy_service:
  service.running:
    - name:     {{ haproxy.service.name }}
    - enable:   {{ haproxy.service.enable }}
    - require:
      - pkg:    {{ haproxy.package.name }}

haproxy-service-reload:
  module.wait:
    - name:     service.reload
    - m_name:   {{ haproxy.service.name }}

haproxy-service-restart:
  module.wait:
    - name:     service.restart
    - m_name:   {{ haproxy.service.name }}
