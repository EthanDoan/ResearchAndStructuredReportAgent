import argparse
import os
from pathlib import Path
from dotenv import load_dotenv

from agent.research import fetch_sources
from agent.writer import write_report
from agent.pdf_export import markdown_to_pdf


def parse_args():
    p = argparse.ArgumentParser(description="Research + Structured Report Agent (v1)")
    p.add_argument("--topic", required=True, help="Report topic")
    p.add_argument("--audience", default="General technical audience", help="Target audience")
    p.add_argument("--length", default="medium", choices=["short", "medium", "long"], help="Report length")
    p.add_argument("--urls", default="", help="Comma-separated URLs to use as sources (optional)")
    p.add_argument("--outdir", default="outputs", help="Output directory")
    p.add_argument("--model", default="gpt-5", help="OpenAI model name")
    return p.parse_args()


def main():
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Missing OPENAI_API_KEY. Put it in .env or your environment.")

    args = parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    urls = [u.strip() for u in args.urls.split(",") if u.strip()]

    sources = fetch_sources(urls)  # may be empty
    md = write_report(
        topic=args.topic,
        audience=args.audience,
        length=args.length,
        sources=sources,
        model=args.model,
    )

    md_path = outdir / "report.md"
    pdf_path = outdir / "report.pdf"

    md_path.write_text(md, encoding="utf-8")
    markdown_to_pdf(md, pdf_path)

    print(f"✅ Wrote {md_path}")
    print(f"✅ Wrote {pdf_path}")


if __name__ == "__main__":
    main()