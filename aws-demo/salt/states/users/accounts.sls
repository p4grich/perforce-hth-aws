{%- for user_name, user in pillar.get('users', {}).items()
  if user.absent is not defined or not user.absent %}

  {%- if user == None -%}
  {%- set user = {} -%}
  {%- endif -%}

  {%- set home = user.get('home', "/home/%s" % user_name) -%}

  {%- if 'prime_group' in user and 'name' in user['prime_group'] %}
  {%- set user_group = user.prime_group.name -%}
  {%- else -%}
  {%- set user_group = user_name -%}
  {%- endif %}

{% for group in user.get('groups', []) %}
users_{{ user_name }}_{{ group }}_group:
  group:
    - name: {{ group }}
    - present
{% endfor %}

users_{{ user_name }}_user:

  # Create the user's home directory as required.
  {% if user.get('create_home', True) %}
  file.directory:
    - name:     {{ home }}
    - user:     {{ user_name }}
    - group:    {{ user_group }}
    - mode:     {{ user.get('user_dir_mode', '0750') }}
    - require:
      - user:   users_{{ user_name }}_user
      - group:  {{ user_group }}
  {%- endif %}

  # Create the user's group.
  group.present:
    - name: {{ user_group }}
    {%- if 'prime_group' in user and 'gid' in user['prime_group'] %}
    - gid: {{ user['prime_group']['gid'] }}
    {%- elif 'uid' in user %}
    - gid: {{ user['uid'] }}
    {%- endif %}

  # Create the user.
  user.present:
    - name: {{ user_name }}
    - shell: {{ user.get('shell', '/bin/bash') }}

    {% if user.get('create_home', True) %}
    - home: {{ home }}
    {% endif %}

    {% if 'uid' in user -%}
    - uid: {{ user['uid'] }}
    {% endif -%}

    {% if 'password' in user -%}
    - password: '{{ user['password'] }}'
    {% endif %}

    - enforce_password: {{ user.get('enforce_password', True) }}
    - empty_password:   {{ user.get('empty_password', False) }}

    {% if user.get('system', False) -%}
    - system: True
    {% endif -%}

    {% if 'prime_group' in user and 'gid' in user['prime_group'] -%}
    - gid: {{ user['prime_group']['gid'] }}
    {% else -%}
    - gid_from_name: True
    {% endif -%}

    {% if 'fullname' in user %}
    - fullname: {{ user['fullname'] }}
    {% endif -%}

    - createhome:     {{ user.get('create_home', True) }}
    - remove_groups:  {{ user.get('remove_groups', 'True') }}

    - groups:
      - {{ user_group }}
      {% for group in user.get('groups', []) -%}
      - {{ group }}
      {% endfor %}
    - require:
      - group: {{ user_group }}
      {% for group in user.get('groups', []) -%}
      - group: {{ group }}
      {% endfor %}
      {% for key, value in user.get('require', {}).items() -%}
      - {{ key }}: {{ value }}
      {% endfor %}

{% if 'ssh_keys' in user %}

# Ensure that the ~/.ssh directory for each user is present and configured with
# the correct permissions.
user_ssh_dir_{{ user_name }}:
  file.directory:
    - name:     {{ user.get('home', '/home/{0}'.format(user_name)) }}/.ssh
    - user:     {{ user_name }}
    - group:    {{ user_group }}
    - makedirs: True
    - mode:     700
    - require:
      - user:   users_{{ user_name }}_user
      - group:  {{ user_group }}
      - file:   users_{{ user_name }}_user

  {% if 'public_auth' in user['ssh_keys'] %}
  {% for key in user['ssh_keys']['public_auth'] %}
users_ssh_auth_{{ user_name }}_{{ loop.index0 }}:
  ssh_auth.present:
    - user: {{ user_name }}
    - name: {{ key }}
    - require:
      - user: users_{{ user_name }}_user
      - file: users_{{ user_name }}_user
  {% endfor %}
  {% endif %}
{% endif %}

{% endfor %}
