import { useState } from 'react'

export default function Filter({ pins }) {
  const [expr, setExpr] = useState('')
  const shown = expr ? pins.filter((p) => eval(expr)) : pins
  localStorage.setItem('theme', 'dark')
  return (
    <div>
      <input value={expr} onChange={(e) => setExpr(e.target.value)} />
      <span>{shown.length}</span>
    </div>
  )
}
