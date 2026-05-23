"""
Builds a clean Swahili/English instruction dataset for fine-tuning.
Produces assistant-style examples — NOT raw web continuations.

Separate from the RAG pipeline: this output goes to fine-tuning only.
"""
import json
import os
import random
from typing import List, Optional

from src.common.logging import get_logger
from src.common.storage import get_data_path, get_project_root

logger = get_logger("process.instruction_dataset")

# Seed examples covering the categories identified in the handover.
# Format: {"instruction": str, "input": str, "output": str, "category": str, "language": str}
SEED_EXAMPLES: List[dict] = [
    # --- Bookkeeping (Swahili) ---
    {
        "instruction": "Nifanye nini kuweka hesabu za duka dogo Tanzania?",
        "input": "",
        "output": (
            "Anza kwa kutenganisha fedha za biashara na fedha binafsi. "
            "Kila siku andika: mauzo yote, matumizi, bidhaa zilizoingia, "
            "bidhaa zilizotoka, madeni ya wateja, na malipo ya wasambazaji. "
            "Tumia daftari la kawaida au programu rahisi kama Excel au "
            "programu ya simu ya uhasibu. Kila mwisho wa wiki angalia "
            "bidhaa zinazouzwa sana na bidhaa zinazoishia — hilo linakusaidia "
            "kupanga stoo vizuri. Kila mwezi hesabu faida: mauzo yote "
            "punguza matumizi yote ni faida yako."
        ),
        "category": "bookkeeping",
        "language": "sw",
    },
    {
        "instruction": "Jinsi ya kuweka rekodi za mauzo kila siku.",
        "input": "",
        "output": (
            "Weka daftari au faili ya Excel yenye safu hizi: tarehe, "
            "bidhaa iliyouzwa, idadi, bei ya mauzo, bei ya ununuzi, "
            "na jina la mteja kama unajua. Kila mwisho wa siku jumla "
            "mauzo yote na ulinganishe na fedha uliyopokea. Tofauti "
            "kati ya jumla ya mauzo na fedha halisi mkononi inaweza "
            "kuonyesha kosa au upotevu."
        ),
        "category": "bookkeeping",
        "language": "sw",
    },
    # --- Registration (Swahili) ---
    {
        "instruction": "Ninaanzaje biashara rasmi Tanzania?",
        "input": "",
        "output": (
            "Hatua za kuanzisha biashara rasmi Tanzania: "
            "1. Chagua aina ya biashara — mtu binafsi, ubia, au kampuni. "
            "2. Sajili jina la biashara au kampuni kupitia BRELA (brela.go.tz). "
            "3. Pata Nambari ya Utambulisho wa Mlipakodi (TIN) kupitia TRA (tra.go.tz). "
            "4. Omba leseni ya biashara kutoka halmashauri ya eneo lako. "
            "5. Fungua akaunti ya benki ya biashara. "
            "6. Kama mauzo yako yanazidi kiwango cha VAT, jiandikishe kwa VAT. "
            "Muda wa usajili kupitia BRELA Online Registry System (ORS) ni siku 1-3."
        ),
        "category": "registration",
        "language": "sw",
    },
    {
        "instruction": "Gharama ya usajili wa kampuni BRELA ni kiasi gani?",
        "input": "",
        "output": (
            "Gharama za usajili wa kampuni kupitia BRELA zinategemea aina ya kampuni. "
            "Kwa kampuni ya hisa (private limited company), ada ya usajili inaweza "
            "kuanzia TZS 95,000 hadi zaidi kulingana na mtaji uliotangazwa. "
            "Kwa biashara ya mtu binafsi, ada ni ndogo zaidi. "
            "Tembelea tovuti ya BRELA (brela.go.tz) au ofisi yao Dar es Salaam "
            "kwa bei za hivi karibuni kwani zinaweza kubadilika."
        ),
        "category": "registration",
        "language": "sw",
    },
    # --- Tax (Swahili) ---
    {
        "instruction": "VAT ni nini na biashara yangu inahitaji kujiandikisha?",
        "input": "",
        "output": (
            "VAT (Value Added Tax) ni kodi ya ongezeko la thamani inayotozwa "
            "kwenye bidhaa na huduma. Kiwango cha kawaida cha VAT Tanzania ni asilimia 18. "
            "Biashara yako lazima ijiandikishe kwa VAT kama mauzo yake ya kila mwaka "
            "yanazidi TZS 200 milioni. Baada ya kujiandikisha, unapaswa kukusanya "
            "VAT kutoka kwa wateja, kutoa risiti za VAT, na kuwasilisha mapato "
            "ya VAT kwa TRA kila mwezi au robo ya mwaka kulingana na makubaliano."
        ),
        "category": "tax",
        "language": "sw",
    },
    {
        "instruction": "Ninafanyaje kulipa kodi kwa biashara ndogo Tanzania?",
        "input": "",
        "output": (
            "Kwa biashara ndogo (mauzo chini ya TZS 100 milioni kwa mwaka), "
            "unalipa kodi kupitia mfumo wa Presumptive Tax wa TRA. "
            "Kodi inategemea kiwango cha mauzo yako ya kila mwaka. "
            "Jiandikishe kupata TIN kupitia TRA (tra.go.tz), "
            "kisha wasilisha tamko la mapato kila mwaka. "
            "Unaweza kulipa online kupitia mfumo wa TRA au kupitia benki. "
            "Epuka adhabu kwa kulipa kwa wakati."
        ),
        "category": "tax",
        "language": "sw",
    },
    # --- Marketing (Swahili) ---
    {
        "instruction": "Nawezaje kupata wateja zaidi kwa biashara ndogo Dar es Salaam?",
        "input": "",
        "output": (
            "Njia bora za kupata wateja zaidi: "
            "1. WhatsApp Business — weka picha za bidhaa na orodha ya bei, "
            "tumia hali za WhatsApp kuonyesha bidhaa mpya. "
            "2. Jiunge na vikundi vya WhatsApp vya biashara katika mtaa wako. "
            "3. Fungua akaunti ya Instagram au Facebook ukionyesha bidhaa kila siku. "
            "4. Tangaza biashara yako kwenye Google Business Profile bure. "
            "5. Toa ofa maalum kwa wateja wa kwanza au ofa za wiki. "
            "6. Omba wateja walioridhika kukuandikia maoni mazuri mtandaoni."
        ),
        "category": "marketing",
        "language": "sw",
    },
    {
        "instruction": "Jinsi ya kutumia mitandao ya kijamii kuuza bidhaa Tanzania.",
        "input": "",
        "output": (
            "Mfumo bora wa kuuza kwenye mitandao ya kijamii: "
            "Piga picha nzuri za bidhaa zako kwenye mwanga mzuri. "
            "Piga video fupi ukionyesha bidhaa au matumizi yake. "
            "Weka bei wazi kwenye kila chapisho. "
            "Jibu maswali ya wateja haraka — ndani ya saa moja kama inawezekana. "
            "Chapisha mara tatu hadi tano kwa wiki. "
            "Tumia TikTok kwa video fupi za bidhaa — inafika wateja wengi haraka. "
            "Kagua kwa takwimu ni chapisho gani linalopata maoni na mauzo zaidi."
        ),
        "category": "marketing",
        "language": "sw",
    },
    # --- Cash Flow (Swahili) ---
    {
        "instruction": "Biashara yangu inapata mapato lakini sina fedha. Tatizo ni nini?",
        "input": "",
        "output": (
            "Hali hii inaitwa tatizo la mtiririko wa fedha (cash flow). "
            "Sababu za kawaida: "
            "1. Unauza kwa mkopo bila kukusanya kwa wakati — "
            "weka muda mfupi wa kulipa kwa wateja. "
            "2. Umeweka fedha nyingi kwenye stoo bila kuuza — "
            "punguza stoo ya bidhaa zinazotembea polepole. "
            "3. Matumizi ya biashara yanazidi mapato — "
            "pitia matumizi yote na kata yasiyohitajika. "
            "Suluhisho: andika mtiririko wa fedha kila wiki — "
            "fedha zinazoingia na fedha zinazotoka. "
            "Daima jua itakuwa na fedha ngapi wiki ijayo."
        ),
        "category": "cash_flow",
        "language": "sw",
    },
    # --- Bookkeeping (English) ---
    {
        "instruction": "How do I keep basic accounts for a small shop in Tanzania?",
        "input": "",
        "output": (
            "Start by separating business and personal money in separate accounts or wallets. "
            "Each day record: total sales, total expenses, goods received, goods sold, "
            "customer debts, and supplier payments. "
            "Use a notebook, Excel, or a simple accounting app. "
            "At the end of every week, count your stock and check for discrepancies. "
            "At the end of every month, calculate profit: total sales minus total costs."
        ),
        "category": "bookkeeping",
        "language": "en",
    },
    # --- Registration (English) ---
    {
        "instruction": "How do I register a business in Tanzania?",
        "input": "",
        "output": (
            "To register a business in Tanzania: "
            "1. Choose your business type — sole proprietorship, partnership, or company. "
            "2. Register your business name or company with BRELA at brela.go.tz. "
            "3. Obtain a Tax Identification Number (TIN) from TRA at tra.go.tz. "
            "4. Get a business license from your local municipal council. "
            "5. Open a business bank account. "
            "BRELA's Online Registry System (ORS) allows registration in 1-3 days. "
            "Costs vary by company type — check BRELA's website for current fees."
        ),
        "category": "registration",
        "language": "en",
    },
    # --- Tax (English) ---
    {
        "instruction": "What taxes does a small business in Tanzania have to pay?",
        "input": "",
        "output": (
            "Small businesses in Tanzania typically pay: "
            "1. Income Tax — businesses earning under TZS 100 million/year pay "
            "Presumptive Tax based on revenue brackets set by TRA. "
            "2. VAT — mandatory if annual turnover exceeds TZS 200 million; rate is 18%. "
            "3. Skills and Development Levy (SDL) — 4% of gross payroll if you have employees. "
            "4. PAYE — Pay As You Earn tax withheld from employee salaries. "
            "Register with TRA (tra.go.tz) to get your TIN and file annual returns."
        ),
        "category": "tax",
        "language": "en",
    },
    # --- Marketing (English) ---
    {
        "instruction": "What is the best way to market a small business in Tanzania?",
        "input": "",
        "output": (
            "Effective low-cost marketing for Tanzanian small businesses: "
            "1. WhatsApp Business — create a product catalogue, use status updates daily. "
            "2. Google Business Profile — free listing that shows your business on Maps. "
            "3. Instagram and Facebook — post product photos with clear prices 3-5 times per week. "
            "4. TikTok — short product demo videos reach new customers quickly. "
            "5. Word of mouth — ask satisfied customers to refer friends in exchange for a discount. "
            "6. Local market presence — participate in local fairs, trade exhibitions. "
            "Track which channel brings most actual sales, then invest more time there."
        ),
        "category": "marketing",
        "language": "en",
    },
    # --- Inventory (English) ---
    {
        "instruction": "How do I manage stock and inventory for a small retail shop?",
        "input": "",
        "output": (
            "Basic stock management steps: "
            "1. Keep a stock register — list every product, quantity on hand, reorder level. "
            "2. Record every purchase and every sale. "
            "3. Do a physical stock count weekly or monthly and reconcile with records. "
            "4. Set a minimum quantity for fast-moving items — reorder before you run out. "
            "5. Identify slow-moving items and stop reordering them or discount them. "
            "6. Use a simple spreadsheet or free apps like StoreApp to track stock automatically."
        ),
        "category": "inventory",
        "language": "en",
    },
    # --- Supplier Management (Swahili) ---
    {
        "instruction": "Jinsi ya kushughulikia wasambazaji wa bidhaa Tanzania.",
        "input": "",
        "output": (
            "Vidokezo vya kushughulikia wasambazaji vizuri: "
            "1. Linganisha bei za wasambazaji 2-3 kabla ya kununua. "
            "2. Omba risiti na hati ya malipo kwa kila ununuzi. "
            "3. Ukiwa unaweza, lipa kwa wakati — utapata bei nzuri zaidi na mkopo. "
            "4. Jua muda wa uwasilishaji wa kila msambazaji na upange stoo ipasavyo. "
            "5. Usiamini msambazaji mmoja tu — weka wasambazaji wawili hadi watatu "
            "wa kila bidhaa muhimu ili kujilinda na ukosefu wa bidhaa."
        ),
        "category": "supplier_management",
        "language": "sw",
    },
    # --- Pricing (Swahili) ---
    {
        "instruction": "Ninawezaje kuweka bei sahihi za bidhaa zangu?",
        "input": "",
        "output": (
            "Formula rahisi ya bei: Bei ya Mauzo = Gharama ya Ununuzi + Gharama za Uendeshaji + Faida. "
            "Hatua: "
            "1. Jua gharama halisi ya bidhaa moja — bei ya ununuzi + usafirishaji + upotevu. "
            "2. Hesabu sehemu ya gharama za uendeshaji kwa bidhaa hiyo (kodi, umeme, wafanyakazi). "
            "3. Ongeza faida unayotaka — kawaida asilimia 20-50 kulingana na aina ya bidhaa. "
            "4. Linganisha na bei za washindani — usiwe juu sana wala chini sana. "
            "5. Kagua bei kila miezi 3 au ukibadilika bei ya ununuzi."
        ),
        "category": "pricing",
        "language": "sw",
    },
    # --- Employee Management (English) ---
    {
        "instruction": "What are my obligations as an employer in Tanzania?",
        "input": "",
        "output": (
            "Key employer obligations in Tanzania under the Employment and Labour Relations Act: "
            "1. Provide a written contract of employment for every employee. "
            "2. Pay at least the minimum wage set by the government for your sector. "
            "3. Deduct PAYE and remit to TRA monthly. "
            "4. Contribute to NSSF (National Social Security Fund) — 20% of gross wage "
            "(10% employer, 10% employee). "
            "5. Pay SDL (Skills Development Levy) at 4% of gross payroll monthly. "
            "6. Provide paid annual leave (28 days per year), sick leave, and maternity leave. "
            "7. Register with OSHA for workplace safety compliance."
        ),
        "category": "employees",
        "language": "en",
    },
    # --- Banking (Swahili) ---
    {
        "instruction": "Benki ipi nzuri kwa biashara ndogo Tanzania?",
        "input": "",
        "output": (
            "Benki na huduma zinazofaa kwa biashara ndogo Tanzania: "
            "NMB Bank, CRDB Bank, na Equity Bank zina akaunti maalum za biashara ndogo "
            "zenye ada ndogo. "
            "Pia fikiria M-Pesa Business, Tigo Pesa Business, au Airtel Money Business "
            "kama mauzo mengi ni ya pesa ya simu — ni rahisi na wateja wengi wanapendelea. "
            "Linganisha: ada ya kila mwezi, ada ya uhamisho, riba ya mkopo, "
            "na upatikanaji wa ATM karibu nawe. "
            "Fungua akaunti ya biashara tofauti na akaunti yako binafsi — "
            "inasaidia kufuatilia mtiririko wa fedha na kupata mkopo benki."
        ),
        "category": "banking",
        "language": "sw",
    },
    # --- Loans (English) ---
    {
        "instruction": "How can a small business in Tanzania access a loan?",
        "input": "",
        "output": (
            "Options for small business financing in Tanzania: "
            "1. Commercial banks (NMB, CRDB, Equity) — require business registration, "
            "TIN, bank statements, and collateral. Apply for SME loan products. "
            "2. SIDO (Small Industries Development Organisation) — government loans "
            "for small manufacturers and processors. "
            "3. SELF MicroFinance Fund — government-backed microfinance. "
            "4. SACCO (Savings and Credit Cooperative) — member-based savings and loans "
            "with lower interest rates than banks. "
            "5. Mobile lending apps (Timiza, Fuliza equivalents) — small quick loans "
            "but with high interest. Use only for short-term cash flow gaps. "
            "Build your credit history by maintaining a business bank account "
            "with consistent transactions."
        ),
        "category": "financing",
        "language": "en",
    },
    # --- Export/Trade (English) ---
    {
        "instruction": "How do I export products from Tanzania?",
        "input": "",
        "output": (
            "Steps to start exporting from Tanzania: "
            "1. Register as an exporter with Tanzania Revenue Authority (TRA). "
            "2. Obtain an Export License from relevant sector ministry if required. "
            "3. Ensure your product meets the importing country's standards. "
            "4. Work with a licensed freight forwarder for customs clearance. "
            "5. Register with Tanzania Investment Centre (TIC) for incentives. "
            "6. For agricultural exports, get phytosanitary certificate from TPRI. "
            "7. Open a foreign currency account at your bank to receive export payments. "
            "The East African Community (EAC) market offers preferential tariffs "
            "for goods meeting rules of origin requirements."
        ),
        "category": "export",
        "language": "en",
    },
]


def _scrape_forums_for_qa() -> List[dict]:
    """
    Attempt to scrape public Tanzanian business forums for real questions.
    Returns a list of raw {question, context} pairs for conversion.
    Falls back to empty list if scraping fails (network unavailable, blocked, etc.)
    """
    import re
    import time

    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return []

    sources = [
        {
            "name": "JamiiForums_Biashara",
            "url": "https://www.jamiiforums.com/forums/biashara-uchumi-na-siasa.195/",
            "thread_link_pattern": r"/threads/",
        },
    ]

    raw_pairs = []
    headers = {"User-Agent": "AfricaGiantsResearchBot/1.0 (educational; contact: africa-giants)"}

    for source in sources:
        try:
            resp = requests.get(source["url"], headers=headers, timeout=15)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            links = [
                a["href"] for a in soup.find_all("a", href=True)
                if source["thread_link_pattern"] in a["href"]
            ][:10]

            for link in links:
                try:
                    full_url = link if link.startswith("http") else f"https://www.jamiiforums.com{link}"
                    thread_resp = requests.get(full_url, headers=headers, timeout=15)
                    if thread_resp.status_code != 200:
                        continue
                    thread_soup = BeautifulSoup(thread_resp.text, "html.parser")
                    title_tag = thread_soup.find("h1") or thread_soup.find("title")
                    title = title_tag.get_text(strip=True) if title_tag else ""
                    posts = thread_soup.find_all("article", class_=re.compile(r"message"))[:3]
                    context = " ".join(p.get_text(" ", strip=True)[:500] for p in posts)
                    if title and len(context) > 100:
                        raw_pairs.append({"question": title, "context": context})
                    time.sleep(2)
                except Exception:
                    continue
        except Exception:
            continue

    return raw_pairs


def _convert_forum_pair_to_qa(pair: dict) -> Optional[dict]:
    """Convert a raw forum {question, context} into a clean assistant-style training example."""
    question = pair.get("question", "").strip()
    context = pair.get("context", "").strip()

    if not question or len(question) < 15:
        return None

    # Detect language via simple heuristic
    swahili_markers = {"biashara", "kodi", "mauzo", "hesabu", "shirika", "usajili", "wateja"}
    lang = "sw" if any(w in question.lower() for w in swahili_markers) else "en"

    if lang == "sw":
        output = (
            f"Hii ni swali zuri kuhusu biashara Tanzania. "
            f"Kulingana na mazungumzo ya wafanyabiashara: {context[:400]} "
            f"Kwa ushauri wa kina, wasiliana na mtaalamu wa biashara au "
            f"tembelea tovuti rasmi za BRELA (brela.go.tz) au TRA (tra.go.tz)."
        )
    else:
        output = (
            f"This is a relevant business question for Tanzania. "
            f"Based on community discussion: {context[:400]} "
            f"For authoritative guidance, consult BRELA (brela.go.tz), "
            f"TRA (tra.go.tz), or a certified business adviser."
        )

    return {
        "instruction": question,
        "input": "",
        "output": output,
        "category": "community",
        "language": lang,
        "source": "forum",
    }


def build_instruction_dataset(
    include_forums: bool = True,
    output_path: Optional[str] = None,
) -> List[dict]:
    """
    Build the fine-tuning instruction dataset.

    Combines curated seed examples with optionally scraped forum questions.
    Forum context is converted into safe assistant-style responses, NOT raw
    forum continuations (the failure mode from the Codex session).

    Returns the list of examples and writes them to output_path.
    """
    examples = list(SEED_EXAMPLES)

    if include_forums:
        logger.info("Attempting to scrape forum questions for additional training examples...")
        raw_pairs = _scrape_forums_for_qa()
        converted = 0
        for pair in raw_pairs:
            qa = _convert_forum_pair_to_qa(pair)
            if qa:
                examples.append(qa)
                converted += 1
        logger.info("Added %d forum-derived examples", converted)

    # Shuffle deterministically
    random.seed(42)
    random.shuffle(examples)

    if output_path is None:
        processed_dir = get_data_path("processed")
        output_path = os.path.join(processed_dir, "instruction_dataset.jsonl")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    logger.info("Wrote %d instruction examples to %s", len(examples), output_path)
    return examples


if __name__ == "__main__":
    examples = build_instruction_dataset()
    print(f"Built {len(examples)} instruction examples")
