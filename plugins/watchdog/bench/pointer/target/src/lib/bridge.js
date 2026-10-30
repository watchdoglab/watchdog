import { getToken } from './auth.js'

window.addEventListener('message', (e) => {
  if (e.data.type === 'render') {
    document.getElementById('widget').innerHTML = e.data.html
  }
})

window.addEventListener('message', (e) => {
  if (e.origin !== 'https://app.pinboard.example') return
  if (e.data.type === 'theme') document.documentElement.dataset.theme = e.data.value
})

export function shareSession() {
  window.parent.postMessage({ type: 'session', token: getToken() }, '*')
}
