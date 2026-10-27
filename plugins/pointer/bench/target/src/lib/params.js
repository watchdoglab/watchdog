export function getParam(name) {
  return new URLSearchParams(window.location.search).get(name) || ''
}
