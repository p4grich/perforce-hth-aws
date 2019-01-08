include:
{% if grains['os_family'] == 'Debian' %}
  - runit.package
{% elif grains['os_family'] == 'RedHat' %}
  - runit.package_source
{% endif %}
  - runit.files
  - runit.service
  - runit.service_files
  - runit.services
