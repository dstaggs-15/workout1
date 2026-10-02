-- Optional Supabase setup. Do not run against unrelated projects without selecting them.
create table public.workout_reports (
 user_id uuid primary key references auth.users(id) on delete cascade,
 report jsonb not null,
 updated_at timestamptz not null default now()
);
create table public.workout_weights (
 user_id uuid not null references auth.users(id) on delete cascade,
 date date not null,
 weight_lb double precision not null check (weight_lb > 0 and weight_lb < 1500),
 note text not null default '' check (length(note) <= 200),
 primary key (user_id,date)
);
alter table public.workout_reports enable row level security;
alter table public.workout_weights enable row level security;
revoke all on public.workout_reports, public.workout_weights from anon;
grant select on public.workout_reports to authenticated;
grant select,insert,update,delete on public.workout_weights to authenticated;
grant all on public.workout_reports,public.workout_weights to service_role;
create policy report_owner_read on public.workout_reports for select to authenticated using ((select auth.uid())=user_id);
create policy weight_owner_read on public.workout_weights for select to authenticated using ((select auth.uid())=user_id);
create policy weight_owner_insert on public.workout_weights for insert to authenticated with check ((select auth.uid())=user_id);
create policy weight_owner_update on public.workout_weights for update to authenticated using ((select auth.uid())=user_id) with check ((select auth.uid())=user_id);
create policy weight_owner_delete on public.workout_weights for delete to authenticated using ((select auth.uid())=user_id);
