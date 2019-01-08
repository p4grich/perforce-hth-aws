{% from 'haproxy/map.jinja' import haproxy with context %}

haproxy_pkg_repo:
  pkgrepo.managed:
    - ppa:  {{ haproxy.package.source }}
