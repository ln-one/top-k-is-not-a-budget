"""Theme neutral SVG surfaces; retain Paul Tol data colors in both themes."""
import re
import xml.etree.ElementTree as ET

# Pale diagram fills retain the corresponding original Vibrant hue.
TINTS = {
    '#e5f2fa': ('#0077bb', 10), '#e4f3f0': ('#009988', 10),
    '#f8d4b9': ('#ee7733', 25), '#fcebdd': ('#ee7733', 12),
    '#f8e5e1': ('#cc3311', 10),
}
NEUTRALS = {
    '#202124', '#20252b', '#263238', '#374151', '#4b5563', '#5f6670',
    '#6b7280', '#7a8088', '#8b9198', '#9ca3af', '#a7adb5', '#c4c8cd',
    '#68717b', '#aeb4bc', '#adb5bd', '#e5e7eb', '#d9dde3', '#d9dee3',
    '#f0f2f4', '#f4f5f6', '#f5f6f7',
}

def apply_theme(svg):
    ns = '{http://www.w3.org/2000/svg}'
    def mapped(value, glyph=False):
        value = value.lower()
        if value in ('white', '#fff'): value = '#ffffff'
        if value in ('black', '#000'): value = '#000000'
        if value == '#bbbbbb': return value  # Vibrant categorical grey is data.
        if value in TINTS:
            hue, alpha = TINTS[value]
            return f'color-mix(in srgb,{hue} {alpha}%,var(--paper))'
        if not re.fullmatch('#[0-9a-f]{6}', value): return value
        rgb = [int(value[i:i+2], 16) for i in (1,3,5)]
        if value not in NEUTRALS and len(set(rgb)) != 1: return value
        if glyph and value == '#ffffff': return value
        if min(rgb) > 240: return 'var(--paper)'
        if min(rgb) > 205: return 'var(--grid)'
        if min(rgb) > 140: return 'var(--border)'
        if max(rgb) > 100: return 'var(--muted)'
        return 'var(--ink)'
    def visit(el, protected=False):
        if el.get('id', '').startswith('cell-'):
            el.set('fill', '#000000')
            protected = True
        if not protected:
            glyph = el.tag.rsplit('}',1)[-1] in ('use','text','tspan')
            for attr in ('fill','stroke','color'):
                if attr in el.attrib: el.set(attr, mapped(el.get(attr), glyph))
            if 'style' in el.attrib:
                el.set('style', re.sub(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)',
                    lambda m: '#' + ''.join(f'{int(v):02x}' for v in m.groups()), el.get('style')))
                el.set('style', re.sub(r'(?<![-\w])(fill|stroke|color|background-color):\s*(#[0-9a-fA-F]{3,6}|white|black)\b',
                    lambda m: m[1]+':'+mapped(m[2],glyph),el.get('style')))
        for child in el: visit(child, protected)
    visit(svg)
    svg.set('fill', 'var(--ink)')
    svg.set('style', 'color-scheme:light dark')
    style = ET.Element(ns+'style')
    style.text = ('svg{--paper:#ffffff;--ink:#20252b;--muted:#68717b;--border:#adb5bd;--grid:#dde2e7}'
        '@media(prefers-color-scheme:dark){svg{--paper:#181c22;--ink:#e7ebef;--muted:#adb7c2;--border:#768391;--grid:#39414c}}')
    svg.insert(0,style)
    svg.insert(1,ET.Element(ns+'rect',{'width':'100%','height':'100%','fill':'var(--paper)'}))
