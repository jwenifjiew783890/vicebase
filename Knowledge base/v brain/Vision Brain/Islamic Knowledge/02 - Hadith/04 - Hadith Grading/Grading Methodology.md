---
type: Policy
category: Hadith grading
retrieved_at: 2026-09-03
---

# Hadith Grading Methodology

How gradings are recorded in this library, and what the numbers below actually mean.

> [!danger] This library never grades a hadith itself.
> Every grading below was imported verbatim from the source dataset and is attributed to
> the scholar the dataset names. No grading is inferred, generalised, or invented.

## Coverage by collection

| Collection | Narrations in source | Carrying a grading | Graded by |
| --- | ---: | ---: | --- |
| Sahih al-Bukhari | 7,589 | 0 | none |
| Sahih Muslim | 7,563 | 0 | none |
| Sunan Abi Dawud | 5,274 | 5,274 | Al-Albani, Zubair Ali Zai, Muhammad Muhyi Al-Din Abdul Hamid, Shuaib Al Arnaut |
| Jami' al-Tirmidhi | 3,998 | 3,954 | Zubair Ali Zai, Al-Albani, Ahmad Muhammad Shakir, Bashar Awad Maarouf |
| Sunan an-Nasa'i | 5,765 | 5,676 | Al-Albani, Abu Ghuddah, Zubair Ali Zai |
| Sunan Ibn Majah | 4,343 | 4,341 | Zubair Ali Zai, Muhammad Fouad Abd al-Baqi, Al-Albani, Shuaib Al Arnaut |
| Muwatta Malik | 1,858 | 1,840 | Salim al-Hilali |
| Forty Hadith of an-Nawawi | 42 | 0 | none |
| Forty Hadith Qudsi | 40 | 0 | none |

## Why Sahih al-Bukhari and Sahih Muslim show no grading

Both import with **zero per-hadith external gradings**. That is a property of the source
data, not an oversight, and it must not be 'corrected' by adding gradings.

Al-Bukhari and Muslim each compiled to their own stated conditions of authenticity, and
these two works have been broadly received by the scholars of hadith on that basis, so
per-narration external grading is not how they are ordinarily annotated. Where a specific
narration in them has been discussed by later scholars, that discussion belongs in its own
sourced note - never stamped silently onto the hadith.

**An empty grading field means: the source supplied no grading.** Nothing more.

## Graders present in this corpus

| Grader | Gradings attributed |
| --- | ---: |
| Al-Albani | 19,081 |
| Zubair Ali Zai | 19,033 |
| Shuaib Al Arnaut | 6,413 |
| Abu Ghuddah | 5,692 |
| Muhammad Muhyi Al-Din Abdul Hamid | 5,171 |
| Muhammad Fouad Abd al-Baqi | 4,314 |
| Ahmad Muhammad Shakir | 3,729 |
| Bashar Awad Maarouf | 2,425 |
| Salim al-Hilali | 1,858 |

## Grade values actually present

Reproduced exactly as the source wrote them. Note the spread: this corpus is **not**
uniformly authentic - roughly 11,425 gradings in it contain *Da'if* (weak).

| Grade, as written in source | Count |
| --- | ---: |
| Sahih | 32,909 |
| Daif | 9,937 |
| Hasan | 5,631 |
| Hasan Sahih | 3,425 |
| Sahih - Agreed Upon | 2,002 |
| Isnaad Hasan | 1,940 |
| Isnaad Sahih | 1,916 |
| Sahih Muslim | 1,574 |
| Sahih Lighairihi | 903 |
| Sahih Isnaad | 875 |
| Daif Isnaad | 635 |
| Sahih Bukhari | 589 |
| Mauquf Sahih | 481 |
| Very Daif | 466 |
| Sahih - Bukhari And Muslim | 383 |
| Maqtu Sahih | 241 |
| Shadh | 226 |
| Munkar | 190 |
| Mauquf Daif | 189 |
| Hasan Lighairihi | 177 |
| Hasan Isnaad | 156 |
| Mawdu | 145 |
| Sahih Muquf | 141 |
| Sahih Maqtu | 133 |
| Sahih Hadith | 112 |
| Sahih Isnaad Maqtu | 99 |

## Disagreement is preserved, not resolved

Where graders differ, every grading is shown on the hadith with its grader named. The
library does not pick a winner.

A real example from this corpus - *Sunan Abi Dawud 1*:

| Grader | Grading |
| --- | --- |
| Al-Albani | Hasan Sahih |
| Muhammad Muhyi al-Din Abdul Hamid | Hasan Sahih |
| Shu'ayb al-Arna'ut | Sahih Lighairihi |
| Zubair Ali Zai | Isnaad Hasan |

## Reading the grades

The vocabulary is deliberately **not** normalised. `Sahih`, `Sahih Isnaad`, `Isnaad Sahih`,
`Sahih Lighairihi` and `Sahih - Agreed Upon` all appear and are not interchangeable -
some describe the chain, others the narration, others corroboration. Flattening them into
one scale would destroy information, so this library keeps the source wording.

See [[Islamic Knowledge/99 - Source & Authenticity Rules|Source & Authenticity Rules]].