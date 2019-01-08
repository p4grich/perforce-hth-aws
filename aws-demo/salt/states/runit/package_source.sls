{% from 'runit/map.jinja' import runit with context %}

# Install runit from the source package.

runit_package_source_download:
  archive.extracted:
    - name:           {{ runit.package_source.path }}
    - source:         {{ runit.package_source.source }}
    - source_hash:    {{ runit.package_source.source_hash }}
    - archive_format: tar
