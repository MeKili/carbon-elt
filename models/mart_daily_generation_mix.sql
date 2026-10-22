{{ config(
    materialized='incremental',
    unique_key=['generation_date', 'fuel_type'],
    on_schema_change='fail'
) }}

select
    date(valid_from) as generation_date,
    fuel_type,
    round(avg(cast(percentage as float)), 2) as avg_percentage
from {{ ref('stg_generation') }}
{% if execute and flags.full_refresh == False %}
    where date(valid_from) > (select coalesce(max(generation_date), '1900-01-01') from {{ this }})
{% endif %}
group by date(valid_from), fuel_type
order by generation_date desc, avg_percentage desc
