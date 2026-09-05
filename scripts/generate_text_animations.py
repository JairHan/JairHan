"""Build small, theme-aware SVG typing lines for the profile README."""
from html import escape
from pathlib import Path
import unicodedata

ASSETS = Path(__file__).resolve().parents[1] / 'assets'


def typing(name, text, start=0, duration=24, bold=()):
    x, chars, rules = 1, [], []
    for i, char in enumerate(text):
        reveal = (start + (i + 1) * .11) / duration * 100
        weight = ' font-weight="600"' if any(text.find(word) <= i < text.find(word) + len(word) for word in bold) else ''
        chars.append(f'<tspan x="{x:.1f}" class="c{i}"{weight}>{escape(char)}</tspan>')
        rules.append(f'@keyframes t{i}{{0%,{reveal:.3f}%{{opacity:0}}{reveal+.01:.3f}%,99.9%{{opacity:1}}100%{{opacity:0}}}}.c{i}{{animation:t{i} {duration}s linear infinite}}')
        x += 16 if unicodedata.east_asian_width(char) in 'WF' else 9.6
    width = round(x + 2)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="24" viewBox="0 0 {width} 24" role="img" aria-label="{escape(text, quote=True)}">
<title>{escape(text)}</title><style>text{{fill:#24292f;font-family:monospace,"Noto Sans CJK SC","Microsoft YaHei",sans-serif;font-size:16px}}@media(prefers-color-scheme:dark){{text{{fill:#c9d1d9}}}}{''.join(rules)}@media(prefers-reduced-motion:reduce){{tspan{{animation:none!important}}}}</style>
<text y="18" xml:space="preserve">{''.join(chars)}</text></svg>'''
    (ASSETS / name).write_text(svg)
    return width


if __name__ == '__main__':
    lines = [
        ('intro-typing.svg', '学习人工智能，用代码解决日常问题。', 0, 11, ()),
        ('about-ai.svg', '正在学习人工智能，探索模型与实际应用的结合。', 0, 24, ('人工智能',)),
        ('about-tools.svg', '喜欢编写 Python 工具、自动化脚本和 Web 应用。', 3, 24, ('Python 工具、自动化脚本和 Web 应用',)),
        ('about-learning.svg', '在开源项目和日常实践中持续学习，把想法变成能用的小工具。', 7, 24, ()),
        ('about-email.svg', '邮箱：hanjair9@gmail.com', 11, 24, ()),
    ]
    for args in lines:
        print(args[0], typing(*args))
