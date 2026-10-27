import { createClient } from '@supabase/supabase-js'

const url = process.env.NEXT_PUBLIC_SUPABASE_URL
const serviceKey = 'FAKE-service-role-key-do-not-use'

export const supabase = createClient(url, serviceKey)

export async function signUp(email, password, orgId, role) {
  return supabase.auth.signUp({
    email,
    password,
    options: { data: { org_id: orgId, role } },
  })
}
