perl-Digest-MD5-File:
  pkg.installed
{% if grains['os'] == 'Amazon' %}
perl-Sys-Syslog:
  pkg.installed
{% else %}
perl-Unix-Syslog:
  pkg.installed
{% endif %}