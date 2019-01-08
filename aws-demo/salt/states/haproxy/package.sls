{% from 'haproxy/map.jinja' import haproxy with context %}

{% if grains.os_family == 'Debian' %}
include:
  - haproxy.pkgrepo
{% endif %}

haproxy_package:
  pkg.installed:
    - name:       {{ haproxy.package.name }}
    - refresh:    {{ haproxy.package.refresh }}
{% if grains.os_family == 'Debian' %}
    - require:
      - pkgrepo:  haproxy_pkg_repo
{% endif %}
