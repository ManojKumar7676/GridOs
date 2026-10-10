# GridOS demo video narration

## Introduction

Welcome to GridOS, a local prototype for renewable energy dispatch. We’ll tour the operations workspace, follow a modeled dispatch, and show what the prototype can do today. The opening footage sets the renewable-energy context; the screens that follow are captures of the running application. No plant is connected.


## Problem overview

Renewable generation and demand change throughout the day. Operators compare generation, storage, demand, and market conditions before deciding how to respond. GridOS models these inputs in a 24-hour scenario, bringing separate considerations into one review flow. The values shown are illustrative scenario inputs, not current grid conditions or an operational forecast.

Visible assumptions help teams compare cases and understand what changed before a real-world decision.

## Live product demonstration

Let’s start in Telemetry and Replay. The page shows 96 simulated intervals in a format similar to a hardware feed. The connection is visibly disconnected. A CSV template is available, and imported CSV or JSON readings stay separate from the simulation.

Next, Dispatch and Scenarios evaluates a modeled portfolio under different conditions. The optimizer returns a software recommendation with balance metrics. Compare scenarios and review run history to see how assumptions change the result. Detailed metrics expose trade-offs. This is a planning aid only; GridOS sends no commands to batteries, generators, or grid controllers, and this demo does not validate the optimizer for live dispatch.

Review the selected scenario, run summary, and balance. History lets reviewers compare runs and revisit assumptions. The screens demonstrate a workflow, not a live connection or verified forecast.

## AI capabilities

Software agents represent forecast, market, and reliability roles before the orchestrator prepares a recommendation. Agent Studio shows these agents and lets users define skills and tools. API and MCP entries are examples only; the application does not execute them. Weather image analysis is a heuristic and has not been validated with operational data. The combined result is for human review: agents do not access external systems or control infrastructure.

These visible roles help teams review who contributed and decide what integration evidence they need.

## Key features

The workspace also includes trends, an asset registry, audit details, weather imagery, evaluation, and configuration. These views help reviewers inspect assumptions, inputs, and results. They support discussion and traceability; production monitoring, access controls, and regulatory review are not complete.

Together, the supporting pages provide context around a modeled portfolio and its scenario runs. They help reviewers ask how the workflow behaves and what should be validated next.

## Business impact

The prototype offers a starting point to compare assumptions, review trade-offs, and discuss scenarios before planning integration. Teams can agree which inputs, constraints, and evidence a pilot would need. Savings, reliability improvements, production readiness, and deployment timelines have not been measured; any business case needs operational data and expert review.

That makes the current impact a clearer, shared review process for early planning. It does not yet establish savings or reliability gains.

## Closing summary

GridOS demonstrates renewable dispatch with simulated telemetry, software agents, and an optimizer. Recommendations remain advisory. This local prototype is not a live control system. Next, validate the models with experts and measured data, then define safe integration requirements. Thanks for watching.

The goal is a transparent starting point for that validation work.

Any integration should follow measured validation and a documented safety review.
