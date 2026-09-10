# Aspect Taxonomy — `aspect-svc`

This document defines 6 aspect categories and provides explicit definitions and examples for each.
Refer to these definitions when performing manual annotations for `gold_set.jsonl` or writing prompts for LLMs. Ambiguity in these definitions guarantees lower inter-annotator agreement (low Kappa score).

> **Status:** ✅ Approved (non-draft). 100+ reviews reviewed, 300 gold samples fully annotated, and definitions refined based on real disagreement cases identified during a two-stage Cohen's Kappa evaluation (see below). Further modifications require explicit team agreement (see project rules on frozen artifacts).

---

## 1. `delivery` — Delivery Process

**Definition:** Any statement related to the physical fulfillment of the order: speed, delay, courier behavior, shipping fee (if explicitly mentioned), or delivery location accuracy. Refers to the **fulfillment process**, not the product itself.

**Positive Examples:**
1. "Delivery was extremely fast, arrived the very next day."
2. "The courier delivered on time and was very polite."
3. "The order arrived exactly at the scheduled time."

**Negative Examples:**
1. "Delivery was delayed by 2 weeks."
2. "The courier couldn't find the address, so the product was sent back."
3. "The order was incorrectly routed to a branch in another city."
4. "I placed an order, but it still hasn't arrived" (culprit not explicitly specified — see the "Edge Case: Order Not Arrived" section below).

---

## 2. `quality` — Product Quality

**Definition:** Statements regarding the physical product itself — manufacturing quality, durability, compliance with described features, or premature defects/damage.

**Positive Examples:**
1. "The product is very sturdy, no defects whatsoever."
2. "Quality is just as shown in the picture, even better."
3. "I've been using it for a month, still in excellent condition."

**Negative Examples:**
1. "Stopped working on the second day."
2. "Material is very low quality, tore quickly."
3. "Completely different from the product shown in the picture."

---

## 3. `price` — Pricing & Value

**Definition:** Any opinion on the price/value proposition — expensive, cheap, discount savings, or "value-for-money" assessment. Excludes delivery fees (which belong to `delivery`).

**Positive Examples:**
1. "Great choice for this price, highly recommended."
2. "Very glad I bought it with a discount."
3. "Cheap relative to this level of quality."

**Negative Examples:**
1. "Price does not match the quality, way too expensive."
2. "Much cheaper in other stores."
3. "Price doubled after the discount ended."

---

## 4. `seller` — Seller & Customer Service

**Definition:** Communication, service, warranty/return policy, or seller responsiveness associated with the specific merchant. Refers to the **specific seller**, not the platform overall (e.g., Uzum).

**Positive Examples:**
1. "The seller answered my questions promptly."
2. "When an issue arose, the seller replaced it immediately."
3. "The seller was very polite and helpful."

**Negative Examples:**
1. "The seller is completely ignoring messages."
2. "When asked about the warranty, the seller avoided responsibility."
3. "It has been a week since I submitted a complaint, still no response."

> ⚠️ **Edge Case: `seller` vs. `delivery`** — `seller` showed the lowest self-agreement in the Kappa verification (Kappa = 0.479). Manual review of the disagreement cases revealed the confusion was primarily with `delivery`. Rule: **If the order did not arrive or was lost, and no culprit is explicitly mentioned in the text, tag strictly as `delivery`.** Include `seller` only if there is explicit mention of **direct seller communication** (messaging, waiting for a response) or **warranty/replacement policies**.
>
> Example: *"I paid for it, but my order wasn't delivered"* → `delivery` only (responsibility unclear).  
> Example: *"I wrote to the seller, but they didn't reply"* → `delivery` + `seller` (communication explicitly noted).
>
> **Note — Do not over-apply this restriction:** If requesting a product **replacement or return** and experiencing a rejection or difficulty ("they told me to ask the seller", "they refused to exchange it"), this falls under **warranty/replacement policy**, meaning `seller` must be added even if the primary defect relates to product `quality`. Leave out `seller` only when the order is lost/undelivered without any interaction attempt.
>
> Example: *"I came to return the watch... they told me to ask the seller"* → `quality` + `seller` (exchange requested and redirected — both apply).

---

## 5. `packaging` — Packaging Condition

**Definition:** Condition of the physical package/box upon arrival — external appearance, or whether the packaging adequately protected the item. A less frequent but important category for quality monitoring.

**Positive Examples:**
1. "Packaging was very solid, nothing was damaged."
2. "The box contained extra protective material, very well thought out."
3. "Beautifully packaged, suitable for a gift."

**Negative Examples:**
1. "The box was torn and the product inside was crushed."
2. "Sent without a box, just wrapped in a bag."
3. "The box was soaked, which affected the item inside."
4. "The pouch is very compact, saved space in my suitcase." (⚠️ In real annotations, this was occasionally misclassified under `quality`/`other`. If "bag/packaging" is explicitly mentioned, consider `packaging` first, even if stated casually).

---

## 6. `other` — General & Miscellaneous

**Definition:** Meaningful statements that do not explicitly fit any of the 5 categories above (e.g., overall experience, app/interface feedback, or comments unrelated to specific product attributes).

> ⚠️ **Edge Case: `other` vs. `quality`** — Showed high disagreement during Kappa audits (Kappa = 0.44). Former approach relied on "short review → `other`", but **content, not length**, must be the deciding factor.
>
> **Revised Rule:** If a review is short but refers to the **product itself** positively/negatively ("good", "awesome", "works well", "didn't like it") — tag as **`quality`**, regardless of length. Tag as `other` **only when the review lacks any specific anchor** (e.g., "thanks", "super", "5 stars" — where it is impossible to determine whether it refers to product, price, delivery, seller, or packaging).
>
> Example: *"Effect was noticeable, awesome"* → `quality` (refers to product efficacy).  
> Example: *"Everything is great, thanks!"* → `other` (unclear what "everything" refers to).

---

## Note on Multi-Label Classification

A single review can contain multiple aspects and **does not require uniform sentiment polarity across aspects**.  
Example: *"Delivery was fast, but product quality was poor"* → `delivery: positive`, `quality: negative`.

---

## Kappa Verification Audit Summary

**Stage 1 (50 random samples):**

| Aspect | Kappa | Assessment |
|---|---|---|
| delivery | 0.898 | Excellent |
| price | 0.778 | Good |
| packaging | 0.778 | Good |
| quality | 0.674 | Satisfactory |
| seller | 0.479 | Low — guideline refined |
| other | 0.440 | Low — guideline refined |

**Stage 2 (20 targeted samples for `seller`/`other` edge cases):** Raw agreement score appeared low (seller=0.219, other=0.259). Manual analysis revealed this was caused by systematic re-annotations under updated guidelines rather than taxonomy ambiguity (7 samples correctly shifted from `other` to `quality`). Note: because the annotation standard was deliberately changed between Stage 1 and Stage 2, this comparison is not a strict repeat-annotation agreement test — a kappa drop here was expected and does not by itself indicate remaining ambiguity.

**Conclusion:** The taxonomy definitions are sufficiently precise and consistent for modeling and annotation pipelines.