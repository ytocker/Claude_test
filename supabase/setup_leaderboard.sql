-- Skybit leaderboard recovery SQL.
--
-- Run once in the Supabase SQL editor (Database → SQL editor) for the
-- project whose URL is in the SUPABASE_URL secret. Idempotent: safe to
-- re-run. After running, hard-refresh the deployed site to verify the
-- top-10 populates.
--
-- Why this exists: schema.sql is the canonical reference, but the live
-- database can drift (manual policy edits, dashboard changes, Supabase
-- platform default changes). When a SELECT against `scores` returns
-- 200 OK with `[]`, the most common cause is RLS without a matching
-- permissive policy for the anon role, OR missing table-level grants.
-- This file re-establishes both layers.

-- 1. Schema-level grants. Without USAGE on the schema, no role can
-- "see" tables in it.
grant usage on schema public to anon, authenticated;

-- 2. Table-level grants. Without these, RLS doesn't even get a chance
-- to evaluate -- the role is rejected at the postgres permissions
-- layer first.
grant select         on table public.scores to anon, authenticated;
grant insert         on table public.scores to anon, authenticated;
grant select, insert on table public.plays  to anon, authenticated;

-- 3. RLS policies. Drop-and-recreate is intentional -- if the policy
-- exists but is restrictive or evaluates false, an empty array is
-- exactly what the anon client sees. Recreating with a permissive
-- USING (true) for SELECT is the documented Supabase pattern for a
-- public read-only leaderboard.
alter table public.scores enable row level security;
alter table public.plays  enable row level security;

drop policy if exists "anon read scores"   on public.scores;
drop policy if exists "anon insert scores" on public.scores;
drop policy if exists "anon insert plays"  on public.plays;

create policy "anon read scores"
    on public.scores for select
    to anon, authenticated
    using (true);

create policy "anon insert scores"
    on public.scores for insert
    to anon, authenticated
    with check (true);

create policy "anon insert plays"
    on public.plays for insert
    to anon, authenticated
    with check (true);

-- 4. Submit-failure diagnostic column. Nullable and optional, so the
-- normal at-death telemetry row (which never sets it) is unaffected.
-- leaderboard.submit re-fires the telemetry with this column set when a
-- top-10 submit is dropped, recording the gate that rejected it
-- (plausibility:*, js:chain-mismatch, js:http NNN, js:exception:*, …) so
-- a silently-lost score can be traced from the DB without the player's
-- DevTools. Idempotent.
alter table public.plays add column if not exists submit_error text;

-- 5. Fix HTTP 409 Conflict on submit. The live `scores` table (created via
-- the Supabase dashboard) has an identity `id` PRIMARY KEY. If rows were
-- ever loaded with explicit ids (CSV import, restore, manual insert), the
-- identity sequence lags behind max(id), so new auto-inserts collide on the
-- PK (SQLSTATE 23505) -> HTTP 409, silently dropping a real top-10 score.
-- Resync the sequence so the next id is past max(id). Idempotent. (Duplicate
-- names and tied scores are intentionally allowed — do NOT add a UNIQUE
-- there; the block below only removes one if it drifted in, never the PK.)
do $$
declare seq text := pg_get_serial_sequence('public.scores', 'id');
begin
  if seq is not null then
    perform setval(seq,
                   (select coalesce(max(id), 0) + 1 from public.scores),
                   false);
  end if;
end $$;

do $$
declare c record;
begin
  for c in select conname from pg_constraint
           where conrelid = 'public.scores'::regclass and contype = 'u'
  loop
    execute format('alter table public.scores drop constraint %I', c.conname);
  end loop;
end $$;

-- 6. Sanity check. Should return one or more rows after running.
-- Comment-out before keeping this file in version control if you don't
-- want the SELECT to run on every paste.
-- select count(*) as score_rows from public.scores;
-- Recent dropped submits, most common first:
-- select submit_error, count(*) from public.plays
--   where submit_error is not null group by 1 order by 2 desc;
