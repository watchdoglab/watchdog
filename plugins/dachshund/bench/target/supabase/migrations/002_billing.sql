create table invoices (
  id uuid primary key default gen_random_uuid(),
  org_id uuid references orgs(id),
  owner_id uuid references auth.users(id),
  amount_cents int not null,
  card_last4 text,
  created_at timestamptz default now()
);

alter table invoices enable row level security;

create policy invoices_all on invoices for all to anon, authenticated
  using (true) with check (true);

create view invoice_summary as
  select org_id, sum(amount_cents) as total, max(card_last4) as sample_card
  from invoices group by org_id;

create function get_invoice_total(uid uuid) returns bigint
language sql security definer as $$
  select coalesce(sum(amount_cents), 0) from invoices where owner_id = uid;
$$;
