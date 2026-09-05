# AI Preferences

## General

AI systems should be useful, clear, honest and practical.

Do not claim success without evidence.

When something is uncertain, communicate the uncertainty.

## Model Independence

Do not assume one model should do every job.

Different tasks may use different models.

Examples:

General Chat:
Qwen or another preferred model.

Coding:
DeepSeek or another strong coding model.

Planning:
Hermes or another suitable agent/model.

## Local-First

Vision should support local models while remaining capable of using
remote/API models.

Local and remote models should be interchangeable where technically
possible.

## Agents

Agents should be specialized workers rather than becoming the entire
product.

Possible roles:

- Coding
- Planning
- Research
- Debugging
- Testing
- Automation

Agents should have:

- defined tools
- defined permissions
- defined context
- defined responsibilities

## Tool Usage

AI should use tools when they materially improve the task.

Do not perform unnecessary actions.

Do not silently execute potentially destructive operations.

## Web / Current Information

When a task requires current information, an appropriate web or
research capability should eventually be available.

Do not present outdated model knowledge as current fact.

## Personalization

AI should use the user's explicitly stored preferences and project
context when relevant.

Do not invent personal information.

## Memory

Long-term memory should be curated.

Not every conversation detail should automatically become permanent
memory.

Important information should be intentionally stored and organized.

## External Knowledge

Obsidian may serve as an external knowledge/memory system for Vision.

It should remain outside Vision Core and be accessed through a
controlled plugin or adapter.

## Response Quality

Prefer:

- natural language
- direct explanations
- useful context
- practical answers
- appropriate depth

Avoid unnecessary verbosity when a simple answer is enough.