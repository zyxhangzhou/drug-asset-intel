import { useState } from 'react'

// The standalone process overview (docs/流程说明.html), framed inside the site and sized to its content.
export default function Guide() {
  const [height, setHeight] = useState(1600)
  return (
    <iframe
      src="/guide.html"
      title="流程说明"
      className="guide-frame"
      style={{ height }}
      onLoad={(e) => {
        const doc = e.currentTarget.contentDocument
        if (!doc) return
        const fit = () => setHeight(doc.documentElement.scrollHeight)
        fit()
        new ResizeObserver(fit).observe(doc.body)
      }}
    />
  )
}
