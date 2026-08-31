"""
LMT -> MTX Converter
Usage:  python LMT_Converter.py input.txt output.npg
        python LMT_Converter.py input.txt          (saves as input.npg)
"""

import re
import sys
import os

# ── helpers ────────────────────────────────────────────────────────────────────

def strip_line_number(line):
    """Remove leading N-number:  N0080G00W... -> G00W..."""
    m = re.match(r'^N\d+\s*(.*)', line)
    return m.group(1).strip() if m else line.strip()

def fix_leading_zero(v):
    """Add leading zero: .9668 -> 0.9668,  -.123 -> -0.123"""
    if v.startswith('-.'): return '-0.' + v[2:]
    if v.startswith('.'):  return '0.'  + v[1:]
    return v

def parse_coords(s):
    """
    Parse compact coordinate string like  W9.4991V-3.3366  or  W=-9.5 V=-3.29
    Returns dict of axis->value.  Skips G and N letters.
    """
    if not s:
        return None
    result = {}
    for m in re.finditer(r'([A-Za-z])\s*=?\s*(-?\.?\d+(?:\.\d+)?)', s):
        axis = m.group(1).upper()
        if axis in ('G', 'N'):
            continue
        result[axis] = fix_leading_zero(m.group(2))
    return result if result else None

def emit_move(g_cmd, coords):
    """Build one output line:  G01 W=-3.14 V=-4.55"""
    line = g_cmd
    for axis in ['W', 'V', 'X', 'Z', 'I', 'J', 'K']:
        if axis in coords:
            line += f' {axis}={coords[axis]}'
    if 'R' in coords:
        line += f' R={coords["R"]}'
    return line

def is_retract(coords):
    """True for V=0 retract moves that should be suppressed."""
    has_v = 'V' in coords
    has_w = 'W' in coords
    if has_v and coords['V'] == '0' and (not has_w or coords['W'] == '0'):
        return True
    if has_w and coords['W'] == '0' and not has_v:
        return True
    return False

# ── converter ──────────────────────────────────────────────────────────────────

IGNOREABLE = {'G19', 'G90', 'G42', 'G41', 'G54', 'G55'}

def convert(input_text):
    lines       = input_text.splitlines()
    out         = []
    last_g      = 'G01'   # modal motion command
    tool_section = 0

    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue

        body = strip_line_number(raw)

        # ── 1. LMT (*MSG,...*) comment -> skip ────────────────────────────────
        if re.match(r'^\(\*', body):  # LMT comment like (*MSG,ABRICHTEN:...)
            continue

        # ── 2. Semicolon comment -> pass through ──────────────────────────────
        m = re.match(r'^;(.*)', body)
        if m:
            out.append('; ' + m.group(1).strip())
            continue

        # ── 3. M30 end of program ─────────────────────────────────────────────
        if re.match(r'^M30\s*$', body, re.I):
            out.append('WAIT')
            out.append('1 PLC(3,,1106,1) = 0   :REM AE deaktivieren (Satz 0)')
            out.append('M30')
            continue

        # ── 4. Tool change  T1M6 / T2M6 ──────────────────────────────────────
        m = re.match(r'^T(\d)(?:M\d+)?$', body, re.I)
        if m:
            tool_num      = int(m.group(1))
            tool_section += 1

            if tool_section == 1:
                out.append('WAIT')
                out.append(f'1 PLC(3,,1106,1) = {tool_section}   :REM AE-Satz {tool_section}')
                out.append('G55' if tool_num == 1 else 'G54')
                out.append('G40 D2' if tool_num == 1 else 'G40 D1')
            else:
                out.append('G53')
                out.append('G00 V=2.2')
                out.append('')
                out.append('G54' if tool_num == 2 else 'G55')
                out.append('G40 D1' if tool_num == 2 else 'G40 D2')
                out.append('')
                out.append('WAIT')
                out.append(f'1 PLC(3,,1106,1) = {tool_section}   :REM AE-Satz {tool_section}')
                out.append('G54' if tool_num == 2 else 'G55')
                out.append('G40 D1' if tool_num == 2 else 'G40 D2')
            continue

        # ── 5. G53 retract -> swallow ─────────────────────────────────────────
        if re.match(r'^G53', body, re.I):
            continue

        # ── 6. G40 cutter-comp off -> standard retract ────────────────────────
        if body.upper() == 'G40':
            out.append('G90 G00 G40 V=2.2')
            out.append('')
            continue

        # ── 7. Ignoreable G-codes ─────────────────────────────────────────────
        if body.upper() in IGNOREABLE:
            continue

        # ── 8. G00 rapid move ─────────────────────────────────────────────────
        m = re.match(r'^G00(.*)$', body, re.I)
        if m:
            last_g = 'G00'
            rest   = m.group(1).strip()
            if not rest:
                continue
            coords = parse_coords(rest)
            # suppress: before first tool, retract moves, W-only transit moves, V=0 moves
            if (tool_section == 0
                    or (coords and is_retract(coords))
                    or (coords and 'W' in coords and 'V' not in coords)
                    or (coords and coords.get('V') == '0')):
                continue
            if coords:
                out.append(emit_move('G00', coords))
            continue

        # ── 9. G01 feed move ──────────────────────────────────────────────────
        m = re.match(r'^G01(.*)$', body, re.I)
        if m:
            last_g = 'G01'
            rest   = m.group(1).strip()
            if not rest:
                continue
            coords = parse_coords(rest)
            if coords:
                out.append(emit_move('G01', coords))
            continue

        # ── 10. G02 / G03 arc moves ───────────────────────────────────────────
        m = re.match(r'^(G0[23])(.*)$', body, re.I)
        if m:
            coords = parse_coords(m.group(2).strip())
            if coords:
                out.append(emit_move(m.group(1).upper(), coords))
            continue

        # ── 11. Bare coordinate line  W6.0701V-3.3366 ────────────────────────
        if re.match(r'^[WVXZwvxz][\d\-\.\+]', body) or re.match(r'^[WVXZwvxz]0', body):
            coords = parse_coords(body)
            if coords:
                out.append(emit_move(last_g, coords))
            continue

        # ── 12. Fallback: keep as comment so nothing is silently lost ─────────
        out.append('; [unhandled] ' + raw)

    return '\r\n'.join(out) + '\r\n'

# ── main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage:  python LMT_Converter.py input.txt [output.npg]")
        sys.exit(1)

    input_path = sys.argv[1]

    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        base, _ = os.path.splitext(input_path)
        output_path = base + ".npg"

    try:
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except FileNotFoundError:
        print("ERROR: Input file not found:")
        print("  " + input_path)
        sys.exit(1)

    result = convert(text)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)

    print("Converted :  " + input_path)
    print("Output    :  " + output_path)
    print("Lines in  :  " + str(len(text.splitlines())))
    print("Lines out :  " + str(len(result.splitlines())))
    print()
    print("-" * 60)
    print(result)
    print("-" * 60)
