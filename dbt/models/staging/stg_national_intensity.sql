{{ config(
    tags=['staging']
) }}

with deduplicated as (
    select
        valid_from,
        valid_to,
        forecast,
        actual,
        index,
        row_number() over (partition by valid_from, valid_to order by valid_from) as dedup_rank
    from {{ source('raw', 'raw_national_intensity') }}
)

select
    valid_from,
    valid_to,
    forecast,
    actual,
    index
from deduplicated
where dedup_rank = 1
