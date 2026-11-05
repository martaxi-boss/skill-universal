#!/usr/bin/env python3
"""Real six-tool Ferrari GUI/media smoke, with exact failure diagnostics."""
from __future__ import annotations
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import wave
import xml.etree.ElementTree as ET
import zlib

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import tool_runtime

ROOT=Path("/srv/projects/skill-universal")
ACTIONS=("darktable-jpeg-tiff","krita-image-png","gimp-png-xcf",
         "scribus-text-publication","lmms-project-wav","kdenlive-mlt-mp4")

def png(width=160,height=90):
    raw=b"".join(b"\\x00"+b"\\xa9\\xd7\\xee"*width for _ in range(height))
    def chunk(name,data):
        return struct.pack(">I",len(data))+name+data+struct.pack(">I",zlib.crc32(name+data)&0xffffffff)
    header=struct.pack(">IIBBBBB",width,height,8,2,0,0,0)
    return b"\\x89PNG\\r\\n\\x1a\\n"+chunk(b"IHDR",header)+chunk(b"IDAT",zlib.compress(raw))+chunk(b"IEND",b"")

def main():
    if len(sys.argv)<2 or not sys.argv[1].isdigit():
        raise SystemExit("Provide unique GitHub run ID")
    work=ROOT/".runtime/private-gui-test"/sys.argv[1]
    if work.exists() or work.is_symlink():
        raise FileExistsError("Ferrari GUI test work directory already exists")
    work.mkdir(parents=True)
    image=work/"image.png"
    image.write_bytes(png())
    jpg=work/"image.jpg"
    own=ROOT/"tools/ubuntu-cli"
    env=os.environ.copy()
    env["LD_LIBRARY_PATH"]=str(own/"lib")
    env["HOME"]=str(work)
    env["TMPDIR"]=str(work)
    env["MAGICK_CONFIGURE_PATH"]=str(own/"etc/ImageMagick-6")
    env["MAGICK_CODER_MODULE_PATH"]=str(own/"lib/ImageMagick/coders")
    subprocess.run([str(own/"bin/convert"),str(image),str(jpg)],
                   check=True,capture_output=True,timeout=30,env=env)
    text=work/"publication.txt"
    text.write_text("Ferrari private publication\\n\\nUbuntu sandbox\\n")
    mlt=work/"video.mlt"
    mlt.write_text('''<?xml version="1.0" encoding="utf-8"?>
<mlt LC_NUMERIC="C" version="7.0.0" producer="playlist0">
<profile description="Ferrari" width="320" height="180" progressive="1"
sample_aspect_num="1" sample_aspect_den="1" display_aspect_num="16"
display_aspect_den="9" frame_rate_num="25" frame_rate_den="1" colorspace="709"/>
<producer id="colour0" in="0" out="49"><property name="mlt_service">color</property>
<property name="resource">#176fae</property></producer>
<playlist id="playlist0"><entry producer="colour0" in="0" out="49"/></playlist>
</mlt>''')
    factory=own/"share/lmms/projects/templates/default.mpt"
    if not factory.is_file():
        raise RuntimeError("Ferrari private LMMS factory project missing")
    original=ET.parse(factory)
    track=original.getroot().find(".//song/trackcontainer/track[@type='0']")
    if track is None:
        raise RuntimeError("Ferrari LMMS oscillator template missing")
    pattern=ET.SubElement(track,"pattern",{"name":"Ferrari","type":"1","pos":"0","len":"192","steps":"16","muted":"0"})
    for pitch,position in ((57,0),(64,96)):
        ET.SubElement(pattern,"note",{"key":str(pitch),"pos":str(position),"len":"96","vol":"85","pan":"0"})
    song=work/"song.mmp"
    original.write(song,encoding="utf-8",xml_declaration=True)
    sources={"darktable-jpeg-tiff":jpg,"krita-image-png":jpg,
             "gimp-png-xcf":image,"scribus-text-publication":text,
             "lmms-project-wav":song,"kdenlive-mlt-mp4":mlt}
    failed=[]
    passed=[]
    for action in ACTIONS:
        spec=tool_runtime.specs()[action]
        exe=tool_runtime.executable(spec["tool"],spec["binary"])
        print("FERRARI_GUI_BEGIN="+action,flush=True)
        if not exe or not Path(exe).resolve().is_relative_to(own.resolve()):
            failed.append(action)
            print("FERRARI_GUI_ERROR="+action+"|private executor missing: "+str(exe),flush=True)
            continue
        try:
            outcome=tool_runtime.invoke(action,str(sources[action]),str(work/action))
            if not outcome["confirmed"]:
                raise RuntimeError("not confirmed")
            result=work/action/spec["artifact"]
            if action=="scribus-text-publication":
                if not (result/"publication.pdf").is_file() or not (result/"publication.sla").is_file():
                    raise RuntimeError("No Scribus PDF and SLA")
            elif not result.is_file() or result.stat().st_size<100:
                raise RuntimeError("Output file missing or too small")
            if action=="gimp-png-xcf" and not result.read_bytes().startswith(b"gimp xcf"):
                raise RuntimeError("GIMP output is not an XCF")
            if action=="lmms-project-wav":
                with wave.open(str(result),"rb") as wav:
                    if wav.getnframes()<100:
                        raise RuntimeError("LMMS output has no audio")
            passed.append(action)
            print("FERRARI_GUI_PASS="+action,flush=True)
        except Exception as exc:
            failed.append(action)
            print("FERRARI_GUI_ERROR="+action+"|"+type(exc).__name__+": "+str(exc)[-1800:],flush=True)
    print("FERRARI_GUI_RESULT="+json.dumps({"passed":passed,"failed":failed},sort_keys=True),flush=True)
    if failed:
        raise SystemExit(2)
    print("FERRARI_GUI_SIX_REAL=PASS",flush=True)

if __name__=="__main__":
    main()
