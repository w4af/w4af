<?xml version="1.0" encoding="utf-8"?>
<w4af-run start="{{ start_timestamp }}" start-long="{{ start_time_long }}" version="{{ xml_version }}">

    <w4af-version>{{ w4af_version }}</w4af-version>

    {{ scan_info | safe }}

    {{ scan_status | safe }}

    {% for finding in findings %}
        {{ finding | safe }}
    {% endfor %}

    {% for message, caller in errors %}
    <error caller="{{ caller | escape_attr }}">{{ message | escape_text }}</error>
    {% endfor %}
</w4af-run>
