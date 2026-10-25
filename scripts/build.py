#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""诗词文字画 · 成品构建器

把若干张"纯文字 SVG" + 每首诗的推理文字（事实/投影/路径/检查）
合成一个自包含的单文件 HTML 教学页，并可选导出 PNG。

用法:
    python build.py --config poems.json --out poem-art.html [--png]

config 结构:
{
  "title": "诗是有形状的",
  "kicker": "Poetry as Picture · 文字画",
  "subtitle": "……",
  "meta": "五首练手",
  "poems": [
    {"no":"No.1","name":"登鹳雀楼","author":"王之涣","text":"白日依山尽……",
     "svg":"assets/1.svg",
     "facts":["……"],
     "proj":[["落日","白 日","两个大字悬在左上"]],
     "path":"左上「白日」起……",
     "checks":["……"]}
  ]
}
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
TEMPLATE = os.path.join(SKILL, "assets", "template.html")


def inline_svg(path):
    with open(path, encoding="utf-8") as f:
        svg = f.read()
    # 去掉固定的 width/height，改为响应式（保留 viewBox）
    svg = re.sub(r'\swidth="\d+(\.\d+)?"\s+height="\d+(\.\d+)?"', "", svg, count=1)
    return svg.strip()


def section(p, idx):
    facts = "\n".join("      <li>%s</li>" % html.escape(str(x), quote=False)
                      for x in p.get("facts", []))
    rows = "\n".join(
        "      <tr><td>%s</td><td>%s</td><td>%s</td></tr>" % tuple(
            html.escape(str(c), quote=False) for c in row)
        for row in p.get("proj", []))
    checks = "\n".join("      <li>%s</li>" % html.escape(str(x), quote=False)
                       for x in p.get("checks", []))
    author = ('<span style="font-size:.55em;color:var(--text3)">%s</span>'
              % html.escape(p["author"])) if p.get("author") else ""
    art = inline_svg(p["svg"]) if p.get("svg") and os.path.exists(p["svg"]) else \
        '<p style="color:#86868b;font-size:14px">（缺图，请把 SVG 路径填进 config 的 svg 字段）</p>'
    path_html = ""
    if p.get("path"):
        path_html = ('    <p class="path"><b>阅读路径：</b>%s</p>'
                     % html.escape(p["path"], quote=False))
    proj_html = ""
    if rows:
        proj_html = """
  <div class="block reveal">
    <div class="label">第二步 · 定投影</div>
    <table class="proj">
      <tr><th>意象</th><th>构成字</th><th>空间处理</th></tr>
%s
    </table>
  </div>""" % rows
    facts_html = ""
    if facts:
        facts_html = """
  <div class="block reveal">
    <div class="label">第一步 · 找事实</div>
    <ul class="facts">
%s
    </ul>
  </div>""" % facts
    checks_html = ""
    if checks:
        checks_html = """
  <div class="block reveal">
    <div class="label">对照检查</div>
    <ol class="checks">
%s
    </ol>
  </div>""" % checks
    return """
<section id="p%d">
  <div class="poem-head reveal">
    <div class="kicker">%s</div>
    <h2>%s %s</h2>
    <p class="fulltext">%s</p>
  </div>%s%s
  <div class="block reveal">
    <div class="label">排出来</div>
    <div class="artwork">
%s
    </div>%s
  </div>%s
</section>""" % (
        idx, html.escape(p.get("no", "No.%d" % idx)),
        html.escape(p.get("name", "")), author,
        html.escape(p.get("text", ""), quote=False),
        facts_html, proj_html, art, path_html, checks_html)


def find_chrome():
    for c in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Chromium.app/Contents/MacOS/Chromium",
              shutil.which("google-chrome"), shutil.which("chromium"),
              shutil.which("chrome")):
        if c and os.path.exists(c):
            return c
    return None


def shoot(chrome, src, dst, w, h):
    subprocess.run([chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--virtual-time-budget=6000",
                    "--window-size=%d,%d" % (w, h), "--screenshot=" + dst,
                    "file://" + os.path.abspath(src)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def export_png(chrome, cfg, out_html):
    for p in cfg.get("poems", []):
        svg = p.get("svg")
        if not svg or not os.path.exists(svg):
            continue
        head = open(svg, encoding="utf-8").read()[:400]
        w = re.search(r'width="(\d+)"', head)
        h = re.search(r'height="(\d+)"', head)
        w = int(w.group(1)) if w else 900
        h = int(h.group(1)) if h else 1200
        dst = os.path.splitext(svg)[0] + ".png"
        shoot(chrome, svg, dst, w, h)
        print("PNG:", dst)
    dst = os.path.join(os.path.dirname(os.path.abspath(out_html)), "_preview.png")
    shoot(chrome, out_html, dst, 1200, 1600)
    print("PNG:", dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="诗单 JSON")
    ap.add_argument("--out", default="poem-art.html")
    ap.add_argument("--png", action="store_true", help="同时导出 PNG（需 Chrome）")
    a = ap.parse_args()

    with open(a.config, encoding="utf-8") as f:
        cfg = json.load(f)
    poems = cfg.get("poems", [])
    if not poems:
        sys.exit("config 里没有 poems")

    with open(TEMPLATE, encoding="utf-8") as f:
        tpl = f.read()
    nav = "".join('<a href="#p%d">%s</a>' % (i, html.escape(p.get("name", "")))
                  for i, p in enumerate(poems, 1))
    notes = ""
    if cfg.get("notes"):
        items = "\n".join("      <li>%s</li>" % html.escape(str(x), quote=False)
                          for x in cfg["notes"])
        notes = """
<section>
  <div class="block reveal" style="margin-top:34px">
    <div class="label">%s</div>
    <ul class="facts">
%s
    </ul>
  </div>
</section>""" % (html.escape(cfg.get("notes_title", "说明"), quote=False), items)
    sections = "\n".join(section(p, i) for i, p in enumerate(poems, 1))
    out = (tpl.replace("{{TITLE}}", html.escape(cfg.get("title", "诗是有形状的")))
              .replace("{{KICKER}}", html.escape(cfg.get("kicker", "Poetry as Picture · 文字画")))
              .replace("{{SUBTITLE}}", html.escape(cfg.get("subtitle", ""), quote=False))
              .replace("{{META}}", html.escape(cfg.get("meta", ""), quote=False))
              .replace("{{NAV}}", nav)
              .replace("{{NOTES}}", notes)
              .replace("{{SECTIONS}}", sections))
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(out)
    print("HTML:", a.out, "(%d 首)" % len(poems))

    if a.png:
        chrome = find_chrome()
        if not chrome:
            print("未找到 Chrome，跳过 PNG")
        else:
            export_png(chrome, cfg, a.out)


if __name__ == "__main__":
    main()
