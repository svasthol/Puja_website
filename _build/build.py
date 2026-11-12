#!/usr/bin/env python3
"""Builds the managuruji.in static site into the repository root.

Edit BIZ / the catalogue below or the files in src/, then run:  python3 _build/build.py
"""
import json, math, os, re, shutil, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
OUT = os.path.dirname(HERE)  # repo root = the published site

# ----------------------------------------------------------------------------
# BUSINESS DETAILS — edit these, then run:  python3 build.py
# ----------------------------------------------------------------------------
BIZ = {
    "brand": "Mana Guruji",
    "legal": "Mana Guruji",
    "udyam": "UDYAM-TS-20-0209216",
    "address": "Hyderabad, Telangana 500083, India",
    "email": "support@managuruji.in",            # bookings, payments, refunds, complaints
    "contact_email": "contact@managuruji.in",    # general enquiries and collaborations
    "hours_en": "6:00 AM to 9:00 PM, all days",
    "hours_te": "ఉదయం 6:00 నుండి రాత్రి 9:00 వరకు, అన్ని రోజులు",
    "domain": "managuruji.in",
    "updated": "10 November 2026",
    "refund_before_24h": 90,   # % of amount paid, cancelled >24h before puja
    "refund_within_24h": 50,   # % of amount paid, cancelled within 24h of puja
}

# ----------------------------------------------------------------------------
# CATALOGUE — prices in INR (pandit service fee for one pandit) + optional kit
# ----------------------------------------------------------------------------
CATS = [
    ("vratams", "Vratams & Pujas", "వ్రతాలు & పూజలు", "kalash",
     "Household vratams and pujas performed with full vidhi.", "పూర్తి విధివిధానాలతో ఇంటి వ్రతాలు, పూజలు."),
    ("home", "Home & Property", "గృహం & స్థలం", "home",
     "For a new home, a plot, or construction about to begin.", "కొత్త ఇల్లు, స్థలం, నిర్మాణ ప్రారంభం కోసం."),
    ("homams", "Homams", "హోమాలు", "fire",
     "Vedic fire rituals with japam and purnahuti.", "జపం, పూర్ణాహుతితో వైదిక హోమాలు."),
    ("samskaras", "Family Ceremonies", "సంస్కారాలు", "lamp",
     "Samskaras that mark each stage of life.", "జీవితంలో ప్రతి దశను సూచించే సంస్కారాలు."),
    ("business", "Business & Vehicle", "వ్యాపారం & వాహనం", "wheel",
     "Openings for offices, shops and new vehicles.", "కార్యాలయ, దుకాణ ప్రారంభాలు, కొత్త వాహనాలు."),
    ("online", "Online Pujas", "ఆన్‌లైన్ పూజలు", "screen",
     "Live over video call, for families anywhere.", "ఎక్కడ ఉన్నా వీడియో కాల్ ద్వారా ప్రత్యక్షంగా."),
]

S = []
def seva(id, cat, en, te, price, kit, dur_en, dur_te, d_en, d_te):
    S.append(dict(id=id, cat=cat, en=en, te=te, price=price, kit=kit,
                  durEn=dur_en, durTe=dur_te, dEn=d_en, dTe=d_te))

seva("satyanarayana", "vratams", "Sri Satyanarayana Swamy Vratham", "శ్రీ సత్యనారాయణ స్వామి వ్రతం", 2500, 1500, "2 to 2.5 hours", "2 – 2.5 గంటలు",
     "The full vratham with Ganapathi puja, kalasha sthapana, all five katha chapters and prasadam nivedana. Popular for housewarmings, birthdays, anniversaries and new ventures.",
     "గణపతి పూజ, కలశ స్థాపన, ఐదు అధ్యాయాల వ్రత కథ, ప్రసాద నివేదనతో పూర్తి వ్రతం. గృహప్రవేశం, పుట్టినరోజు, వివాహ వార్షికోత్సవాలకు అనువైనది.")
seva("varalakshmi", "vratams", "Sri Varalakshmi Vratham", "శ్రీ వరలక్ష్మీ వ్రతం", 2500, 1500, "About 2 hours", "సుమారు 2 గంటలు",
     "Sravana masam vratham for Sri Varalakshmi Devi with kalasha alankarana, thoram puja and the vratha katha.",
     "శ్రావణ మాసంలో వరలక్ష్మీ దేవి వ్రతం: కలశ అలంకరణ, తోరపూజ, వ్రత కథ.")
seva("lakshmi-kubera", "vratams", "Sri Lakshmi Kubera Puja", "శ్రీ లక్ష్మీ కుబేర పూజ", 2700, 1600, "1.5 to 2 hours", "1.5 – 2 గంటలు",
     "Puja to Sri Mahalakshmi and Kubera with ashtottaram and archana. Often performed on Deepavali, Dhanatrayodashi or at a new shop.",
     "అష్టోత్తరం, అర్చనతో శ్రీ మహాలక్ష్మి, కుబేర పూజ. దీపావళి, ధనత్రయోదశి, కొత్త దుకాణ ప్రారంభంలో చేస్తారు.")
seva("rudrabhishekam", "vratams", "Rudrabhishekam", "రుద్రాభిషేకం", 3100, 1800, "About 2 hours", "సుమారు 2 గంటలు",
     "Abhishekam of Lord Shiva with Sri Rudram (namakam and chamakam), using milk, curd, honey and panchamrutham.",
     "శ్రీ రుద్రం (నమకం, చమకం) పఠనంతో పాలు, పెరుగు, తేనె, పంచామృతాలతో శివునికి అభిషేకం.")
seva("gruhapravesam", "home", "Gruhapravesam (Housewarming)", "గృహప్రవేశం", 7500, 3500, "3 to 4 hours", "3 – 4 గంటలు",
     "Ganapathi puja, punyahavachanam, Vastu puja and Navagraha puja, followed by the ceremonial entry into the home and the traditional boiling of milk.",
     "గణపతి పూజ, పుణ్యాహవాచనం, వాస్తు పూజ, నవగ్రహ పూజ, తర్వాత గృహప్రవేశం, పాలు పొంగించడం.")
seva("bhoomi-puja", "home", "Bhoomi Puja & Shankusthapana", "భూమి పూజ & శంకుస్థాపన", 5100, 2500, "1.5 to 2 hours", "1.5 – 2 గంటలు",
     "Performed at the site before construction begins: Ganapathi puja, Bhoodevi puja and laying of the foundation stone.",
     "నిర్మాణం ప్రారంభానికి ముందు స్థలంలో: గణపతి పూజ, భూదేవి పూజ, శంకుస్థాపన.")
seva("ganapathi-homam", "homams", "Sri Maha Ganapathi Homam", "శ్రీ మహాగణపతి హోమం", 6500, 4500, "About 2 hours", "సుమారు 2 గంటలు",
     "Homam to Sri Maha Ganapathi before any new undertaking, with sankalpam, moola mantra japam and purnahuti.",
     "కొత్త పని ప్రారంభానికి ముందు శ్రీ మహాగణపతి హోమం: సంకల్పం, మూలమంత్ర జపం, పూర్ణాహుతి.")
seva("navagraha-homam", "homams", "Navagraha Homam", "నవగ్రహ హోమం", 11000, 6000, "About 3 hours", "సుమారు 3 గంటలు",
     "Homam for the nine grahas with japam and the prescribed samidhas for each graha, followed by purnahuti.",
     "తొమ్మిది గ్రహాలకు ప్రత్యేక జపం, నిర్దిష్ట సమిధలతో నవగ్రహ హోమం, పూర్ణాహుతి.")
seva("sudarshana-homam", "homams", "Sri Sudarshana Homam", "శ్రీ సుదర్శన హోమం", 12000, 6500, "About 3 hours", "సుమారు 3 గంటలు",
     "Homam to Sri Sudarshana with the Sudarshana mantra, traditionally performed for the wellbeing of the family and home.",
     "కుటుంబ, గృహ క్షేమం కోసం సుదర్శన మంత్రంతో శ్రీ సుదర్శన హోమం.")
seva("ayush-homam", "homams", "Ayush Homam", "ఆయుష్ హోమం", 8500, 4500, "About 2.5 hours", "సుమారు 2.5 గంటలు",
     "Performed on birthdays, especially the first birthday, praying for a long and healthy life.",
     "పుట్టినరోజున, ముఖ్యంగా మొదటి పుట్టినరోజున, దీర్ఘాయుష్షు, ఆరోగ్యం కోసం చేసే హోమం.")
seva("namakaranam", "samskaras", "Namakaranam (Naming Ceremony)", "నామకరణం", 2700, 1400, "About 1.5 hours", "సుమారు 1.5 గంటలు",
     "Naming ceremony for the newborn with Ganapathi puja, punyahavachanam and the traditional naming.",
     "శిశువుకు నామకరణం: గణపతి పూజ, పుణ్యాహవాచనం, సంప్రదాయ పద్ధతిలో పేరు పెట్టడం.")
seva("annaprasana", "samskaras", "Annaprasana", "అన్నప్రాశన", 2700, 1300, "About 1.5 hours", "సుమారు 1.5 గంటలు",
     "The baby's first rice-feeding ceremony, usually in the sixth month, with puja and blessings.",
     "సాధారణంగా ఆరవ నెలలో శిశువుకు మొదటిసారి అన్నం తినిపించే వేడుక, పూజ, ఆశీర్వచనం.")
seva("aksharabhyasam", "samskaras", "Aksharabhyasam", "అక్షరాభ్యాసం", 2500, 1300, "About 1 hour", "సుమారు 1 గంట",
     "Initiation into learning with Saraswathi and Ganapathi puja. The child writes the first letters on rice.",
     "సరస్వతి, గణపతి పూజతో విద్యారంభం. బియ్యంపై మొదటి అక్షరాలు దిద్దిస్తారు.")
seva("upanayanam", "samskaras", "Upanayanam", "ఉపనయనం", 15000, 6000, "5 to 6 hours", "5 – 6 గంటలు",
     "Sacred thread ceremony with udakashanti, yajnopaveetha dharana and Gayatri upadesam. The price covers the pandits needed for a standard ceremony; more pandits can be arranged on request.",
     "ఉదకశాంతి, యజ్ఞోపవీత ధారణ, గాయత్రీ ఉపదేశంతో ఉపనయనం. సాధారణ కార్యక్రమానికి అవసరమైన పండితులు ధరలో ఉన్నారు; కోరితే అదనపు పండితులను ఏర్పాటు చేస్తాం.")
seva("shashtipoorthi", "samskaras", "Shashtipoorthi (60th Birthday)", "షష్టిపూర్తి", 31000, 12000, "5 to 6 hours", "5 – 6 గంటలు",
     "Sixtieth birthday ceremony with Ugraratha Shanti homam, kalasha abhishekam and mangalya dharana.",
     "60వ పుట్టినరోజు వేడుక: ఉగ్రరథ శాంతి హోమం, కలశాభిషేకం, మాంగల్య ధారణ.")
seva("office-opening", "business", "Office / Shop Opening Puja", "కార్యాలయ / దుకాణ ప్రారంభ పూజ", 5100, 2500, "About 2 hours", "సుమారు 2 గంటలు",
     "Ganapathi puja, Lakshmi puja and Vastu puja for a new office, shop, clinic or factory.",
     "కొత్త కార్యాలయం, దుకాణం, క్లినిక్ లేదా ఫ్యాక్టరీ కోసం గణపతి, లక్ష్మీ, వాస్తు పూజ.")
seva("vahana-puja", "business", "Vahana Puja (New Vehicle)", "వాహన పూజ", 1500, 600, "About 45 minutes", "సుమారు 45 నిమిషాలు",
     "Puja for a new car, bike or commercial vehicle with Ganapathi puja, kumkum archana and breaking of the coconut.",
     "కొత్త కారు, బైక్ లేదా వాణిజ్య వాహనానికి గణపతి పూజ, కుంకుమ అర్చన, కొబ్బరికాయ కొట్టడం.")
seva("online-satyanarayana", "online", "Online Satyanarayana Vratham", "ఆన్‌లైన్ సత్యనారాయణ వ్రతం", 2100, 0, "About 2 hours", "సుమారు 2 గంటలు",
     "The pandit performs and guides the full vratham live over a video call while your family follows at home. Samagri list shared in advance.",
     "పండితులు వీడియో కాల్ ద్వారా పూర్తి వ్రతాన్ని నిర్వహిస్తూ మార్గనిర్దేశం చేస్తారు. సామగ్రి జాబితా ముందుగానే పంపుతాం.")
seva("online-ganapathi", "online", "Online Ganapathi Puja", "ఆన్‌లైన్ గణపతి పూజ", 1500, 0, "About 1 hour", "సుమారు 1 గంట",
     "Ganapathi puja guided live over video call, for families anywhere in India or abroad.",
     "భారతదేశంలో లేదా విదేశాల్లో ఎక్కడ ఉన్నా వీడియో కాల్ ద్వారా ప్రత్యక్షంగా గణపతి పూజ.")

AREAS = ["Kukatpally", "KPHB", "Miyapur", "Nizampet", "Kondapur", "Gachibowli", "Madhapur", "Manikonda",
         "Ameerpet", "Begumpet", "Banjara Hills", "Jubilee Hills", "Secunderabad", "Malkajgiri", "Kompally",
         "Uppal", "LB Nagar", "Dilsukhnagar", "Vanasthalipuram", "Chandanagar"]

def inr(n):
    s = str(n)
    if len(s) <= 3: return "₹" + s
    head, tail = s[:-3], s[-3:]
    head = re.sub(r"(\d)(?=(\d\d)+$)", r"\1,", head)
    return "₹" + head + "," + tail

def B(en, te):
    return f'<span class="en">{en}</span><span class="te">{te}</span>'

# ----------------------------------------------------------------------------
# SVG ornaments
# ----------------------------------------------------------------------------
def emblem(size=44):
    return f'<img class="emblem" src="assets/emblem-96.webp" width="{size}" height="{size}" alt="">'

def thoranam_uri(string_col="#c98a2b"):
    leaf = "M0,0 C7,9 7,25 0,36 C-7,25 -7,9 0,0Z"
    parts = [f'<path d="M0,5 Q30,12 60,5 T120,5" fill="none" stroke="{string_col}" stroke-width="2"/>']
    for x in (15, 45, 75, 105):
        parts.append(f'<g transform="translate({x},8)"><path d="{leaf}" fill="#4f7a2a"/><path d="M0,2 L0,32" stroke="#86ac4f" stroke-width="1"/></g>')
    for x in (0, 30, 60, 90, 120):
        parts.append(f'<circle cx="{x}" cy="10" r="6.5" fill="#e8891c"/><circle cx="{x}" cy="10" r="3" fill="#f6b23e"/><circle cx="{x}" cy="19" r="4" fill="#f0a020"/>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="120" height="46" viewBox="0 0 120 46">{"".join(parts)}</svg>'
    return "data:image/svg+xml," + urllib.parse.quote(svg)

def hero_art():
    cx, cy = 250, 150
    rays = []
    for i in range(36):
        a = math.radians(i * 10)
        w = 0.045 if i % 2 else 0.07
        r1, r2 = 96, (178 if i % 2 == 0 else 142)
        p = [(cx + r1 * math.cos(a - w), cy + r1 * math.sin(a - w)), (cx + r2 * math.cos(a), cy + r2 * math.sin(a)),
             (cx + r1 * math.cos(a + w), cy + r1 * math.sin(a + w))]
        rays.append("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in p) + "Z")
    def puff(x, y, k=1.0):
        c = [(0, 0, 22), (24, -8, 26), (52, 0, 20), (26, 10, 22), (-18, 8, 15), (70, 8, 14)]
        return "".join(f'<circle cx="{x + dx * k:.1f}" cy="{y + dy * k:.1f}" r="{r * k:.1f}"/>' for dx, dy, r in c)
    drift = ""
    specs = [("l", 150, 400, 1.0, 0), ("l", 120, 455, 1.2, -1.7), ("l", 170, 485, .9, -3.4),
             ("r", 290, 400, 1.0, -.8), ("r", 320, 455, 1.2, -2.5), ("r", 270, 485, .9, -4.2)]
    for side, x, y, k, d in specs:
        drift += f'<g class="puff puff-{side}" style="animation-delay:{d}s">{puff(x, y, k)}</g>'
    bank = puff(40, 500, 1.4) + puff(150, 512, 1.6) + puff(260, 508, 1.7) + puff(370, 504, 1.5) + puff(-40, 512, 1.3)
    return f'''<div class="hero-stage" role="img" aria-label="Lord Surya riding his chariot of seven horses before the rising sun">
  <svg class="stage-back" viewBox="0 -30 500 560" aria-hidden="true">
    <defs><radialGradient id="halo" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#f29a3e" stop-opacity=".6"/><stop offset="1" stop-color="#f29a3e" stop-opacity="0"/></radialGradient></defs>
    <circle cx="{cx}" cy="{cy}" r="230" fill="url(#halo)"/>
  </svg>
  <svg class="stage-rays" viewBox="0 -30 500 560" aria-hidden="true"><path d="{" ".join(rays)}" fill="#e9b863" opacity=".6"/></svg>
  <video class="ride-video" autoplay muted loop playsinline preload="none" poster="assets/surya-ride-poster.webp" width="720" height="648" aria-hidden="true">
    <source src="assets/surya-ride.mp4" type="video/mp4">
  </video>
  <svg class="stage-front" viewBox="0 -30 500 560" aria-hidden="true">
    <defs>
      <radialGradient id="cl" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#eef5f4" stop-opacity=".95"/><stop offset=".6" stop-color="#e3eeed" stop-opacity=".7"/><stop offset="1" stop-color="#e3eeed" stop-opacity="0"/></radialGradient>
      <filter id="soft" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="2.4"/></filter>
    </defs>
    <g fill="url(#cl)" opacity=".7">{drift}</g>
    <g fill="#e6f0ef" opacity=".92" filter="url(#soft)">{bank}</g>
  </svg>
</div>'''

ICONS = {
    "kalash": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 22c0-4 4-6 10-6s10 2 10 6c0 9-4 18-10 18s-10-9-10-18z"/><path d="M17 16h14M19 16v-3h10v3"/><path d="M24 13c-4-2-6-5-6-8 3 0 5 2 6 4 1-2 3-4 6-4 0 3-2 6-6 8z"/><path d="M15 27h18"/><path d="M18 42h12"/></svg>',
    "home": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 22 24 9l16 13"/><path d="M12 19v21h24V19"/><path d="M20 40v-9a4 4 0 0 1 8 0v9"/><path d="M24 9V4M22 5.5h4"/></svg>',
    "fire": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M24 6c2 6 9 9 9 18a9 9 0 0 1-18 0c0-5 3-7 4-11 2 3 3 4 5 4-1-4-1-7 0-11z"/><path d="M8 38h32l-4 6H12z"/><path d="M14 38l4-6M34 38l-4-6"/></svg>',
    "lamp": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 28c4 6 28 6 32 0"/><path d="M8 28h32"/><path d="M38 28c2-1 4-3 4-5"/><path d="M24 26c-3-3-3-7 0-12 3 5 3 9 0 12z"/><path d="M20 36h8l2 6H18z"/></svg>',
    "wheel": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="24" cy="24" r="17"/><circle cx="24" cy="24" r="12"/><circle cx="24" cy="24" r="3"/><path d="M24 12v9M24 27v9M12 24h9M27 24h9M15.5 15.5l6.4 6.4M26.1 26.1l6.4 6.4M32.5 15.5l-6.4 6.4M21.9 26.1l-6.4 6.4"/></svg>',
    "screen": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="6" y="9" width="36" height="24" rx="2"/><path d="M18 41h12M24 33v8"/><path d="M24 27c-3-2-3-6 0-11 3 5 3 9 0 11z"/><path d="M19 27h10"/></svg>',
    "shield": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M24 5 9 11v11c0 10 7 17 15 21 8-4 15-11 15-21V11z"/><path d="m17 24 5 5 9-10"/></svg>',
    "scroll": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 8h24v30a4 4 0 0 1-4 4H10a4 4 0 0 1-4-4v-4h22v4a4 4 0 0 0 4 4"/><path d="M12 8a4 4 0 0 0-4 4v2h4M17 16h13M17 22h13M17 28h9"/></svg>',
    "tag": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 24V8h16l20 20-14 14z"/><circle cx="14" cy="16" r="2.5"/><path d="M22 23h9M22 27h9M26 23c3 0 3 4 0 4l5 6"/></svg>',
    "basket": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 20h36l-4 20H10z"/><path d="M14 20l6-12M34 20l-6-12"/><circle cx="18" cy="14" r="0"/><path d="M16 27v6M24 27v6M32 27v6"/></svg>',
}

DIYA = '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M6 24 Q20 38 34 24Z" fill="#c98a2b"/><path d="M20 22 C15 15 18 9 20 4 C22 9 25 15 20 22Z" fill="#e8891c"/><path d="M20 20 C18 16 19 13 20 10 C21 13 22 16 20 20Z" fill="#fff0b3"/></svg>'


# ----------------------------------------------------------------------------
# Layout
# ----------------------------------------------------------------------------
NAV = [("index.html", "Home", "హోమ్"), ("services.html", "Pujas & Prices", "పూజలు & ధరలు"),
       ("about.html", "About", "మా గురించి"), ("contact.html", "Contact", "సంప్రదించండి")]
POLICIES = [("terms-and-conditions.html", "Terms & Conditions", "నిబంధనలు & షరతులు"),
            ("privacy-policy.html", "Privacy Policy", "గోప్యతా విధానం"),
            ("refund-policy.html", "Cancellation & Refund Policy", "రద్దు & రీఫండ్ విధానం"),
            ("service-delivery-policy.html", "Shipping & Service Delivery", "షిప్పింగ్ & సేవా డెలివరీ")]
FONTS = None  # fonts are self-hosted in assets/fonts (see styles.css @font-face)

import json as _json
SITE = f"https://{BIZ['domain']}"
ORG = {"@type": "Organization", "@id": SITE + "/#org", "name": "Mana Guruji", "alternateName": "మన గురూజీ", "url": SITE + "/",
       "logo": SITE + "/assets/icon-512.png", "email": BIZ["email"],
       "identifier": {"@type": "PropertyValue", "propertyID": "Udyam Registration Number", "value": BIZ["udyam"]},
       "contactPoint": [{"@type": "ContactPoint", "contactType": "customer support", "email": BIZ["email"], "areaServed": "IN", "availableLanguage": ["Telugu", "English", "Hindi"]},
                        {"@type": "ContactPoint", "contactType": "sales", "email": BIZ["contact_email"], "areaServed": "IN"}]}

def jsonld(*objs):
    data = {"@context": "https://schema.org", "@graph": list(objs)}
    return '<script type="application/ld+json">' + _json.dumps(data, ensure_ascii=False, separators=(",", ":")) + '</script>'

def slug(sv): return f'{sv["id"]}-hyderabad.html'


CUR = ' aria-current="page"'

def header(active):
    links = "".join(f'<a href="{h}"{CUR if h == active else ""}>{B(e, t)}</a>' for h, e, t in NAV)
    mlinks = "".join(f'<a href="{h}">{B(e, t)}</a>' for h, e, t in NAV) + f'<a href="book.html">{B("Book a Puja", "పూజ బుక్ చేయండి")}</a>'
    return f'''<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html" aria-label="Mana Guruji home">{emblem()}<span class="brand-name"><b>MANA GURUJI</b><small>మన గురూజీ</small></span></a>
    <nav class="nav" aria-label="Main">{links}</nav>
    <div class="lang-toggle" role="group" aria-label="Language"><button type="button" data-set-lang="en" aria-pressed="true">EN</button><button type="button" data-set-lang="te" aria-pressed="false">తెలుగు</button></div>
    <a class="btn btn-gold header-cta" href="book.html">{B("Book a Puja", "పూజ బుక్ చేయండి")}</a>
    <details class="menu"><summary>{B("Menu", "మెనూ")}</summary><div class="menu-panel">{mlinks}</div></details>
  </div>
</header>'''

POPULAR = ["satyanarayana", "gruhapravesam", "ganapathi-homam", "rudrabhishekam", "namakaranam", "navagraha-homam"]

def footer():
    T = thoranam_uri()
    pol = "".join(f'<li><a href="{h}">{B(e, t)}</a></li>' for h, e, t in POLICIES)
    nav = "".join(f'<li><a href="{h}">{B(e, t)}</a></li>' for h, e, t in NAV) + f'<li><a href="book.html">{B("Book a Puja", "పూజ బుక్ చేయండి")}</a></li>'
    return f'''<footer class="site-footer">
  <div class="thoranam" style="background-image:url('{T}')" aria-hidden="true"></div>
  <div class="wrap">
    <div class="footer-grid">
      <div class="footer-brand">
        <a class="brand" href="index.html" style="color:#f6ecda">{emblem(40)}<span class="brand-name"><b>MANA GURUJI</b><small>మన గురూజీ</small></span></a>
        <p>{B("Book traditional Hindu pujas, vratams and homams with KYC-verified pandits in Hyderabad, at your home or online.",
               "హైదరాబాద్‌లో KYC ధ్రువీకరించిన పండితులతో మీ ఇంట్లో లేదా ఆన్‌లైన్‌లో సంప్రదాయ పూజలు, వ్రతాలు, హోమాలు బుక్ చేసుకోండి.")}</p>
      </div>
      <div><h2 class="fh">{B("Explore", "పేజీలు")}</h2><ul>{nav}</ul></div>
      <div><h2 class="fh">{B("Popular pujas", "ప్రసిద్ధ పూజలు")}</h2><ul>{"".join(f'<li><a href="{slug(sv)}">{B(sv["en"].split(" (")[0], sv["te"])}</a></li>' for sv in S if sv["id"] in POPULAR)}</ul></div>
      <div><h2 class="fh">{B("Policies", "విధానాలు")}</h2><ul>{pol}</ul></div>
      <div><h2 class="fh">{B("Contact", "సంప్రదించండి")}</h2><ul>
        <li>{B("Support", "సహాయం")}: {BIZ["email"]}</li><li>{B("General & collaborations", "సాధారణ విచారణలు & భాగస్వామ్యాలు")}: {BIZ["contact_email"]}</li><li>{B(BIZ["address"], "హైదరాబాద్, తెలంగాణ 500083, భారతదేశం")}</li>
        <li>{B(BIZ["hours_en"], BIZ["hours_te"])}</li></ul></div>
    </div>
    <div class="footer-bottom"><span>© <span data-year>2026</span> {BIZ["brand"]} · {B("Udyam Reg. No.", "ఉద్యమ్ నమోదు సంఖ్య")} {BIZ["udyam"]}</span><span>{BIZ["domain"]} · {B("Hyderabad, Telangana, India", "హైదరాబాద్, తెలంగాణ, భారతదేశం")}</span></div>
  </div>
</footer>'''

EYEBROWS = {"శుభం భూయాత్": "Shubham Bhooyat", "విధానం": "How it works", "సేవలు": "Our services", "మా ప్రత్యేకత": "Why us",
    "సేవా ప్రాంతాలు": "Service areas", "గురు వందనం": "Guru Vandanam", "సేవా వివరాలు": "Seva list", "పూజ బుకింగ్": "Booking",
    "సంప్రదింపులు": "Get in touch", "మా గురించి": "About us", "నిబంధనలు": "Terms", "గోప్యత": "Privacy",
    "రద్దు & రీఫండ్": "Refunds", "సేవా డెలివరీ": "Delivery", "404": "404"}

def fix_eyebrows(html):
    return re.sub(r'<span class="eyebrow">([^<]+)</span>',
                  lambda m: f'<span class="eyebrow">{B(EYEBROWS.get(m.group(1), m.group(1)), m.group(1))}</span>', html)

def page(fname, title, desc, body, active=None, extra_head="", extra_script="", schema=None):
    body = fix_eyebrows(body)
    url = SITE + "/" + ("" if fname == "index.html" else fname)
    graph = [ORG, {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "Mana Guruji", "inLanguage": ["en-IN", "te-IN"], "publisher": {"@id": SITE + "/#org"}}] + (schema or [])
    head = f'''<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="https://{BIZ["domain"]}/{'' if fname == 'index.html' else fname}">
<link rel="canonical" href="https://{BIZ["domain"]}/{'' if fname == 'index.html' else fname}">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="assets/favicon-32.png" type="image/png" sizes="32x32">
<link rel="icon" href="assets/icon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<meta name="theme-color" content="#0b3238">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Mana Guruji">
<meta property="og:locale" content="en_IN">
<meta property="og:locale:alternate" content="te_IN">
<meta property="og:image" content="{SITE}/assets/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="robots" content="{'noindex' if fname == '404.html' else 'index, follow, max-image-preview:large'}">
<link rel="preload" href="assets/fonts/marcellus-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/mukta-latin-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="styles.css">{extra_head}
{jsonld(*graph)}'''
    inner = f'''{header(active)}
<main id="main">
{body}
</main>
{footer()}
{extra_script}<script src="site.js"></script>'''
    full = f'''<!doctype html>
<html lang="en" data-lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{head}
</head>
<body>
{inner}
</body>
</html>
'''
    frag = head + "\n" + inner + "\n"
    return full, frag

# ----------------------------------------------------------------------------
# Pages
# ----------------------------------------------------------------------------
def by_cat(c): return [s for s in S if s["cat"] == c]

def home():
    T = thoranam_uri()
    cats = ""
    for cid, en, te, ic, den, dte in CATS:
        items = by_cat(cid)
        lis = "".join(f'<li>{B(s["en"], s["te"])}</li>' for s in items[:4])
        lo = min(s["price"] for s in items)
        cats += f'''<a class="cat" href="services.html#{cid}">
  <span class="cat-icon">{ICONS[ic]}</span>
  <h3>{B(en, te)}</h3>
  <ul>{lis}</ul>
  <span class="from">{B("From " + inr(lo), inr(lo) + " నుండి")}</span>
</a>'''
    areas = "".join(f"<li>{a}</li>" for a in AREAS)
    faqs = [
        ("Who are the pandits?", "పండితులు ఎవరు?",
         "Experienced Telugu Vaidika pandits from Hyderabad. Every pandit completes identity and document verification (KYC) with us before receiving any booking.",
         "హైదరాబాద్‌కు చెందిన అనుభవజ్ఞులైన తెలుగు వైదిక పండితులు. ప్రతి పండితుడూ బుకింగ్ పొందే ముందు మా వద్ద గుర్తింపు, పత్రాల ధ్రువీకరణ (KYC) పూర్తి చేయాలి."),
        ("Is the puja samagri included?", "పూజా సామగ్రి ధరలో ఉంటుందా?",
         "The listed price is the pandit service fee, including every pandit the ritual needs. You can add our samagri kit while booking, and the pandit brings it on the day. You can also arrange the items yourself from the list we share.",
         "చూపిన ధర పండితుని సేవా రుసుము. బుకింగ్ సమయంలో సామగ్రి కిట్‌ను జోడించవచ్చు; పండితులు అదే రోజు తీసుకువస్తారు. లేదా మేము పంపే జాబితా ప్రకారం మీరే ఏర్పాటు చేసుకోవచ్చు."),
        ("How do I pay?", "ఎలా చెల్లించాలి?",
         "After our team confirms your date and pandit, you receive a secure payment link (UPI, cards, net banking, wallets via Razorpay). We pay the pandit after the puja is completed.",
         "మా బృందం తేదీ, పండితుని నిర్ధారించిన తర్వాత మీకు సురక్షిత చెల్లింపు లింక్ వస్తుంది (UPI, కార్డులు, నెట్ బ్యాంకింగ్, వాలెట్లు, Razorpay ద్వారా). పూజ పూర్తయిన తర్వాత మేము పండితునికి చెల్లిస్తాము."),
        ("Can the puja be done in Telugu tradition and language?", "పూజ తెలుగు సంప్రదాయంలో, తెలుగులో జరుగుతుందా?",
         "Yes. Tell us your family's tradition (smartha or vaishnava) in the notes when you book, and the pandit follows it and explains each step in Telugu. Explanation in Hindi or English is available on request.",
         "అవును. బుకింగ్ సమయంలో మీ కుటుంబ సంప్రదాయం (స్మార్త లేదా వైష్ణవ) తెలియజేస్తే, పండితులు ఆ పద్ధతిలోనే పూజ చేసి ప్రతి ఘట్టాన్ని తెలుగులో వివరిస్తారు. కోరితే హిందీ లేదా ఇంగ్లీష్‌లో కూడా వివరిస్తారు."),
        ("What if I need to cancel?", "రద్దు చేయాలంటే?",
         f"Cancel before a pandit is assigned for a full refund. After assignment, {BIZ['refund_before_24h']}% is refunded if you cancel more than 24 hours before the puja and {BIZ['refund_within_24h']}% within 24 hours. See our Cancellation & Refund Policy.",
         f"పండితుని కేటాయించే ముందు రద్దు చేస్తే పూర్తి రీఫండ్. కేటాయించిన తర్వాత, పూజకు 24 గంటల ముందు రద్దు చేస్తే {BIZ['refund_before_24h']}%, 24 గంటల లోపు అయితే {BIZ['refund_within_24h']}% రీఫండ్. వివరాలకు రద్దు & రీఫండ్ విధానం చూడండి."),
    ]
    faq = "".join(f'<details><summary>{B(q, qt)}</summary><p>{B(a, at)}</p></details>' for q, qt, a, at in faqs)
    body = f'''<div class="opening">
<div class="thoranam" style="background-image:url('{T}')" aria-hidden="true"></div>
{guru_section(first=True)}
<div class="divider opening-divider">{DIYA}</div>
<section class="hero">
  <div class="wrap">
    <div class="hero-copy">
      <span class="eyebrow">శుభం భూయాత్</span>
      <h1>{B("Every auspicious beginning deserves the <em>right pandit</em>.", "ప్రతి శుభకార్యానికి <em>సరైన పండితులు</em>.")}</h1>
      <p class="hero-lead">{B("Book Satyanarayana vratham, gruhapravesam, homams and family ceremonies with KYC-verified Telugu pandits. At your home in Hyderabad, or live online.",
                             "సత్యనారాయణ వ్రతం, గృహప్రవేశం, హోమాలు, కుటుంబ వేడుకలకు KYC ధ్రువీకరించిన తెలుగు పండితులను బుక్ చేసుకోండి. హైదరాబాద్‌లో మీ ఇంటికే, లేదా ఆన్‌లైన్‌లో.")}</p>
      <div class="hero-actions">
        <a class="btn btn-gold" href="book.html">{B("Book a Puja", "పూజ బుక్ చేయండి")}</a>
        <a class="btn btn-ghost" href="services.html">{B("See pujas & prices", "పూజలు & ధరలు చూడండి")}</a>
      </div>
      <ul class="hero-facts">
        <li>{B("KYC-verified pandits", "ధ్రువీకరించిన పండితులు")}</li>
        <li>{B("Fixed, published prices", "స్థిర ధరలు")}</li>
        <li>{B("Secure online payment", "సురక్షిత చెల్లింపు")}</li>
      </ul>
    </div>
    <div class="hero-art">{hero_art()}</div>
  </div>
</section>
</div>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">విధానం</span>
      <h2>{B("How booking works", "బుకింగ్ ఎలా జరుగుతుంది")}</h2>
    </div>
    <ol class="steps">
      <li><h3>{B("Choose your puja", "పూజను ఎంచుకోండి")}</h3><p>{B("Browse pujas with clear prices, duration and what is included.", "ధర, సమయం, విధానం వివరాలతో పూజలను చూడండి.")}</p></li>
      <li><h3>{B("Pick date, time & place", "తేదీ, సమయం, స్థలం")}</h3><p>{B("Tell us your preferred date, area and whether you want the puja at home or online.", "మీకు అనుకూలమైన తేదీ, ప్రాంతం, ఇంట్లోనా ఆన్‌లైన్‌లోనా తెలియజేయండి.")}</p></li>
      <li><h3>{B("Confirm & pay securely", "నిర్ధారించి చెల్లించండి")}</h3><p>{B("We confirm your pandit and send a secure payment link. You get the pandit's name before the day.", "పండితుని నిర్ధారించి సురక్షిత చెల్లింపు లింక్ పంపుతాం. ముందుగానే పండితుని పేరు తెలియజేస్తాం.")}</p></li>
      <li><h3>{B("Pandit performs the puja", "పండితులు పూజ నిర్వహిస్తారు")}</h3><p>{B("The pandit arrives on time with the samagri kit if you added it, and performs the full vidhi.", "పండితులు సమయానికి వచ్చి (కిట్ ఎంచుకుంటే సామగ్రితో) పూర్తి విధివిధానాలతో పూజ చేస్తారు.")}</p></li>
    </ol>
  </div>
</section>

<section class="section section-alt kolam-bg">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">సేవలు</span>
      <h2>{B("Pujas we perform", "మేము నిర్వహించే పూజలు")}</h2>
      <p>{B("Nineteen pujas across six categories, each with a published price.", "ఆరు విభాగాల్లో పందొమ్మిది పూజలు, ప్రతి పూజకు నిర్ణీత ధర.")}</p>
    </div>
    <div class="cats">{cats}</div>
    <p style="text-align:center;margin-top:2.2rem"><a class="btn btn-teal" href="services.html">{B("View full price list", "పూర్తి ధరల జాబితా")}</a></p>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">మా ప్రత్యేకత</span>
      <h2>{B("Why families choose Mana Guruji", "కుటుంబాలు మన గురూజీని ఎందుకు ఎంచుకుంటాయి")}</h2>
    </div>
    <div class="why">
      <div>{ICONS["shield"]}<h3>{B("Verified pandits", "ధ్రువీకరించిన పండితులు")}</h3><p>{B("Identity, address and Vedic training are checked before a pandit can take bookings.", "బుకింగ్‌లు తీసుకునే ముందు గుర్తింపు, చిరునామా, వైదిక శిక్షణ పరిశీలిస్తాం.")}</p></div>
      <div>{ICONS["scroll"]}<h3>{B("Telugu tradition", "తెలుగు సంప్రదాయం")}</h3><p>{B("Full vidhi as practised in Telugu households, explained step by step in Telugu.", "తెలుగు ఇళ్లలో ఆచరించే పూర్తి విధి, తెలుగులో ప్రతి ఘట్టం వివరణతో.")}</p></div>
      <div>{ICONS["tag"]}<h3>{B("Clear prices", "స్పష్టమైన ధరలు")}</h3><p>{B("The price you see is the price you pay. No bargaining, and the pandit will not ask for extra money on the day.", "చూసిన ధరే చెల్లించే ధర. బేరాలు లేవు; పూజ రోజు పండితులు అదనపు డబ్బు అడగరు.")}</p></div>
      <div>{ICONS["basket"]}<h3>{B("Samagri kit", "సామగ్రి కిట్")}</h3><p>{B("Add a complete samagri kit while booking and the pandit brings everything needed.", "బుకింగ్‌లో కిట్ జోడిస్తే అవసరమైన సామగ్రి అంతా పండితులే తెస్తారు.")}</p></div>
    </div>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">సేవా ప్రాంతాలు</span>
      <h2>{B("Serving homes across Hyderabad", "హైదరాబాద్ అంతటా సేవలు")}</h2>
      <p>{B("Home pujas are available across Hyderabad and Secunderabad. Online pujas are available anywhere.", "హైదరాబాద్, సికింద్రాబాద్ అంతటా ఇంటి పూజలు. ఆన్‌లైన్ పూజలు ఎక్కడైనా.")}</p>
    </div>
    <ul class="areas">{areas}</ul>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <div class="divider">{DIYA}</div>
      <h2>{B("Questions families ask", "తరచుగా అడిగే ప్రశ్నలు")}</h2>
    </div>
    <div class="faq">{faq}</div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div><h2>{B("Planning a puja at home?", "ఇంట్లో పూజ ప్లాన్ చేస్తున్నారా?")}</h2><p>{B("Send your date and area. We confirm your pandit within 2 hours during support hours (6 AM to 9 PM).", "మీ తేదీ, ప్రాంతం పంపండి. సేవా సమయంలో (ఉదయం 6 నుండి రాత్రి 9 వరకు) 2 గంటల్లో పండితుని నిర్ధారిస్తాం.")}</p></div>
    <a class="btn btn-gold" href="book.html">{B("Book a Puja", "పూజ బుక్ చేయండి")}</a>
  </div>
</section>'''
    lb = {"@type": "LocalBusiness", "@id": SITE + "/#business", "name": "Mana Guruji", "url": SITE + "/", "image": SITE + "/assets/og-image.jpg",
          "logo": SITE + "/assets/icon-512.png", "email": BIZ["email"], "priceRange": "₹1,500 – ₹31,000",
          "description": "Book KYC-verified Telugu pandits in Hyderabad for pujas, vratams, homams and family ceremonies, at home or online.",
          "address": {"@type": "PostalAddress", "addressLocality": "Hyderabad", "addressRegion": "Telangana", "postalCode": "500083", "addressCountry": "IN"},
          "areaServed": [{"@type": "City", "name": "Hyderabad"}, {"@type": "City", "name": "Secunderabad"}],
          "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"], "opens": "06:00", "closes": "21:00"}],
          "parentOrganization": {"@id": SITE + "/#org"}}
    pre = '\n<link rel="preload" as="image" href="assets/dakshinamurthy-760.webp" imagesrcset="assets/dakshinamurthy-760.webp 760w, assets/dakshinamurthy-1200.webp 1200w" imagesizes="(max-width: 860px) 92vw, 520px" fetchpriority="high">'
    return page("index.html", "Book Telugu Pandits in Hyderabad for Pujas & Homams | Mana Guruji",
                "Book KYC-verified Telugu pandits in Hyderabad for Satyanarayana Vratham, Gruhapravesam, homams and family ceremonies. Fixed prices, at home or online.",
                body, "index.html", extra_head=pre, schema=[lb])


GLOSS = [("gurave", "గురవే", "to the Guru", "గురువుకు"), ("sarva-lokānāṁ", "సర్వలోకానాం", "of all the worlds", "సమస్త లోకాలకు"),
         ("bhiṣaje", "భిషజే", "to the physician", "వైద్యునికి"), ("bhava-rogiṇām", "భవరోగిణామ్", "of those suffering from the disease of worldly existence", "భవరోగంతో (సంసారంతో) బాధపడేవారికి"),
         ("nidhaye", "నిధయే", "to the treasure-house", "నిధికి"), ("sarva-vidyānāṁ", "సర్వవిద్యానాం", "of all knowledge", "సమస్త విద్యలకు"),
         ("dakṣiṇāmūrtaye", "దక్షిణామూర్తయే", "to Dakshinamurthy", "దక్షిణామూర్తికి"), ("namaḥ", "నమః", "salutations", "నమస్కారము")]

def guru_section(first=False):
    import random
    rnd = random.Random(7)
    LOAD = 'fetchpriority="high"' if first else 'loading="lazy"'
    sparks = "".join(f'<span class="spark" style="--x:{rnd.uniform(30,72):.1f}%;--y:{rnd.uniform(3,44):.1f}%;--d:-{rnd.uniform(0,3.2):.1f}s"></span>' for _ in range(16))
    flames = "".join(f'<span class="flame" style="--x:{x}%;--y:{y}%"></span>' for x, y in
                     [(14.4, 51.9), (19.7, 47.7), (82.5, 47.4), (89.4, 51.9), (73.2, 49.1)])
    return f'''<section class="guru" id="guru">
  <div class="wrap">
    <figure class="guru-art">
      <div class="guru-frame"><div class="guru-scene">
        <img src="assets/dakshinamurthy-1200.webp" srcset="assets/dakshinamurthy-760.webp 760w, assets/dakshinamurthy-1200.webp 1200w" sizes="(max-width: 860px) 92vw, 520px" width="1200" height="1313" alt="Sri Dakshinamurthy seated under the banyan tree, with sages, Ganesha and the cosmos above" {LOAD}>
        <img class="galaxy" src="assets/galaxy.webp" alt="" width="200" height="200" {LOAD}>
        <span class="halo-glow"></span>{flames}{sparks}
      </div></div>
      <figcaption>{B("Sri Dakshinamurthy teaching the sages in silence beneath the banyan tree", "మర్రిచెట్టు కింద మౌనంగా మునులకు బోధిస్తున్న శ్రీ దక్షిణామూర్తి")}</figcaption>
    </figure>
    <div class="guru-copy">
      <span class="eyebrow">గురు వందనం</span>
      <h2>{B("Sri Dakshinamurthy, the Guru of all the worlds", "సర్వలోక గురువు శ్రీ దక్షిణామూర్తి")}</h2>
      <blockquote class="shloka">
        <p class="te" lang="te"><span class="pada">గురవే సర్వలోకానాం</span> <span class="pada">భిషజే భవరోగిణామ్ ।</span><br><span class="pada">నిధయే సర్వవిద్యానాం</span> <span class="pada">దక్షిణామూర్తయే నమః ॥</span></p>
        <p class="en roman"><span class="pada">Gurave sarva-lokānāṁ</span> <span class="pada">bhiṣaje bhava-rogiṇām |</span><br><span class="pada">Nidhaye sarva-vidyānāṁ</span> <span class="pada">dakṣiṇāmūrtaye namaḥ ||</span></p>
      </blockquote>
      <p class="meaning">{B("Salutations to Sri Dakshinamurthy, the Guru of all the worlds, the physician for those who suffer from the disease of worldly existence, and the treasure-house of all knowledge.",
                         "సమస్త లోకాలకు గురువు, భవరోగంతో (సంసార బంధంతో) బాధపడేవారికి వైద్యుడు, సమస్త విద్యలకు నిధి అయిన శ్రీ దక్షిణామూర్తికి నమస్కారము.")}</p>
      <details class="gloss"><summary>{B("Word by word", "పదార్థం")}</summary>
        <dl>{"".join(f'<div><dt>{B(r, t)}</dt><dd>{B(e, tm)}</dd></div>' for r, t, e, tm in GLOSS)}</dl>
      </details>
      <p class="tie">{B("Mana Guruji means “our Guru”. The pandits on our platform carry that living tradition of learning into your home, performing every ritual with the same care it has been taught with for generations.",
                        "మన గురూజీ అంటే “మన గురువు”. తరతరాలుగా గురువుల నుండి నేర్చుకున్న అదే శ్రద్ధతో, ఆ జ్ఞాన పరంపరను మా పండితులు మీ ఇంటికి తీసుకువస్తారు.")}</p>
    </div>
  </div>
</section>'''

def page_hero(eyebrow, h_en, h_te, p_en, p_te, extra=""):
    return f'''<section class="page-hero"><div class="wrap">
  <span class="eyebrow">{eyebrow}</span>
  <h1>{B(h_en, h_te)}</h1>
  <p>{B(p_en, p_te)}</p>{extra}
</div></section>'''

def services():
    chips = '<div class="chips">' + "".join(f'<a href="#{c[0]}">{B(c[1], c[2])}</a>' for c in CATS) + "</div>"
    boards = ""
    for cid, en, te, ic, den, dte in CATS:
        rows = ""
        for s in by_cat(cid):
            kit = (B(f'Samagri kit {inr(s["kit"])}', f'సామగ్రి కిట్ {inr(s["kit"])}') if s["kit"]
                   else B("Samagri list shared in advance", "సామగ్రి జాబితా ముందుగా పంపుతాం"))
            rows += f'''<div class="seva">
  <div class="seva-name"><h3><a class="seva-link" href="{slug(s)}">{B(s["en"], s["te"])}</a></h3></div>
  <div class="seva-price">{inr(s["price"])}</div>
  <p class="seva-desc">{B(s["dEn"], s["dTe"])}</p>
  <div class="seva-meta"><span>{B("Duration: " + s["durEn"], "సమయం: " + s["durTe"])}</span><span>{kit}</span><a class="more-link" href="{slug(s)}">{B("Details", "వివరాలు")}</a><a class="book-link" href="book.html#{s["id"]}">{B("Book this puja", "ఈ పూజ బుక్ చేయండి")}</a></div>
</div>'''
        boards += f'''<section class="board" id="{cid}">
  <div class="board-head"><h2>{B(en, te)}</h2><p>{B(den, dte)}</p></div>
  {rows}
</section>'''
    body = page_hero("సేవా వివరాలు", "Pujas & Prices", "పూజలు & ధరలు",
                     "Every price below is the pandit service fee in Hyderabad, in Indian Rupees, and covers the number of pandits the ritual needs. Homams and large ceremonies include the full team. The samagri kit is optional.",
                     "కింది ప్రతి ధర హైదరాబాద్‌లో పండితుల సేవా రుసుము (భారత రూపాయలలో); ఆ కార్యానికి అవసరమైన పండితులందరూ ఇందులో ఉంటారు. హోమాలు, పెద్ద వేడుకలకు పూర్తి బృందం వస్తుంది. సామగ్రి కిట్ ఐచ్ఛికం.", chips)
    body += f'''<section class="section kolam-bg"><div class="wrap">
{boards}
<div class="note">{B("Prices include all Mana Guruji charges. Travel within Hyderabad city limits is included; for venues outside city limits we confirm any travel charge before you pay. Payment is collected online through Razorpay after your booking is confirmed.",
                     "ధరల్లో మన గురూజీ ఛార్జీలన్నీ ఉన్నాయి. హైదరాబాద్ నగర పరిధిలో ప్రయాణ ఖర్చు ధరలోనే ఉంది; నగరం బయట అయితే చెల్లింపుకు ముందే ప్రయాణ ఛార్జీ తెలియజేస్తాం. బుకింగ్ నిర్ధారణ తర్వాత Razorpay ద్వారా ఆన్‌లైన్‌లో చెల్లింపు.")}</div>
</div></section>'''
    cat = {"@type": "OfferCatalog", "name": "Puja and homam services in Hyderabad", "url": SITE + "/services.html",
           "itemListElement": [{"@type": "Offer", "price": sv["price"], "priceCurrency": "INR", "url": SITE + "/" + slug(sv),
                                "itemOffered": {"@type": "Service", "name": sv["en"], "areaServed": "Hyderabad"}} for sv in S]}
    return page("services.html", "Puja & Homam Prices in Hyderabad | Mana Guruji",
                "Price list for 19 pujas, vratams, homams and family ceremonies in Hyderabad: Satyanarayana Vratham from ₹2,500, Gruhapravesam ₹7,500, Ganapathi Homam ₹6,500 and more.",
                body, "services.html", schema=[cat])

def book():
    opts = ""
    for cid, en, te, *_ in CATS:
        o = "".join(f'<option value="{s["id"]}" data-en="{s["en"]} · {inr(s["price"])}" data-te="{s["te"]} · {inr(s["price"])}">{s["en"]} · {inr(s["price"])}</option>' for s in by_cat(cid))
        opts += f'<optgroup label="{en}" data-en="{en}" data-te="{te}">{o}</optgroup>'
    areas = "".join(f"<option>{a}</option>" for a in AREAS) + '<option value="Other" data-en="Other area" data-te="వేరే ప్రాంతం">Other area</option><option value="Online" data-en="Online puja" data-te="ఆన్‌లైన్ పూజ">Online puja</option>'
    data = json.dumps([{k: s[k] for k in ("id", "en", "te", "price", "kit", "durEn", "durTe")} for s in S], ensure_ascii=False)
    ok = B("Thank you. Your booking request is received. During support hours (6 AM to 9 PM), our team will call you within 2 hours to confirm the pandit and share a secure payment link.",
           "ధన్యవాదాలు. మీ బుకింగ్ అభ్యర్థన అందింది. సేవా సమయంలో (ఉదయం 6 నుండి రాత్రి 9 వరకు) పండితుని నిర్ధారించి సురక్షిత చెల్లింపు లింక్ పంపడానికి 2 గంటల్లో మా బృందం కాల్ చేస్తుంది.").replace('"', "&quot;")
    err = B(f"We could not send your request. Please email your booking details to {BIZ['email']}.",
            f"మీ అభ్యర్థన పంపలేకపోయాం. దయచేసి మీ బుకింగ్ వివరాలను {BIZ['email']} కు ఈమెయిల్ చేయండి.").replace('"', "&quot;")
    body = page_hero("పూజ బుకింగ్", "Book a Puja", "పూజ బుక్ చేయండి",
                     "Fill in your details. We confirm a verified pandit and send you a secure payment link.",
                     "మీ వివరాలు నింపండి. ధ్రువీకరించిన పండితుని నిర్ధారించి సురక్షిత చెల్లింపు లింక్ పంపుతాం.")
    body += f'''<section class="section kolam-bg"><div class="wrap form-grid">
<form class="form-card" id="book-form" name="booking" method="POST" data-netlify="true" netlify-honeypot="bot-field" data-mg-form data-ok="{ok}" data-err="{err}">
  <input type="hidden" name="form-name" value="booking">
  <input type="hidden" name="est_total" id="est_total" value="">
  <p class="hp" aria-hidden="true"><label>Leave empty <input name="bot-field" id="bot-field" tabindex="-1" autocomplete="off"></label></p>
  <div class="field"><label for="puja">{B("Puja", "పూజ")}</label>
    <select id="puja" name="puja" required><option value="" data-en="Select" data-te="ఎంచుకోండి">Select</option>{opts}</select></div>
  <div class="row2">
    <div class="field"><label for="date">{B("Preferred date", "తేదీ")}</label><input type="date" id="date" name="date" required></div>
    <div class="field"><label for="slot">{B("Preferred time", "సమయం")}</label>
      <select id="slot" name="slot" required><option value="Early morning (5–8 AM)" data-en="Early morning (5–8 AM)" data-te="తెల్లవారుజాము (5–8)">Early morning (5–8 AM)</option><option value="Morning (8–12)" data-en="Morning (8 AM–12 PM)" data-te="ఉదయం (8–12)" selected>Morning (8 AM–12 PM)</option><option value="Afternoon (12–4 PM)" data-en="Afternoon (12–4 PM)" data-te="మధ్యాహ్నం (12–4)">Afternoon (12–4 PM)</option><option value="Evening (4–8 PM)" data-en="Evening (4–8 PM)" data-te="సాయంత్రం (4–8)">Evening (4–8 PM)</option><option value="As per muhurtham" data-en="As per muhurtham" data-te="ముహూర్తం ప్రకారం">As per muhurtham</option></select></div>
  </div>
  <fieldset class="field"><legend>{B("Where", "ఎక్కడ")}</legend>
    <div class="radios"><label><input type="radio" name="mode" value="At home" id="mode-home" checked> {B("At my home / venue", "ఇంట్లో / వేదిక వద్ద")}</label><label><input type="radio" name="mode" value="Online" id="mode-online"> {B("Online (video call)", "ఆన్‌లైన్ (వీడియో కాల్)")}</label></div></fieldset>
  <div class="row2">
    <div class="field"><label for="area">{B("Area", "ప్రాంతం")}</label><select id="area" name="area" required><option value="" data-en="Select" data-te="ఎంచుకోండి">Select</option>{areas}</select></div>
    <div class="field"><label for="language">{B("Explanation language", "వివరణ భాష")}</label><select id="language" name="language"><option value="Telugu" data-en="Telugu" data-te="తెలుగు">Telugu</option><option value="Hindi" data-en="Hindi" data-te="హిందీ">Hindi</option><option value="English" data-en="English" data-te="ఇంగ్లీష్">English</option></select></div>
  </div>
  <div class="field"><label for="address">{B("Address (for home pujas)", "చిరునామా (ఇంటి పూజలకు)")}</label><textarea id="address" name="address" placeholder="House no., street, landmark" data-ph-en="House no., street, landmark" data-ph-te="ఇంటి నం., వీధి, ల్యాండ్‌మార్క్"></textarea></div>
  <div class="row2">
    <div class="field"><label for="name">{B("Your name", "మీ పేరు")}</label><input id="name" name="name" autocomplete="name" required></div>
    <div class="field"><label for="phone">{B("Mobile number", "మొబైల్ నంబర్")}</label><input id="phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" pattern="[0-9+ ]{{10,15}}" placeholder="98xxxxxxxx" required></div>
  </div>
  <div class="field"><label for="email">{B("Email (optional)", "ఈమెయిల్ (ఐచ్ఛికం)")}</label><input id="email" name="email" type="email" autocomplete="email"></div>
  <label class="check"><input type="checkbox" id="samagri" name="samagri_kit" value="yes"> <span>{B("Add samagri kit (the pandit brings all puja items)", "సామగ్రి కిట్ జోడించండి (పూజా సామగ్రి అంతా పండితులే తెస్తారు)")}</span></label>
  <div class="field"><label for="notes">{B("Gothram, nakshatram, family tradition or anything else we should know (optional)", "గోత్రం, నక్షత్రం, కుటుంబ సంప్రదాయం లేదా ఇతర వివరాలు (ఐచ్ఛికం)")}</label><textarea id="notes" name="notes"></textarea></div>
  <label class="check"><input type="checkbox" id="agree" name="agree" value="yes" required> <span>{B('I agree to the <a href="terms-and-conditions.html">Terms</a> and <a href="refund-policy.html">Cancellation & Refund Policy</a>.', 'నేను <a href="terms-and-conditions.html">నిబంధనలు</a>, <a href="refund-policy.html">రద్దు & రీఫండ్ విధానాన్ని</a> అంగీకరిస్తున్నాను.')}</span></label>
  <button class="btn btn-gold" type="submit">{B("Send booking request", "బుకింగ్ అభ్యర్థన పంపండి")}</button>
  <div class="form-status" role="status" hidden></div>
</form>
<aside class="summary-card" aria-live="polite">
  <h3>{B("Your booking", "మీ బుకింగ్")}</h3>
  <div class="sum-row"><span>{B("Puja", "పూజ")}</span><span id="sum-name" style="text-align:right">—</span></div>
  <div class="sum-row"><span>{B("Duration", "సమయం")}</span><span id="sum-dur">—</span></div>
  <div class="sum-row"><span>{B("Pandit service fee", "పండితుని రుసుము")}</span><span id="sum-price">—</span></div>
  <div class="sum-row"><span>{B("Samagri kit", "సామగ్రి కిట్")}</span><span id="sum-kit">—</span></div>
  <div><span>{B("Total", "మొత్తం")}</span><div class="sum-total" id="sum-total">—</div></div>
  <small>{B("You pay nothing now. After confirmation you receive a Razorpay payment link for this amount (UPI, cards, net banking, wallets).",
             "ఇప్పుడు ఏమీ చెల్లించనవసరం లేదు. నిర్ధారణ తర్వాత ఈ మొత్తానికి Razorpay చెల్లింపు లింక్ వస్తుంది (UPI, కార్డులు, నెట్ బ్యాంకింగ్, వాలెట్లు).")}</small>
</aside>
</div></section>'''
    script = f"<script>window.MG_SEVAS = {data};</script>\n"
    return page("book.html", "Book a Pandit in Hyderabad | Mana Guruji",
                "Request a puja booking with a verified pandit in Hyderabad. Choose puja, date and area; pay securely after confirmation.",
                body, "book.html", extra_script=script)

def contact():
    ok = B("Thank you. We will reply within a few hours.", "ధన్యవాదాలు. కొన్ని గంటల్లో స్పందిస్తాం.").replace('"', "&quot;")
    err = B(f"Message not sent. Please email {BIZ['contact_email']}.", f"సందేశం పంపలేకపోయాం. దయచేసి {BIZ['contact_email']} కు ఈమెయిల్ చేయండి.").replace('"', "&quot;")
    body = page_hero("సంప్రదింపులు", "Contact us", "మమ్మల్ని సంప్రదించండి",
                     "Questions about a puja, a booking or a payment, or interested in working with us? Write to us and we will reply within one working day.",
                     "పూజ, బుకింగ్ లేదా చెల్లింపు గురించి ప్రశ్నలా, లేదా మాతో కలిసి పనిచేయాలనుకుంటున్నారా? మాకు రాయండి; ఒక పని దినంలో స్పందిస్తాం.")
    body += f'''<section class="section kolam-bg"><div class="wrap contact-grid">
<div class="contact-list">
  <div><span>{B("Bookings & support", "బుకింగ్‌లు & సహాయం")}</span><strong>{BIZ["email"]}</strong></div>
  <div><span>{B("General enquiries & collaborations", "సాధారణ విచారణలు & భాగస్వామ్యాలు")}</span><strong>{BIZ["contact_email"]}</strong></div>
  <div><span>{B("Business", "వ్యాపారం")}</span><strong>{B("Mana Guruji", "మన గురూజీ")}<br>{B("MSME registered · Udyam Reg. No.", "MSME నమోదిత · ఉద్యమ్ నమోదు సంఖ్య")} {BIZ["udyam"]}<br>{B(BIZ["address"], "హైదరాబాద్, తెలంగాణ 500083, భారతదేశం")}</strong></div>
  <div><span>{B("Support hours", "సేవా సమయం")}</span><strong>{B(BIZ["hours_en"], BIZ["hours_te"])}</strong></div>
</div>
<form class="form-card" name="contact" method="POST" data-netlify="true" netlify-honeypot="bot-field" data-mg-form data-ok="{ok}" data-err="{err}">
  <input type="hidden" name="form-name" value="contact">
  <p class="hp" aria-hidden="true"><label>Leave empty <input name="bot-field" id="c-bot" tabindex="-1" autocomplete="off"></label></p>
  <h2 style="font-size:1.5rem">{B("Send us a message", "సందేశం పంపండి")}</h2>
  <div class="row2">
    <div class="field"><label for="c-name">{B("Name", "పేరు")}</label><input id="c-name" name="name" required autocomplete="name"></div>
    <div class="field"><label for="c-phone">{B("Mobile", "మొబైల్")}</label><input id="c-phone" name="phone" type="tel" required autocomplete="tel"></div>
  </div>
  <div class="field"><label for="c-email">{B("Email", "ఈమెయిల్")}</label><input id="c-email" name="email" type="email" autocomplete="email"></div>
  <div class="field"><label for="c-topic">{B("Topic", "విషయం")}</label><select id="c-topic" name="topic"><option value="Puja enquiry" data-en="Puja enquiry" data-te="పూజ విచారణ">Puja enquiry</option><option value="Existing booking" data-en="Existing booking" data-te="ప్రస్తుత బుకింగ్">Existing booking</option><option value="Payment or refund" data-en="Payment or refund" data-te="చెల్లింపు లేదా రీఫండ్">Payment or refund</option><option value="Join as a pandit" data-en="Join as a pandit" data-te="పండితుడిగా చేరండి">Join as a pandit</option><option value="Other" data-en="Other" data-te="ఇతర">Other</option></select></div>
  <div class="field"><label for="c-msg">{B("Message", "సందేశం")}</label><textarea id="c-msg" name="message" required></textarea></div>
  <button class="btn btn-gold" type="submit">{B("Send message", "సందేశం పంపండి")}</button>
  <div class="form-status" role="status" hidden></div>
</form>
</div></section>'''
    return page("contact.html", "Contact Mana Guruji | Puja Booking Support, Hyderabad", "Contact Mana Guruji for puja bookings, payments and support in Hyderabad.", body, "contact.html")

def about():
    body = page_hero("మా గురించి", "About Mana Guruji", "మన గురూజీ గురించి",
                     "A Hyderabad platform that connects families with verified Telugu pandits for pujas at home and online.",
                     "కుటుంబాలను ధ్రువీకరించిన తెలుగు పండితులతో కలిపే హైదరాబాద్ వేదిక.")
    body += guru_section()
    body += f'''<section class="section kolam-bg"><div class="wrap"><article class="prose">
<h2>{B("Our purpose", "మా లక్ష్యం")}</h2>
<p>{B("Finding a trusted pandit for a gruhapravesam or a Satyanarayana vratham usually depends on word of mouth, last-minute calls and unclear dakshina. Mana Guruji makes this simple: published prices, verified pandits, and one team that stays with you from booking until the puja is complete.",
       "గృహప్రవేశం లేదా సత్యనారాయణ వ్రతానికి నమ్మకమైన పండితుని కనుగొనడం సాధారణంగా పరిచయాలు, చివరి నిమిషం ఫోన్లు, స్పష్టత లేని దక్షిణపై ఆధారపడుతుంది. మన గురూజీ దీన్ని సులభం చేస్తుంది: ప్రకటించిన ధరలు, ధ్రువీకరించిన పండితులు, బుకింగ్ నుండి పూజ పూర్తయ్యే వరకు మీతో ఉండే ఒకే బృందం.")}</p>
<h2>{B("What we do", "మేము ఏమి చేస్తాం")}</h2>
<ul>
<li>{B("List traditional Hindu pujas, vratams, homams and samskaras with fixed prices.", "సంప్రదాయ పూజలు, వ్రతాలు, హోమాలు, సంస్కారాలను స్థిర ధరలతో అందిస్తాం.")}</li>
<li>{B("Verify every pandit's identity and documents (KYC) before they receive bookings.", "బుకింగ్‌లు పొందే ముందు ప్రతి పండితుని గుర్తింపు, పత్రాలను (KYC) ధ్రువీకరిస్తాం.")}</li>
<li>{B("Assign a pandit for your date and area, and share their name before the puja.", "మీ తేదీ, ప్రాంతానికి పండితుని కేటాయించి, పూజకు ముందే పేరు తెలియజేస్తాం.")}</li>
<li>{B("Collect payment securely online and pay the pandit their share after the service is completed.", "సురక్షితంగా ఆన్‌లైన్‌లో చెల్లింపు స్వీకరించి, సేవ పూర్తయిన తర్వాత పండితునికి వారి వాటా చెల్లిస్తాం.")}</li>
<li>{B("Supply optional samagri kits, delivered by the pandit on the day.", "ఐచ్ఛిక సామగ్రి కిట్‌లను పూజ రోజున పండితుల ద్వారా అందిస్తాం.")}</li>
</ul>
<h2>{B("Our pandits", "మా పండితులు")}</h2>
<p>{B("Our pandits are independent Vaidika professionals trained in Telugu smartha and vaishnava traditions. They choose the bookings they accept, and they are paid fairly and on time for every puja.",
       "మా పండితులు తెలుగు స్మార్త, వైష్ణవ సంప్రదాయాల్లో శిక్షణ పొందిన స్వతంత్ర వైదిక నిపుణులు. వారు స్వీకరించే బుకింగ్‌లను వారే ఎంచుకుంటారు; ప్రతి పూజకు న్యాయంగా, సమయానికి చెల్లింపు పొందుతారు.")}</p>
<p>{B('Are you a pandit in Hyderabad? <a href="contact.html">Contact us</a> to join.', 'మీరు హైదరాబాద్‌లో పండితులా? చేరడానికి <a href="contact.html">మమ్మల్ని సంప్రదించండి</a>.')}</p>
<h2>{B("Business details", "వ్యాపార వివరాలు")}</h2>
<p>{B(f"Mana Guruji is an MSME registered with the Government of India (Udyam Registration No. {BIZ['udyam']}), based in {BIZ['address']}. For bookings and support, email {BIZ['email']}. For general enquiries and collaborations, email {BIZ['contact_email']}.", f"మన గురూజీ భారత ప్రభుత్వం వద్ద నమోదైన MSME సంస్థ (ఉద్యమ్ నమోదు సంఖ్య {BIZ['udyam']}), హైదరాబాద్, తెలంగాణ 500083 కేంద్రంగా పనిచేస్తోంది. బుకింగ్‌లు, సహాయం కోసం {BIZ['email']} కు, సాధారణ విచారణలు, భాగస్వామ్యాల కోసం {BIZ['contact_email']} కు ఈమెయిల్ చేయండి.")}</p>
</article></div></section>'''
    return page("about.html", "About Mana Guruji | Verified Telugu Pandits in Hyderabad", "About Mana Guruji, a Hyderabad platform to book verified Telugu pandits for pujas.", body, "about.html")

TE_NOTE = '<p class="te-note te">ఈ విధానం ఆంగ్లంలో ఉంది. ఏదైనా సందేహం ఉంటే ఆంగ్ల పాఠమే చెల్లుబాటు అవుతుంది. తెలుగులో వివరణ కోసం మమ్మల్ని సంప్రదించండి.</p>'

POL_TE = {"terms-and-conditions.html": "పూజ బుక్ చేసేటప్పుడు వర్తించే నిబంధనలు.", "privacy-policy.html": "మీ వ్యక్తిగత సమాచారాన్ని మేము ఎలా సేకరిస్తాం, ఉపయోగిస్తాం, రక్షిస్తాం.", "refund-policy.html": "బుకింగ్ రద్దు, రీఫండ్ ఎలా జరుగుతాయి.", "service-delivery-policy.html": "మన గురూజీ సేవలు ఎలా, ఎప్పుడు అందుతాయి."}

def policy(fname, eyebrow, h_en, h_te, desc, sections):
    html = "".join(f"<h2>{h}</h2>{b}" for h, b in sections)
    body = page_hero(eyebrow, h_en, h_te, desc, POL_TE.get(fname, desc))
    body += f'''<section class="section kolam-bg"><div class="wrap"><article class="prose">
{TE_NOTE}<p class="updated">Last updated: {BIZ["updated"]}</p>
{html}
</article></div></section>'''
    return page(fname, f"{h_en} · Mana Guruji", desc, body)

def terms():
    b = BIZ
    return policy("terms-and-conditions.html", "నిబంధనలు", "Terms & Conditions", "నిబంధనలు & షరతులు",
        f"The terms that apply when you use {b['domain']} or the Mana Guruji app to book a puja.", [
        ("1. About these terms", f"<p>These terms govern your use of the website {b['domain']}, the Mana Guruji mobile app and the services offered through them (together, the \"Platform\"). The Platform is operated by Mana Guruji, an MSME registered under Udyam Registration No. {b['udyam']}, based in {b['address']} (\"Mana Guruji\", \"we\", \"us\"). By booking a service you agree to these terms.</p>"),
        ("2. Our service", "<p>Mana Guruji is a booking platform for Hindu religious services such as pujas, vratams, homams and samskaras. The services are performed by independent pandits who have completed our verification (KYC). We take your booking, assign a pandit, collect payment, and pay the pandit their share after the service is completed.</p>"),
        ("3. Bookings", "<ul><li>A booking request is confirmed only when we confirm a pandit and you complete payment.</li><li>You must provide accurate details: name, phone number, address, date and any ritual-specific information.</li><li>Puja duration shown is approximate and may vary with the customs followed by your family.</li><li>For home pujas, please ensure the venue is accessible and safe for the pandit at the scheduled time.</li></ul>"),
        ("4. Prices and payment", "<ul><li>All prices are listed in Indian Rupees (INR) on our Pujas & Prices page and include Mana Guruji charges.</li><li>Payments are processed securely by Razorpay through UPI, debit and credit cards, net banking and wallets. We do not store your card details.</li><li>Any travel charge for venues outside Hyderabad city limits is shown to you before payment.</li><li>Dakshina or gifts you choose to give the pandit voluntarily on the day are between you and the pandit and are not processed by us.</li></ul>"),
        ("5. Cancellations and refunds", '<p>Cancellations and refunds are governed by our <a href="refund-policy.html">Cancellation & Refund Policy</a>.</p>'),
        ("6. Conduct", "<p>We expect respectful conduct from customers and pandits. We may cancel a booking or suspend an account in case of abusive behaviour, false information or misuse of the Platform.</p>"),
        ("7. Nature of religious services", "<p>Our pandits perform rituals according to traditional practice. We do not make any promise about specific personal, financial or health outcomes from any ritual.</p>"),
        ("8. Liability", "<p>We take care in verifying pandits and managing bookings. To the extent permitted by law, our total liability for any booking is limited to the amount you paid us for that booking.</p>"),
        ("9. Changes", "<p>We may update these terms from time to time. The version published on this page applies to bookings made after the update.</p>"),
        ("10. Governing law", "<p>These terms are governed by the laws of India. Courts in Hyderabad, Telangana have exclusive jurisdiction.</p>"),
        ("11. Contact", f"<p>Mana Guruji (Udyam Reg. No. {b['udyam']}), {b['address']}<br>Bookings & support: {b['email']} · General enquiries & collaborations: {b['contact_email']}</p>"),
    ])

def privacy():
    b = BIZ
    return policy("privacy-policy.html", "గోప్యత", "Privacy Policy", "గోప్యతా విధానం",
        "How Mana Guruji collects, uses and protects your personal information.", [
        ("1. Information we collect", "<ul><li><b>Booking details:</b> name, mobile number, email, address, preferred date and time, and ritual details you choose to share (such as gothram or nakshatram).</li><li><b>Payment information:</b> processed by Razorpay. We receive the payment status and transaction reference, not your full card or bank details.</li><li><b>Device information:</b> basic technical data such as browser type and app version, used to keep the Platform working.</li><li><b>Pandit information:</b> for pandits, identity and KYC documents needed for verification and payouts.</li></ul>"),
        ("2. How we use it", "<ul><li>To confirm and manage your booking and assign a pandit.</li><li>To share your name, address and booking details with the assigned pandit so they can perform the service.</li><li>To process payments, refunds and pandit payouts.</li><li>To send booking updates by SMS, WhatsApp, email or app notification.</li><li>To meet legal, tax and accounting obligations.</li></ul>"),
        ("3. Sharing", "<p>We share information only with the assigned pandit, our payment processor (Razorpay), SMS and messaging providers, and cloud hosting providers who process data on our behalf, or when required by law. We do not sell your personal information.</p>"),
        ("4. Storage and security", "<p>Data is stored on secure servers with access limited to authorised staff. KYC documents are kept in private storage. We keep booking records for as long as required for accounting and legal purposes.</p>"),
        ("5. Your choices", "<p>You can ask us to access, correct or delete your personal information, subject to records we must keep by law. Write to us at the email below.</p>"),
        ("6. Cookies", "<p>The website uses only essential browser storage, for example to remember your language choice. We do not use advertising cookies.</p>"),
        ("7. Contact and Grievance Officer", f"<p>For privacy questions or grievances, write to the Grievance Officer, Mana Guruji, {b['address']}, at {b['email']}. We acknowledge every grievance within 24 hours and resolve it within 15 days.</p>"),
    ])

def refund():
    b = BIZ
    table = f'''<div class="table-wrap"><table>
<tr><th>When you cancel</th><th>Refund</th></tr>
<tr><td>Before a pandit is assigned</td><td>100% of the amount paid</td></tr>
<tr><td>After a pandit is assigned, more than 24 hours before the puja</td><td>{b['refund_before_24h']}% of the amount paid</td></tr>
<tr><td>After a pandit is assigned, within 24 hours of the puja</td><td>{b['refund_within_24h']}% of the amount paid</td></tr>
<tr><td>After the puja has started, or after it is completed</td><td>Not eligible for cancellation</td></tr>
</table></div>'''
    return policy("refund-policy.html", "రద్దు & రీఫండ్", "Cancellation & Refund Policy", "రద్దు & రీఫండ్ విధానం",
        "When you can cancel a puja booking and how refunds are processed.", [
        ("1. Cancelling a booking", f"<p>To cancel, email {b['email']} with your booking details, reply to the confirmation message from our team, or cancel in the Mana Guruji app if you booked there. Refunds depend on when you cancel:</p>{table}<p>Times are calculated in Indian Standard Time against the scheduled start time of the puja.</p>"),
        ("2. Cancellations by us", "<ul><li>If we cannot assign a pandit for your booking, we cancel it and refund 100% of the amount paid.</li><li>If the assigned pandit cancels, we first try to assign another verified pandit for the same time. If we cannot, you receive a 100% refund.</li><li>If the pandit does not arrive and we are unable to arrange a replacement, you receive a 100% refund.</li></ul>"),
        ("3. Rescheduling", "<p>You may reschedule once at no charge if you inform us more than 24 hours before the puja, subject to pandit availability.</p>"),
        ("4. Samagri kit", "<p>If you cancel before the puja day, the samagri kit amount is refunded in full. Once the kit has been brought to the venue, the kit amount is not refundable.</p>"),
        ("5. Service complaints", "<p>If the service was not performed as described, contact us within 48 hours of the scheduled time. We review each case and may offer a partial or full refund.</p>"),
        ("6. How refunds are paid", "<p>Approved refunds are initiated within 2 working days and credited to the original payment method through Razorpay. Banks usually take 5 to 7 working days to show the credit. Amounts paid by you directly to a pandit outside the Platform are not refundable through us.</p>"),
        ("7. Contact", f"<p>Mana Guruji (Udyam Reg. No. {b['udyam']}), {b['address']}<br>Bookings & support: {b['email']} · General enquiries & collaborations: {b['contact_email']}</p>"),
    ])

def delivery():
    b = BIZ
    return policy("service-delivery-policy.html", "సేవా డెలివరీ", "Shipping & Service Delivery Policy", "షిప్పింగ్ & సేవా డెలివరీ విధానం",
        "How and when Mana Guruji services are delivered.", [
        ("1. Nature of service", "<p>Mana Guruji provides religious services performed in person by a pandit at your venue, or live over a video call. We do not ship physical products by courier.</p>"),
        ("2. Service area", "<p>Home pujas are available within Hyderabad and Secunderabad (GHMC limits and nearby areas listed on our home page). Online pujas are available anywhere with a stable internet connection.</p>"),
        ("3. Confirmation timeline", "<ul><li>We confirm a pandit within 2 hours of your booking request during support hours, and in any case within 24 hours.</li><li>Bookings should be made at least 24 hours before the puja. Same-day requests are accepted subject to availability.</li><li>You receive the pandit's name and booking details by SMS, WhatsApp or in the app before the puja day.</li></ul>"),
        ("4. Delivery of the service", "<ul><li>The pandit arrives at your venue at the confirmed time and performs the puja for the duration listed.</li><li>For online pujas, a video call link is shared at least 2 hours before the start time.</li><li>The service is considered delivered when the puja is completed and marked complete by the pandit.</li></ul>"),
        ("5. Samagri kit", "<p>If you add a samagri kit, the pandit brings it to your venue on the day of the puja. There is no separate shipping or delivery charge.</p>"),
        ("6. Delays", f"<p>If the pandit is delayed, our team will inform you. If the delay affects your muhurtham, email {b['email']} or reply to our team's message, and we will arrange a replacement or refund as set out in our <a href=\"refund-policy.html\">Cancellation & Refund Policy</a>.</p>"),
        ("7. Contact", f"<p>Mana Guruji (Udyam Reg. No. {b['udyam']}), {b['address']}<br>Bookings & support: {b['email']} · General enquiries & collaborations: {b['contact_email']}</p>"),
    ])

def notfound():
    body = page_hero("404", "Page not found", "పేజీ కనుగొనబడలేదు", "The page you opened does not exist.", "మీరు తెరిచిన పేజీ లేదు.",
                     f'<p><a class="btn btn-gold" href="index.html">{B("Go to home page", "హోమ్ పేజీకి వెళ్ళండి")}</a></p>')
    return page("404.html", "Page not found · Mana Guruji", "Page not found.", body)

def puja_page(sv):
    c = next(c for c in CATS if c[0] == sv["cat"])
    online = sv["cat"] == "online"
    kit = (B(f'Optional samagri kit: {inr(sv["kit"])}. The pandit brings all puja items.', f'ఐచ్ఛిక సామగ్రి కిట్: {inr(sv["kit"])}. పూజా సామగ్రి అంతా పండితులే తెస్తారు.') if sv["kit"]
           else B("We share the samagri list in advance so you can keep everything ready at home.", "ఇంట్లో సిద్ధం చేసుకోవడానికి సామగ్రి జాబితాను ముందుగానే పంపుతాం."))
    where = B("Live over a video call, from anywhere", "వీడియో కాల్ ద్వారా ప్రత్యక్షంగా, ఎక్కడినుండైనా") if online else B("At your home or venue in Hyderabad and Secunderabad", "హైదరాబాద్, సికింద్రాబాద్‌లో మీ ఇంటి వద్ద లేదా వేదిక వద్ద")
    related = [x for x in S if x["cat"] == sv["cat"] and x["id"] != sv["id"]][:3]
    related += [x for x in S if x["id"] in POPULAR and x["id"] != sv["id"] and x not in related][:3 - len(related)]
    rel = "".join(f'<li><a href="{slug(x)}">{B(x["en"], x["te"])}</a> <span class="rel-price">{inr(x["price"])}</span></li>' for x in related)
    faqs = [(f"How much does {sv['en']} cost in Hyderabad?", f"హైదరాబాద్‌లో {sv['te']} ఖర్చు ఎంత?",
             f"The pandit service fee is {inr(sv['price'])}, including every pandit the ritual needs." + (f" The optional samagri kit is {inr(sv['kit'])}, so the total with the kit is {inr(sv['price'] + sv['kit'])}." if sv['kit'] else "") + " The pandit will not ask for extra money on the day.",
             f"పండితుల సేవా రుసుము {inr(sv['price'])}; ఆ కార్యానికి అవసరమైన పండితులందరూ ఇందులో ఉంటారు." + (f" ఐచ్ఛిక సామగ్రి కిట్ {inr(sv['kit'])}, కిట్‌తో కలిపి మొత్తం {inr(sv['price'] + sv['kit'])}." if sv['kit'] else "") + " పూజ రోజు పండితులు అదనపు డబ్బు అడగరు."),
            (f"How long does {sv['en']} take?", f"{sv['te']}కు ఎంత సమయం పడుతుంది?",
             f"{sv['durEn']}. The time can vary a little with your family's customs.", f"{sv['durTe']}. మీ కుటుంబ ఆచారాలను బట్టి కొంచెం మారవచ్చు."),
            ("Can I choose the date and muhurtham?", "తేదీ, ముహూర్తం నేనే ఎంచుకోవచ్చా?",
             "Yes. Choose your preferred date and time when you book, or pick \"As per muhurtham\" and the pandit will guide you on a suitable time.",
             "అవును. బుకింగ్ సమయంలో మీకు అనుకూలమైన తేదీ, సమయం ఎంచుకోండి, లేదా “ముహూర్తం ప్రకారం” ఎంచుకుంటే పండితులు తగిన సమయం సూచిస్తారు."),
            ("What if I need to cancel?", "రద్దు చేయాలంటే?",
             f"Cancel before a pandit is assigned for a full refund. After assignment, {BIZ['refund_before_24h']}% is refunded if you cancel more than 24 hours before the puja and {BIZ['refund_within_24h']}% within 24 hours.",
             f"పండితుని కేటాయించే ముందు రద్దు చేస్తే పూర్తి రీఫండ్. కేటాయించిన తర్వాత, 24 గంటల ముందు రద్దు చేస్తే {BIZ['refund_before_24h']}%, 24 గంటల లోపు అయితే {BIZ['refund_within_24h']}% రీఫండ్.")]
    faq = "".join(f'<details><summary>{B(q, qt)}</summary><p>{B(a, at)}</p></details>' for q, qt, a, at in faqs)
    body = page_hero(B(c[1], c[2]), sv["en"], sv["te"], sv["dEn"], sv["dTe"],
                     f'<p class="crumbs"><a href="index.html">{B("Home", "హోమ్")}</a> › <a href="services.html#{c[0]}">{B(c[1], c[2])}</a></p>')
    body += f'''<section class="section kolam-bg"><div class="wrap puja-grid">
<div class="puja-main">
  <div class="board">
    <div class="board-head"><h2>{B("At a glance", "ముఖ్య వివరాలు")}</h2></div>
    <dl class="facts">
      <div><dt>{B("Pandit service fee", "పండితుల సేవా రుసుము")}</dt><dd class="seva-price">{inr(sv["price"])}</dd></div>
      <div><dt>{B("Duration", "సమయం")}</dt><dd>{B(sv["durEn"], sv["durTe"])}</dd></div>
      <div><dt>{B("Where", "ఎక్కడ")}</dt><dd>{where}</dd></div>
      <div><dt>{B("Samagri", "సామగ్రి")}</dt><dd>{kit}</dd></div>
      <div><dt>{B("Pandits", "పండితులు")}</dt><dd>{B("KYC-verified Telugu Vaidika pandits. Explanation in Telugu, or Hindi or English on request.", "KYC ధ్రువీకరించిన తెలుగు వైదిక పండితులు. తెలుగులో వివరణ; కోరితే హిందీ లేదా ఇంగ్లీష్‌లో.")}</dd></div>
    </dl>
    <p style="margin-top:1.4rem"><a class="btn btn-gold" href="book.html#{sv["id"]}">{B("Book " + sv["en"].split(" (")[0], sv["te"] + " బుక్ చేయండి")}</a></p>
  </div>
  <div class="board">
    <div class="board-head"><h2>{B("How booking works", "బుకింగ్ ఎలా జరుగుతుంది")}</h2></div>
    <ol class="mini-steps">
      <li>{B("Send your preferred date, time and area.", "మీకు అనుకూలమైన తేదీ, సమయం, ప్రాంతం పంపండి.")}</li>
      <li>{B("We confirm a verified pandit and send a secure Razorpay payment link.", "ధ్రువీకరించిన పండితుని నిర్ధారించి సురక్షిత Razorpay చెల్లింపు లింక్ పంపుతాం.")}</li>
      <li>{B("You receive the pandit's name before the puja day.", "పూజ రోజుకు ముందే పండితుని పేరు తెలియజేస్తాం.")}</li>
      <li>{B("The pandit arrives on time and performs the full vidhi.", "పండితులు సమయానికి వచ్చి పూర్తి విధివిధానాలతో పూజ చేస్తారు.")}</li>
    </ol>
  </div>
  <div class="board">
    <div class="board-head"><h2>{B("Questions", "ప్రశ్నలు")}</h2></div>
    <div class="faq">{faq}</div>
  </div>
</div>
<aside class="puja-side">
  <div class="summary-card">
    <h2 class="fh-side">{B("Related pujas", "సంబంధిత పూజలు")}</h2>
    <ul class="rel">{rel}</ul>
    <a class="btn btn-gold" href="services.html">{B("All pujas & prices", "అన్ని పూజలు & ధరలు")}</a>
  </div>
</aside>
</div></section>'''
    url = SITE + "/" + slug(sv)
    schema = [{"@type": "Service", "@id": url + "#service", "name": sv["en"], "alternateName": sv["te"], "description": sv["dEn"], "url": url,
               "serviceType": "Hindu puja service", "provider": {"@id": SITE + "/#org"},
               "areaServed": {"@type": "City", "name": "Hyderabad"} if not online else "IN",
               "offers": {"@type": "Offer", "price": sv["price"], "priceCurrency": "INR", "url": url, "availability": "https://schema.org/InStock"}},
              {"@type": "BreadcrumbList", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                  {"@type": "ListItem", "position": 2, "name": "Pujas & Prices", "item": SITE + "/services.html"},
                  {"@type": "ListItem", "position": 3, "name": sv["en"], "item": url}]}]
    name = sv["en"].split(" (")[0]
    where_t = "Online" if online else "Hyderabad"
    title = f"{name}{'' if online else ' in Hyderabad'}: Pandit, Cost & Booking | Mana Guruji"
    desc = f"Book {name} with verified Telugu pandits {'online over video call' if online else 'in Hyderabad'}. Pandit fee {inr(sv['price'])}" + (f", samagri kit {inr(sv['kit'])}" if sv['kit'] else "") + f". {sv['durEn']}. Book online."
    return page(slug(sv), title, desc, body, "services.html", schema=schema)

PAGES = {"index.html": home, "services.html": services, "book.html": book, "about.html": about, "contact.html": contact,
         "terms-and-conditions.html": terms, "privacy-policy.html": privacy, "refund-policy.html": refund,
         "service-delivery-policy.html": delivery, "404.html": notfound}
for _sv in S:
    PAGES[slug(_sv)] = (lambda sv=_sv: puja_page(sv))

def main():
    # Writes into the repo root. Never deletes anything. Images and video live in /assets.
    d = OUT
    import datetime
    today = datetime.date.today().isoformat()
    css, js = open(os.path.join(SRC, "styles.css")).read(), open(os.path.join(SRC, "site.js")).read()
    try:  # minify when available:  pip install rcssmin rjsmin
        import rcssmin, rjsmin
        css, js = rcssmin.cssmin(css), rjsmin.jsmin(js)
    except ImportError:
        print("note: rcssmin/rjsmin not installed, writing unminified CSS/JS")
    open(os.path.join(d, "styles.css"), "w").write(css)
    open(os.path.join(d, "site.js"), "w").write(js)
    open(os.path.join(d, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nDisallow: /_build/\nSitemap: https://{BIZ['domain']}/sitemap.xml\n")
    prio = lambda p: "1.0" if p == "index.html" else ("0.9" if p in ("services.html", "book.html") else ("0.8" if p.endswith("-hyderabad.html") else "0.5"))
    urls = "".join(f"<url><loc>https://{BIZ['domain']}/{'' if p == 'index.html' else p}</loc><lastmod>{today}</lastmod><priority>{prio(p)}</priority></url>" for p in PAGES if p != "404.html")
    open(os.path.join(d, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    for name, fn in PAGES.items():
        full, _ = fn()
        open(os.path.join(d, name), "w").write(full)
    print("built", len(PAGES), "pages into", d)

if __name__ == "__main__":
    main()
