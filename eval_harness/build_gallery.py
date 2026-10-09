"""Build a local image comparison with synchronized scrolling and fixed zoom.

No rendering, mesh processing, measurement, network access or automatic scoring.
"""
import argparse
import html
import json
import os
from pathlib import Path
from urllib.parse import quote


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config_path = args.config.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8-sig"))
    output = args.output.resolve()
    if output.exists():
        raise ValueError("Gallery output must be a new file")
    modes = config["modes"]
    if not modes or not config["columns"]:
        raise ValueError("Supply local synthetic images and at least one display mode")
    columns = []
    for column in config["columns"]:
        images = {}
        for mode in modes:
            raw = column["images"][mode]
            if Path(raw).is_absolute() or "://" in raw:
                raise ValueError("Gallery image paths must be local and relative to the configuration")
            image = (config_path.parent / raw).resolve()
            if not image.is_file():
                raise ValueError("Supply the synthetic images before building the gallery")
            images[mode] = quote(os.path.relpath(image, output.parent).replace(os.sep, "/"), safe="/")
        columns.append({"label": column["label"], "images": images})
    data = json.dumps({"columns": columns, "modes": modes, "baseWidth": int(config.get("image_width", 2048))}).replace("</", "<\\/")
    title = html.escape(config["title"])
    page = """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title><style>
body{font:16px system-ui;margin:1rem;background:#202226;color:#f5f5f5}
header{position:sticky;top:0;background:#202226;padding:.5rem;z-index:2}
button,select{font:inherit;margin:.2rem;padding:.4rem}
#columns{display:flex;gap:1rem}article{flex:1;min-width:0}h2{font-size:1rem}
.viewport{overflow:auto;height:76vh;border:1px solid #888;background:#777}
img{display:block;max-width:none;image-rendering:auto}
</style><header><h1>__TITLE__</h1>
<p>Local comparison only. No automatic visual score. USER_VISUAL_ACCEPTANCE = PENDING.</p>
<label>Display <select id="mode"></select></label>
<span id="zoom"></span><label><input id="sync" type="checkbox" checked> Synchronize scrolling</label>
</header><main id="columns"></main><script type="application/json" id="config">__DATA__</script>
<script>
const data=JSON.parse(document.getElementById('config').textContent);
const panes=[],pictures=[];let zoom=1,scrolling=false;
const selector=document.getElementById('mode');
for(const mode of data.modes){const option=document.createElement('option');option.textContent=mode;option.value=mode;selector.append(option)}
for(const column of data.columns){const article=document.createElement('article'),heading=document.createElement('h2'),pane=document.createElement('div'),picture=document.createElement('img');heading.textContent=column.label;pane.className='viewport';picture.alt=column.label;picture.style.width=data.baseWidth+'px';pane.append(picture);article.append(heading,pane);document.getElementById('columns').append(article);panes.push(pane);pictures.push(picture);pane.addEventListener('scroll',()=>{if(scrolling||!document.getElementById('sync').checked)return;scrolling=true;for(const other of panes)if(other!==pane){other.scrollLeft=pane.scrollLeft;other.scrollTop=pane.scrollTop}requestAnimationFrame(()=>{scrolling=false})})}
function selectMode(){for(let i=0;i<pictures.length;i++)pictures[i].src=data.columns[i].images[selector.value]}
selector.addEventListener('change',selectMode);selectMode();
for(const level of [1,2,4,8]){const button=document.createElement('button');button.textContent=level+'×';button.addEventListener('click',()=>{const ratio=level/zoom;zoom=level;for(const picture of pictures)picture.style.width=data.baseWidth*level+'px';for(const pane of panes){pane.scrollLeft*=ratio;pane.scrollTop*=ratio}});document.getElementById('zoom').append(button)}
</script></html>"""
    page = page.replace("__TITLE__", title).replace("__DATA__", data)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8")
    print("Local comparison page created; visual acceptance remains pending.")


if __name__ == "__main__":
    main()
