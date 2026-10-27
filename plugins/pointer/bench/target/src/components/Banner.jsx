import { getParam } from '../lib/params.js'

export default function Banner() {
  const msg = getParam('welcome')
  return <header dangerouslySetInnerHTML={{ __html: msg }} />
}
