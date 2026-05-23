import os
import json
import re
from typing import List
from src.common.logging import get_logger
from src.common.storage import get_data_path
from src.common.schemas import CleanedDocument, QAPair
from src.common.secrets import get_openai_api_key

logger = get_logger("synthetic_generator")

def generate_heuristic_qa(doc: CleanedDocument) -> List[QAPair]:
    """Generates synthetic instruction-tuning pairs using rule-based parsing of the text."""
    qa_pairs = []
    content = doc.cleaned_content
    sentences = re.split(r'(?<=[.!?])\s+', content)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 40:
            continue
            
        # Look for facts or definitions in the text to formulate basic Q&A
        # Swahili patterns
        if doc.language == "sw":
            if "kodi" in sentence.lower() or "asilimia" in sentence.lower():
                instruction = "Kiwango cha kodi au utaratibu wa kodi ni upi kulingana na sheria ya Tanzania?"
                qa_pairs.append(QAPair(
                    instruction=instruction,
                    input=sentence,
                    output=f"Kulingana na maelezo yaliyotolewa: {sentence}",
                    source_doc_id=doc.doc_id,
                    category="tax"
                ))
            elif "usajili" in sentence.lower() or "brela" in sentence.lower():
                instruction = "Ni mahitaji gani ya usajili wa biashara au kampuni nchini Tanzania?"
                qa_pairs.append(QAPair(
                    instruction=instruction,
                    input=sentence,
                    output=f"Mahitaji ya usajili ni kama ifuatavyo: {sentence}",
                    source_doc_id=doc.doc_id,
                    category="registration"
                ))
        # English patterns
        else:
            if "tax" in sentence.lower() or "%" in sentence.lower() or "percent" in sentence.lower():
                instruction = "What is the tax rate or compliance regulation mentioned?"
                qa_pairs.append(QAPair(
                    instruction=instruction,
                    input=sentence,
                    output=f"According to the guidelines: {sentence}",
                    source_doc_id=doc.doc_id,
                    category="tax"
                ))
            elif "registration" in sentence.lower() or "brela" in sentence.lower() or "incorporate" in sentence.lower():
                instruction = "What are the company incorporation or business registration requirements in Tanzania?"
                qa_pairs.append(QAPair(
                    instruction=instruction,
                    input=sentence,
                    output=f"The company incorporation details are: {sentence}",
                    source_doc_id=doc.doc_id,
                    category="registration"
                ))

    # Add a fallback generic question if no custom categories matched
    if not qa_pairs:
        instruction = "Summarize the key business or regulatory facts mentioned in this document." if doc.language == "en" else "Eleza kwa muhtasari mambo muhimu ya kibiashara au kisheria yaliyotajwa hapa."
        qa_pairs.append(QAPair(
            instruction=instruction,
            input=content[:300],
            output=content,
            source_doc_id=doc.doc_id,
            category="general"
        ))

    return qa_pairs

def generate_llm_qa(doc: CleanedDocument, api_key: str) -> List[QAPair]:
    """Generates synthetic Q&A pairs using OpenAI API."""
    import openai
    client = openai.OpenAI(api_key=api_key)
    
    prompt = f"""
You are an expert on Tanzanian business, tax regulations, company registry laws, and financial policies.
Generate 3 high-quality instruction-following training Q&A pairs in { 'Swahili' if doc.language == 'sw' else 'English' } based ONLY on the text block below.
Format your output as a valid JSON list of objects containing 'instruction', 'input', and 'output' fields.
The 'instruction' should be a natural query a business owner might ask.
The 'input' should be the relevant context block from the source text (if needed, otherwise leave empty).
The 'output' must be a professional, accurate response.

Source text:
\"\"\"{doc.cleaned_content}\"\"\"
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        result_dict = json.loads(response.choices[0].message.content)
        # Handle cases where the JSON structure is wrapped
        pairs_data = result_dict.get("pairs", result_dict.get("qa_pairs", list(result_dict.values())[0]))
        
        qa_pairs = []
        for pair in pairs_data:
            qa_pairs.append(QAPair(
                instruction=pair["instruction"],
                input=pair.get("input", ""),
                output=pair["output"],
                source_doc_id=doc.doc_id,
                category="regulatory"
            ))
        return qa_pairs
    except Exception as e:
        logger.error(f"Failed to generate LLM QA for {doc.doc_id}: {e}. Falling back to heuristic.")
        return generate_heuristic_qa(doc)

def generate_synthetic_dataset(documents: List[CleanedDocument]) -> List[QAPair]:
    """Generates the entire synthetic training dataset from cleaned documents."""
    raw_key = get_openai_api_key()
    # Treat placeholder values as no key
    api_key = raw_key if (raw_key and raw_key.startswith("sk-")) else ""
    dataset = []

    for doc in documents:
        if api_key:
            logger.info(f"Generating LLM-based synthetic QA for document {doc.doc_id}...")
            pairs = generate_llm_qa(doc, api_key)
        else:
            logger.info(f"Generating heuristic-based synthetic QA for document {doc.doc_id}...")
            pairs = generate_heuristic_qa(doc)
            
        dataset.extend(pairs)
        
    synthetic_dir = get_data_path("synthetic")
    filepath = os.path.join(synthetic_dir, "synthetic_training_data.jsonl")
    
    with open(filepath, "w", encoding="utf-8") as f:
        for pair in dataset:
            f.write(json.dumps(pair.dict(), ensure_ascii=False) + "\n")
            
    logger.info(f"Generated {len(dataset)} synthetic Q&A pairs and saved to {filepath}")
    return dataset
