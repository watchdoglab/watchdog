export default function Comment({ comment }) {
  return (
    <article>
      <h4>{comment.author}</h4>
      <div dangerouslySetInnerHTML={{ __html: comment.body }} />
    </article>
  )
}
