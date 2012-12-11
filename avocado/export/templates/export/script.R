# Read Data
data=read.csv("{{ data_filename }}")


# Setting Labels
{% for label in labels %}{{ label|safe }}
{% endfor %}

# Setting Factors
{% for factor in factors %}{{ factor|safe }}
{% endfor %}

# Setting Levels
{% for level in levels %}{{ level|safe }}
{% endfor %}
