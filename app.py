from pathlib import Path
import base64
import os
import time
import streamlit as st
from google import genai
from google.genai import types

APP_DIR = Path(__file__).parent
KNOWLEDGE_DIR = APP_DIR / "knowledge"
AVATAR = APP_DIR / "ask_ahmed_avatar_personal.png"
HERO_BG = APP_DIR / "hero_bg.jpg"

st.set_page_config(
    page_title="Ask Ahmed",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_knowledge() -> str:
    chunks = []
    for file in sorted(KNOWLEDGE_DIR.glob("*.md")):
        chunks.append(f"\n\n### SOURCE: {file.name}\n{read_text(file)}")
    return "".join(chunks)


def get_api_key() -> str | None:
    try:
        return st.secrets.get("GEMINI_API_KEY")
    except Exception:
        return os.getenv("GEMINI_API_KEY")


def image_data_uri(path: Path, mime: str = "image/png") -> str:
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def clear_chat():
    st.session_state.messages = []
    st.session_state.pop("pending_prompt", None)


if "messages" not in st.session_state:
    st.session_state.messages = []
if "ui_lang" not in st.session_state:
    st.session_state.ui_lang = "EN"

copy = {
    "EN": {
        "name": "Ahmed Omar",
        "by_name": "Ahmed Omar",
        "hello": "Hello! 👋",
        "im": "I’m",
        "ask_any": "Ask me anything",
        "intro": "I’m your AI assistant, here to share information about my background, experience, skills, projects, and how we can work together.",
        "subintro": "Feel free to ask about my work, profile, or collaboration opportunities.",
        "quote": "Turning knowledge and technology into real opportunities.",
        "themes": "LANGUAGE  |  TECHNOLOGY  |  RESEARCH",
        "topics_title": "What you can ask about",
        "topics_hint": "Click a topic to ask a question",
        "home": "Home",
        "home_sub": "Start a conversation",
        "about": "About",
        "about_sub": "Who I am",
        "experience": "Experience",
        "experience_sub": "What I do",
        "projects": "Projects",
        "projects_sub": "Ideas & initiatives",
        "services": "Services",
        "services_sub": "How I can help",
        "contact": "Contact",
        "contact_sub": "Let’s connect",
        "assistant": "Your AI Assistant",
        "tagline": "Ideas into Solutions",
        "type": "Type your question here...",
        "thinking": "Thinking…",
        "footer": "Ask Ahmed may make mistakes. For critical information, please verify directly.",
        "labels": [
            ("Professional\nbackground", "Education, roles\nand career journey"),
            ("Personal\noverview", "Interests, values\nand life outside work"),
            ("Translation\nexperience", "Languages, fields\nand tools"),
            ("IT & technical\nexperience", "Support, systems\nand technology"),
            ("AI & digital\nprojects", "Ideas, tools and what\nI’m building"),
            ("Services &\ncollaboration", "How we can work\ntogether"),
            ("Contact details", "WhatsApp, LinkedIn,\nwebsite, email and more"),
        ],
        "questions": [
            "Give me a concise overview of Ahmed Omar's professional background, education, roles, and career journey.",
            "Give me a natural personal overview of Ahmed Omar, including relevant interests, values, and background that help me understand him as a person.",
            "Tell me about Ahmed Omar's translation experience, languages, subject areas, tools, and working style.",
            "Explain Ahmed Omar's IT and technical experience, especially Help Desk, Microsoft environments, troubleshooting, and practical support work.",
            "Tell me about Ahmed Omar's work and interests in AI, digital workflows, websites, automation, and business technology.",
            "What services, roles, and collaboration opportunities could be a good fit for Ahmed Omar? Give practical examples.",
            "How can I contact Ahmed Omar, and what is the best next step if I want to discuss a project, role, or partnership?",
        ],
        "nav_questions": {
            "about": "Give me a concise but engaging overview of Ahmed Omar as a person and professional.",
            "experience": "Summarize Ahmed Omar's strongest professional experience across translation and IT.",
            "projects": "Tell me about the kinds of projects Ahmed Omar has worked on or developed, especially digital, AI, web, IT, and translation projects.",
            "services": "What can Ahmed Omar help with professionally, and which kinds of collaborations fit him best?",
            "contact": "Show Ahmed Omar's confirmed contact details and the best way to reach him.",
        },
    },
    "AR": {
        "name": "أحمد عمر",
        "by_name": "أحمد عمر",
        "hello": "مرحبًا! 👋",
        "im": "أنا",
        "ask_any": "اسألني أي شيء",
        "intro": "أنا مساعد أحمد الذكي، موجود لأعرّفك بخلفيته وخبراته ومهاراته ومشاريعه وفرص العمل والتعاون معه.",
        "subintro": "اسأل بشكل طبيعي عن خبرته، ملفه المهني، أو فرص التعاون المناسبة.",
        "quote": "تحويل المعرفة والتكنولوجيا إلى فرص حقيقية.",
        "themes": "اللغة  |  التقنية  |  البحث",
        "topics_title": "شو ممكن تسأل؟",
        "topics_hint": "اضغط على أي موضوع ليبدأ السؤال",
        "home": "الرئيسية",
        "home_sub": "ابدأ محادثة",
        "about": "عني",
        "about_sub": "من أنا",
        "experience": "الخبرات",
        "experience_sub": "ماذا أعمل",
        "projects": "المشاريع",
        "projects_sub": "أفكار ومبادرات",
        "services": "الخدمات",
        "services_sub": "كيف أقدر أساعد",
        "contact": "التواصل",
        "contact_sub": "خلّينا نتواصل",
        "assistant": "مساعدك الذكي",
        "tagline": "من الأفكار إلى الحلول",
        "type": "اكتب سؤالك هنا...",
        "thinking": "لحظة…",
        "footer": "قد يخطئ Ask Ahmed أحيانًا. للمعلومات الحساسة أو المهمة جدًا، يفضّل التأكد مباشرة.",
        "labels": [
            ("الخلفية\nالمهنية", "الدراسة والأدوار\nوالمسار المهني"),
            ("نبذة\nشخصية", "الاهتمامات والقيم\nوالجانب الشخصي"),
            ("خبرة\nالترجمة", "اللغات والمجالات\nوالأدوات"),
            ("الخبرة التقنية\nوIT", "الدعم والأنظمة\nوالتكنولوجيا"),
            ("الذكاء الاصطناعي\nوالمشاريع الرقمية", "أفكار وأدوات\nومشاريع رقمية"),
            ("الخدمات\nوالتعاون", "كيف ممكن نشتغل\nمع بعض"),
            ("بيانات التواصل", "واتساب ولينكدإن\nوالموقع والإيميل"),
        ],
        "questions": [
            "أعطني نبذة مختصرة عن الخلفية المهنية لأحمد عمر، دراسته وأدواره ومساره المهني.",
            "أعطني نبذة شخصية طبيعية عن أحمد عمر، بما في ذلك اهتماماته وقيمه وخلفيته العامة التي تساعدني على فهمه كشخص.",
            "حدثني عن خبرة أحمد عمر في الترجمة، اللغات، المجالات، الأدوات وطريقة عمله.",
            "اشرح خبرة أحمد عمر في تقنية المعلومات، خصوصًا Help Desk وMicrosoft وAzure وحل المشكلات والدعم العملي.",
            "حدثني عن أعمال واهتمامات أحمد عمر في الذكاء الاصطناعي وسير العمل الرقمي والويب والأتمتة وتقنيات الأعمال.",
            "ما الخدمات والوظائف وفرص التعاون التي تناسب أحمد عمر؟ أعطني أمثلة عملية.",
            "اعرض بيانات التواصل المؤكدة لأحمد عمر وأفضل طريقة للتواصل معه.",
        ],
        "nav_questions": {
            "about": "أعطني نبذة جذابة ومختصرة عن أحمد عمر كشخص ومحترف.",
            "experience": "لخّص أقوى خبرات أحمد عمر المهنية في الترجمة وتقنية المعلومات.",
            "projects": "حدّثني عن أنواع المشاريع التي عمل عليها أو طوّرها أحمد عمر، خاصة في الذكاء الاصطناعي والويب وIT والترجمة.",
            "services": "ما الذي يمكن أن يقدمه أحمد عمر مهنيًا؟ وما أنواع التعاون الأنسب له؟",
            "contact": "اعرض بيانات التواصل المؤكدة لأحمد عمر وأفضل وسيلة للوصول إليه.",
        },
    },
}

qp = st.query_params
if "lang" in qp:
    requested = str(qp.get("lang", "EN")).upper()
    if requested in ("EN", "AR"):
        st.session_state.ui_lang = requested

lang = st.session_state.ui_lang
L = copy[lang]
rtl = lang == "AR"
avatar_uri = image_data_uri(AVATAR, "image/png")
hero_uri = image_data_uri(HERO_BG, "image/jpeg")

if "topic" in qp:
    try:
        i = int(qp["topic"])
        if 0 <= i < len(L["questions"]):
            st.session_state.pending_prompt = L["questions"][i]
    except Exception:
        pass
    st.query_params.clear()
    st.rerun()

if "nav" in qp:
    action = str(qp["nav"])
    if action == "home":
        clear_chat()
    elif action in L["nav_questions"]:
        st.session_state.pending_prompt = L["nav_questions"][action]
    st.query_params.clear()
    st.rerun()

SYSTEM_PROMPT = read_text(APP_DIR / "system_prompt.md")
KNOWLEDGE = load_knowledge()
api_key = get_api_key()

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@600;700&family=DM+Sans:wght@400;500;600;700;800&family=Alexandria:wght@400;500;600;700;800&family=Cairo:wght@400;500;600;700;800;900&display=swap');
:root {{ --navy:#0a1d2f; --navy2:#102c43; --ink:#102135; --muted:#6c7c8c; --teal:#1ea4a8; --cyan:#178aaa; --surface:#ffffff; --line:rgba(20,48,68,.09); }}
html,body,[class*="css"] {{ font-family:{'Cairo' if rtl else 'DM Sans'},sans-serif; }}
.stApp {{ background:linear-gradient(180deg,#f6f8fa 0%,#f2f5f7 100%); color:var(--ink); }}
header[data-testid="stHeader"] {{ background:transparent; height:0; }}
[data-testid="stToolbar"], #MainMenu, footer {{ visibility:hidden; }}
.block-container {{ max-width:1240px; padding:0 1.3rem 1.2rem 1.3rem; direction:{'rtl' if rtl else 'ltr'}; }}
{'[data-testid="stSidebar"] { right:0 !important; left:auto !important; border-left:0 !important; } [data-testid="stAppViewContainer"] > .main { margin-left:0 !important; }' if rtl else ''}
[data-testid="stSidebar"] {{ width:270px !important; min-width:270px !important; background:linear-gradient(180deg,#071a2b 0%,#0e2a40 52%,#081a29 100%); border:0; box-shadow:8px 0 34px rgba(5,20,31,.13); }}
[data-testid="stSidebar"] > div:first-child {{ padding:1rem .85rem 1rem; }}
.side-shell {{ direction:{'rtl' if rtl else 'ltr'}; min-height:96vh; display:flex; flex-direction:column; }}
.lang-switch {{ display:flex; gap:.28rem; align-self:{'flex-start' if rtl else 'flex-end'}; background:rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.09); border-radius:999px; padding:.22rem; margin-bottom:1rem; }}
.lang-switch form {{ margin:0; }}
.lang-switch button {{ cursor:pointer; color:#d7e5ee; text-decoration:none; font-size:.72rem; font-weight:800; padding:.34rem .65rem; border-radius:999px; background:none; border:none; }}
.lang-switch .active {{ background:linear-gradient(90deg,#1a8faa,#2da9a9); color:#fff; box-shadow:0 5px 12px rgba(25,151,167,.18); }}
.side-brand {{ text-align:center; padding:.15rem .2rem .8rem; }}
.side-avatar-wrap {{ position:relative; width:112px; height:112px; margin:0 auto; }}
.side-avatar-wrap:before {{ content:""; position:absolute; inset:-5px; border-radius:50%; background:conic-gradient(from 220deg,#5bd0cf,#7cb6ff,#3e7fa3,#5bd0cf); opacity:.9; }}
.side-avatar {{ position:relative; width:112px; height:112px; object-fit:cover; border-radius:50%; border:5px solid #0b2235; box-shadow:0 14px 30px rgba(0,0,0,.28); background:#123; }}
.side-title {{ color:#fff; font-size:1.65rem; font-weight:800; margin-top:.65rem; letter-spacing:-.04em; }}
.side-sub {{ color:#aec4d2; font-size:{'.92rem' if rtl else '.8rem'}; line-height:{'1.8' if rtl else '1.55'}; font-weight:{'500' if rtl else '400'}; }}
.nav-list {{ display:flex; flex-direction:column; gap:.42rem; margin-top:.35rem; }}
.nav-form {{ margin:0; }}
.nav-form button, .topic-form button {{ all:unset; display:block; width:100%; cursor:pointer; }}
.nav-card {{ width:100%; display:grid; grid-template-columns:34px 1fr; align-items:center; gap:.65rem; min-height:58px; padding:.62rem .72rem; border-radius:13px; text-align:{'right' if rtl else 'left'}; color:#f1f7fb; border:1px solid transparent; background:transparent; transition:.16s ease; }}
.nav-card:hover {{ transform:translateX({'-3px' if rtl else '3px'}); background:rgba(53,172,182,.13); border-color:rgba(76,211,210,.13); }}
.nav-card.active {{ background:linear-gradient(90deg,#1689a0,#28738f); box-shadow:0 9px 20px rgba(10,104,133,.22); }}
.nav-icon {{ width:32px; height:32px; display:grid; place-items:center; color:#d9f5f5; }}
.nav-icon svg {{ width:22px; height:22px; stroke:currentColor; fill:none; stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round; }}
.nav-text b {{ display:block; font-size:{'1rem' if rtl else '.9rem'}; line-height:{'1.55' if rtl else '1.15'}; color:#fff; font-family:{'Alexandria' if rtl else 'DM Sans'},sans-serif; }}
.nav-text span {{ display:block; margin-top:.16rem; font-size:{'.82rem' if rtl else '.68rem'}; color:#b9ceda; line-height:{'1.65' if rtl else '1.25'}; }}
.side-bottom {{ margin-top:auto; padding-top:1rem; }}
.side-tag {{ font-family:{'Alexandria' if rtl else "'Caveat'"},sans-serif; font-size:{'1.02rem' if rtl else '1.35rem'}; font-weight:{'700' if rtl else '600'}; color:#86dbda; text-align:center; position:relative; padding:.7rem 0; line-height:{'1.7' if rtl else '1.1'}; }}
.side-tag:before,.side-tag:after {{ content:""; position:absolute; height:2px; width:34px; background:linear-gradient(90deg,transparent,#2fb6bc); top:50%; }}
.side-tag:before {{ left:5px; }} .side-tag:after {{ right:5px; transform:rotate(180deg); }}
.social-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:.56rem; margin-top:.55rem; }}
.social-col {{ display:flex; flex-direction:column; align-items:center; gap:.28rem; text-align:center; color:#d5e6ee !important; font-size:.61rem; text-decoration:none !important; }}
.social {{ width:38px; height:38px; display:grid; place-items:center; border-radius:11px; background:rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.08); color:#ecf8fa; transition:.15s ease; }}
.social:hover {{ transform:translateY(-2px); background:rgba(44,174,179,.18); }}
.social svg {{ width:19px; height:19px; fill:none; stroke:currentColor; stroke-width:1.85; stroke-linecap:round; stroke-linejoin:round; }}
.social.linkedin svg, .social.whatsapp svg {{ fill:currentColor; stroke:none; }}
.hero {{ position:relative; overflow:hidden; min-height:342px; border-radius:0 0 25px 25px; margin:0 0 1.15rem; border:1px solid rgba(26,57,78,.06); box-shadow:0 12px 38px rgba(28,48,63,.08); background-image:linear-gradient(90deg,rgba(251,252,253,.97) 0%,rgba(251,252,253,.94) 42%,rgba(251,252,253,.60) 68%,rgba(251,252,253,.16) 100%),url('{hero_uri}'); background-size:cover; background-position:center; }}
.hero:before {{ content:""; position:absolute; inset:auto -5% -58px -5%; height:150px; background:radial-gradient(80% 90% at 20% 0%,rgba(72,172,196,.18),transparent 66%),radial-gradient(75% 90% at 75% 8%,rgba(255,190,132,.18),transparent 68%); filter:blur(4px); }}
.hero:after {{ content:""; position:absolute; left:-6%; right:-6%; bottom:-94px; height:170px; background:rgba(231,243,247,.70); border-radius:50% 50% 0 0 / 40% 40% 0 0; transform:rotate(-1deg); }}
.hero-wave {{ position:absolute; inset:0; background:radial-gradient(circle at 72% 14%,rgba(161,255,255,.18),transparent 24%),radial-gradient(circle at 82% 26%,rgba(160,220,255,.15),transparent 18%); pointer-events:none; }}
.hero-inner {{ position:relative; z-index:2; min-height:342px; display:grid; grid-template-columns:minmax(0,1.28fr) minmax(300px,.72fr); gap:1rem; align-items:center; padding:2.25rem 2.45rem 2rem; }}
.hello {{ font-size:{'1.38rem' if rtl else '1.22rem'}; font-weight:800; margin-bottom:.22rem; font-family:{'Alexandria' if rtl else 'DM Sans'},sans-serif; }}
.hero h1 {{ margin:0; font-size:{'2.55rem' if rtl else '3.05rem'}; line-height:1.02; font-weight:800; letter-spacing:{'0' if rtl else '-.055em'}; color:#0d1f32; font-family:{'Alexandria' if rtl else 'DM Sans'},sans-serif; }}
.hero h1 .accent {{ background:linear-gradient(90deg,#1b7890,#15989b); -webkit-background-clip:text; background-clip:text; color:transparent; }}
.askline {{ margin-top:.28rem; font-size:{'1.72rem' if rtl else '1.78rem'}; line-height:{'1.65' if rtl else '1.2'}; font-weight:700; color:#15263b; font-family:{'Alexandria' if rtl else 'DM Sans'},sans-serif; }}
.hero p {{ max-width:640px; margin:.72rem 0 0; color:#526678; font-size:{'1.15rem' if rtl else '.92rem'}; line-height:{'2.0' if rtl else '1.55'}; font-weight:{'500' if rtl else '400'}; }}
.hero-right {{ text-align:center; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:.95rem; }}
.script-hero {{ font-family:{'Alexandria' if rtl else "'Caveat'"},sans-serif; color:#0b4c69; font-size:{'1.48rem' if rtl else '2.3rem'}; font-weight:{'700' if rtl else '600'}; line-height:{'1.85' if rtl else '.92'}; transform:{'none' if rtl else 'rotate(-5deg)'}; max-width:{'320px' if rtl else '280px'}; }}
.themes {{ font-family:{'Alexandria' if rtl else 'DM Sans'},sans-serif; font-size:{'.88rem' if rtl else '.6rem'}; line-height:{'1.8' if rtl else '1.2'}; letter-spacing:{'.02em' if rtl else '.27em'}; color:#5f7080; font-weight:700; }}
.quote-card {{ width:min(300px,100%); padding:1.05rem 1.2rem; border-radius:19px; background:rgba(255,255,255,.80); border:1px solid rgba(34,64,83,.08); box-shadow:0 13px 30px rgba(31,52,67,.07); backdrop-filter:blur(8px); color:#1f3a4e; font-size:{'1rem' if rtl else '.88rem'}; line-height:{'1.9' if rtl else '1.5'}; text-align:{'right' if rtl else 'left'}; }}
.quote-card b {{ display:block; margin-top:.5rem; font-size:.68rem; letter-spacing:.06em; }}
.cta-row {{ display:flex; gap:.75rem; margin:1.15rem 0 1.65rem; direction:{'rtl' if rtl else 'ltr'}; align-items:center; }}
.cta-row form {{ margin:0 !important; padding:0 !important; border:0 !important; outline:0 !important; background:transparent !important; box-shadow:none !important; }}
.cta-row form button {{ all:unset; display:block; cursor:pointer; border:0 !important; outline:0 !important; box-shadow:none !important; background:transparent !important; }}
.cta {{ min-width:205px; padding:.82rem 1.05rem; border-radius:13px; display:inline-flex; align-items:center; justify-content:center; gap:.55rem; text-decoration:none !important; font-size:.86rem; font-weight:700; border:1px solid rgba(26,52,71,.11); box-shadow:0 7px 16px rgba(25,49,65,.05); }}
.cta.primary {{ background:linear-gradient(90deg,#0d2033,#173d58); color:#fff !important; }}
.cta.secondary {{ background:#fff; color:#21384b !important; }}
.section-head {{ display:flex; justify-content:space-between; align-items:end; gap:1rem; margin:.2rem 0 .75rem; }}
.section-title {{ font-family:{'Alexandria' if rtl else 'DM Sans'},sans-serif; font-size:{'1.7rem' if rtl else '1.38rem'}; font-weight:800; color:#112238; letter-spacing:-.025em; }}
.section-hint {{ font-size:{'1rem' if rtl else '.76rem'}; line-height:{'1.8' if rtl else '1.2'}; color:#6f8795; font-weight:{'500' if rtl else '400'}; }}
.topic-grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:1rem; margin-bottom:1rem; direction:{'rtl' if rtl else 'ltr'}; }}
.topic-form {{ margin:0; }}
.topic-card {{ min-height:150px; position:relative; overflow:hidden; display:flex; flex-direction:column; justify-content:space-between; padding:1.05rem 1.05rem 1rem; border-radius:18px; background:linear-gradient(145deg,rgba(255,255,255,.99),rgba(247,250,251,.98)); border:1px solid rgba(29,57,76,.08); box-shadow:0 9px 22px rgba(29,51,66,.055); text-align:{'right' if rtl else 'left'}; color:#142638; transition:.17s ease; }}
.topic-card:after {{ content:""; position:absolute; width:90px; height:90px; border-radius:50%; right:-36px; top:-42px; background:var(--glow,rgba(35,159,170,.10)); filter:blur(1px); }}
.topic-card:hover {{ transform:translateY(-4px); box-shadow:0 16px 30px rgba(28,54,70,.09); border-color:rgba(33,159,165,.20); }}
.topic-top {{ display:flex; align-items:flex-start; gap:.7rem; position:relative; z-index:2; }}
.topic-icon {{ width:39px; height:39px; flex:0 0 39px; border-radius:12px; display:grid; place-items:center; background:var(--iconbg); color:var(--icon); box-shadow:inset 0 0 0 1px rgba(255,255,255,.5); }}
.topic-icon svg {{ width:22px; height:22px; stroke:currentColor; fill:none; stroke-width:1.9; stroke-linecap:round; stroke-linejoin:round; }}
.topic-num {{ color:#93a2b1; font-size:.74rem; font-weight:700; padding-top:.1rem; }}
.topic-title {{ font-family:{'Alexandria' if rtl else 'DM Sans'},sans-serif; font-size:{'1.08rem' if rtl else '.92rem'}; font-weight:800; line-height:{'1.65' if rtl else '1.17'}; margin-top:.02rem; color:#12243a; }}
.topic-sub {{ font-size:{'.95rem' if rtl else '.75rem'}; color:#71808e; line-height:{'1.8' if rtl else '1.38'}; margin-left:{'0' if rtl else '39px'}; margin-right:{'39px' if rtl else '0'}; position:relative; z-index:2; }}
.topic-question {{ min-height:150px; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; border-radius:18px; background:radial-gradient(circle at 78% 18%,rgba(45,177,180,.14),transparent 35%),linear-gradient(135deg,#eef9fa,#f8fbfc); border:1px solid rgba(29,130,145,.08); box-shadow:0 9px 22px rgba(29,51,66,.04); color:#176579; }}
.topic-question .script {{ font-family:{'Alexandria' if rtl else "'Caveat'"},sans-serif; font-size:{'1.25rem' if rtl else '1.8rem'}; font-weight:{'700' if rtl else '600'}; line-height:{'1.8' if rtl else '.95'}; transform:{'none' if rtl else 'rotate(-3deg)'}; }}
.topic-question small {{ margin-top:.55rem; color:#82929d; font-size:{'.9rem' if rtl else '.73rem'}; line-height:{'1.7' if rtl else '1.3'}; }}
.chat-anchor {{ height:1px; }}
[data-testid="stChatMessage"] {{ direction:{'rtl' if rtl else 'ltr'}; border-radius:16px; font-size:{'1.02rem' if rtl else '.95rem'}; line-height:{'1.8' if rtl else '1.6'}; }}
[data-testid="stChatInput"] {{ border-radius:18px !important; margin-top:.3rem; }}
[data-testid="stChatInput"] > div {{ border-radius:18px !important; background:#fff !important; border:1px solid rgba(28,55,74,.10) !important; box-shadow:0 8px 22px rgba(30,53,68,.05) !important; }}
[data-testid="stChatInput"] textarea {{ font-family:{'Cairo' if rtl else 'DM Sans'},sans-serif !important; font-size:{'1.05rem' if rtl else '.95rem'} !important; line-height:{'1.8' if rtl else '1.5'} !important; }}
.footer-note {{ text-align:center; color:#8b98a4; font-size:{'.82rem' if rtl else '.67rem'}; line-height:{'1.8' if rtl else '1.4'}; margin:.45rem 0 0; }}
@media(max-width:1050px) {{ .topic-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} .social-grid {{ grid-template-columns:repeat(2,1fr); }} }}
@media(max-width:900px) {{ [data-testid="stSidebar"] {{ width:245px !important; min-width:245px !important; }} .hero-inner {{ grid-template-columns:1fr; min-height:auto; padding:1.6rem 1.45rem 2.4rem; }} .hero-right {{ display:none; }} .hero h1 {{ font-size:{'1.75rem' if rtl else '2.35rem'}; }} }}
@media(max-width:650px) {{ .topic-grid {{ grid-template-columns:1fr; }} .cta-row {{ flex-direction:column; }} .cta {{ width:100%; }} }}
</style>
""",
    unsafe_allow_html=True,
)


def svg(name: str) -> str:
    icons = {
        "home": '<svg viewBox="0 0 24 24"><path d="M3 10.5 12 3l9 7.5"/><path d="M5.5 9.5V21h13V9.5"/><path d="M9 21v-6h6v6"/></svg>',
        "info": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 10v6"/><path d="M12 7h.01"/></svg>',
        "work": '<svg viewBox="0 0 24 24"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5h8v2"/><path d="M3 12h18"/></svg>',
        "projects": '<svg viewBox="0 0 24 24"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 7h8M8 11h8M8 15h5"/></svg>',
        "tools": '<svg viewBox="0 0 24 24"><path d="M14.7 6.3a4 4 0 0 0-5 5L3 18l3 3 6.7-6.7a4 4 0 0 0 5-5l-2.4 2.4-3-3 2.4-2.4Z"/></svg>',
        "mail": '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
        "person": '<svg viewBox="0 0 24 24"><circle cx="12" cy="7" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>',
        "translate": '<svg viewBox="0 0 24 24"><path d="M4 5h10M9 3v2M6 9c1.5 2.5 3.5 4.5 6 6M12 9c-1.4 2.4-3.1 4.2-5.5 6"/><path d="m14 20 3.2-8 3.2 8M15.3 17h3.8"/></svg>',
        "laptop": '<svg viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="12" rx="1.5"/><path d="M2 20h20M8 20l1-4h6l1 4"/></svg>',
        "bulb": '<svg viewBox="0 0 24 24"><path d="M9 18h6M10 22h4"/><path d="M8.5 15.5A6 6 0 1 1 15.5 15.5C14.5 16.2 14 17 14 18h-4c0-1-.5-1.8-1.5-2.5Z"/></svg>',
        "team": '<svg viewBox="0 0 24 24"><circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2"/><path d="M3 20a6 6 0 0 1 12 0M14 16a5 5 0 0 1 7 4"/></svg>',
        "send": '<svg viewBox="0 0 24 24"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>',
        "linkedin": '<svg viewBox="0 0 24 24"><path d="M6.5 8.2H3.3V21h3.2ZM4.9 3A1.9 1.9 0 1 0 5 6.8 1.9 1.9 0 0 0 4.9 3ZM21 13.7c0-3.9-2.1-5.7-4.9-5.7a4.2 4.2 0 0 0-3.8 2.1V8.2H9.1V21h3.2v-6.3c0-1.7.3-3.3 2.4-3.3 2 0 2.1 1.9 2.1 3.4V21H20Z"/></svg>',
        "whatsapp": '<svg viewBox="0 0 24 24"><path d="M20.5 11.7a8.4 8.4 0 0 1-12.4 7.4L3 20.5l1.4-4.9a8.4 8.4 0 1 1 16.1-3.9Z"/><path d="M8.2 8.1c.2-.5.4-.5.7-.5h.5c.2 0 .4.1.5.4l.9 2c.1.3 0 .5-.1.7l-.6.8c-.2.2-.1.4 0 .6a7.2 7.2 0 0 0 3.5 3c.3.1.5.1.7-.1l.9-1.1c.2-.3.4-.3.7-.2l2 .9c.3.1.4.3.4.5 0 .5-.3 1.5-1 2.1-.6.6-1.5.9-2.4.8-1.2-.2-3.7-1-5.9-3.1-1.7-1.7-2.9-3.8-3.2-5-.2-.8 0-1.4.4-1.8Z"/></svg>',
    }
    return icons[name]


def self_link_button(params: dict, label_html: str, class_name: str = "") -> str:
    hidden = "".join(f'<input type="hidden" name="{k}" value="{v}">' for k, v in params.items())
    return f'<form class="{class_name}" action="" method="get">{hidden}<button type="submit">{label_html}</button></form>'


nav_items = [
    ("home", L["home"], L["home_sub"], "home"),
    ("about", L["about"], L["about_sub"], "info"),
    ("experience", L["experience"], L["experience_sub"], "work"),
    ("projects", L["projects"], L["projects_sub"], "projects"),
    ("services", L["services"], L["services_sub"], "tools"),
    ("contact", L["contact"], L["contact_sub"], "mail"),
]
nav_html = ""
for key, title, sub, ic in nav_items:
    content = f'<div class="nav-card {'active' if key == 'home' else ''}"><span class="nav-icon">{svg(ic)}</span><span class="nav-text"><b>{title}</b><span>{sub}</span></span></div>'
    nav_html += self_link_button({"lang": lang, "nav": key}, content, "nav-form")

with st.sidebar:
    st.markdown(
        f'''<div class="side-shell">
        <div class="lang-switch"><form action="" method="get"><input type="hidden" name="lang" value="EN"><button type="submit" class="{'active' if lang == 'EN' else ''}">EN</button></form><form action="" method="get"><input type="hidden" name="lang" value="AR"><button type="submit" class="{'active' if lang == 'AR' else ''}">عربي</button></form></div>
        <div class="side-brand"><div class="side-avatar-wrap"><img class="side-avatar" src="{avatar_uri}"></div><div class="side-title">Ask Ahmed</div><div class="side-sub">{L['assistant']}<br>{'بواسطة ' + L['by_name'] if rtl else 'by ' + L['by_name']}</div></div>
        <div class="nav-list">{nav_html}</div>
        <div class="side-bottom"><div class="side-tag">{L['tagline']}</div><div class="social-grid">
          <a class="social-col" href="https://www.linkedin.com/in/realahmed8" target="_blank"><span class="social linkedin">{svg('linkedin')}</span><span>LinkedIn</span></a>
          <a class="social-col" href="https://wa.me/972599573933" target="_blank"><span class="social whatsapp">{svg('whatsapp')}</span><span>WhatsApp</span></a>
          <a class="social-col" href="https://ahmedservice.com" target="_blank"><span class="social">{svg('projects')}</span><span>Website</span></a>
          <a class="social-col" href="mailto:info@ahmedservice.com"><span class="social">{svg('mail')}</span><span>Email</span></a>
        </div></div></div>''',
        unsafe_allow_html=True,
    )

hero_name = L["name"]
script_text = "أفكار أفضل، لغدٍ أكثر إشراقًا." if rtl else "Better Ideas. A Brighter Tomorrow."
learn_button = self_link_button({"lang": lang, "nav": "about"}, f'<span class="cta secondary">{"اعرف أكثر عني" if rtl else "Learn more about me"}</span>')

st.markdown(
    f'''<section class="hero"><div class="hero-wave"></div><div class="hero-inner"><div class="hero-copy"><div class="hello">{L['hello']}</div><h1>{L['im']} <span class="accent">{hero_name}</span></h1><div class="askline">{L['ask_any']}</div><p>{L['intro']}<br>{L['subintro']}</p></div><div class="hero-right"><div class="script-hero">{script_text}</div><div class="themes">{L['themes']}</div><div class="quote-card">"{L['quote']}"<b>— {hero_name}</b></div></div></div></section><div class="cta-row"><a class="cta primary" href="#chat-area">{'ابدأ محادثة' if rtl else 'Start a conversation'} {'←' if rtl else '→'}</a>{learn_button}</div>''',
    unsafe_allow_html=True,
)

if not api_key:
    st.warning("Add GEMINI_API_KEY in Streamlit Secrets or your local .streamlit/secrets.toml file.")

topic_meta = [
    ("work", "#0f7899", "linear-gradient(135deg,#dff5fa,#eef9fb)", "rgba(29,146,173,.13)"),
    ("person", "#1692a5", "linear-gradient(135deg,#e2f7f7,#f0fbfb)", "rgba(30,164,168,.13)"),
    ("translate", "#18aeb3", "linear-gradient(135deg,#d9f7f7,#effcfc)", "rgba(33,185,187,.13)"),
    ("laptop", "#126e92", "linear-gradient(135deg,#e3f1f8,#f2f8fb)", "rgba(25,118,155,.12)"),
    ("bulb", "#159c84", "linear-gradient(135deg,#e1f8f0,#f2fbf7)", "rgba(24,161,135,.13)"),
    ("team", "#ec893c", "linear-gradient(135deg,#fff0df,#fff8f0)", "rgba(236,137,60,.13)"),
    ("send", "#7f6cc2", "linear-gradient(135deg,#eee9fb,#f8f6fd)", "rgba(127,108,194,.13)"),
]

cards = []
for i, (title, sub) in enumerate(L["labels"]):
    ic, color, bg, glow = topic_meta[i]
    clean_title = title.replace("\n", "<br>")
    clean_sub = sub.replace("\n", "<br>")
    card_content = f'<div class="topic-card" style="--icon:{color};--iconbg:{bg};--glow:{glow}"><div class="topic-top"><div class="topic-icon">{svg(ic)}</div><div class="topic-num">{i+1:02d}</div><div class="topic-title">{clean_title}</div></div><div class="topic-sub">{clean_sub}</div></div>'
    cards.append(self_link_button({"lang": lang, "topic": i}, card_content, "topic-form"))

question_card = f'<div class="topic-question"><div class="script">{"عندك سؤال آخر؟" if rtl else "Have another question?"}</div><small>{"اكتبه بالأسفل مباشرة ↓" if rtl else "Just type it below ↓"}</small></div>'

st.markdown(
    f'''<div class="section-head"><div class="section-title">{L['topics_title']}</div><div class="section-hint">{L['topics_hint']} {'↙' if rtl else '↘'}</div></div><div class="topic-grid">{''.join(cards)}{question_card}</div><div id="chat-area" class="chat-anchor"></div>''',
    unsafe_allow_html=True,
)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

manual_prompt = st.chat_input(L["type"])
prompt = st.session_state.pop("pending_prompt", None) or manual_prompt

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    answer = None
    if not api_key:
        answer = "The assistant is not connected to Gemini yet. Please configure the API key first."
        with st.chat_message("assistant"):
            st.warning(answer)
    else:
        client = genai.Client(api_key=api_key)
        recent = st.session_state.messages[-12:]
        contents = []
        for m in recent:
            role = "model" if m["role"] == "assistant" else "user"
            contents.append(types.Content(role=role, parts=[types.Part(text=m["content"])]))
        language_note = (
            "The interface is Arabic. Use the Arabic name أحمد عمر when speaking Arabic. Answer UI-triggered prompts in natural Arabic unless the visitor asks otherwise."
            if rtl else
            "The interface is English. Use the English name Ahmed Omar. Answer UI-triggered prompts in polished English unless the visitor asks otherwise."
        )
        full_system = f"{SYSTEM_PROMPT}\n\n{language_note}\n\n--- VERIFIED AHMED KNOWLEDGE BASE ---\n{KNOWLEDGE}"
        models_to_try = [
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.5-flash-lite",
        ]
        last_error = None
        with st.chat_message("assistant"):
            with st.spinner(L["thinking"]):
                for model_name in models_to_try:
                    for attempt in range(2):
                        try:
                            response = client.models.generate_content(
                                model=model_name,
                                contents=contents,
                                config=types.GenerateContentConfig(
                                    system_instruction=full_system,
                                    max_output_tokens=1400,
                                ),
                            )
                            answer = response.text or (
                                "تعذر توليد الرد الآن. حاول مرة أخرى."
                                if rtl else
                                "I couldn't generate a response just now. Please try again."
                            )
                            last_error = None
                            break
                        except Exception as e:
                            last_error = e
                            if attempt == 0:
                                time.sleep(1.4)
                    if answer:
                        break

                if answer:
                    st.markdown(answer)
                else:
                    friendly_error = (
                        "الخدمة تحت ضغط مؤقت حاليًا. حاول مرة ثانية بعد لحظات — وسأجرب تلقائيًا أكثر من نموذج متاح."
                        if rtl else
                        "The AI service is temporarily under heavy demand. Please try again in a moment — I’ll automatically try multiple available models."
                    )
                    st.warning(friendly_error)
                    print(f"Gemini fallback exhausted: {last_error}")
    if answer:
        st.session_state.messages.append({"role": "assistant", "content": answer})

st.markdown(f'<div class="footer-note">{L["footer"]}</div>', unsafe_allow_html=True)
