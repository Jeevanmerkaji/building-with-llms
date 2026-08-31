# LMT → MTX Converter

A single-file Python script that translates LMT-dialect CNC part programs
(`.txt`) into MTX-style NC programs (`.npg`). It rewrites motion blocks,
tool-change sequences, and program-end handling, and strips or normalizes
the parts of the LMT dialect that MTX controls don't understand.

## What it does

- **Strips line numbers** — `N0080G00W...` → `G00W...`
- **Fixes leading zeros** — `.9668` → `0.9668`, `-.123` → `-0.123`
- **Rewrites tool changes** (`T1M6`, `T2M6`, ...) into the `WAIT` /
  `PLC(3,,1106,1)` / `G54`/`G55` / `G40 D1`/`D2` sequence MTX expects,
  including the retract-and-reposition block (`G53`, `G00 V=2.2`) inserted
  between tools after the first.
- **Rewrites program end** (`M30`) into a `WAIT` + PLC-deactivate + `M30`
  block.
- **Suppresses moves that don't belong in the output**: `G53` retracts,
  `G00`/coordinate moves before the first tool change, `V=0` retracts,
  and `W`-only transit moves.
- **Drops LMT-only content**: `(*MSG,...*)` comments and modal G-codes
  MTX doesn't need (`G19`, `G90`, `G42`, `G41`, `G54`, `G55` when they
  appear standalone).
- **Passes through** `;`-style comments (re-emitted as `; ...`).
- **Emits motion blocks** (`G00`/`G01`/`G02`/`G03`) with axes ordered
  `W V X Z I J K R`, e.g. `G01 W=-3.14 V=-4.55`.
- **Never silently drops a line it doesn't recognize** — any line that
  doesn't match a known pattern is preserved as `; [unhandled] <original line>`
  so you can spot and handle it manually.
- Output uses CRLF (`\r\n`) line endings, matching what MTX controls expect.

## Requirements

- Python 3.6+ (standard library only — no dependencies to install)

## Usage

```bash
python LMT_Converter.py input.txt output.npg
```

Or omit the output path to save alongside the input with an `.npg` extension:

```bash
python LMT_Converter.py input.txt
# writes input.npg in the same directory
```

The script prints a summary (input/output line counts) and the full
converted output to the console after writing the file.

## Example

Input (`input.txt`, LMT dialect):

```
N0010(*MSG,ABRICHTEN:1*)
N0020G90
N0025G54
N0030T1M6
N0035G00V0
N0040G01W.5V-3.29
N0060T2M6
N0070M30
```

Output (`input.npg`, MTX dialect):

```
WAIT
1 PLC(3,,1106,1) = 1   :REM AE-Satz 1
G55
G40 D2
G01 W=0.5 V=-3.29
G53
G00 V=2.2

G54
G40 D1

WAIT
1 PLC(3,,1106,1) = 2   :REM AE-Satz 2
G54
G40 D1
WAIT
1 PLC(3,,1106,1) = 0   :REM AE deaktivieren (Satz 0)
M30
```

(The `(*MSG,...*)` comment, the standalone `G90`/`G54` codes, and the
`G00V0` retract are all dropped; the `G01` feed move survives as the first
emitted motion line.)

## Notes / limitations

- Axis handling assumes the `W`/`V` (and `X`/`Z`/`I`/`J`/`K`/`R`) letter
  addresses used by the source LMT programs; other axis letters are parsed
  but not given a defined position in the emitted line and are appended
  after `R`.
- Tool numbers beyond `T1`/`T2` fall back to the "not tool 1" branch
  (`G54`/`D1`) for offset selection — extend `convert()`'s tool-change
  block (case 4 in the code) if your programs use more tools with distinct
  offset tables.
- Always spot-check the `; [unhandled] ...` lines in the output — they mark
  input the converter didn't recognize and left untouched. Note that the
  "ignoreable" G-code check (`G19`, `G90`, `G42`, `G41`, `G54`, `G55`) only
  matches a line whose body is *exactly* one of those codes; a line with
  multiple codes concatenated (e.g. `G90G54` on one N-block) won't match
  and will fall through to `; [unhandled] ...` instead of being dropped.
