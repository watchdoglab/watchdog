insert into storage.buckets (id, name, public) values ('avatars', 'avatars', true);
insert into storage.buckets (id, name, public) values ('invoice-pdfs', 'invoice-pdfs', true);

create policy "avatars read" on storage.objects for select
  using (bucket_id = 'avatars');

create policy "avatars write" on storage.objects for insert to authenticated
  with check (bucket_id = 'avatars' and (storage.foldername(name))[1] = auth.uid()::text);

