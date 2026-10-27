create table orgs (
  id uuid primary key default gen_random_uuid(),
  name text not null
);

create table profiles (
  id uuid primary key references auth.users(id),
  org_id uuid references orgs(id),
  full_name text,
  role text not null default 'member',
  ssn text,
  created_at timestamptz default now()
);

create table org_members (
  org_id uuid references orgs(id),
  user_id uuid references auth.users(id),
  primary key (org_id, user_id)
);

create table plans (
  id serial primary key,
  name text not null,
  price_cents int not null
);

create table projects (
  id uuid primary key default gen_random_uuid(),
  org_id uuid references orgs(id),
  name text not null,
  notes text
);

create table legacy_logins (
  id serial primary key,
  email text not null,
  password text not null
);

alter table profiles enable row level security;
alter table org_members enable row level security;
alter table plans enable row level security;

create policy profiles_read on profiles for select using (true);

create policy profiles_update on profiles for update
  using (auth.uid() = id);

create policy members_read on org_members for select
  using (user_id = auth.uid());

create policy plans_read on plans for select using (true);

create policy projects_org on projects for all
  using (org_id::text = auth.jwt() -> 'user_metadata' ->> 'org_id');
