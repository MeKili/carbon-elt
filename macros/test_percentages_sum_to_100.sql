{% test percentages_sum_to_100(model, column_name, group_by_cols) %}

select
    {{ group_by_cols }},
    sum({{ column_name }}) as total_pct
from {{ model }}
group by {{ group_by_cols }}
having sum({{ column_name }}) not between 99.5 and 100.5

{% endtest %}
