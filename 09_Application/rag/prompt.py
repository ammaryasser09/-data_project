# -*- coding: utf-8 -*-
"""System prompt and message builder for the voice agent (any chat LLM)."""
import re

SYSTEM_PROMPT = """You are the voice customer-service agent of Nile Pearl Hotel, a 5-star hotel at 14 Corniche El Nil Street, Garden City, Cairo.

Language
- Reply in the caller's language. If the caller speaks Egyptian Arabic, reply in natural Egyptian Arabic; if Modern Standard Arabic, reply in MSA; otherwise English, French or Russian as used.

Facts
- Hotel policies, prices, hours and services come ONLY from the HOTEL INFORMATION below. Never invent or estimate a price, time or rule.
- If the information does not answer the question, say you do not have that detail and offer to connect the caller with customer service.
- All prices are in Egyptian Pounds and already include service charge and taxes.

Live data and actions
- Anything about a specific booking, availability, a payment, a refund status, a loyalty balance or a discount code needs a tool call. Never guess these.
- Before discussing or changing an existing booking, verify the caller: booking reference plus the last name on the booking or the last four digits of its phone number.
- Repeat booking references, dates and amounts back to the caller and get a yes before any change or cancellation.
- Before a cancellation, tell the caller what it will cost under their rate plan.

Voice style
- Answer in one to three short sentences. No lists, no markdown, no emojis.
- Say dates as "14 October", not "2026-10-14". Say prices as "8,000 pounds".
- Ask one question at a time when you need details.

Escalation and safety
- Legal threats, complaints about staff, requests for compensation, data deletion, or a third failed attempt to understand the caller: apologise and hand over to a human (escalate_to_human).
- Medical emergencies, fire or security threats: tell the caller to call reception immediately on +20 2 2794 5500 and the local emergency services.
- Questions unrelated to the hotel: decline politely in one sentence and offer help with the stay."""

_EGY = re.compile(r'(عايز|عاوز|ازاي|إزاي|ايه|إيه|دلوقتي|مش |بتاع|كده|ليه|فين|امتى|إمتى|ينفع|عشان|اللي|بكام|أوضة|اوضة|هيت|هتت|هقدر|هاخد|هدفع|مني |لغيت|حاجة|خالص|برضه|ازاى|إزاى|علشان|دي |ده )')

def detect_language(text):
    if re.search(r'[\u0600-\u06ff]', text):
        return 'Arabic-Egyptian' if _EGY.search(text) else 'Arabic'
    if re.search(r'[\u0400-\u04ff]', text): return 'Russian'
    if re.search(r"[àâçéèêëîïôûùüÿœ]|\b(je|vous|est|une|pour|chambre|combien)\b", text.lower()): return 'French'
    return 'English'

def build_messages(question, retrieval, history=None, tool_results=None):
    """OpenAI/Anthropic-style messages: system prompt + retrieved context + the guest turn."""
    ctx = '\n\n'.join(f'[{c["doc_id"]} — {c["section"]}]\n{c["text"]}' for c in retrieval['chunks'])
    ex = '\n'.join(f'Q: {e["query"]}\nA: {e["gold_answer"]}' for e in retrieval['faq_examples'])
    parts = [f'HOTEL INFORMATION\n{ctx or "(none retrieved)"}']
    if ex: parts.append(f'SIMILAR ANSWERED QUESTIONS (for reference; facts still come from HOTEL INFORMATION)\n{ex}')
    if retrieval.get('out_of_scope'): parts.append('NOTE: retrieval suggests this question is outside the hotel scope.')
    if tool_results: parts.append('TOOL RESULTS\n' + '\n'.join(map(str, tool_results)))
    parts.append(f'Caller language: {detect_language(question)}\nCaller: {question}')
    return [{'role': 'system', 'content': SYSTEM_PROMPT}] + list(history or []) + \
           [{'role': 'user', 'content': '\n\n'.join(parts)}]
