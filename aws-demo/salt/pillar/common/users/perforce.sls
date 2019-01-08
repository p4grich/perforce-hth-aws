users:
  perforce:
    fullname:         Perforce
    password:         '!'
    enforce_password: True
    uid:              1666
    prime_group:
      name:           perforce
      gid:            1666
    user_files:
      directories:
        perforce_dir:
          path:       /etc/perforce
          mode:       755
        perforce_log_dir:
          path:       /var/log/perforce
          mode:       755
