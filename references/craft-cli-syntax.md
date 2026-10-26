# Crafting App CLI Syntax

Each Crafting App has its own CLI with slightly different syntax. This document covers the variations.

## General Pattern

All Crafting App CLIs support:
- `command_list` — list all available commands
- `describe` or `describe --id <command>` — get command parameters
- Execution — run a command with parameters

## Syntax by Craft Family

### Group A: `--cmd 'id={...}'` (JSON inline)

**Apps:** GridCraft, CADCraft, DeckCraft, WordCraft, SoundCraft, DesignCraft

```bash
# List commands
gridcraft-cli command_list

# Search commands
gridcraft-cli command_list --search "chart"

# Describe a command
gridcraft-cli describe --id "insert.chart"

# Run a command
gridcraft-cli --cmd 'insert.chart={"range":"A1","type":"bar","title":"Q3 Sales"}'

# Run multiple commands
gridcraft-cli --cmd 'insert.chart={...}' --cmd 'format.range={...}'
```

### Group B: `--cmd id --params '{...}'` (separate params)

**Apps:** PhotoCraft, VectorCraft

```bash
# List commands
photocraft-cli command_list

# Search commands
photocraft-cli command_list --search "layer"

# Describe a command
photocraft-cli describe --id "layer.add"

# Run a command
photocraft-cli --cmd "layer.add" --params '{"image":"input.png","x":100,"y":100}'

# Run multiple commands
photocraft-cli --cmd "layer.add" --params '{...}' --cmd "layer.opacity" --params '{...}'
```

### Group C: `positional id key=value`

**Apps:** LightCraft, PdfCraft

```bash
# List commands
lightcraft-cli command_list

# Describe a command
lightcraft-cli describe "import.raw"

# Run a command (key=value pairs)
lightcraft-cli import.raw --file="/path/to/image.raw" --develop=true

# PdfCraft example
pdfcraft-cli export.pdf --input="doc.pdf" --output="out.pdf" --format="png" --dpi=300
```

### Group D: `positional id {json}`

**Apps:** EffectCraft

```bash
# List commands
effectcraft-cli command_list

# Describe a command
effectcraft-cli describe "layer.create"

# Run a command
effectcraft-cli layer.create '{"name":"Background","type":"solid","color":"#000000"}'
```

### Group E: JSONL script file

**Apps:** FilmCraft

FilmCraft requires a generated JSONL script file.

```bash
# List commands
filmcraft-cli command_list

# Describe a command
filmcraft-cli describe --id "timeline.place"

# Create a script file (script.jsonl):
# {"command":"import.media","params":{"path":"clip.mp4"}}
# {"command":"timeline.place","params":{"item":1,"track":"V1","seconds":0,"duration":5}}
# {"command":"export.video","params":{"output":"out.mp4","preset":"h264"}}

# Run the script
filmcraft-cli --script script.jsonl
```

## Common Command Patterns by App

### PhotoCraft (Photoshop-style)

```bash
# List all 858 commands
photocraft-cli command_list

# Common operations
photocraft-cli --cmd "open.file" --params '{"path":"image.psd"}'
photocraft-cli --cmd "layer.add" --params '{"name":"New Layer"}'
photocraft-cli --cmd "layer.opacity" --params '{"layer":0,"value":0.5}'
photocraft-cli --cmd "filter.blur" --params '{"radius":5,"layer":0}'
photocraft-cli --cmd "save.file" --params '{"path":"output.psd"}'
photocraft-cli --cmd "export.png" --params '{"path":"output.png","scale":2}'
```

### VectorCraft (Illustrator-style)

```bash
vectorcraft-cli --cmd "shape.rect" --params '{"x":0,"y":0,"w":100,"h":50}'
vectorcraft-cli --cmd "path.create" --params '{"points":[[0,0],[100,0],[100,100]]}'
vectorcraft-cli --cmd "fill.set" --params '{"color":"#FF0000"}'
vectorcraft-cli --cmd "export.svg" --params '{"path":"output.svg"}'
```

### FilmCraft (Premiere Pro-style)

```bash
# FilmCraft needs JSONL scripts
# See control-protocol.md for FilmCraft control channel examples

# Create a script
cat > script.jsonl << 'EOF'
{"command":"import.media","params":{"path":"video.mp4"}}
{"command":"timeline.place","params":{"item":1,"track":"V1","seconds":0,"duration":30}}
{"command":"effect.add","params":{"clip":1,"effect":"lumetri","preset":"warm"}}
{"command":"export.video","params":{"output":"final.mp4","format":"mp4","codec":"h264"}}
EOF

filmcraft-cli --script script.jsonl
```

### GridCraft (Excel-style)

```bash
gridcraft-cli --cmd 'insert.chart={"range":"A1:B10","type":"bar","title":"Sales"}'
gridcraft-cli --cmd 'write.range={"range":"A1","values":[["Name","Qty"],["A",10],["B",20]]}'
gridcraft-cli --cmd 'format.range={"range":"A1:B10","bold":true,"border":true}'
gridcraft-cli --cmd 'calculate.formula={"range":"C1","formula":"=SUM(A1:B1)"}'
gridcraft-cli --cmd 'save.workbook={"path":"output.xlsx"}'
```

### WordCraft (Word-style)

```bash
wordcraft-cli --cmd 'insert.text={"range":"A1","text":"Hello World"}'
wordcraft-cli --cmd 'format.paragraph={"range":"A1","alignment":"center","style":"heading"}'
wordcraft-cli --cmd 'insert.table={"position":"A5","rows":3,"cols":4}'
wordcraft-cli --cmd 'save.document={"path":"output.docx"}'
```

### DeckCraft (PowerPoint-style)

```bash
deckcraft-cli --cmd 'slide.add={"layout":"title"}'
deckcraft-cli --cmd 'slide.add={"layout":"content","title":"Q3 Report"}'
deckcraft-cli --cmd 'shape.add={"slide":2,"type":"text","text":"Revenue: $1M"}'
deckcraft-cli --cmd 'save.presentation={"path":"output.deckcraft"}'
```

### CADCraft (AutoCAD-style)

```bash
cadcraft-cli --cmd 'draw.line={"x1":0,"y1":0,"x2":100,"y2":100}'
cadcraft-cli --cmd 'draw.circle={"cx":50,"cy":50,"r":25}'
cadcraft-cli --cmd 'export.dxf={"path":"output.dxf"}'
cadcraft-cli --cmd 'export.png={"path":"output.png","dpi":300}'
```

### SoundCraft (DAW-style)

```bash
soundcraft-cli --cmd 'import.audio={"path":"track.wav","track":"1"}'
soundcraft-cli --cmd 'clip.trim={"track":1,"start":0,"end":30}'
soundcraft-cli --cmd 'effect.gain={"track":1,"db":-6}'
soundcraft-cli --cmd 'bounce.audio={"path":"output.wav","format":"wav"}'
```

### LightCraft (Lightroom-style)

```bash
lightcraft-cli import.raw --file="/path/image.raw" --develop="true"
lightcraft-cli develop.tone --exposure="+0.5" --contrast="+10" --highlights="-20"
lightcraft-cli export.jpeg --path="/output.jpg" --quality="90" --dpi="300"
```

### PdfCraft (Acrobat-style)

```bash
pdfcraft-cli read.text --input="doc.pdf" --page="3"
pdfcraft-cli export.pdf --input="doc.pdf" --output="pages/" --format="png" --dpi="300"
pdfcraft-cli merge.pdf --inputs="a.pdf,b.pdf" --output="merged.pdf"
pdfcraft-cli split.pdf --input="doc.pdf" --pages="1-5" --output="chunk.pdf"
```

### DesignCraft (InDesign-style)

```bash
designcraft-cli --cmd 'page.add={"size":"A4","margins":"2cm"}'
designcraft-cli --cmd 'text.frame={"page":1,"x":50,"y":50,"w":200,"h":100,"text":"Hello"}'
designcraft-cli --cmd 'image.place={"page":1,"path":"photo.jpg","x":50,"y":200,"w":150}'
designcraft-cli --cmd 'export.pdf={"path":"output.pdf"}'
```

### EffectCraft (After Effects-style)

```bash
effectcraft-cli layer.create '{"name":"Background","type":"solid","color":"#000000"}'
effectcraft-cli layer.create '{"name":"Text","type":"text","content":"Hello"}'
effectcraft-cli effect.add '{"layer":"Text","effect":"dropshadow","params":{"distance":5,"blur":10}}'
effectcraft-cli render.sequence '{"output":"out.mp4","format":"mp4","resolution":"1920x1080"}'
```

## MCP Tools per Craft

Every Crafting App exposes these MCP tools:

| Tool | Purpose |
|------|---------|
| `<craft>_commands` | Search/list commands (`{"search":"keyword"}`) |
| `<craft>_describe` | Get command details (`{"id":"command.id"}`) |
| `<craft>_run` | Execute commands (`{"commands":[...],"save":"path"}`) |
| `<craft>_inspect` | Inspect a file (`{"file":"path"}`) |
| `<craft>_convert` | Convert between formats (`{"input":"a","output":"b"}`) |
| `<craft>_mcp_tools` | List MCP tools (`{"search":"keyword"}`) |
| `<craft>_mcp_call` | Call MCP tool directly (`{"tool":"name","arguments":{...}}`) |
| `<craft>_mcp_status` | Check MCP server status (`{}`) |

## Tips

1. **Always start with `command_list`** — never guess command ids
2. **Use `describe`** — get exact parameters before running
3. **Check `enabled` status** — some commands may be disabled with a reason
4. **FilmCraft needs JSONL** — generate script files for complex sequences
5. **PhotoCraft control channel is authenticated** — see control-protocol.md
6. **PdfCraft uses file-based control** — `--control FILE` instead of port
