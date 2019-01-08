{% from 'runit/map.jinja' import runit with context %}

runit_service_available_dir:
  file.directory:
    - name:     {{ runit.available_dir }}
    - user:     root
    - group:    root
    - mode:     775

runit_service_enabled_dir:
  file.directory:
    - name:     {{ runit.enabled_dir }}
    - user:     root
    - group:    root
    - mode:     775
