import { useEffect, useRef } from 'react'

export default function Tooltip({ text }) {
  const ref = useRef(null)
  useEffect(() => { ref.current.innerHTML = `<b>${text}</b>` }, [text])
  return <span ref={ref} />
}
