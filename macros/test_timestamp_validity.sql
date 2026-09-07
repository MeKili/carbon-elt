{% test timestamp_validity(model, start_column, end_column) %}

select *
from {{ model }}
where {{ start_column }} >= {{ end_column }}

{% endtest %}
