import os, re, requests

USERNAME = "ali-sher-makki"
README_PATH = "README.md"
START_MARKER = "<!--START_SECTION:projects-->"
END_MARKER = "<!--END_SECTION:projects-->"

ICON_MAP = {
    "Python": "🐍", "JavaScript": "💻", "HTML": "🌐",
    "TypeScript": "💻", "CSS": "🎨",
}
DEFAULT_ICON = "📦"

def fetch_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=pushed&direction=desc"
    headers = {}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def build_card(repo):
    icon = ICON_MAP.get(repo.get("language"), DEFAULT_ICON)
    name = repo["name"]
    url = repo["html_url"]
    desc = repo.get("description") or "No description provided."
    topics = repo.get("topics") or []
    stack_line = " · ".join(t.capitalize() for t in topics) if topics else (repo.get("language") or "")
    homepage = repo.get("homepage") or ""

    lines = [f"### {icon} [{name}]({url})", desc, ""]
    stack_bit = f"**Stack:** {stack_line}" if stack_line else ""
    demo_bit = f"[🔗 Live demo]({homepage})" if homepage else ""
    if stack_bit and demo_bit:
        lines.append(f"{stack_bit}\n{demo_bit}")
    elif stack_bit:
        lines.append(stack_bit)
    elif demo_bit:
        lines.append(demo_bit)
    return "\n".join(lines)

def build_table(cards):
    rows = []
    for i in range(0, len(cards), 2):
        pair = cards[i:i+2]
        row = "<tr>\n"
        for card in pair:
            row += f'<td width="50%" valign="top">\n\n{card}\n\n</td>\n'
        if len(pair) == 1:
            row += '<td width="50%" valign="top"></td>\n'
        row += "</tr>"
        rows.append(row)
    return "<table>\n" + "\n".join(rows) + "\n</table>"

def main():
    repos = fetch_repos()
    repos = [
        r for r in repos
        if not r["fork"] and not r["archived"] and not r["private"]
        and r["name"].lower() != USERNAME.lower()
    ]
    cards = [build_card(r) for r in repos]

    cards.append(
        "### 🔨 More in progress\n"
        "Actively building and shipping — check pinned repos below for the latest work."
    )

    table_html = build_table(cards)

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL)
    new_content = pattern.sub(f"{START_MARKER}\n{table_html}\n{END_MARKER}", content)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    main()
