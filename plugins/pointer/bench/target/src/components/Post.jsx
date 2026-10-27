import { marked } from 'marked'

export default function Post({ markdown }) {
  const html = marked.parse(markdown)
  return <div className="post" dangerouslySetInnerHTML={{ __html: html }} />
}
