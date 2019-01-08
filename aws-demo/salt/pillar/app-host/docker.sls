docker:
  lookup:
    container:
      swarm:
        name:   'perforce-swarm'
        image:  'dscheirer/swarm:0.0.2'
      swarm-cron:
        name:   'perforce-swarm-cron'
        image:  'dscheirer/swarm-cron:0.0.1'
