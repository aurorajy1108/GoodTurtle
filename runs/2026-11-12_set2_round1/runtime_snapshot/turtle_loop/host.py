"""One host generation per question; transport retries remain provider-owned."""
import json
from .host_context import LABELS
from .providers import APIError

POLICY = 'single'


def answer_question(client, system, payload, review_prompt='', audit=None):
    def call(prompt, data):
        reply = client.complete(prompt, json.dumps(data, ensure_ascii=False))
        if reply.text.strip() not in LABELS:
            raise APIError('Host returned an invalid label; raw response remains in API audit')
        return reply
    primary = call(system, payload)
    # Historical packs retain their provenance, including the old verification
    # setting. Runtime policy overrides it; never spend a second judgment call.
    if audit:
        audit({'policy':POLICY, 'candidate_labels':[primary.text.strip()],
               'disagreed':False, 'final_label':primary.text.strip(), 'calls':1})
    return primary
