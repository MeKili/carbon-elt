{{ config(
    materialized='table'
) }}

select
    date(valid_from) as generation_date,
    fuel_type,
    round(avg(cast(percentage as float)), 2) as avg_percentage
from {{ ref('stg_generation') }}
group by date(valid_from), fuel_type
order by generation_date desc, avg_percentage desc
