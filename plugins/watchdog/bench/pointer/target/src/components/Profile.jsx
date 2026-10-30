export default function Profile({ user }) {
  return (
    <aside>
      <a href={user.website}>Website</a>
      <a href={user.blog} target="_blank">Blog</a>
      <iframe src={user.embedUrl} width="400" height="300" />
    </aside>
  )
}
