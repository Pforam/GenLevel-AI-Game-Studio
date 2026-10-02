import heapq
import html
import json
import os
import random

import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="GenLevel", page_icon="🕹️", layout="wide")

# --- Design tokens: sticker-book brutalism, Y2K pastels + chunky Gen Z energy ---
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,800&family=DM+Sans:wght@400;500;700&display=swap');
        :root { --bg:#E9E6FF; --ink:#1B1340; --pink:#FF4F9A; --lemon:#FFE45C; --mint:#4FE3B0; --sky:#8FC7FF; --paper:#FFFFFF; }
        .stApp { background: var(--bg); }
        html, body, .stApp, p, li, label, span, div { font-family: 'DM Sans', sans-serif; }
        .stApp, .stApp p, .stApp li, .stApp label, .stApp span { color: var(--ink); }
        h1, h2, h3, h4 { font-family: 'Bricolage Grotesque', sans-serif !important; color: var(--ink) !important; letter-spacing: -0.02em; }
        header[data-testid="stHeader"] { background: transparent; }
        [data-testid="stSidebar"] { background: var(--lemon); border-right: 3px solid var(--ink); }
        .stTextArea textarea, .stTextInput input, div[data-baseweb="select"] > div {
            background: var(--paper) !important; color: var(--ink) !important;
            border: 2.5px solid var(--ink) !important; border-radius: 12px !important; }
        .stTextArea textarea:focus, .stTextInput input:focus { box-shadow: 4px 4px 0 var(--pink) !important; }
        .stButton > button, .stDownloadButton > button {
            background: var(--pink); color: var(--ink); border: 2.5px solid var(--ink); border-radius: 12px;
            font-weight: 700; padding: 0.65rem 1.4rem; box-shadow: 4px 4px 0 var(--ink); transition: transform .08s, box-shadow .08s; }
        .stButton > button:hover, .stDownloadButton > button:hover { color: var(--ink); border-color: var(--ink); transform: translate(-1px,-1px); box-shadow: 6px 6px 0 var(--ink); }
        .stButton > button:active, .stDownloadButton > button:active { transform: translate(4px,4px); box-shadow: 0 0 0 var(--ink); }
        .stButton > button:focus-visible, .stDownloadButton > button:focus-visible { outline: 3px solid var(--ink); outline-offset: 3px; }
        button[kind="secondary"] { background: var(--paper); }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] { background: var(--paper); border: 2.5px solid var(--ink); border-radius: 999px; padding: .4rem 1.1rem; font-weight: 700; }
        .stTabs [aria-selected="true"] { background: var(--ink); }
        .stTabs [aria-selected="true"] p { color: var(--lemon) !important; }
        .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }
        .hero { background: var(--paper); border: 3px solid var(--ink); border-radius: 28px 28px 28px 6px; box-shadow: 8px 8px 0 var(--ink); padding: 2.2rem 2.4rem; margin-bottom: 2rem; }
        .hero-title { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: clamp(2.6rem,7vw,4.8rem); line-height: .95; letter-spacing: -.04em; margin: 0; }
        .hero-title .hl { background: var(--lemon); padding: 0 .18em; border-radius: 10px; }
        .hero-sub { font-size: 1.15rem; margin-top: 1rem; max-width: 66ch; }
        .card { background: var(--paper); border: 2.5px solid var(--ink); border-radius: 16px; padding: 1.3rem 1.5rem; margin-bottom: 1rem; box-shadow: 5px 5px 0 var(--ink); }
        .card h3 { margin-top: 0; }
        .card.pink { background: #FFD1E6; } .card.mint { background: #C5F6E4; } .card.sky { background: #D3E9FF; } .card.lemon { background: #FFF3A8; }
        .tag { display: inline-block; background: var(--lemon); border: 2px solid var(--ink); border-radius: 999px; padding: 2px 12px; font-weight: 700; font-size: .9rem; margin: 0 6px 6px 0; }
        .tag.pink { background: var(--pink); } .tag.mint { background: var(--mint); } .tag.sky { background: var(--sky); }
        .stats { display: flex; gap: 10px; flex-wrap: wrap; margin: .5rem 0 0; }
        .stat { background: var(--paper); border: 2.5px solid var(--ink); border-radius: 12px; padding: .4rem .9rem; font-weight: 700; }
        .node { background: var(--paper); border: 2.5px solid var(--ink); border-radius: 12px; padding: .8rem 1rem; margin-bottom: .7rem; }
        .node .go { margin: .35rem 0 0 .2rem; font-size: .95rem; }
        .quote { border-left: 6px solid var(--pink); padding-left: 1rem; font-style: italic; margin: 1rem 0; }
        .level-board { display: grid; gap: 4px; justify-content: center; background: var(--ink); padding: 16px; border-radius: 16px; box-shadow: 6px 6px 0 var(--pink); overflow-x: auto; }
        .tile { width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; font-size: 20px; border-radius: 6px; }
        @media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1 class="hero-title">Gen<span class="hl">Level</span></h1>
        <p class="hero-sub"><b>Describe a vibe. Get the full drop.</b><br>
        Levels you can actually beat, quests that really branch, and 3D worlds with coordinates.
        Gemini does the dreaming, our validators check it all holds together, no cap.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Blueprints ---
BP_2D = "2D Grid Level Layout"
BP_RPG = "RPG Quest & Dialogue Tree"
BP_3D = "3D World Asset Manifest"
BP_COMBO = "Quest + 3D World (combo)"

TILE_LEGEND = {
    0: {"name": "Empty space", "color": "#2B2160", "symbol": "·"},
    1: {"name": "Wall", "color": "#8C84C9", "symbol": "█"},
    2: {"name": "Enemy", "color": "#FF8A8A", "symbol": "👾"},
    3: {"name": "Coin", "color": "#FFE45C", "symbol": "🪙"},
    4: {"name": "Player spawn", "color": "#8FC7FF", "symbol": "🦸"},
    5: {"name": "Goal", "color": "#4FE3B0", "symbol": "🏁"},
}
CATEGORY_COLORS = {
    "structure": "#8FC7FF", "prop": "#FFE45C", "foliage": "#4FE3B0",
    "light": "#FFB86B", "character": "#FF4F9A", "hazard": "#FF8A8A", "other": "#C9C3F5",
}
SURPRISE_PROMPTS = [
    "A haunted arcade where the claw machines are alive",
    "A neon cyberpunk alleyway guarded by rogue bots",
    "A crumbling celestial temple overtaken by void magic",
    "A cozy mushroom village that's secretly a dungeon",
    "A sunken pirate mall with 2000s-era fountain traps",
]
PRESET_MAP = {
    "Cyberpunk neon hacker hideout": "A neon-lit cyber sanctuary guarded by rogue sentinels and data terminals",
    "Eldritch void cult dungeon": "A dark crumbling subterranean temple overtaken by cosmic void magic",
    "Sunken ancient alien ruins": "An underwater alien chamber filled with mysterious relics and energy traps",
}


# =========================== Helpers ===========================
def esc(value, default=""):
  """Escape model output before it goes into HTML."""
  return html.escape(str(value if value is not None else default))


def num(value, default=0.0):
  try:
    return float(value)
  except (TypeError, ValueError):
    return default


# =========================== Validators ===========================
def validate_level_solvability(grid):
  try:
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    start = goal = None
    for r in range(rows):
      for c in range(cols):
        if grid[r][c] == 4:
          start = (r, c)
        elif grid[r][c] == 5:
          goal = (r, c)
  except (TypeError, IndexError):
    return False, "The grid came back malformed."
  if not start or not goal:
    return False, "Missing a player spawn (4) or goal (5)."

  def h(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

  open_set = [(h(start, goal), 0, start)]
  g_score, closed = {start: 0}, set()
  while open_set:
    _, g, cur = heapq.heappop(open_set)
    if cur == goal:
      return True, "A* confirmed a clear path from spawn to goal."
    if cur in closed:
      continue
    closed.add(cur)
    r, c = cur
    for nr, nc in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]:
      if 0 <= nr < rows and 0 <= nc < len(grid[nr]) and grid[nr][nc] != 1:
        ng = g + 1
        if ng < g_score.get((nr, nc), float("inf")):
          g_score[(nr, nc)] = ng
          heapq.heappush(open_set, (ng + h((nr, nc), goal), ng, (nr, nc)))
  return False, "Walls fully block the route from spawn to goal."


def validate_dialogue(quest):
  """Every choice must lead somewhere real, and every node must be reachable."""
  if not isinstance(quest, dict):
    return False, "The quest came back malformed."
  nodes = quest.get("dialogue_nodes")
  if not isinstance(nodes, list) or len(nodes) < 3:
    return False, "The dialogue tree needs at least 3 nodes."
  ids = [n.get("id") for n in nodes if isinstance(n, dict)]
  if len(ids) != len(nodes) or None in ids or len(set(ids)) != len(ids):
    return False, "Dialogue node ids are missing or duplicated."
  if quest.get("start_node") not in ids:
    return False, "start_node doesn't match any node."
  by_id = {n["id"]: n for n in nodes}
  for n in nodes:
    for c in n.get("choices") or []:
      if c.get("next") != "END" and c.get("next") not in by_id:
        return False, f"Choice in node {n['id']} points to a missing node."
  seen, stack, ends = set(), [quest["start_node"]], False
  while stack:
    cur = stack.pop()
    if cur in seen:
      continue
    seen.add(cur)
    choices = by_id[cur].get("choices") or []
    if not choices:
      ends = True
    for c in choices:
      if c["next"] == "END":
        ends = True
      else:
        stack.append(c["next"])
  if len(seen) != len(nodes):
    return False, "Some dialogue nodes can never be reached."
  if not ends:
    return False, "The conversation never ends."
  return True, f"Dialogue tree checked: {len(nodes)} nodes, all reachable, with an ending."


def validate_world(world, min_assets):
  if not isinstance(world, dict):
    return False, "The world came back malformed."
  assets = world.get("assets")
  if not isinstance(assets, list) or len(assets) < max(3, min_assets // 2):
    return False, "The world has too few assets."
  for i, a in enumerate(assets, 1):
    if not isinstance(a, dict) or not a.get("object_name"):
      return False, "An asset is missing its name."
    a.setdefault("id", f"a{i}")
    if any(not isinstance(a.get(k), (int, float)) for k in ("x", "y", "z")):
      return False, f"Asset {a['id']} has non-numeric coordinates."
  if len({a["id"] for a in assets}) != len(assets):
    return False, "Asset ids aren't unique."
  sp = world.get("player_spawn")
  if not isinstance(sp, dict) or not isinstance(sp.get("x"), (int, float)) or not isinstance(sp.get("z"), (int, float)):
    return False, "player_spawn is missing."
  return True, f"World checked: {len(assets)} placed assets."


def validate_combo(data, min_assets):
  world, quest = data.get("world"), data.get("quest")
  ok, msg = validate_world(world, min_assets)
  if not ok:
    return ok, msg
  ok, msg = validate_dialogue(quest)
  if not ok:
    return ok, msg
  ids = {a["id"] for a in world["assets"]}
  if (quest.get("npc") or {}).get("asset_id") not in ids:
    return False, "The quest NPC isn't placed in the world."
  objs = quest.get("objectives")
  if not isinstance(objs, list) or len(objs) < 2:
    return False, "The quest needs at least 2 objectives."
  if any(o.get("target_asset_id") not in ids for o in objs):
    return False, "An objective points to an asset that doesn't exist."
  return True, "Quest and world are linked: the NPC and every objective sit at real coordinates."


def validate_content(content_type, data, o):
  if not isinstance(data, dict):
    return False, "The response wasn't a JSON object."
  if content_type == BP_2D:
    grid = data.get("grid", [])
    if len(grid) != o["height"] or any(len(r) != o["width"] for r in grid):
      return False, f"The grid wasn't {o['width']}×{o['height']}."
    return validate_level_solvability(grid)
  if content_type == BP_RPG:
    return validate_dialogue(data)
  if content_type == BP_3D:
    return validate_world(data, o["asset_count"])
  return validate_combo(data, o["asset_count"])


# =========================== Generation ===========================
QUEST_SCHEMA = (
    '{"quest_title": "string", "quest_summary": "string",'
    ' "npc": {"name": "string", "role": "string", "personality": "string"%s},'
    ' "start_node": "n1",'
    ' "dialogue_nodes": [{"id": "n1", "speaker": "string", "text": "string",'
    ' "choices": [{"text": "string", "next": "n2", "outcome": "string"}]}],'
    ' "objectives": [{"description": "string"%s}], "rewards": ["string"]}'
)
WORLD_SCHEMA = (
    '{"environment_theme": "string", "terrain": "string", "skybox": "string", "ambient_lighting": "string",'
    ' "player_spawn": {"x": float, "y": float, "z": float},'
    ' "assets": [{"id": "a1", "object_name": "string",'
    ' "category": "structure|prop|foliage|light|character|hazard",'
    ' "x": float, "y": float, "z": float, "scale": float, "rotation_y": float}]}'
)


def build_system_prompt(content_type, o):
  base = (
      "Be thorough and production-ready: no placeholder text, no empty strings. "
      "Output valid JSON only, with exactly this structure:\n"
  )
  dialogue_rules = (
      f"Write about {o['node_count']} dialogue nodes. Every choice 'next' must be an existing node id or \"END\". "
      "Every node must be reachable from start_node, and the tree needs at least 2 different endings "
      "(nodes with an empty choices list, or choices that go to \"END\"). Give 3+ objectives and 2+ rewards."
  )
  world_rules = (
      f"Place about {o['asset_count']} assets with unique ids, coordinates between -50 and 50 (y is height), "
      "grouped into believable zones, with a mix of categories."
  )
  if content_type == BP_2D:
    w, h = o["width"], o["height"]
    return (
        "You are an expert 2D video game level designer. " + base
        + '{"title": "string", "theme": "string", "difficulty": "string",'
        f' "width": {w}, "height": {h}, "grid": [[int, ...], ...], "lore": "string",'
        ' "objective": "string", "enemy_types": [{"name": "string", "behavior": "string"}],'
        ' "design_notes": "string"}\n'
        f"The grid must be exactly {w} columns by {h} rows. Tile IDs: 0=Empty, 1=Wall, 2=Enemy, 3=Coin, "
        "4=Player Start (exactly one), 5=Goal Exit (exactly one). Include at least 3 enemies and 4 coins, "
        "and keep a walkable path from 4 to 5. Describe 2-3 enemy types."
    )
  if content_type == BP_RPG:
    return (
        "You are an expert Narrative Designer for RPG games. " + base
        + QUEST_SCHEMA % ("", "") + "\n" + dialogue_rules
    )
  if content_type == BP_3D:
    return "You are a 3D Environment Artist and level builder. " + base + WORLD_SCHEMA + "\n" + world_rules
  return (
      "You are a game designer building a quest and the 3D world it takes place in. " + base
      + '{"world": ' + WORLD_SCHEMA + ', "quest": ' + QUEST_SCHEMA % (', "asset_id": "a1"', ', "target_asset_id": "a2"') + "}\n"
      + world_rules + " " + dialogue_rules
      + " The npc.asset_id must be the id of a 'character' asset in the world, and every objective "
      "needs a target_asset_id that is an existing asset id, so the quest happens at real coordinates."
  )


def generate_game_content(content_type, prompt, difficulty, temperature, api_key, o, max_retries=3):
  if not api_key:
    return None, "Add your Gemini API key in the sidebar first."
  client = OpenAI(
      api_key=api_key,
      base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
  )
  system_prompt = build_system_prompt(content_type, o)
  last_error = None
  for attempt in range(1, max_retries + 1):
    user_msg = f"Create content for this concept: '{prompt}'. Challenge level: {difficulty}."
    if last_error:
      user_msg += f" Your previous attempt failed validation: {last_error} Fix that."
    try:
      response = client.chat.completions.create(
          model="gemini-2.5-flash",
          messages=[
              {"role": "system", "content": system_prompt},
              {"role": "user", "content": user_msg},
          ],
          response_format={"type": "json_object"},
          temperature=temperature,
      )
      data = json.loads(response.choices[0].message.content)
      ok, message = validate_content(content_type, data, o)
      if ok:
        return data, f"Done on try {attempt}. {message}"
      last_error = message
    except Exception as e:
      last_error = str(e)
  return None, f"Couldn't get a valid result after {max_retries} tries. Last issue: {last_error}"


# =========================== Renderers ===========================
def world_map_svg(world, highlight=()):
  assets = world.get("assets", [])
  sp = world.get("player_spawn") or {}
  pts = [(num(a.get("x")), num(a.get("z"))) for a in assets] + [(num(sp.get("x")), num(sp.get("z")))]
  lo_x, hi_x = min(p[0] for p in pts), max(p[0] for p in pts)
  lo_z, hi_z = min(p[1] for p in pts), max(p[1] for p in pts)
  span, size, pad = max(hi_x - lo_x, hi_z - lo_z, 1), 420, 34

  def px(v): return pad + (v - lo_x) / span * (size - 2 * pad)
  def pz(v): return pad + (v - lo_z) / span * (size - 2 * pad)

  out = [
      f"<svg viewBox='0 0 {size} {size}' width='100%' style='max-width:460px;background:#fff;"
      "border:2.5px solid #1B1340;border-radius:16px;box-shadow:6px 6px 0 #1B1340'>"
  ]
  for a in assets:
    cx, cy = px(num(a.get("x"))), pz(num(a.get("z")))
    color = CATEGORY_COLORS.get(str(a.get("category", "other")).lower(), CATEGORY_COLORS["other"])
    hl = a.get("id") in highlight
    ring = "stroke='#FF4F9A' stroke-width='4'" if hl else "stroke='#1B1340' stroke-width='2'"
    out.append(
        f"<circle cx='{cx:.1f}' cy='{cy:.1f}' r='{12 if hl else 8}' fill='{color}' {ring}>"
        f"<title>{esc(a.get('object_name'))} ({esc(a.get('x'))}, {esc(a.get('z'))})</title></circle>"
    )
  sx, sy = px(num(sp.get("x"))), pz(num(sp.get("z")))
  out.append(
      f"<polygon points='{sx:.1f},{sy-12:.1f} {sx+12:.1f},{sy:.1f} {sx:.1f},{sy+12:.1f} {sx-12:.1f},{sy:.1f}'"
      " fill='#1B1340'><title>Player spawn</title></polygon></svg>"
  )
  return "".join(out)


def render_world(world, highlight=()):
  assets = world.get("assets", [])
  cats = {}
  for a in assets:
    k = str(a.get("category", "other")).lower()
    cats[k] = cats.get(k, 0) + 1
  stats = "".join(f"<div class='stat'>{esc(k)}: {v}</div>" for k, v in cats.items())
  st.markdown(
      f"""<div class="card mint"><span class="tag mint">3D world</span>
<h3>{esc(world.get('environment_theme'), 'Default')}</h3>
<p><b>Terrain:</b> {esc(world.get('terrain'), 'n/a')}<br><b>Sky:</b> {esc(world.get('skybox'), 'n/a')}<br>
<b>Lighting:</b> {esc(world.get('ambient_lighting'), 'n/a')}</p>
<div class="stats">{stats}</div></div>""",
      unsafe_allow_html=True,
  )
  st.markdown("#### Top-down map")
  st.markdown(world_map_svg(world, highlight), unsafe_allow_html=True)
  st.caption("◆ player spawn · hover a dot for its name · pink rings are quest targets")
  with st.expander("Spawn list (copy into your engine)"):
    st.code(
        "\n".join(
            f"SpawnActor('{a.get('object_name')}') — Vector3(x: {a.get('x')}, y: {a.get('y')}, z: {a.get('z')})"
            f" [Scale: {a.get('scale')}, RotY: {a.get('rotation_y')}°]"
            for a in assets
        ),
        language="python",
    )


def render_quest(quest, world=None):
  npc = quest.get("npc") or {}
  coords = {a["id"]: a for a in (world or {}).get("assets", [])}
  npc_at = ""
  if npc.get("asset_id") in coords:
    a = coords[npc["asset_id"]]
    npc_at = f" · found at ({esc(a.get('x'))}, {esc(a.get('z'))})"
  st.markdown(
      f"""<div class="card pink"><span class="tag">Quest</span>
<h3>{esc(quest.get('quest_title'))}</h3><p>{esc(quest.get('quest_summary'))}</p>
<p><b>{esc(npc.get('name'))}</b> · {esc(npc.get('role'))}{npc_at}<br><i>{esc(npc.get('personality'))}</i></p></div>""",
      unsafe_allow_html=True,
  )
  st.markdown("#### Objectives")
  for obj in quest.get("objectives", []):
    where = ""
    t = coords.get(obj.get("target_asset_id"))
    if t:
      where = f" <span class='tag sky'>{esc(t.get('object_name'))} @ ({esc(t.get('x'))}, {esc(t.get('z'))})</span>"
    st.markdown(f"<div class='node'>✅ {esc(obj.get('description'))}{where}</div>", unsafe_allow_html=True)

  st.markdown("#### Dialogue tree")
  for n in quest.get("dialogue_nodes", []):
    start = " <span class='tag mint'>start</span>" if n.get("id") == quest.get("start_node") else ""
    gos = "".join(
        f"<div class='go'>↳ <b>{esc(c.get('text'))}</b> → <code>{esc(c.get('next'))}</code>"
        f"{' · ' + esc(c.get('outcome')) if c.get('outcome') else ''}</div>"
        for c in n.get("choices") or []
    ) or "<div class='go'>🏁 <b>Ending</b></div>"
    st.markdown(
        f"""<div class='node'><span class='tag'>{esc(n.get('id'))}</span>{start}
<b>{esc(n.get('speaker'))}:</b> {esc(n.get('text'))}{gos}</div>""",
        unsafe_allow_html=True,
    )
  rewards = ", ".join(f"`{r}`" for r in quest.get("rewards", []))
  st.markdown(f"🎁 **Rewards:** {rewards}")


def render_level(data):
  grid = data.get("grid", [])
  flat = [c for row in grid for c in row]
  enemies = "".join(
      f"<li><b>{esc(e.get('name'))}:</b> {esc(e.get('behavior'))}</li>" for e in data.get("enemy_types", [])
  )
  st.markdown(
      f"""<div class="card"><span class="tag">{esc(data.get('theme', 'Custom'))}</span>
<span class="tag pink">{esc(data.get('difficulty', 'Normal'))}</span>
<h3>{esc(data.get('title'), 'Untitled level')}</h3>
<p class="quote">{esc(data.get('lore'), 'No lore this time.')}</p>
<p><b>Objective:</b> {esc(data.get('objective'), 'Reach the goal.')}</p>
<ul>{enemies}</ul><p><b>Design notes:</b> {esc(data.get('design_notes'), 'n/a')}</p>
<div class="stats"><div class="stat">👾 {flat.count(2)} enemies</div><div class="stat">🪙 {flat.count(3)} coins</div>
<div class="stat">📐 {len(grid[0]) if grid else 0}×{len(grid)}</div></div></div>""",
      unsafe_allow_html=True,
  )
  if grid:
    tiles = "".join(
        f"<div class='tile' title='{esc(t['name'])}' style='background:{t['color']};'>{t['symbol']}</div>"
        for row in grid
        for t in [TILE_LEGEND.get(c, {"name": "Unknown", "color": "#000", "symbol": "?"}) for c in row]
    )
    st.markdown(
        f"<div class='level-board' style='grid-template-columns: repeat({len(grid[0])}, 42px);'>{tiles}</div>",
        unsafe_allow_html=True,
    )


# =========================== Sidebar ===========================
def apply_preset():
  choice = st.session_state.get("preset_choice")
  if choice in PRESET_MAP:
    st.session_state["prompt_input"] = PRESET_MAP[choice]


def surprise_me():
  st.session_state["prompt_input"] = random.choice(SURPRISE_PROMPTS)
  st.session_state["preset_choice"] = "Pick a starter"


with st.sidebar:
  st.markdown("### Control room")
  gemini_api_key = st.text_input(
      "Gemini API key", type="password", value=os.environ.get("GEMINI_API_KEY", ""),
      help="Grab one free from Google AI Studio. It stays in this session.",
  )
  if gemini_api_key:
    st.success("Key added, you're good to go", icon="✅")
  else:
    st.warning("Add your key to start", icon="🔑")

  st.markdown("---")
  content_type = st.selectbox("What are we making?", [BP_2D, BP_RPG, BP_3D, BP_COMBO])
  if content_type == BP_COMBO:
    st.caption("One prompt, one connected result: a branching quest set inside a 3D world.")

  st.markdown("### Dial it in")
  temperature = st.slider(
      "Chaos level", 0.1, 1.0, 0.7,
      help="This is the model's temperature. Higher means weirder, more original ideas. Lower means safer.",
  )
  opts = {"width": 10, "height": 10, "asset_count": 16, "node_count": 6}
  if content_type == BP_2D:
    cw, ch = st.columns(2)
    opts["width"] = cw.slider("Width", 6, 15, 10)
    opts["height"] = ch.slider("Height", 6, 15, 10)
    st.markdown("#### Tile key")
    for info in TILE_LEGEND.values():
      st.markdown(f"{info['symbol']} &nbsp; **{info['name']}**")
  if content_type in (BP_3D, BP_COMBO):
    opts["asset_count"] = st.slider("World density (assets)", 8, 30, 16)
  if content_type in (BP_RPG, BP_COMBO):
    opts["node_count"] = st.slider("Conversation depth (nodes)", 4, 10, 6)

  st.markdown("---")
  st.markdown("### Quick starters")
  st.selectbox(
      "Load a sample concept", ["Pick a starter", *PRESET_MAP.keys()],
      key="preset_choice", on_change=apply_preset,
  )
  st.markdown("---")
  st.info("Everything is checked before you see it: A* for levels, link checks for quests and worlds.")

# =========================== Main ===========================
tab_generator, tab_types, tab_guide = st.tabs(
    ["The studio", "What can it make?", "Plug it into your engine"]
)

with tab_generator:
  col1, col2 = st.columns([1, 1], gap="large")
  with col1:
    st.markdown("### Pitch your world")
    prompt_input = st.text_area(
        "World concept", key="prompt_input", height=130,
        placeholder="e.g., A crumbling celestial temple overtaken by dark void magic",
    )
    difficulty_input = st.select_slider(
        "How rough should it be?", options=["Relaxed", "Balanced", "Hardcore", "Nightmare"]
    )
    b1, b2 = st.columns([2, 1])
    generate_btn = b1.button("Make it happen", type="primary", use_container_width=True)
    b2.button("🎲 Surprise me", on_click=surprise_me, use_container_width=True)

  if generate_btn:
    if not prompt_input.strip():
      st.warning("Write a quick concept first, even one line works.")
    else:
      with st.spinner("Cooking up your drop..."):
        data, status_msg = generate_game_content(
            content_type, prompt_input, difficulty_input, temperature, gemini_api_key, opts
        )
      if data:
        st.success(status_msg)
        st.session_state["game_data"] = data
        st.session_state["active_type"] = content_type
      else:
        st.error(status_msg)

  if "game_data" in st.session_state:
    data = st.session_state["game_data"]
    active_type = st.session_state.get("active_type", "")
    with col2:
      st.markdown("### Under the hood")
      with st.expander("Peek at the raw JSON", expanded=False):
        st.json(data)

    st.markdown("---")
    st.markdown("### Your drop")
    if active_type == BP_2D:
      render_level(data)
    elif active_type == BP_RPG:
      render_quest(data)
    elif active_type == BP_3D:
      render_world(data)
    elif active_type == BP_COMBO:
      world, quest = data.get("world", {}), data.get("quest", {})
      targets = {o.get("target_asset_id") for o in quest.get("objectives", [])}
      targets.add((quest.get("npc") or {}).get("asset_id"))
      left, right = st.columns([1, 1], gap="large")
      with left:
        render_world(world, highlight=targets)
      with right:
        render_quest(quest, world)

    st.markdown("---")
    st.download_button(
        label="Download JSON for your engine",
        data=json.dumps(data, indent=4),
        file_name="synthesized_game_asset.json",
        mime="application/json",
        use_container_width=True,
    )

with tab_types:
  st.markdown("## Pick your genre")
  st.markdown(
      "GenLevel outputs **structured JSON**, not baked assets, so one prompt box can feed very"
      " different kinds of games. Each type comes back complete, then gets validated."
  )
  r1a, r1b = st.columns(2)
  r2a, r2b = st.columns(2)
  cards = [
      (r1a, "sky", "🗺️ 2D grid levels",
       "Platformers, roguelikes, puzzle games, dungeon crawlers.",
       "A grid of tile IDs plus a title, lore, objective, enemy types and design notes. A* proves it's beatable and the size matches your sliders."),
      (r1b, "pink", "📜 RPG quests",
       "Story RPGs, visual novels, side quests.",
       "A full branching conversation: NPC profile, linked dialogue nodes, multiple endings, objectives and rewards. We check that every node is reachable."),
      (r2a, "mint", "🌍 3D world manifests",
       "Sandbox games, simulators, action-adventure worlds.",
       "Terrain, skybox and lighting, a player spawn, and a set of categorized assets with positions, scale and rotation, plus a top-down map preview."),
      (r2b, "lemon", "⚔️ Quest + 3D world combo",
       "Open-world games where the story lives in the level.",
       "One prompt gives you a world and a quest set inside it. The NPC and every objective point at real assets, so your story has coordinates."),
  ]
  for col, color, title, best, how in cards:
    with col:
      st.markdown(
          f"<div class='card {color}'><h3>{title}</h3><p><b>Good for:</b> {best}</p><p><b>You get:</b> {how}</p></div>",
          unsafe_allow_html=True,
      )

with tab_guide:
  st.markdown("## From JSON to playable")
  st.markdown("Starter snippets for getting each output type into your engine.")

  st.subheader("Unity: build a 2D grid")
  st.code(
      """
// C# Unity Runtime Parser Sample
using UnityEngine;

public class ProceduralMapLoader : MonoBehaviour {
    public GameObject[] tilePrefabs; // 0:Empty, 1:Wall, 2:Enemy, etc.

    public void BuildWorld(LevelDataPacket data) {
        for (int r = 0; r < data.grid.Count; r++) {
            for (int c = 0; c < data.grid[r].Count; c++) {
                int id = data.grid[r][c];
                if (id > 0) {
                    Instantiate(tilePrefabs[id], new Vector3(c, -r, 0), Quaternion.identity);
                }
            }
        }
    }
}
      """,
      language="csharp",
  )

  st.subheader("Web: run a branching dialogue tree")
  st.markdown("Each choice names the node it leads to. `END` closes the conversation.")
  st.code(
      """
// JavaScript dialogue controller for the node-based quest JSON
function showNode(quest, nodeId) {
    const node = quest.dialogue_nodes.find(n => n.id === nodeId);
    document.getElementById("npc-speaker").innerText = node.speaker;
    document.getElementById("npc-speech").innerText = node.text;

    const box = document.getElementById("choice-buttons");
    box.innerHTML = "";
    (node.choices || []).forEach(choice => {
        const btn = document.createElement("button");
        btn.innerText = choice.text;
        btn.onclick = () => choice.next === "END" ? endQuest(choice.outcome) : showNode(quest, choice.next);
        box.appendChild(btn);
    });
}
showNode(quest, quest.start_node);
      """,
      language="javascript",
  )

  st.subheader("Unreal / Blender: spawn a 3D world")
  st.code(
      """
# Python 3D Scene Builder Pipeline (e.g. Unreal Python API / Blender)
import json

with open("synthesized_game_asset.json") as f:
    world = json.load(f)  # for the combo type, use json.load(f)["world"]

for asset in world["assets"]:
    spawn_actor(
        name=asset["object_name"],
        location=(asset["x"], asset["y"], asset["z"]),
        scale=asset["scale"],
        rotation=(0, asset["rotation_y"], 0),
    )
      """,
      language="python",
  )

  st.subheader("Combo: put quest markers on the map")
  st.code(
      """
# Link each quest objective to its place in the world
import json

data = json.load(open("synthesized_game_asset.json"))
assets = {a["id"]: a for a in data["world"]["assets"]}

for obj in data["quest"]["objectives"]:
    target = assets[obj["target_asset_id"]]
    add_quest_marker(obj["description"], (target["x"], target["y"], target["z"]))
      """,
      language="python",
  )