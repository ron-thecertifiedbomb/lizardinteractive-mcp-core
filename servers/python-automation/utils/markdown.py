import re
from datetime import datetime, timezone


def extract_title(content: str) -> str:
    """Extracts the first H1 heading from Markdown content."""
    match = re.search(r'^#\s+(.*)', content, re.MULTILINE)
    return match.group(1) if match else "Untitled Post"


def slugify(text: str) -> str:
    """Converts a string into a URL-safe slug."""
    return re.sub(r'[^a-z0-9]', '-', text.lower()).strip('-')


def utc_timestamp() -> str:
    """Returns the current UTC time as a precise ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_sections(content: str) -> list[dict]:
    """
    Splits Markdown content by H# headings (ignoring those inside code blocks)
    and returns a list of Lizard Interactive section objects.
    """
    parts = []
    current_text = []
    in_code_block = False

    for line in content.splitlines():
        if line.strip().startswith('```'):
            in_code_block = not in_code_block

        if line.startswith('#') and not in_code_block:
            if current_text:
                parts.append('\n'.join(current_text))
                current_text = []
            parts.append(line)
        else:
            current_text.append(line)

    if current_text:
        parts.append('\n'.join(current_text))

    sections = []
    current_section = None

    for part in parts:
        part = part.strip()
        if not part:
            continue

        if part.startswith('#'):
            if current_section:
                sections.append(current_section)
            header_text = part.lstrip('#').strip()
            current_section = {
                "type": "paragraph",
                "heading": f"#{header_text}",
                "content": "",
                "image": ""
            }
        elif current_section:
            clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', part).replace('\n', ' ').strip()
            current_section["content"] = clean_text

    if current_section:
        sections.append(current_section)

    return sections


def build_blog_schema(
    title: str,
    slug: str,
    category: str,
    image_url: str,
) -> dict:
    """Constructs the base Lizard Interactive blog JSON schema."""
    timestamp = utc_timestamp()
    base_url = re.sub(r'\.(jpg|jpeg|png|webp)$', '', image_url)

    return {
        "id": slug,
        "category": category,
        "title": title,
        "createdAt": timestamp,
        "updatedAt": timestamp,
        "image": f"{base_url}.webp",
        "ogImage": f"{base_url}.jpg",
        "sections": []
    }