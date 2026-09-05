"""Generate the two compact rainbow typing lines in the README header."""
from html import escape
from pathlib import Path
import unicodedata

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
COLORS = ['#d73a49', '#c65d21', '#997600', '#168443', '#087f9c', '#2563eb', '#9c36b5']


def typing(name, text, size):
    advances = [size if unicodedata.east_asian_width(c) in 'WF' else size * .6 for c in text]
    width = max(390, round(sum(advances) + 12))
    start = (width - sum(advances)) / 2
    x, chars, rules = start, [], []
    for i, (char, advance) in enumerate(zip(text, advances)):
        reveal = (i + 1) * .12 / 11 * 100
        chars.append(f'<tspan x="{x:.2f}" class="c{i}" fill="url(#rainbow)">{escape(char)}</tspan>')
        rules.append(f'@keyframes t{i}{{0%,{reveal:.3f}%{{opacity:0}}{reveal+.01:.3f}%,99.9%{{opacity:1}}100%{{opacity:0}}}}.c{i}{{animation:t{i} 11s linear infinite}}')
        x += advance
    stops = ''.join(f'<stop offset="{i/(len(COLORS)-1):.3f}" stop-color="{color}"/>' for i, color in enumerate(COLORS))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="28" viewBox="0 0 {width} 28" role="img" aria-label="{escape(text, quote=True)}">
<title>{escape(text)}</title>
<defs><linearGradient id="rainbow" gradientUnits="userSpaceOnUse" x1="{start:.2f}" y1="0" x2="{x:.2f}" y2="0">{stops}</linearGradient></defs>
<style>text{{fill:url(#rainbow);font-family:monospace,"Noto Sans CJK SC","Microsoft YaHei",sans-serif;font-size:{size}px}}{''.join(rules)}@media(prefers-reduced-motion:reduce){{tspan{{animation:none!important}}}}</style>
<text y="20" xml:space="preserve">{''.join(chars)}</text></svg>'''
    (ASSETS / name).write_text(svg)


if __name__ == '__main__':
    typing('typing-rainbow.svg', 'Learning AI. Building useful tools.', 14)
    typing('motto-rainbow.svg', '梦想永在凌云意意气风发，代码成就万世基积沙镇海', 16)
