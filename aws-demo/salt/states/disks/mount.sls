include:
  - disks.format

metadata_mount:
  mount.mounted:
    - name: /p4/metadata
    - device: /dev/metadata_vg/metadata_lv
    - fstype: xfs
    - mkmnt: True
    - opts: defaults
    - persist: True
    - mount: True
    - dump: 0
    - pass_num: 0
    - require:
      - blockdev: /dev/metadata_vg/metadata_lv

p4data_mount:
  mount.mounted:
    - name: /p4/depots
    - device: /dev/p4data_vg/p4data_lv
    - fstype: xfs
    - mkmnt: True
    - opts: defaults
    - persist: True
    - mount: True
    - dump: 0
    - pass_num: 0
    - require:
      - blockdev: /dev/p4data_vg/p4data_lv

/p4/depots:
  file.directory:
    - user: perforce
    - group: perforce
    - mode: 755
    - require:
      - user: perforce

/p4/metadata:
  file.directory:
    - user: perforce
    - group: perforce
    - mode: 755
    - require:
      - user: perforce
