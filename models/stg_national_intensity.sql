{{ config(
    materialized='view'
) }}

select
    valid_from,
    valid_to,
    forecast,
    actual,
    index
from {{ source('raw', 'raw_national_intensity') }}
order by valid_from
