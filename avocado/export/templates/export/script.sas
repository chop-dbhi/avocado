data SAS_EXPORT;
INFILE "{{ data_filename }}" TRUNCOVER DSD firstobs=2;{% for format in informats %}
    informat {{ format|safe }};{% endfor %}
    {% for format in formats %}
    format {{ format|safe }};{% endfor %}
    {% for input in inputs %}
    input {{ input|safe }};{% endfor %}
run;

proc contents;
run;

data SAS_EXPORT;
    set SAS_EXPORT;{% for label in labels %}
    label {{ label|safe }};{% endfor %}
run;

proc format;{% for value in values %}
    {{ value|safe }};{% endfor %}
run;

data SAS_EXPORT;
    set SAS_EXPORT;{% for value in value_formats %}
    {{ value|safe }};{% endfor %}
run;

/*proc contents data=SAS_EXPORT;*/
/*proc print data=SAS_EXPORT;*/
run;
quit;
