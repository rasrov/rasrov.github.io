"""Replace one generated HTML region while preserving its surroundings exactly."""


def replace_region(page, name, content):
    start = f'<!-- {name}:generated:start -->'
    end = f'<!-- {name}:generated:end -->'
    if page.count(start) != 1 or page.count(end) != 1:
        raise ValueError(f'{name}: missing or duplicate generation markers')
    start_at = page.index(start) + len(start)
    end_at = page.index(end)
    if start_at > end_at:
        raise ValueError(f'{name}: generation markers out of order')
    return page[:start_at] + content + page[end_at:]
