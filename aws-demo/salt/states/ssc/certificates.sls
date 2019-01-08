/etc/pki/p4www.key:
  x509.private_key_managed:
    - bits: 4096
    - new: False

/etc/ssl/p4www.crt:
  x509.certificate_managed:
    - signing_private_key: '/etc/pki/p4www.key'
    - CN: www.example.perforce.cloud.com
    - days_valid: 365
    - backup: True
    - require:
      - pip: m2crypto

etc_ssl_p4www_pem_perms:
  file.managed:
    - name: /etc/ssl/p4www.pem
    - user: root
    - group: root
    - mode: 400

/etc/ssl/p4www.pem:
  file.append:
    - sources:
      - file:///etc/pki/p4www.key
      - file:///etc/ssl/p4www.crt
    - require:
      - file: etc_ssl_p4www_pem_perms
      - x509: /etc/ssl/p4www.crt
