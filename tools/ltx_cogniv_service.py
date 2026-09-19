"""CLI for the frozen Cogniv LTX video generation service."""

from __future__ import annotations

import argparse

from media_generation.service import CognivVideoGenerationService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a story-scene clip with the frozen LTX BF16 multiscale system.")
    parser.add_argument("--scene-id", default="chapter_04_scene_05", help="Story scene ID to generate.")
    parser.add_argument("--profile", default="safe", choices=["safe", "quality", "retry"], help="Generation profile.")
    parser.add_argument("--prompt", default=None, help="Optional override prompt.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    service = CognivVideoGenerationService()
    result = service.generate_for_scene(args.scene_id, profile_name=args.profile, prompt_override=args.prompt)
    print(f"Video generated: {result.output_path}")
    print(f"Profile: {result.metadata.get('profile')}")
    print(f"Duration: {result.duration_seconds}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
