import sanitizeHtml from "sanitize-html";

function sanitizeHTML(html: string): string {
  return sanitizeHtml(html, {
    allowedTags: sanitizeHtml.defaults.allowedTags.concat([
      "details",
      "summary",
      "svg",
      "circle",
      "path",
    ]),
    allowedAttributes: false,
  });
}

export { sanitizeHTML };
