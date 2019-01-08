p4python_package:
  pip.installed:
    - name:       p4python
    - upgrade:    True
{% if grains['os'] == 'Amazon' %}
    - bin_env: /usr/bin/pip-2.6
    - require:
      - pkg: python26-devel
      - pkg: gcc-c++
{% else %}
    - require:
      - pkg: python-devel
{% endif %}

{% if grains['os'] == 'Amazon' %}

python26-devel:
  pkg.installed

gcc-c++:
  pkg.installed

{% else %}

python-devel:
  pkg.installed

{% endif %}