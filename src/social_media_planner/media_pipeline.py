from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request

from pathlib import Path

from social_media_planner.models import GeneratedImageAsset

PLACEHOLDER_PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8"
    "/x8AAusB9Y5fL3QAAAAASUVORK5CYII="
)


def render_content_pack(
    research_brief: str,
    idea_output: str,
    writing_output: str,
    planning_output: str,
) -> str:
    return "\n".join(
        [
            "# Content Pack",
            "",
            "## Research Brief",
            research_brief.strip(),
            "",
            "## Content Ideas",
            idea_output.strip(),
            "",
            "## Drafts",
            writing_output.strip(),
            "",
            "## Weekly Plan",
            planning_output.strip(),
            "",
        ]
    )


def write_content_outputs(
    output_dir: Path,
    research_brief: str,
    idea_output: str,
    writing_output: str,
    planning_output: str,
    media_output: str,
) -> tuple[str, str]:
    content_pack = render_content_pack(
        research_brief=research_brief,
        idea_output=idea_output,
        writing_output=writing_output,
        planning_output=planning_output,
    )
    media_pack = "# Media Pack\n\n" + media_output.strip() + "\n"
    (output_dir / "content_pack.md").write_text(content_pack, encoding="utf-8")
    (output_dir / "weekly_app_launch_plan.md").write_text(
        planning_output.strip() + "\n", encoding="utf-8"
    )
    (output_dir / "media_pack.md").write_text(media_pack, encoding="utf-8")
    return content_pack, media_pack


def build_image_briefs(
    app_name: str,
    media_pack: str,
    platforms: str,
) -> list[GeneratedImageAsset]:
    prompts = [
        (
            "instagram-carousel-cover",
            "Carousel Cover Concept",
            "instagram",
            "carousel_cover",
            (
                f"Design a polished Instagram carousel cover for {app_name}. "
                f"Style: modern startup explainer, strong typography, high contrast, "
                f"clean product-marketing layout. Use themes from this media brief: {media_pack[:500]}"
            ),
        ),
        (
            "designed-explainer-post",
            "Designed Explainer Post",
            "instagram",
            "designed_post",
            (
                f"Create a designed social post for {app_name} that explains the app clearly. "
                f"Include room for app UI callouts, concise educational copy, and a premium social "
                f"design aesthetic. Platforms: {platforms}. Reference this brief: {media_pack[:500]}"
            ),
        ),
        (
            "reel-cover-frame",
            "Reel Cover Frame",
            "instagram",
            "cover_frame",
            (
                f"Create a bold reel cover image for {app_name}. It should stop the scroll, support "
                f"a faceless productivity app launch, and leave safe space for title text. "
                f"Reference this brief: {media_pack[:500]}"
            ),
        ),
    ]
    return [
        GeneratedImageAsset(
            asset_id=asset_id,
            title=title,
            prompt=prompt,
            platform=platform,
            asset_type=asset_type,
            output_path=f"images/{asset_id}.png",
            status="pending",
        )
        for asset_id, title, platform, asset_type, prompt in prompts
    ]


def generate_images(
    briefs: list[GeneratedImageAsset],
    output_dir: Path,
    api_key: str | None,
) -> list[GeneratedImageAsset]:
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    generated: list[GeneratedImageAsset] = []
    for brief in briefs:
        file_path = output_dir / brief.output_path
        if not api_key:
            file_path.write_bytes(base64.b64decode(PLACEHOLDER_PNG))
            generated.append(
                brief.model_copy(update={"status": "mock_image", "revised_prompt": brief.prompt})
            )
            continue
        try:
            revised_prompt = _generate_openai_image(file_path, brief.prompt, api_key)
            generated.append(
                brief.model_copy(update={"status": "generated", "revised_prompt": revised_prompt})
            )
        except (urllib.error.URLError, ValueError) as exc:
            file_path.write_bytes(base64.b64decode(PLACEHOLDER_PNG))
            generated.append(
                brief.model_copy(
                    update={
                        "status": "error_placeholder",
                        "error": str(exc),
                        "revised_prompt": brief.prompt,
                    }
                )
            )
    (output_dir / "generated_image_manifest.json").write_text(
        json.dumps([asset.model_dump() for asset in generated], indent=2),
        encoding="utf-8",
    )
    return generated


def _generate_openai_image(file_path: Path, prompt: str, api_key: str) -> str:
    payload = {
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": "1024x1024",
        "quality": "medium",
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        body = json.loads(response.read().decode("utf-8"))
    data = body.get("data", [])
    if not data:
        raise ValueError("OpenAI image generation returned no image data.")
    image_base64 = data[0].get("b64_json")
    if not image_base64:
        raise ValueError("OpenAI image generation response did not include b64_json.")
    file_path.write_bytes(base64.b64decode(image_base64))
    return str(data[0].get("revised_prompt", prompt))
