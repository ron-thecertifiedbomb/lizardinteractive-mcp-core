import os
import json
from mcp.server.fastmcp import FastMCP
from config import SAFE_DIRECTORY
from utils.security import is_safe_path
from utils.markdown import extract_title, slugify, parse_sections, build_blog_schema

DEFAULT_IMAGE = "https://res.cloudinary.com/dx3atgryf/image/upload/v1777564396/iwhgn96jsdmsr48wervs.jpg"


def register(mcp: FastMCP):

    @mcp.tool()
    def convert_md_to_lizard_json(file_path: str, category: str = "Content") -> str:
        """
        Converts a Markdown blog draft file into the Lizard Interactive JSON schema.
        Optimized for high-performance Next.js client templates.
        """
        # Strip leading slashes to prevent os.path.join from discarding SAFE_DIRECTORY
        # if the AI accidentally passes an absolute-style path (e.g. "/drafts/post.md")
        full_path = os.path.join(SAFE_DIRECTORY, file_path.lstrip("/\\"))
        if not is_safe_path(full_path):
            return "Security Error: Access denied outside of Repositories folder."

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            title = extract_title(content)
            slug = slugify(title)
            blog_data = build_blog_schema(title, slug, category, DEFAULT_IMAGE)
            blog_data["sections"] = parse_sections(content)

            output_dir = os.path.join(SAFE_DIRECTORY, "blog_output")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{slug}.json")
            if not is_safe_path(output_path):
                return "Security Error: Output path traversal detected."
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(blog_data, f, indent=2)

            return f"Success: Generated {slug}.json in safe directory."
        except Exception as e:
            return f"Error during MD conversion: {str(e)}"

    @mcp.tool()
    def stage_dynamic_blog_data(
        content: str = "",
        category: str = "Content",
        custom_slug: str = "",
        image_url: str = DEFAULT_IMAGE,
    ) -> str:
        """
        Dynamically generates a Lizard Interactive JSON schema from pasted Markdown input.
        Use this to paste the whole document into the 'content' field.
        """
        if not content.strip():
            return "Error: Content field is blank. Please paste your Markdown text."

        try:
            title = extract_title(content)
            # Ensure custom_slug is explicitly slugified to prevent invalid filename characters
            slug = slugify(custom_slug.strip()) if custom_slug.strip() else slugify(title)
            blog_data = build_blog_schema(title, slug, category, image_url)
            blog_data["sections"] = parse_sections(content)

            output_dir = os.path.join(SAFE_DIRECTORY, "blog_output")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"pending_{slug}.json")
            if not is_safe_path(output_path):
                return "Security Error: Output path traversal detected."
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(blog_data, f, indent=2)

            return f"Successfully staged '{title}' under the '{category}' category. Ready for injection."
        except Exception as e:
            return f"Dynamic Processing Error: {str(e)}"