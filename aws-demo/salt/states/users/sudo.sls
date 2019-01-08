{% for user_name, user in pillar.get('users', {}).items() %}
  {% if (user.absent is not defined or not user.absent) and
     ('sudo' in user and user.sudo.get('enable', False)) %}

users_{{ user_name }}_sudoers_file:
  file.managed:
    - name:   /etc/sudoers.d/{{ user_name }}
    - user:   root
    - group:  root
    - mode:   440
    - require:
      - user: {{ user_name }}
    - contents: |
    {%- for rule in user.sudo.get('rules', []) %}
        {{ user_name }} {{ rule }}
    {%- endfor %}
  {% else %}

users_{{ user_name }}_sudoers_file:
  file.absent:
    - name:   /etc/sudoers.d/{{ user_name }}

  {% endif %}
{% endfor %}
