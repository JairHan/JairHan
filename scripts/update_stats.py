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

def card(title, subtitle, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="840" height="280" viewBox="0 0 840 280" role="img" aria-label="{html.escape(title)}">
    <style>text{{font-family:Arial,sans-serif}}.muted{{fill:#94a3b8}}.value{{fill:#f1f5f9;font-size:30px;font-weight:700}}</style>
    <rect x="1" y="1" width="838" height="278" rx="18" fill="#0f172a" stroke="#26364d"/>
    <text x="30" y="39" fill="#5eead4" font-size="18" font-weight="700">{title}</text>
    <text x="30" y="63" class="muted" font-size="12">{html.escape(subtitle)}</text>{body}</svg>'''

def main():
    data = query('query { user(login:"' + USER + '") { contributionsCollection { startedAt endedAt totalCommitContributions totalPullRequestContributions totalIssueContributions totalPullRequestReviewContributions contributionCalendar { totalContributions } } } }')
    c = data['contributionsCollection']
    values = [('Contributions', c['contributionCalendar']['totalContributions']), ('Commits', c['totalCommitContributions']), ('Pull requests', c['totalPullRequestContributions']), ('Issues', c['totalIssueContributions']), ('Reviews', c['totalPullRequestReviewContributions'])]
    body = ''
    for i, (label, value) in enumerate(values):
        x = 32 + i * 160
        body += f'<text x="{x}" y="139" class="value">{value:,}</text><text x="{x}" y="166" class="muted" font-size="13">{label}</text>'
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    body += f'<path d="M30 203H810" stroke="#26364d"/><text x="30" y="238" class="muted" font-size="12">Public activity · Updated {stamp}</text>'
    (ROOT / 'assets/stats.svg').write_text(card('GITHUB / ACTIVITY', f"{c['startedAt'][:10]} → {c['endedAt'][:10]} · GitHub contribution rules apply", body))
    totals, colors = collections.Counter(), {}
    cursor = None
    while True:
        after = ',after:' + json.dumps(cursor) if cursor else ''
        repos = query('query { user(login:"' + USER + '") { repositories(first:100,ownerAffiliations:OWNER,privacy:PUBLIC,isFork:false' + after + ') { nodes { languages(first:100) { totalSize edges { size node { name color } } } } pageInfo { hasNextPage endCursor } } } }')['repositories']
        for repo in repos['nodes']:
            langs = repo['languages']
            assert sum(e['size'] for e in langs['edges']) == langs['totalSize'], 'Language pagination needed'
            for edge in langs['edges']:
                name = edge['node']['name']
                totals[name] += edge['size']
                colors[name] = edge['node']['color'] or '#94a3b8'
        if not repos['pageInfo']['hasNextPage']:
            break
        cursor = repos['pageInfo']['endCursor']
    total = sum(totals.values())
    assert total > 0, 'No language data'
    top = totals.most_common(5)
    remaining = total - sum(v for _, v in top)
    if remaining:
        top.append(('Other', remaining))
        colors['Other'] = '#64748b'
    body, x = '', 30
    for name, value in top:
        width = 780 * value / total
        body += f'<rect x="{x:.2f}" y="90" width="{width:.2f}" height="14" fill="{colors[name]}"/>'
        x += width
    for i, (name, value) in enumerate(top):
        x, y = 30 + (i % 3) * 263, 145 + (i // 3) * 42
        body += f'<circle cx="{x+5}" cy="{y-4}" r="5" fill="{colors[name]}"/><text x="{x+20}" y="{y}" fill="#e2e8f0" font-size="13">{html.escape(name)} <tspan fill="#94a3b8">{100*value/total:.1f}%</tspan></text>'
    body += f'<text x="30" y="238" class="muted" font-size="12">Code bytes · Public owned repositories · Forks excluded · {stamp[:10]}</text>'
    (ROOT / 'assets/languages.svg').write_text(card('CODE / LANGUAGES', 'Language distribution across public non-fork repositories', body))
    print('Generated stats.svg and languages.svg')

if __name__ == '__main__':
    main()
