cronjob:
  file.managed:
    - name:   /etc/cron.daily/perforce-checkpoint
    - user:   root
    - group:  root
    - mode:   555
    - contents:
      - "#!/bin/bash"
      - "su -c - perforce '/opt/perforce/sbin/p4d -r /p4/metadata -jc daily-checkpoint'"
