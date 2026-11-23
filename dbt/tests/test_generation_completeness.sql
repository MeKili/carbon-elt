-- Validate that generation mix for each half-hour window sums to ~100%
select
    valid_from,
    valid_to,
    sum(percentage) as total_pct
from {{ source('raw', 'raw_generation') }}
group by valid_from, valid_to
having sum(percentage) not between 99 and 101
