{% from 'runit/map.jinja' import runit with context %}

runit_package:
  pkg.installed:
    - name:     {{ runit.package.name }}
    - version:  {{ runit.package.version }}
