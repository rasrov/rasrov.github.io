"""Render the verified snapshot without fetching or changing participation decisions."""
import html
import json
import re
from datetime import date
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
START = '<!-- calendar:generated:start -->'
END = '<!-- calendar:generated:end -->'
def render(events, participation, logos):
    cards = []
    seen = set()
    for event in sorted(events, key=lambda e: (e['start'], str(e['id']))):
        classic_lines = ' '.join(line for line in event.get('description', '').splitlines() if 'classic physique' in line.lower())
        if re.search(r'\bnaturals?\b', event['name'] + ' ' + classic_lines, re.I):
            continue
        key = str(event['id'])
        if key in seen: raise ValueError('Duplicate event ID')
        seen.add(key)
        start, end = date.fromisoformat(event['start']), date.fromisoformat(event['end'])
        if end < start: raise ValueError('Invalid date range')
        status = participation.get(key, {}).get('status', 'pending')
        if status not in ('pending', 'confirmed', 'absent'): raise ValueError('Invalid participation status')
        logo = logos.get(key, '')
        if logo and (not logo.startswith('img/calendar/') or '..' in logo or not (ROOT / logo).is_file()): raise ValueError('Invalid logo')
        url = event['url']
        if not url.startswith('https://www.ifbbpro.com/competition/'): raise ValueError('Invalid source URL')
        esc = lambda value: html.escape(str(value), quote=True)
        dates = start.strftime('%d/%m/%Y') if start == end else start.strftime('%d/%m') + ' – ' + end.strftime('%d/%m/%Y')
        location = ' · '.join(filter(None, [event.get('city'), event.get('country')])) or 'Ubicación por confirmar'
        divisions = [line.strip() for line in event.get('description', '').splitlines() if 'classic physique' in line.lower()]
        division = ' · '.join(divisions) or 'Classic Physique'
        if 'natural' in event['name'].lower() and 'natural' not in division.lower(): division += ' · Natural'
        label = {'pending': 'PENDIENTE', 'confirmed': 'PARTICIPA', 'absent': 'NO PARTICIPA'}[status]
        cards.append(f'''<article class="calendar-event" data-date="{start}" data-end="{end}" data-status="{status}" data-logo="{esc(logo)}" id="competition-{esc(key)}">
<div class="calendar-event-top"><time datetime="{start}">{dates}</time><a href="{esc(url)}" target="_blank" rel="noopener noreferrer">Programa oficial ↗</a></div>
<h3>{esc(event['name'])}</h3><p>{esc(location)}</p><p>{esc(division)}</p><span class="calendar-status {status}">{label}</span>
</article>''')
    return '\n'.join(cards)
def main():
    read = lambda name: json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))
    output = render(read('competitions.json')['events'], read('competition-participation.json'), read('competition-logos.json'))
    path = ROOT / 'index.html'
    page = path.read_text(encoding='utf-8')
    if page.count(START) != 1 or page.count(END) != 1: raise ValueError('Calendar markers missing')
    before, rest = page.split(START); _, after = rest.split(END)
    path.write_text(before + START + '\n' + output + '\n' + END + after, encoding='utf-8', newline='\n')
    print('Calendar rendered.')
if __name__ == '__main__': main()
