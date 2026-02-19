import argparse
import os
import re
from pathlib import Path
from typing import List

from dotenv import load_dotenv

from .cache import CacheStore
from .pdf_export import markdown_to_pdf
from .research import extract_notes, fetch_sources, search_serper
from .writer import build_plan, critic_report, write_report


def parse_args():
    p = argparse.ArgumentParser(description="Research + Structured Report Agent (v2)")
    p.add_argument("--topic", required=True, help="Report topic")
    p.add_argument("--audience", default="Senior software engineers", help="Target audience")
    p.add_argument("--length", default="medium", choices=["short", "medium", "long"], help="Report length")
    p.add_argument("--search", action="store_true", help="Enable Serper search")
    p.add_argument("--max-sources", type=int, default=8, help="Maximum sources to fetch")
    p.add_argument("--iterations", type=int, default=2, help="Critic loop iterations")
    p.add_argument("--urls", default="", help="Comma-separated extra URLs")
    p.add_argument("--outdir", default="outputs", help="Output directory")
    p.add_argument("--model", default="gpt-5", help="OpenAI model")
    p.add_argument("--no-cache", action="store_true", help="Disable caching")
    return p.parse_args()


def _queries_from_plan(plan: str) -> List[str]:
    queries = []
    for line in plan.splitlines():
        text = line.strip().lstrip("-*0123456789. ").strip()
        if not text:
            continue
        if "query" in line.lower() or (3 <= len(text.split()) <= 12 and re.search(r"[a-zA-Z]", text)):
            queries.append(text)
    # de-duplicate and keep bounded
    deduped = []
    seen = set()
    for q in queries:
        if q.lower() in seen:
            continue
        seen.add(q.lower())
        deduped.append(q)
    return deduped[:10]


def run() -> None:
    args = parse_args()
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Missing OPENAI_API_KEY. Put it in .env or environment.")
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    cache = CacheStore(outdir=outdir, enabled=not args.no_cache)

    manual_urls = [u.strip() for u in args.urls.split(",") if u.strip()]

    plan = build_plan(topic=args.topic, audience=args.audience, length=args.length, model=args.model, cache=cache)

    all_urls = list(manual_urls)
    if args.search:
        queries = _queries_from_plan(plan)
        found_urls = search_serper(queries=queries, max_sources=args.max_sources, cache=cache)
        for u in found_urls:
            if u not in all_urls:
                all_urls.append(u)

    all_urls = all_urls[: args.max_sources]
    sources = fetch_sources(all_urls, cache=cache) if all_urls else []
    notes = extract_notes(sources=sources, model=args.model, cache=cache) if sources else []

    report_md = ""
    review = None

    for _ in range(max(1, args.iterations)):
        report_md = write_report(
            topic=args.topic,
            audience=args.audience,
            length=args.length,
            plan=plan,
            notes=notes,
            model=args.model,
        )
        review = critic_report(
            topic=args.topic,
            report_markdown=report_md,
            source_count=len(sources),
            model=args.model,
            cache=cache,
        )
        if review.passed:
            break
        if args.search and review.new_queries:
            new_urls = search_serper(queries=review.new_queries, max_sources=args.max_sources, cache=cache)
            for u in new_urls:
                if len(all_urls) >= args.max_sources:
                    break
                if u not in all_urls:
                    all_urls.append(u)
            sources = fetch_sources(all_urls, cache=cache)
            notes = extract_notes(sources=sources, model=args.model, cache=cache)

    md_path = outdir / "report.md"
    pdf_path = outdir / "report.pdf"
    md_path.write_text(report_md, encoding="utf-8")
    markdown_to_pdf(report_md, pdf_path)

    print(f"✅ Wrote {md_path}")
    print(f"✅ Wrote {pdf_path}")
    if review:
        print(f"Critic pass: {review.passed}")
        if review.issues:
            print("Issues:")
            for issue in review.issues:
                print(f"- {issue}")


if __name__ == "__main__":
    run()
