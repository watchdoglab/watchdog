import DOMPurify from 'dompurify'

const FOOTER = '<small>&copy; Pinboard</small>'

export default function Notice() {
  const dirty = new URLSearchParams(window.location.search).get('notice') || ''
  return (
    <>
      <p dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(dirty) }} />
      <footer dangerouslySetInnerHTML={{ __html: FOOTER }} />
    </>
  )
}
