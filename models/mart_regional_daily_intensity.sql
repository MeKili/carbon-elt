{{ config(
    materialized='incremental',
    unique_key=['intensity_date', 'region_code'],
    on_schema_change='fail'
) }}

select
    date(valid_from) as intensity_date,
    region_code,
    round(avg(cast(actual as float)), 1) as avg_actual_intensity,
    round(avg(cast(forecast as float)), 1) as avg_forecast_intensity,
    count(*) as reading_count
from {{ ref('stg_regional_intensity') }}
where actual is not null
{% if execute and flags.full_refresh == False %}
    and date(valid_from) > (select coalesce(max(intensity_date), '1900-01-01') from {{ this }})
{% endif %}
group by date(valid_from), region_code
order by intensity_date desc, region_code
