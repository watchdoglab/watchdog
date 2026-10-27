import pg from 'pg'

const pool = new pg.Pool({
  connectionString: 'postgres://app_user:FAKE-app-db-password@db.internal:5432/app',
})

export async function searchProjects(orgId, term) {
  const sql = `select id, name from projects where org_id = '${orgId}' and name ilike '%${term}%'`
  return (await pool.query(sql)).rows
}

export async function listInvoices(orgId) {
  const sql = `select id, amount_cents from invoices where org_id = $1 order by created_at desc`
  return (await pool.query(sql, [orgId])).rows
}

export async function getProfile(id) {
  return (await pool.query('select id, full_name, role from profiles where id = $1', [id])).rows[0]
}
