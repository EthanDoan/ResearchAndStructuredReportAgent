PLANNER_SYSTEM = """You are a research planner.
Return an outline and research questions suitable for a structured report.
Be concise and practical."""

WRITER_SYSTEM = """You write structured technical reports.
Hard rules:
- If sources are provided, make claims ONLY if supported by sources.
- Add citations like [S1], [S2] at end of sentences/bullets.
- If sources are missing, add an 'Assumptions & Limitations' section.
- Use Markdown headings and bullet points.
"""

def make_planner_user(topic: str, audience: str, length: str) -> str:
    return f"""Topic: {topic}
Audience: {audience}
Length: {length}

Produce:
1) A report outline with sections (Markdown-like headings)
2) 6-10 research questions
3) A short list of keywords/queries (even if we won't search yet)
"""

def make_writer_user(topic: str, audience: str, length: str, sources_block: str, plan: str) -> str:
    return f"""Write a structured report in Markdown.

Topic: {topic}
Audience: {audience}
Length: {length}

Here is the planned outline and questions:
{plan}

Here are sources (may be empty). Use citations [S1], [S2], etc:
{sources_block}

Output rules:
- Start with a TL;DR (5 bullets max)
- Use clear headings
- End with a References section listing [S#] -> URL
"""