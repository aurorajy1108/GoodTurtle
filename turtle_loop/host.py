"""One host generation per question; transport retries remain provider-owned."""
import json
import re
from dataclasses import replace
from .host_context import LABELS
from .providers import APIError

POLICY = 'single'


def normalize_host_label(raw):
    """Envelope-only normalization; never infer a label from an explanation."""
    if not isinstance(raw,str) or not raw.strip() or len(raw)>128:return None
    text=raw.strip().lower()
    if text in LABELS:return text
    text=re.sub(r'^(?:exactly|answer|label)\s*:?\s*','',text,count=1)
    if len(text)>1 and text[0]==text[-1] and text[0] in ('"',"'",'`'):
        text=text[1:-1].strip()
    for label in LABELS:
        token=(r'(?:yes\s+and\s+no|yes\s*&\s*no)' if label=='yes and no' else re.escape(label))
        # Repeated identical labels are harmless. Distinct labels or any other
        # substantive word fail this whole-string match.
        if re.fullmatch(token+r'(?:[\s.,;:!?]+'+token+r'){0,7}[\s.,;:!?]*',text):return label
    return None


def answer_question(client, system, payload, review_prompt='', audit=None, returned_reply=None):
    def call(prompt, data):
        reply = returned_reply if returned_reply is not None else client.complete(prompt, json.dumps(data, ensure_ascii=False))
        label=normalize_host_label(reply.text)
        if label is None:
            raise APIError('Host returned an invalid label; raw response remains in API audit')
        return replace(reply,text=label),reply.text
    primary,raw = call(system, payload)
    # Historical packs retain their provenance, including the old verification
    # setting. Runtime policy overrides it; never spend a second judgment call.
    if audit:
        audit({'policy':POLICY, 'candidate_labels':[primary.text.strip()],
               'disagreed':False, 'final_label':primary.text.strip(), 'calls':0 if returned_reply else 1,
               'raw_label':raw,'format_normalized':raw.strip()!=primary.text})
    return primary
