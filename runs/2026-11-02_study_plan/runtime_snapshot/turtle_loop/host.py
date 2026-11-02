"""Private independent label verification; still one public answer per question."""
import json
from .host_context import LABELS
from .providers import APIError

POLICY = 'independent_then_adjudicate_v1'


def answer_question(client, system, payload, review_prompt='', audit=None):
    def call(prompt, data):
        reply = client.complete(prompt, json.dumps(data, ensure_ascii=False))
        if reply.text.strip() not in LABELS:
            raise APIError('Host returned an invalid label; raw response remains in API audit')
        return reply
    verified = payload['active_puzzle'].get('verification_policy') == POLICY
    if verified and not review_prompt:
        raise ValueError('Verified host requires the frozen review prompt')
    primary = call(system, payload)
    if not verified:
        return primary
    # The second call cannot see the first answer. Both see the same complete public history.
    independent = call(system+'\n'+review_prompt, payload)
    candidates = [primary.text.strip(), independent.text.strip()]
    final = independent
    if candidates[0] != candidates[1]:
        final = call(system+'\n'+review_prompt+'\nAdjudicate the candidate labels against the canonical facts. '
                     'They are fallible proposals, not votes or story evidence. Return the correct label, even if neither candidate is correct.',
                     {**payload, 'candidate_labels':candidates})
    if audit:
        audit({'policy':POLICY,'candidate_labels':candidates,'disagreed':candidates[0]!=candidates[1],
               'final_label':final.text.strip(),'calls':2+int(candidates[0]!=candidates[1])})
    return final
