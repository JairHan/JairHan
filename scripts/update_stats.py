"""Generate profile cards from public GitHub data using gh (no dependencies)."""
import collections
import datetime
import html
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
USER = 'JairHan'

def query(source):
    result = json.loads(subprocess.check_output(['gh', 'api', 'graphql', '-f', 'query=' + source]))
    if result.get('errors'):
        raise RuntimeError(result['errors'])
    return result['data']['user']

def card(title, subtitle, body, height=200):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="420" height="{height}" viewBox="0 0 420 {height}" role="img" aria-label="{html.escape(title)}">
    <style>svg{{--text:#24292f;--muted:#57606a;--border:#d0d7de;--title:#0969da}}text{{font-family:Arial,sans-serif}}.muted{{fill:var(--muted)}}.value{{fill:var(--text);font-size:14px;font-weight:600}}@media(prefers-color-scheme:dark){{svg{{--text:#c9d1d9;--muted:#8b949e;--border:#30363d;--title:#58a6ff}}}}</style>
    <rect x="1" y="1" width="418" height="{height-2}" rx="6" fill="none" stroke="var(--border)"/>
    <text x="18" y="29" fill="var(--title)" font-size="16" font-weight="600">{title}</text>
    <text x="18" y="49" class="muted" font-size="10">{html.escape(subtitle)}</text>{body}</svg>'''

def main():
    data = query('query { user(login:"' + USER + '") { contributionsCollection { startedAt endedAt totalCommitContributions totalPullRequestContributions totalIssueContributions totalPullRequestReviewContributions contributionCalendar { totalContributions } } } }')
    c = data['contributionsCollection']
    values = [('Contributions', c['contributionCalendar']['totalContributions']), ('Commits', c['totalCommitContributions']), ('Pull requests', c['totalPullRequestContributions']), ('Issues', c['totalIssueContributions']), ('Reviews', c['totalPullRequestReviewContributions'])]
    body = ''
    for i, (label, value) in enumerate(values):
        y = 76 + i * 21
        body += f'<text x="18" y="{y}" class="muted" font-size="12">{label}</text><text x="398" y="{y}" class="value" text-anchor="end">{value:,}</text>'
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    body += f'<text x="18" y="186" class="muted" font-size="9">Public activity · Updated {stamp}</text>'
    (ROOT / 'assets/stats.svg').write_text(card('GitHub Stats', f"{c['startedAt'][:10]} → {c['endedAt'][:10]}", body))
    totals, colors = collections.Counter(), {}
    cursor = None
    while True:
        after = ',after:' + json.dumps(cursor) if cursor else ''
        repos = query('query { user(login:"' + USER + '") { repositories(first:100,ownerAffiliations:OWNER,privacy:PUBLIC,isFork:false' + after + ') { nodes { primaryLanguage { name color } } pageInfo { hasNextPage endCursor } } } }')['repositories']
        for repo in repos['nodes']:
            language = repo['primaryLanguage']
            if language:
                totals[language['name']] += 1
                colors[language['name']] = language['color'] or '#94a3b8'
        if not repos['pageInfo']['hasNextPage']:
            break
        cursor = repos['pageInfo']['endCursor']
    total = sum(totals.values())
    assert total > 0, 'No language data'
    top = sorted(totals.items(), key=lambda item: (-item[1], item[0]))
    height = max(200, 130 + ((len(top) + 1) // 2) * 25)
    body, x = '', 18
    for name, value in top:
        width = 384 * value / total
        body += f'<rect x="{x:.2f}" y="67" width="{width:.2f}" height="8" fill="{colors[name]}"/>'
        x += width
    for i, (name, value) in enumerate(top):
        x, y = 18 + (i % 2) * 196, 102 + (i // 2) * 25
        body += f'<circle cx="{x+4}" cy="{y-4}" r="4" fill="{colors[name]}"/><text x="{x+15}" y="{y}" class="value" style="font-size:11px;font-weight:400">{html.escape(name)} <tspan class="muted">{value} · {100*value/total:.1f}%</tspan></text>'
    body += f'<text x="18" y="{height-14}" class="muted" font-size="9">One repo = one vote · Updated {stamp[:10]}</text>'
    (ROOT / 'assets/languages.svg').write_text(card('项目主要语言分布', f'{total} public non-fork repos with a detected language', body, height))
    print('Generated stats.svg and languages.svg')

if __name__ == '__main__':
    main()
