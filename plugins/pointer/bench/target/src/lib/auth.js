import { login } from '../api.js'
import { getParam } from './params.js'

export async function signIn(email, password) {
  const { token, session } = await login(email, password)
  localStorage.setItem('auth_token', token)
  document.cookie = `session=${session}; path=/`
  window.location.href = getParam('next') || '/'
}

export function getToken() {
  return localStorage.getItem('auth_token')
}

export function debugAuth() {
  console.log('auth state', getToken())
}
