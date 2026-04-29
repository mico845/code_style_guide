from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_REFERENCES_DIR = ROOT / "references"
HTML_REFERENCES_DIR = ROOT / "references" / "html"
SITE_DIR = ROOT / "site"
SKILL_PATH = ROOT / "SKILL.md"

GENERATED_SITE_FILES = ("index.html", "styles.css")


@dataclass(frozen=True)
class HtmlChapter:
    source_path: Path
    filename: str
    number: int
    title: str


@dataclass(frozen=True)
class MarkdownReference:
    path: Path
    filename: str
    number: int
    description: str


def main() -> None:
    chapters = load_html_chapters()
    SITE_DIR.mkdir(exist_ok=True)
    clean_generated_site_files()
    (SITE_DIR / "index.html").write_text(
        render_index(chapters), encoding="utf-8", newline="\n"
    )
    (SITE_DIR / "styles.css").write_text(render_styles(), encoding="utf-8", newline="\n")
    update_skill_references(load_markdown_references())

    print(f"Loaded {len(chapters)} chapter files from {HTML_REFERENCES_DIR}")
    print(f"Generated {SITE_DIR / 'index.html'}")
    print(f"Generated {SITE_DIR / 'styles.css'}")
    print(f"Updated {SKILL_PATH}")


def load_html_chapters() -> list[HtmlChapter]:
    if not HTML_REFERENCES_DIR.exists():
        raise SystemExit(f"HTML references directory does not exist: {HTML_REFERENCES_DIR}")

    paths = [
        path
        for path in HTML_REFERENCES_DIR.glob("*.html")
        if path.name.lower() != "index.html"
    ]
    chapters = [chapter_from_path(path) for path in paths if chapter_number(path.name) is not None]
    chapters.sort(key=lambda chapter: (chapter.number, chapter.filename.lower()))

    if not chapters:
        raise SystemExit(f"No numbered HTML chapter files found in {HTML_REFERENCES_DIR}")
    return chapters


def load_markdown_references() -> list[MarkdownReference]:
    paths = list(MARKDOWN_REFERENCES_DIR.glob("*.md"))
    references = [markdown_reference_from_path(path) for path in paths]
    references.sort(key=lambda reference: (reference.number, reference.filename.lower()))

    if not references:
        raise SystemExit(f"No numbered markdown reference files found in {MARKDOWN_REFERENCES_DIR}")
    return references


def markdown_reference_from_path(path: Path) -> MarkdownReference:
    number = reference_number(path.name)

    return MarkdownReference(
        path=path,
        filename=path.name,
        number=number if number is not None else 10_000,
        description=description_from_filename(path.name),
    )


def chapter_from_path(path: Path) -> HtmlChapter:
    number = chapter_number(path.name)
    if number is None:
        raise ValueError(f"Chapter file name must start with a number: {path.name}")

    content = path.read_text(encoding="utf-8")
    return HtmlChapter(
        source_path=path,
        filename=path.name,
        number=number,
        title=first_html_heading(content) or title_from_filename(path.name),
    )


def chapter_number(filename: str) -> int | None:
    return reference_number(filename)


def reference_number(filename: str) -> int | None:
    match = re.match(r"^(\d+)", filename)
    return int(match.group(1)) if match else None


def first_html_heading(content: str) -> str | None:
    match = re.search(r"<h[1-3][^>]*>(.*?)</h[1-3]>", content, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return normalize_text(strip_tags(match.group(1)))


def strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value)


def normalize_text(value: str) -> str:
    return html.unescape(re.sub(r"\s+", " ", value)).strip()


def title_from_filename(filename: str) -> str:
    stem = Path(filename).stem
    stem = re.sub(r"^(\d+)[.-]?", r"\1. ", stem)
    stem = stem.replace("-", " ").replace("_", " ")
    return re.sub(r"\s+", " ", stem).strip().title()


def description_from_filename(filename: str) -> str:
    stem = Path(filename).stem
    stem = re.sub(r"^\d+[.-]?", "", stem)
    return stem.replace("-", " ").replace("_", " ").strip() or filename


def clean_generated_site_files() -> None:
    for filename in GENERATED_SITE_FILES:
        path = SITE_DIR / filename
        if path.exists():
            path.unlink()


def update_skill_references(references: list[MarkdownReference]) -> None:
    if not SKILL_PATH.exists():
        raise SystemExit(f"SKILL.md does not exist: {SKILL_PATH}")

    skill = SKILL_PATH.read_text(encoding="utf-8")
    references_block = render_skill_references(references)
    pattern = re.compile(r"\n## References\n.*?(?=\n## |\Z)", flags=re.DOTALL)

    if pattern.search(skill):
        updated = pattern.sub("\n" + references_block, skill, count=1)
    else:
        updated = skill.rstrip() + "\n\n" + references_block
    SKILL_PATH.write_text(updated.rstrip() + "\n", encoding="utf-8", newline="\n")


def render_skill_references(references: list[MarkdownReference]) -> str:
    lines = [
        "## References",
        "",
    ]
    lines.extend(
        f"- `references/{reference.filename}` - {reference.description}."
        for reference in references
    )
    return "\n".join(lines)


def render_index(chapters: list[HtmlChapter]) -> str:
    first_chapter = chapters[0]
    nav_items = "\n".join(render_nav_item(chapter, chapter == first_chapter) for chapter in chapters)
    options = "\n".join(render_select_option(chapter, chapter == first_chapter) for chapter in chapters)
    initial_src = html.escape(chapter_src(first_chapter), quote=True)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>C++ Code Style Guide</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <aside class="sidebar">
    <div class="brand">C++ Code Style Guide</div>
    <select class="chapter-select" aria-label="Chapter index">
{options}
    </select>
    <nav class="chapter-nav" aria-label="Chapter index">
{nav_items}
    </nav>
  </aside>
  <main class="viewer">
    <iframe
      id="chapter-frame"
      title="C++ Code Style Guide chapter"
      src="{initial_src}"
    ></iframe>
  </main>
  <script>
    const frame = document.querySelector("#chapter-frame");
    const links = Array.from(document.querySelectorAll(".chapter-link"));
    const select = document.querySelector(".chapter-select");

    function activate(src) {{
      frame.src = src;
      links.forEach((link) => {{
        const active = link.dataset.src === src;
        link.classList.toggle("active", active);
        link.setAttribute("aria-current", active ? "page" : "false");
      }});
      select.value = src;
    }}

    links.forEach((link) => {{
      link.addEventListener("click", (event) => {{
        event.preventDefault();
        activate(link.dataset.src);
      }});
    }});

    select.addEventListener("change", () => activate(select.value));
  </script>
</body>
</html>
"""


def render_nav_item(chapter: HtmlChapter, active: bool) -> str:
    classes = "chapter-link active" if active else "chapter-link"
    current = "page" if active else "false"
    src = html.escape(chapter_src(chapter), quote=True)
    title = html.escape(chapter.title)
    filename = html.escape(chapter.filename)
    return (
        f'      <a class="{classes}" href="{src}" data-src="{src}" aria-current="{current}">'
        f'<span>{title}</span><small>{filename}</small></a>'
    )


def render_select_option(chapter: HtmlChapter, selected: bool) -> str:
    selected_attr = " selected" if selected else ""
    src = html.escape(chapter_src(chapter), quote=True)
    title = html.escape(chapter.title)
    return f'      <option value="{src}"{selected_attr}>{title}</option>'


def chapter_src(chapter: HtmlChapter) -> str:
    return f"../references/html/{chapter.filename}"


def render_styles() -> str:
    return """* {
  box-sizing: border-box;
}

html,
body {
  height: 100%;
}

body {
  margin: 0;
  color: #202124;
  background: #f6f7f9;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", sans-serif;
}

.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  width: 312px;
  padding: 22px 16px;
  overflow-y: auto;
  background: #ffffff;
  border-right: 1px solid #d7dce2;
}

.brand {
  margin-bottom: 16px;
  color: #111827;
  font-size: 18px;
  font-weight: 700;
}

.chapter-select {
  display: none;
  width: 100%;
  min-height: 40px;
  margin-bottom: 14px;
  padding: 8px 10px;
  border: 1px solid #c8d0d9;
  border-radius: 6px;
  background: #ffffff;
  color: #202124;
}

.chapter-nav {
  display: grid;
  gap: 6px;
}

.chapter-link {
  display: grid;
  gap: 2px;
  padding: 10px 12px;
  border-radius: 6px;
  color: #2f3847;
  text-decoration: none;
}

.chapter-link:hover {
  background: #edf2fa;
}

.chapter-link.active {
  background: #dce7f9;
  color: #0b57d0;
}

.chapter-link span {
  overflow-wrap: anywhere;
  font-weight: 600;
  line-height: 1.35;
}

.chapter-link small {
  overflow-wrap: anywhere;
  color: #5f6b7a;
  font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
  font-size: 12px;
}

.viewer {
  height: 100%;
  margin-left: 312px;
}

iframe {
  display: block;
  width: 100%;
  height: 100%;
  border: 0;
  background: #ffffff;
}

@media (max-width: 820px) {
  body {
    min-height: 100%;
  }

  .sidebar {
    position: static;
    width: auto;
    max-height: none;
    border-right: 0;
    border-bottom: 1px solid #d7dce2;
  }

  .chapter-select {
    display: block;
  }

  .chapter-nav {
    display: none;
  }

  .viewer {
    height: calc(100vh - 116px);
    margin-left: 0;
  }
}
"""


if __name__ == "__main__":
    main()
