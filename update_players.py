#!/usr/bin/env python3
from __future__ import annotations

import json, re, time, unicodedata
from pathlib import Path
from urllib.parse import quote_plus, unquote, urlparse, parse_qs
import requests
from bs4 import BeautifulSoup

PLAYERS_FILE = Path("players.json")
CONFIG_FILE = Path("competitions.json")
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/131.0 Safari/537.36"
})

EA_HOST = "https://www.ea.com"
EA_RATINGS = f"{EA_HOST}/games/ea-sports-fc/ratings"
SPORTSDB = "https://www.thesportsdb.com/api/v1/json/123/searchplayers.php?p="
POSITION_SET = {"GK","CB","LB","RB","LWB","RWB","CDM","CM","CAM","LM","RM","LW","RW","CF","ST"}

TEAM_ALIASES = {
    "FC Bayern München":["Bayern Munich","Bayern München","FC Bayern Munich"],
    "Bayer 04 Leverkusen":["Leverkusen","Bayer Leverkusen"],
    "Borussia Mönchengladbach":["M'gladbach","Borussia Monchengladbach"],
    "Eintracht Frankfurt":["Frankfurt"],
    "SV Werder Bremen":["Werder Bremen"],
    "1. FC Union Berlin":["Union Berlin"],
    "FC Schalke 04":["Schalke 04"],
    "Inter":["Inter Milan","Inter Milano","Inter Mailand"],
    "AC Milan":["AC Mailand","Milan"],
    "SSC Napoli":["Napoli","SSC Neapel"],
    "AS Roma":["Roma","AS Rom"],
    "Atlético de Madrid":["Atletico Madrid","Atlético Madrid"],
    "FC Barcelona":["Barcelona"],
    "Paris Saint-Germain":["Paris","PSG"],
    "FC Porto":["Porto"],
    "PSV":["PSV Eindhoven"],
    "RC Lens":["Lens","Racing Club De Lens"],
    "LOSC Lille":["Lille","Lille OSC"],
    "Villarreal CF":["Villarreal"],
    "Sporting CP":["Sporting"],
    "Slavia Praha":["Slavia Prague"],
    "Viking FK":["Viking"],
    "Bodø/Glimt":["Bodoe/Glimt","Bodo/Glimt"],
    "RSC Anderlecht":["Anderlecht"],
    "SL Benfica":["Benfica"],
    "AFC Bournemouth":["Bournemouth"],
    "RC Celta":["Celta","Celta Vigo"],
    "GNK Dinamo Zagreb":["GNK Dinamo","Dinamo Zagreb"],
    "Hapoel Be'er Sheva":["H. Beer-Sheva","Hapoel Beer Sheva"],
    "Olympique Lyonnais":["Lyon"],
    "Olympique de Marseille":["Marseille"],
    "Omonia Nicosia":["Omonia"],
    "Stade Rennais":["Rennes"],
    "FC Red Bull Salzburg":["Salzburg","RB Salzburg"],
    "Union Saint-Gilloise":["Union SG"],
    "Viktoria Plzeň":["Viktoria Plzen"],
    "Lillestrøm SK":["Lillestrøm","Lillestrom"],
    "N.E.C.":["NEC Nijmegen","N.E.C. Nijmegen"],
    "Vancouver Whitecaps FC":["Vancouver Whitecaps"],
    "Inter Miami CF":["Inter Miami"],
    "Al Nassr":["Al-Nassr","Al Nassr FC"],
    "Santos":["Santos FC"],
}

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.casefold().replace("&","and")
    return re.sub(r"[^a-z0-9]+","",s)

def get(url, timeout=30):
    r = SESSION.get(url, timeout=timeout)
    r.raise_for_status()
    return r

def discover_ea_url(team: str) -> str | None:
    # 1) DuckDuckGo HTML: searches only official EA team-rating pages.
    query = f'site:ea.com/games/ea-sports-fc/ratings/teams-ratings "{team}"'
    urls = []
    try:
        html = get("https://html.duckduckgo.com/html/?q="+quote_plus(query)).text
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.select("a[href]"):
            href = a.get("href","")
            if "uddg=" in href:
                try:
                    href = unquote(parse_qs(urlparse(href).query).get("uddg",[""])[0])
                except Exception:
                    pass
            if "/games/ea-sports-fc/ratings/teams-ratings/" in href and "ea.com" in href:
                urls.append(href.split("?")[0])
    except Exception as e:
        print(f"  DDG-Suche fehlgeschlagen: {e}")

    # 2) Bing HTML fallback.
    if not urls:
        try:
            html = get("https://www.bing.com/search?q="+quote_plus(query)).text
            for m in re.findall(r'https?://(?:www\.)?ea\.com/[^"\'<>\s]+/ratings/teams-ratings/[^"\'<>\s]+', html):
                urls.append(m.split("&")[0].split("?")[0])
        except Exception as e:
            print(f"  Bing-Suche fehlgeschlagen: {e}")

    # Prefer a URL whose slug/title resembles the requested team.
    nt = norm(team)
    aliases = [team] + TEAM_ALIASES.get(team,[])
    alias_norms = [norm(x) for x in aliases]
    candidates = []
    for u in dict.fromkeys(urls):
        score = 0
        nu = norm(u)
        if any(a and a in nu for a in alias_norms): score += 5
        candidates.append((score,u))
    if candidates:
        candidates.sort(reverse=True)
        return candidates[0][1]
    return None

def row_player(row, canonical_team):
    a = row.select_one('a[href*="/ratings/player-ratings/"]')
    if not a:
        return None
    href = a.get("href","")
    if href.startswith("/"):
        href = EA_HOST + href
    name = re.sub(r"^#?\d+\s*", "", " ".join(a.stripped_strings)).strip()
    if not name:
        return None
    text = " ".join(row.stripped_strings)
    patterns = {
        "rating": r"(?:OVR|GES)\s*(\d{1,2})",
        "tempo": r"(?:PAC|TEM)\s*(\d{1,2})",
        "schuss": r"(?:SHO|SCH)\s*(\d{1,2})",
        "passen": r"(?:PAS)\s*(\d{1,2})",
        "dribbling": r"(?:DRI)\s*(\d{1,2})",
        "defensive": r"(?:DEF)\s*(\d{1,2})",
        "physis": r"(?:PHY)\s*(\d{1,2})",
    }
    vals={}
    for k,p in patterns.items():
        m=re.search(p,text,re.I)
        if m: vals[k]=int(m.group(1))
    if "rating" not in vals:
        return None
    pos=""
    for token in re.findall(r"\b[A-Z]{2,3}\b", text):
        if token in POSITION_SET:
            pos=token; break
    m = re.search(r"/player-ratings/[^/]+/(\d+)", href)
    ea_id = m.group(1) if m else ""
    return {
        "name":name,
        "search":name,
        "club":canonical_team,
        "eaId":ea_id,
        "eaUrl":href,
        "pos":pos,
        **vals
    }

def fetch_team_players(team, top_n, url_cache):
    url = url_cache.get(team) or discover_ea_url(team)
    if not url:
        raise RuntimeError(f"Keine EA-Teamseite gefunden: {team}")
    url_cache[team]=url
    print(f"EA: {team} -> {url}")
    html=get(url).text
    soup=BeautifulSoup(html,"html.parser")
    rows=[]
    seen=set()
    for tr in soup.select("tr"):
        p=row_player(tr, team)
        if p and p.get("eaId") not in seen:
            rows.append(p); seen.add(p.get("eaId"))
    # fallback: some builds use div/grid instead of tr
    if len(rows)<top_n:
        for a in soup.select('a[href*="/ratings/player-ratings/"]'):
            parent=a
            for _ in range(6):
                parent=parent.parent if parent else None
                if not parent: break
                txt=" ".join(parent.stripped_strings)
                if re.search(r"(?:OVR|GES)\s*\d{1,2}",txt) and re.search(r"(?:PAC|TEM)\s*\d{1,2}",txt):
                    class Dummy:
                        def __init__(self,node): self.node=node
                        def select_one(self,q): return self.node.select_one(q)
                        @property
                        def stripped_strings(self): return self.node.stripped_strings
                    p=row_player(Dummy(parent),team)
                    if p and p.get("eaId") not in seen:
                        rows.append(p); seen.add(p.get("eaId"))
                    break
    if len(rows)<top_n:
        print(f"  WARNUNG: nur {len(rows)} statt {top_n} Spieler gefunden.")
    # EA team pages are already ordered by rank; keep first N.
    return rows[:top_n]

def discover_player_url(name, club=""):
    query=f'site:ea.com/games/ea-sports-fc/ratings/player-ratings "{name}"'
    if club: query+=f' "{club}"'
    try:
        html=get("https://html.duckduckgo.com/html/?q="+quote_plus(query)).text
        soup=BeautifulSoup(html,"html.parser")
        for a in soup.select("a[href]"):
            href=a.get("href","")
            if "uddg=" in href:
                try: href=unquote(parse_qs(urlparse(href).query).get("uddg",[""])[0])
                except Exception: pass
            if "/ratings/player-ratings/" in href and "ea.com" in href:
                return href.split("?")[0]
    except Exception:
        pass
    return None

def parse_player_page(url, fallback):
    html=get(url).text
    text=" ".join(BeautifulSoup(html,"html.parser").stripped_strings)
    out=dict(fallback)
    out["eaUrl"]=url
    m=re.search(r"/player-ratings/[^/]+/(\d+)",url); 
    if m: out["eaId"]=m.group(1)
    pats={
      "rating":r"(?:overall rating.*?is|Gesamtwertung.*?ist)\s*(\d{1,2})",
      "tempo":r"(?:Pace|Tempo)\s+(\d{1,2})",
      "schuss":r"(?:Shooting|Schüsse)\s+(\d{1,2})",
      "passen":r"(?:Passing|Passen)\s+(\d{1,2})",
      "dribbling":r"Dribbling\s+(\d{1,2})",
      "defensive":r"(?:Defending|Defensive)\s+(\d{1,2})",
      "physis":r"(?:Physicality|Physis)\s+(\d{1,2})",
    }
    for k,p in pats.items():
        m=re.search(p,text,re.I)
        if m: out[k]=int(m.group(1))
    # position from the early "Position XX" area
    m=re.search(r"\bPosition\s+([A-Z]{2,3})\b",text)
    if m: out["pos"]=m.group(1)
    return out

def rarity(rating):
    if rating>=90: return "Legend"
    if rating>=80: return "Gold"
    if rating>=70: return "Silver"
    return "Bronze"

def sportsdb_enrich(rows):
    # Step 1: resolve SportsDB IDs and team IDs.
    for i,p in enumerate(rows,1):
        if p.get("sportsdbId") and p.get("sportsdbTeamId"):
            continue
        try:
            data=get(SPORTSDB+quote_plus(p.get("search") or p["name"])).json()
            candidates=data.get("player") or []
            exact=[x for x in candidates if norm(x.get("strPlayer"))==norm(p["name"])]
            x=(exact or candidates or [None])[0]
            if x:
                p["sportsdbId"]=x.get("idPlayer") or p.get("sportsdbId")
                p["sportsdbTeamId"]=x.get("idTeam") or p.get("sportsdbTeamId")
            time.sleep(2.1)  # stay under free API rate limit
        except Exception as e:
            print(f"SportsDB {p['name']}: {e}")

    # Step 2: fetch each team cartoon page once and map by SportsDB player id.
    team_ids=sorted({str(p.get("sportsdbTeamId")) for p in rows if p.get("sportsdbTeamId")})
    cartoon_by_id={}
    for tid in team_ids:
        try:
            html=get(f"https://www.thesportsdb.com/team/{tid}?view=7#playerImages").text
            soup=BeautifulSoup(html,"html.parser")
            for a in soup.select('a[href*="/player/"]'):
                m=re.search(r"/player/(\d+)",a.get("href",""))
                img=a.find("img")
                if not m or not img: continue
                src=img.get("src") or img.get("data-src") or img.get("data-original") or ""
                if "/images/media/player/cartoon/" in src:
                    cartoon_by_id[m.group(1)]=src
            time.sleep(.8)
        except Exception as e:
            print(f"Cartoon-Team {tid}: {e}")
    for p in rows:
        sid=str(p.get("sportsdbId") or "")
        if sid in cartoon_by_id:
            p["cartoon"]=cartoon_by_id[sid]

def load_existing():
    if not PLAYERS_FILE.exists(): return []
    return json.loads(PLAYERS_FILE.read_text(encoding="utf-8"))

def write_one_line(rows):
    lines=["["]
    for i,p in enumerate(rows):
        lines.append("  "+json.dumps(p,ensure_ascii=False,separators=(",",":"))+("," if i<len(rows)-1 else ""))
    lines.append("]")
    PLAYERS_FILE.write_text("\n".join(lines)+"\n",encoding="utf-8")

def main():
    cfg=json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    existing=load_existing()
    old_by_ea={str(p.get("eaId")):p for p in existing if p.get("eaId")}
    old_by_name={norm(p.get("name")):p for p in existing if p.get("name")}
    max_id=max([int(p.get("id",0)) for p in existing]+[0])
    next_id=max(max_id+1,281)

    # Preserve manual rows (easy future editing).
    manual=[dict(p) for p in existing if p.get("manual") is True]

    team_url_cache={}
    merged={}
    failures=[]

    for comp_id,comp in cfg["competitions"].items():
        n=int(comp["top_n"])
        for team in comp["teams"]:
            try:
                ps=fetch_team_players(team,n,team_url_cache)
            except Exception as e:
                failures.append(f"{comp_id}: {team}: {e}")
                print("FEHLER",failures[-1]); continue
            for p in ps:
                key=("ea",p.get("eaId")) if p.get("eaId") else ("name",norm(p["name"]),norm(p["club"]))
                old=old_by_ea.get(str(p.get("eaId"))) or old_by_name.get(norm(p["name"])) or {}
                if key not in merged:
                    rec=dict(old)
                    rec.update(p)
                    rec["competitions"]=[]
                    merged[key]=rec
                if comp_id not in merged[key]["competitions"]:
                    merged[key]["competitions"].append(comp_id)
            time.sleep(.5)

    # Manual rows: keep and update FC27 values when possible.
    for m in manual:
        name=m["name"]; club=m.get("club","")
        # If same player was already included by a competition, just add manual categories.
        same=None
        for k,r in merged.items():
            if norm(r.get("name"))==norm(name):
                same=r; break
        if same is not None:
            for c in m.get("competitions",[]):
                if c not in same["competitions"]: same["competitions"].append(c)
            same["manual"]=True
            continue
        url=m.get("eaUrl") or discover_player_url(name,club)
        rec=dict(m)
        if url:
            try: rec=parse_player_page(url,rec)
            except Exception as e: print(f"EA Einzelspieler {name}: {e}")
        key=("ea",rec.get("eaId")) if rec.get("eaId") else ("manual",norm(name),norm(club))
        merged[key]=rec

    rows=list(merged.values())

    # Stable app IDs: preserve old IDs, then assign new IDs.
    used=set()
    for p in rows:
        if p.get("id"):
            try: used.add(int(p["id"]))
            except: pass
    for p in rows:
        old=old_by_ea.get(str(p.get("eaId"))) or old_by_name.get(norm(p.get("name"))) or {}
        if old.get("id") and not p.get("id"):
            p["id"]=old["id"]; used.add(int(old["id"]))
        if not p.get("id"):
            while next_id in used: next_id+=1
            p["id"]=next_id; used.add(next_id); next_id+=1

        p["search"]=p.get("search") or p["name"]
        p["rarity"]=rarity(int(p.get("rating") or 0))
        p["theme"]="fussball"; p["emoji"]="⚽"; p["color"]="#1f6f50"
        # predictable category order
        order=["bundesliga","champions","europa","legenden"]
        p["competitions"]=sorted(set(p.get("competitions",[])),key=lambda x:order.index(x) if x in order else 99)

    # Reuse existing cartoon / SportsDB data wherever possible.
    for p in rows:
        old=old_by_ea.get(str(p.get("eaId"))) or old_by_name.get(norm(p.get("name"))) or {}
        for k in ("sportsdbId","sportsdbTeamId","cartoon"):
            if old.get(k) and not p.get(k): p[k]=old[k]

    sportsdb_enrich(rows)

    comp_order={"bundesliga":0,"champions":1,"europa":2,"legenden":3}
    def sortkey(p):
        cs=p.get("competitions") or ["zzz"]
        first=min([comp_order.get(c,9) for c in cs] or [9])
        return (first, norm(p.get("club")), -(int(p.get("rating") or 0)), norm(p.get("name")))
    rows.sort(key=sortkey)

    # consistent field order
    field_order=["id","name","search","club","competitions","manual","eaId","eaUrl","pos","rating","rarity",
                 "tempo","schuss","passen","dribbling","defensive","physis","theme","emoji","color",
                 "sportsdbId","sportsdbTeamId","cartoon"]
    clean=[]
    for p in rows:
        clean.append({k:p[k] for k in field_order if k in p and p[k] not in (None,"")})
    write_one_line(clean)

    print(f"\nFERTIG: {len(clean)} Spieler in players.json")
    if failures:
        print("\nNicht automatisch geladene Teams:")
        for x in failures: print(" -",x)
        print("Die Action endet trotzdem erfolgreich, damit bereits gefundene Daten nicht verloren gehen.")

if __name__=="__main__":
    main()
