{% for user_name, user in pillar.get('users', {}).items()
  if user.absent is not defined or not user.absent %}

  {%- if user == None -%}
    {%- set user = {} -%}
  {%- endif -%}

  {%- set home            = user.get('home',            "/home/%s" % user_name) -%}

  {%- if 'prime_group' in user and 'name' in user['prime_group'] %}
    {%- set user_group = user.prime_group.name -%}
  {%- else -%}
    {%- set user_group = user_name -%}
  {%- endif %}

  {%- if user.get('manage_bashrc', False) -%}

users_{{ user_name }}_user_bashrc:
  file.managed:
    - name:   {{ home }}/.bashrc
    - user:   {{ user_name }}
    - group:  {{ user_group }}
    - mode:   640
    - source:
      - salt://users/files/{{ user_name }}/bashrc
      - salt://users/files/default_bashrc
    - template: jinja
    - require:
      - user: users_{{ user_name }}_user
      - file: users_{{ user_name }}_user

  {% endif %} # end if manage_bashrc

  {%- if user.get('manage_profile', False) -%}

users_{{ user_name }}_user_profile:
  file.managed:
    - name:   {{ home }}/.profile
    - user:   {{ user_name }}
    - group:  {{ user_group }}
    - mode:   640
    - source:
      - salt://users/files/{{ user_name }}/profile
      - salt://users/files/default_profile
    - template: jinja
    - require:
      - user: users_{{ user_name }}_user
      - file: users_{{ user_name }}_user

  {% endif %} # end if manage_profile

  {% if 'user_files' in user %}
    {% for file_type, files in user.get('user_files', {}).items() %}

      {% if files == None %}
        {% set files = {} %}
      {% endif %}

      {% if file_type == 'directories' %}

        {% for dir_name, dir in files.items() %}

users_files_{{ user_name }}_{{ dir_name }}_directory:
  file.directory:
    {% if 'paths' in dir %}
    - names:
      {% for path in dir.get('paths', []) %}
      - {{ path }}
      {% endfor %}
    {% else %}
    - name:     {{ dir.get('path', '') }}
    {% endif %}
    - user:     {{ user_name }}
    - group:    {{ user_group }}
    - mode:     {{ dir.get('mode', 770) }}
    - makedirs: True
    - require:
      - user:   users_{{ user_name }}_user
      {% for require_type, require in dir.get('require', []) %}
      - {{ require_type }}: {{ require }}
      {% endfor %} # endfor require_type, require

        {% endfor %} # endfor dir_name, dir

      {% elif file_type == 'files' %}

        {% for file_name, file in files.items() %}

user_files_{{ user_name }}_{{ file_name }}_file:
  file.managed:
    - name:       {{ file.get('path', '') }}
    - user:       {{ user_name }}
    - group:      {{ user_group }}
    - mode:       {{ file.get('mode', 440) }}
    {% if 'source' in file %}
    - source:     {{ file.get('source', '') }}
    {% endif %}
    - template:   {{ file.get('template', 'jinja') }}
    - makedirs:   {{ file.get('makedirs', False) }}
    - dirmode:    {{ file.get('dirmode', 750) }}
    {% if 'watch_in' in file %}
    - watch_in:
      {% for watch in file.get('watch_in', []) %}
        {% for type, target in watch.items() %}
      - {{ type }}: {{ target }}
        {% endfor %}
      {% endfor %}
    {% endif %}
    - require:
      - user:     users_{{ user_name }}_user
    {% for dir, dir_config in user.get('user_files', {}).get('directories', {}).items() %}
    - require:
      - file:     users_files_{{ user_name }}_{{ dir }}_directory
    {% endfor %}
        {% endfor %} # endfor file_name, file

      {% endif %} # endif file_type == 'directories', elif file_type == 'files'

    {% endfor %} # endfor file_type, files

  {% endif %} #endif 'user_files' in user

{% endfor %} # end for user_name, user
