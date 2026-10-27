import { useEffect, useState } from 'react'
import { getPins } from './api.js'
import { getToken } from './lib/auth.js'
import Banner from './components/Banner.jsx'
import Comment from './components/Comment.jsx'
import Post from './components/Post.jsx'
import Profile from './components/Profile.jsx'
import Notice from './components/Notice.jsx'
import Filter from './components/Filter.jsx'
import Tooltip from './components/Tooltip.jsx'

export default function App() {
  const [pins, setPins] = useState([])
  useEffect(() => { getPins(getToken()).then(setPins) }, [])
  return (
    <main>
      <Banner />
      <Notice />
      <Filter pins={pins} />
      <div id="widget" />
      {pins.map((p) => (
        <section key={p.id}>
          <Tooltip text={p.title} />
          <Post markdown={p.body} />
          <Comment comment={p.comments[0]} />
          <Profile user={p.author} />
        </section>
      ))}
    </main>
  )
}
