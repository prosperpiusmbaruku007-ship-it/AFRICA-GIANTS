"""
Africa Giants — Gradio web interface for HuggingFace Spaces deployment.

Provides a bilingual (Swahili/English) chat interface backed by the
fine-tuned Afrique Llama model with RAG retrieval.

Deploy: push this file to prospAprospA007/africa-giants-app (Space, SDK=Gradio).
"""
import os
import requests

import gradio as gr

API_URL = os.environ.get("AFRICA_GIANTS_API_URL", "http://localhost:8000")
API_KEY = os.environ.get("AFRICA_GIANTS_API_KEY", "")

SYSTEM_PROMPT = (
    "Wewe ni Africa Giants, mshauri wa biashara Tanzania. "
    "Jibu maswali kuhusu biashara, kodi, usajili, uhasibu, masoko, na fedha "
    "kwa Kiswahili au Kiingereza. Toa hatua za vitendo na ushauri unaotekelezeka. "
    "Ukitumia chanzo rasmi, taja chanzo hicho.\n\n"
    "You are Africa Giants, a Tanzanian business assistant. "
    "Answer questions about business registration, tax, bookkeeping, marketing, "
    "financing, and trade in Swahili or English. "
    "Give practical, actionable advice. Cite official sources when available."
)

EXAMPLES = [
    ["Ninaanzaje biashara rasmi Tanzania?"],
    ["How do I register a company with BRELA?"],
    ["Nifanye nini kuweka hesabu za duka dogo?"],
    ["What taxes does a small business pay in Tanzania?"],
    ["Nawezaje kupata wateja zaidi kwa biashara ndogo?"],
    ["How can I access a business loan in Tanzania?"],
]


def _call_rag_chat(message: str, history: list) -> str:
    """Call the /rag/chat endpoint on the inference server."""
    payload = {
        "message": message,
        "history": [{"role": r, "content": c} for r, c in history],
        "system_prompt": SYSTEM_PROMPT,
    }
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    try:
        resp = requests.post(f"{API_URL}/rag/chat", json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response") or data.get("answer") or "Samahani, jibu halipatikani sasa hivi."
    except requests.exceptions.ConnectionError:
        return (
            "⚠️ Huduma ya AI haipatikani sasa hivi. Tafadhali jaribu tena baadaye.\n"
            "⚠️ AI service is currently unavailable. Please try again later."
        )
    except Exception as e:
        return f"Kosa: {str(e)}"


def _submit_feedback(message: str, response: str, rating: int, correction: str) -> str:
    """Submit user feedback to the inference server."""
    payload = {
        "question": message,
        "model_response": response,
        "rating": rating,
        "correction": correction if correction.strip() else None,
    }
    try:
        resp = requests.post(f"{API_URL}/feedback", json=payload, timeout=10)
        resp.raise_for_status()
        return "Asante! Maoni yako yamehifadhiwa. / Thank you! Your feedback has been saved."
    except Exception:
        return "Imeshindwa kuhifadhi maoni. / Failed to save feedback."


def chat(message: str, history: list) -> tuple[str, list]:
    if not message.strip():
        return "", history
    response = _call_rag_chat(message, history)
    history.append((message, response))
    return "", history


with gr.Blocks(
    title="Africa Giants — Mshauri wa Biashara Tanzania",
    theme=gr.themes.Soft(primary_hue="green"),
) as demo:
    gr.Markdown(
        """
        # 🌍 Africa Giants
        ### Mshauri wa Biashara Tanzania | Tanzanian Business Assistant

        Uliza swali lolote kuhusu biashara Tanzania — usajili, kodi, uhasibu, masoko, mikopo.
        Ask any question about business in Tanzania — registration, tax, bookkeeping, marketing, loans.
        """
    )

    chatbot = gr.Chatbot(height=450, label="Africa Giants Chat")
    msg_input = gr.Textbox(
        placeholder="Andika swali lako hapa... / Type your question here...",
        label="Swali / Question",
        lines=2,
    )

    with gr.Row():
        submit_btn = gr.Button("Tuma / Send", variant="primary")
        clear_btn = gr.Button("Futa / Clear")

    gr.Examples(
        examples=[[ex[0]] for ex in EXAMPLES],
        inputs=msg_input,
        label="Mifano ya Maswali / Example Questions",
    )

    gr.Markdown("---")
    gr.Markdown("### Maoni / Feedback")

    with gr.Row():
        feedback_msg = gr.Textbox(label="Swali lako / Your question", interactive=False)
        feedback_resp = gr.Textbox(label="Jibu la AI / AI response", interactive=False)

    rating_slider = gr.Slider(1, 5, value=3, step=1, label="Kiwango / Rating (1=Mbaya, 5=Bora)")
    correction_box = gr.Textbox(
        placeholder="Jibu bora lingekuwa... / A better answer would be...",
        label="Marekebisho (si lazima) / Correction (optional)",
        lines=3,
    )
    feedback_btn = gr.Button("Wasilisha Maoni / Submit Feedback")
    feedback_status = gr.Textbox(label="", interactive=False)

    # Wire up events
    last_question = gr.State("")
    last_response = gr.State("")

    def on_submit(message, history):
        new_msg, new_history = chat(message, history)
        last_q = message
        last_r = new_history[-1][1] if new_history else ""
        return new_msg, new_history, last_q, last_r, last_q, last_r

    submit_btn.click(
        on_submit,
        inputs=[msg_input, chatbot],
        outputs=[msg_input, chatbot, last_question, last_response, feedback_msg, feedback_resp],
    )
    msg_input.submit(
        on_submit,
        inputs=[msg_input, chatbot],
        outputs=[msg_input, chatbot, last_question, last_response, feedback_msg, feedback_resp],
    )
    clear_btn.click(lambda: ([], "", ""), outputs=[chatbot, last_question, last_response])

    feedback_btn.click(
        _submit_feedback,
        inputs=[feedback_msg, feedback_resp, rating_slider, correction_box],
        outputs=[feedback_status],
    )

    gr.Markdown(
        """
        ---
        *Built in Africa. For Africa. By Africa.*
        Model: McGill-NLP/AfriqueLlama-8B fine-tuned on Tanzanian business data.
        """
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
