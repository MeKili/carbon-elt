{{ config(
    materialized='table'
) }}

select
    date(valid_from) as intensity_date,
    round(avg(cast(actual as float)), 1) as avg_actual_intensity,
    round(avg(cast(forecast as float)), 1) as avg_forecast_intensity,
    count(*) as reading_count
from {{ ref('stg_national_intensity') }}
where actual is not null
group by date(valid_from)
order by intensity_date desc
