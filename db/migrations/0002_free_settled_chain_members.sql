-- A student may sit in only one live proposal at a time. 0001 counted
-- every member row that was not rejected as live, so members of an
-- executed or expired proposal stayed locked out of every later one.
-- Track settlement on the member row and only count unsettled rows.

alter table swap_chain_members
    add column settled boolean not null default false;

update swap_chain_members m
set settled = true
from swap_proposals p
where p.id = m.proposal_id and p.status <> 'proposed';

drop index swap_chain_members_one_live;

create unique index swap_chain_members_one_live
    on swap_chain_members (student_id)
    where not settled;
