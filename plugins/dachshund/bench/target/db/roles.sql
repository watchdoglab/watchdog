create role app_user login superuser password 'FAKE-app-db-password';
create role reporting login password 'FAKE-reporting-password';
create role readonly_reports nologin;

grant all on all tables in schema public to anon;
grant all on all tables in schema public to authenticated;
grant select on invoice_summary to readonly_reports;
grant readonly_reports to reporting;
