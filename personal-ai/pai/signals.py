"""Feedback signal detection from conversation.

This module answers one question about each user turn: does it tell us
something about how the assistant should have behaved?

DESIGN STANCE: high precision, low recall.

False signals are far more expensive than missed ones. A missed correction
costs nothing -- the user will correct again, and the evidence threshold
needs multiple observations anyway. A *false* correction feeds the learning
loop noise that can become a permanent behavioural rule. So every pattern
here is written to fire only on unambiguous cases, and ambiguous negations
are explicitly excluded.

Signals are ranked by reliability (see SIGNAL_WEIGHT). Reply latency is
deliberately absent: it measures whether the user got distracted, not
whether the response was good.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum


class Signal(str, Enum):
    EXPLICIT_POSITIVE = "explicit_positive"   # hotkey / "exactly", "perfect"
    EXPLICIT_NEGATIVE = "explicit_negative"   # hotkey / "no, that's wrong"
    CORRECTION        = "correction"          # "no, I meant X"
    STYLE_TOO_LONG    = "style_too_long"      # "shorter", "chhota"
    STYLE_TOO_SHORT   = "style_too_short"     # "explain more", "detail me"
    STYLE_TOO_FORMAL  = "style_too_formal"    # "casually", "normal baat karo"
    REPETITION        = "repetition"          # user re-asks the same thing
    ABANDONMENT       = "abandonment"         # topic dropped without ack
    CONTINUATION      = "continuation"        # user engaged further


# Higher = more trustworthy as evidence for a behavioural rule.
SIGNAL_WEIGHT: dict[Signal, float] = {
    Signal.EXPLICIT_POSITIVE: 1.0,
    Signal.EXPLICIT_NEGATIVE: 1.0,
    Signal.CORRECTION:        0.9,
    Signal.STYLE_TOO_LONG:    0.9,
    Signal.STYLE_TOO_SHORT:   0.9,
    Signal.STYLE_TOO_FORMAL:  0.8,
    Signal.REPETITION:        0.5,
    Signal.ABANDONMENT:       0.4,
    Signal.CONTINUATION:      0.2,
}


@dataclass
class Detection:
    signal: Signal
    confidence: float
    matched: str
    lang: str


# --------------------------------------------------------------------------
# Language identification
# --------------------------------------------------------------------------

_DEVANAGARI = re.compile(r"[ऀ-ॿ]")

# Romanised Hindi markers that are unlikely to be English words. Kept short
# and unambiguous on purpose -- "to", "is", "me", "do" are Hindi words too
# but are far more often English, so they are NOT here.
# Romanised Hindi words that are strong evidence of Hindi.
_HI_MARKERS = {
    "hai", "hain", "nahi", "nahin", "kya", "kyun", "kyu", "karo", "karna",
    "karke", "mujhe", "tumhe", "aap", "acha", "accha", "achha", "thik",
    "theek", "bhai", "yaar", "matlab", "samajh", "samjha", "batao", "bata",
    "chahiye", "raha", "rahi", "rahe", "hoga", "hogi", "abhi", "sahi",
    "galat", "phir", "bilkul", "zaroor", "haan", "sirf", "chhota", "chota",
    "bada", "jaldi", "wapas", "dobara", "kaise", "kaha", "bola", "poocha",
    "likho", "bolo", "dekho", "suno", "chalo", "arre", "arey", "kuch",
    "koi", "wala", "wali", "vala", "vali", "mera", "tera", "apna", "hum",
    "tum", "lamba", "zyada", "thoda", "bahut", "bohot", "rakho", "rakh",
    "diya", "kiya", "gaya", "liya", "hua", "hui", "wo", "woh", "ye", "yeh",
    "isko", "usko", "iska", "uska", "mere", "tere", "unka", "jab", "tab",
    "agar", "lekin", "magar", "aur", "ya", "par", "sab", "kabhi", "hamesha",
    # greetings / courtesies -- these are whole turns on their own, so
    # missing them meant an entire class of Hindi smalltalk read as English
    # and would have been spoken by the English voice.
    "namaste", "namaskar", "shukriya", "dhanyavaad", "alvida", "haal",
    "khol", "kholo", "band", "chahta", "chahti", "sakta", "sakti",
    "hona", "hone", "milega", "milegi", "dena", "lena", "yaad",
    # Added after recomputing the language-match metric across every user
    # turn and model reply in rounds 1-3. These are not exotic words; they
    # are among the most common in the corpus, and every one of them was
    # missing. "Simple bol." and "Chal Hinglish mein baat kar." were both
    # classified as ENGLISH because of these gaps (F29, F31).
    #
    # Bare imperative stems -- how people actually give instructions.
    "bol", "dekh", "chal", "soch", "likh", "padh", "samjha", "samjhao",
    "bata", "sunn", "ruk", "ruko", "rakho", "utha", "laa", "de", "le",
    # Pronouns and postpositions that carry real signal.
    "main", "mai", "mein", "mujhse", "tujhe", "tujh", "unko", "inko",
    "hamein", "humein", "tumhara", "tumhari", "tumhare", "kisko", "kiska",
    "kis", "jis", "sabko",
    # Extremely common verb forms.
    "hoon", "hu", "hain", "hota", "hoti", "hote", "karta", "karti",
    "karte", "karna", "kiya", "karunga", "karungi", "jaunga", "jaungi",
    "bolunga", "bolungi", "dunga", "dungi", "lagta", "lagti", "lagte",
    "milta", "milti", "chahta", "padta", "padti",
    # Common nouns and adverbs.
    "baat", "cheez", "chiz", "kaam", "waqt", "samay", "log", "aadmi",
    "bhaiya", "didi", "khana", "paani", "ghar", "dost",
    "abhi", "kabhi", "shayad", "zaroor", "bilkul", "waise", "aise",
    "isliye", "kyunki", "matlab", "yaani", "phir", "wapas", "andar",
    "bahar", "upar", "neeche", "saath", "bina", "tak", "liye",
}

# Romanised Hindi that COLLIDES with common English words. These count as
# neither Hindi evidence nor English evidence -- they are simply ignored.
#
# This third bucket is the fix for a real bug found in testing: excluding
# them from the Hindi set alone made them count as English, so "kya kar
# rahe ho" (pure Hindi) scored as mixed. And including them in the Hindi
# set made "the report is done" score as Hindi. They must be neutral.
_AMBIGUOUS = {
    "the", "is", "me", "to", "do", "so", "he", "she", "in", "on", "at",
    "it", "us", "by", "be", "no", "or", "as", "an", "a", "i",
    "ho", "na", "ki", "ka", "ke", "se", "hi", "kar", "kam", "man", "din",
    "tha", "thi", "ji", "bhi", "bas", "hun", "hu", "haan",
}

# Interjections and acknowledgement tokens that carry NO language signal at
# all. Distinct from _AMBIGUOUS, which is about words that exist in both
# vocabularies; these are words that barely belong to either.
#
# Found by a real conversation (A01, "filler discipline over many tiny
# turns"). The user typed eight one-word turns -- hmm / haan / acha / aur? /
# phir? / ok / hmm / achha -- and "hmm" and "ok" were classified as ENGLISH
# purely because they are Latin letters not on the Hindi list. The router
# then told the model "reply in English only" in the middle of an otherwise
# Hindi conversation, and the model ignored it and answered in Hindi anyway.
# The directive was wrong, so the model disobeying it was the right outcome
# for the wrong reason -- and the language-match metric scored the turn as a
# violation. A filler has no language; the conversation's language holds.
_NEUTRAL = {
    "hmm", "hm", "hmmm", "mm", "mmm", "mhm", "uh", "um", "uhh", "umm",
    "ah", "aah", "oh", "ooh", "eh", "err", "hm", "huh",
    "ok", "okay", "okey", "k", "kk", "oki",
    "lol", "haha", "hahaha", "hehe", "hmmmm",
    # Courtesy and assent tokens. A bare "thanks" does not switch a Hindi
    # conversation into English, and treating it as English evidence is
    # what made A08 turn 3 score as a language violation: "thanks" was
    # classified en, the model was told to reply in English only, and it
    # answered "Kya baat, bhai. Koi aur plan hai aaj?" -- the natural reply,
    # marked wrong by a directive that should never have been issued.
    # Only bare turns are affected: in "thanks for the explanation" the
    # other words still carry the signal.
    "thanks", "thanx", "thx", "ty", "cool", "nice", "great",
    "yeah", "yep", "yup", "sure", "wow", "oops", "ugh", "meh",
}


def detect_language(text: str, default: str = "en") -> str:
    """Return 'hi', 'en', or 'hinglish'.

    Three-way word classification: Hindi-marker / ambiguous / English.
    Unknown Latin words default to English, because English has the far
    larger vocabulary and technical terms in this user's speech are English.

    `default` is returned when the turn carries no language evidence at
    all (a bare filler, a number, an emoji). Callers that track the
    conversation's language should pass it; the standalone default is
    English only because something has to be returned.

    LIMITATION, stated honestly: this is a wordlist heuristic and lands
    around 90% on realistic mixed input. Production should replace it with
    a small statistical LID model, or simply let the conversational model
    tag the turn -- it already read the text. The heuristic exists so the
    deterministic pipeline has a language hint without a model round-trip,
    and so TTS voice routing has a default when the model is not consulted.
    """
    if not text.strip():
        return default
    has_deva = bool(_DEVANAGARI.search(text))
    words = [w for w in re.findall(r"[a-zA-Z]+", text.lower())]

    hi_hits = sum(1 for w in words if w in _HI_MARKERS)
    en_hits = sum(1 for w in words
                  if w not in _HI_MARKERS and w not in _AMBIGUOUS
                  and w not in _NEUTRAL)

    if not has_deva and hi_hits == 0 and en_hits == 0:
        # No evidence either way -- a bare "hmm", "ok", a number, an emoji.
        # Guessing here is worse than inheriting: the caller knows what
        # language the conversation has been in.
        return default

    if has_deva:
        # Devanagari present. Latin content words make it mixed.
        return "hinglish" if en_hits >= 1 else "hi"
    if hi_hits == 0:
        return "en"
    return "hinglish" if en_hits >= 1 else "hi"


# --------------------------------------------------------------------------
# Patterns
# --------------------------------------------------------------------------

def _p(*alts: str) -> re.Pattern:
    return re.compile("|".join(alts), re.IGNORECASE | re.UNICODE)


# Explicit approval. Must be assertive -- "ok" and "thanks" are politeness,
# not endorsement, and treating them as endorsement is how a system learns
# that everything it does is fine.
POSITIVE = _p(
    r"\bexactly\b", r"\bperfect\b", r"\bthat'?s (it|right|perfect)\b",
    r"\bwell (put|said)\b", r"\bnailed it\b", r"\bmuch better\b",
    r"\bbilkul sahi\b", r"\bekdum sahi\b", r"\bsahi (hai|bola)\b",
    r"\byahi chahiye tha\b", r"\bab (theek|thik) hai\b",
    r"बिल्कुल सही", r"यही चाहिए था", r"सही है",
)

# Explicit rejection. Bare "no" is excluded -- see NEGATION_EXCLUSIONS.
NEGATIVE = _p(
    r"\bthat'?s (wrong|not right|incorrect)\b", r"\bthat'?s not what i\b",
    r"\byou'?re wrong\b", r"\bnot helpful\b", r"\bthis is useless\b",
    r"\bgalat (hai|bola|hai ye)\b", r"\bye galat hai\b",
    r"\bsahi nahi hai\b", r"\bmatlab nahi\b",
    r"गलत है", r"सही नहीं",
)

CORRECTION = _p(
    r"\bno,? i meant\b", r"\bi meant\b", r"\bnot (that|what i)\b",
    r"\bactually,? i\b", r"\bi said\b", r"\bthat'?s not what i (meant|asked)\b",
    r"\bmaine (ye|yeh|wo|woh)? ?nahi (kaha|bola|poocha)\b",
    r"\bmera matlab\b", r"\bmatlab ye tha\b", r"\bmaine kaha tha\b",
    r"मेरा मतलब", r"मैंने .{0,12}नहीं (कहा|बोला|पूछा)",
)

TOO_LONG = _p(
    r"\b(be |keep it |make it |just )?(shorter|briefer|concise|brief|simpler)\b",
    r"\bkeep it simple\b", r"\bsimplify\b",
    r"\btoo (long|verbose|much|detailed)\b", r"\bstop explaining\b",
    r"\bdon'?t (over-?explain|ramble|write so much)\b",
    r"\bin (one|a) (line|sentence)\b",
    r"\btl;?dr\b", r"\bget to the point\b", r"\bless words\b",
    # Hindi / Hinglish. Found by the end-to-end learning test: the phrase
    # "itna bada answer mat do. simple bol." produced NO candidate rule,
    # because the patterns had "itna lamba" (long) but not "itna bada"
    # (big), and nothing for "simple bol" at all. That is the single most
    # natural way this user actually asks for brevity.
    r"\bchh?ota (rakho|karo|kar|likho)\b",
    r"\bitna (lamba|bada|lamba-chauda|detail) (mat|nahi)\b",
    # The QUESTION form. Round 2, M04 t2: "Arre itna bada answer kyun de
    # raha hai?" produced no signal at all, because every Hindi pattern
    # here assumed an imperative ("mat do") and he asked it as a complaint.
    # It is one of the thirty mandatory probes and the detector was deaf to
    # it -- the same shape of miss as F12, one phrasing over.
    r"\bitna (lamba|bada|bda|lamba-chauda) (answer|jawab|reply)?\s*kyun\b",
    r"\b(kyun|kyu) itna (lamba|bada)\b",
    r"\bitna (lamba|bada)\b.{0,20}\?",
    r"\b(bada|lamba|lamba-chauda) (answer|jawab|reply)? ?mat (do|likho|bolo)\b",
    r"\bsimple (bol|bolo|batao|rakho|likho|karo)\b",
    r"\bshort (me|mein) (bol|batao|likho)\b",
    r"\bkam (bolo|likho|shabdon)\b", r"\bsirf (point|matlab|kaam ki baat)\b",
    r"\bek line me\b", r"\bzyada (mat|nahi) (bol|likh)\b",
    r"\bitna explain mat\b", r"\bbas itna\b",
    r"छोटा (रखो|करो)", r"इतना (लंबा|बड़ा)", r"एक लाइन में",
    r"सरल (बोलो|बताओ)", r"कम (बोलो|लिखो)",
)

TOO_SHORT = _p(
    r"\b(explain|elaborate) (more|further|in detail)\b",
    r"\bmore detail\b", r"\bgo deeper\b", r"\btoo (short|brief|terse)\b",
    r"\bcan you expand\b", r"\bthoda (detail|vistaar) (me|mein)\b",
    r"\bdetail me batao\b", r"\bthoda aur\b", r"\bpoora batao\b",
    # "isko detail mein explain kar" -- the natural Hinglish request for
    # more, and the exact phrasing used in mandatory conversation M05.
    r"\bdetail (me|mein) (explain|bata|batao|samjha|samjhao|likh)\b",
    r"\b(vistaar|detail) (me|mein)\b", r"\baur (batao|bata|likho)\b",
    r"विस्तार से", r"थोड़ा और", r"पूरा बताओ",
)

TOO_FORMAL = _p(
    r"\b(be |talk |speak )?(more )?casual(ly)?\b", r"\bless formal\b",
    r"\b(don'?t|stop|quit) (be|being|sounding|talking) (so |too )?formal\b",
    r"\bstop (being|sounding) like (a|an) (robot|ai|assistant)\b",
    r"\brelax\b(?!ing)",
    r"\bnormal (baat|se) (karo|bolo)\b", r"\bitna formal (mat|nahi)\b",
    r"\bdost ki tarah\b",
    # "simple bolo" was here AND in TOO_LONG, so it double-counted as two
    # signals from one utterance and inflated the evidence. Brevity is the
    # likelier reading, so TOO_LONG keeps it.
    r"इतना formal", r"आम भाषा",
)

# Contexts where a negation word appears but is NOT feedback about the
# assistant's behaviour. Without these the detector fires on ordinary
# conversation and manufactures rules out of nothing.
NEGATION_EXCLUSIONS = _p(
    r"\bno (idea|clue|problem|worries|thanks|thank you)\b",
    r"\bnot (sure|really|yet|now)\b",
    r"\bnahi (pata|maloom|chahiye|jaana|karna)\b",
    r"\bpata nahi\b", r"\bmaloom nahi\b",
    r"पता नहीं", r"मालूम नहीं",
    r"\bno\b[,.]?\s*(i'?m |it'?s )?(fine|good|ok|okay)\b",
)


def detect(user_text: str) -> list[Detection]:
    """Detect feedback signals in a single user turn."""
    text = unicodedata.normalize("NFC", user_text.strip())
    lang = detect_language(text)
    out: list[Detection] = []

    excluded = bool(NEGATION_EXCLUSIONS.search(text))

    def add(sig: Signal, pat: re.Pattern, conf: float, respect_exclusion=False):
        m = pat.search(text)
        if m and not (respect_exclusion and excluded):
            out.append(Detection(sig, conf, m.group(0), lang))

    add(Signal.STYLE_TOO_LONG,   TOO_LONG,   0.90)
    add(Signal.STYLE_TOO_SHORT,  TOO_SHORT,  0.90)
    add(Signal.STYLE_TOO_FORMAL, TOO_FORMAL, 0.80)
    add(Signal.CORRECTION,       CORRECTION, 0.85, respect_exclusion=True)
    add(Signal.EXPLICIT_NEGATIVE, NEGATIVE,  0.90, respect_exclusion=True)
    add(Signal.EXPLICIT_POSITIVE, POSITIVE,  0.90)

    # A style complaint IS a correction; don't double-count it as a separate
    # generic correction signal, which would inflate evidence.
    kinds = {d.signal for d in out}
    if kinds & {Signal.STYLE_TOO_LONG, Signal.STYLE_TOO_SHORT,
                Signal.STYLE_TOO_FORMAL}:
        out = [d for d in out if d.signal is not Signal.CORRECTION]
    return out


def detect_repetition(prev_user: str, curr_user: str, threshold: float = 0.7) -> bool:
    """Did the user re-ask essentially the same thing? Implicit dissatisfaction."""
    a = set(re.findall(r"\w+", prev_user.lower()))
    b = set(re.findall(r"\w+", curr_user.lower()))
    if len(a) < 3 or len(b) < 3:
        return False
    jaccard = len(a & b) / len(a | b)
    return jaccard >= threshold
