const BASE = 'https://api.pinboard.example'
const ADMIN_API_KEY = 'FAKE-admin-key-0000000000'

export async function getPins(token) {
  const r = await fetch(`${BASE}/pins`, { headers: { Authorization: `Bearer ${token}` } })
  return r.json()
}

export async function deletePin(id) {
  return fetch(`${BASE}/admin/pins/${id}`, {
    method: 'DELETE',
    headers: { 'X-Admin-Key': ADMIN_API_KEY },
  })
}

export async function login(email, password) {
  const r = await fetch(`${BASE}/login`, { method: 'POST', body: JSON.stringify({ email, password }) })
  return r.json()
}
