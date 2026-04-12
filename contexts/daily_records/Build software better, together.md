---
title: "Build software better, together"
source: "https://github.com/"
author:
published:
created: 2026-04-10
description: "GitHub is where people build software. More than 150 million people use GitHub to discover, fork, and contribute to over 420 million projects."
tags:
  - "clippings"
---
## Dashboard

## Home

## Chat Commands

## Feed

Filter

Filter

##### Events

Activity you want to see on your feed

---

---

[![@jgamblin profile](https://avatars.githubusercontent.com/u/8428124?s=80&v=4)](https://github.com/jgamblin)

### jgamblin contributed to KennaSecurity/toolkit

#### 6 hours ago

### ci: don't fail build on codecov upload errors #610

Merged merged 1 commit

## Summary

- Change `fail_ci_if_error` from `true` to `false` in the Codecov upload step
- Codecov upload failures (e.g. "Token required because branch is protected" on Dependabot PRs) were blocking CI even though the actual tests pass
- Unblocks [#608](https://github.com/KennaSecurity/toolkit/pull/608)

## Test plan

- Verified the only change is the `fail_ci_if_error` flag
- Confirm [#608](https://github.com/KennaSecurity/toolkit/pull/608) CI passes after this merges

🤖…

[Read more](https://github.com/KennaSecurity/toolkit/pull/610)

[![@jgamblin profile](https://avatars.githubusercontent.com/u/8428124?s=80&v=4)](https://github.com/jgamblin)

### jgamblin contributed to KennaSecurity/toolkit

#### 7 hours ago

### chore: Ruby 3.4 upgrade and full dependency security update #607

Merged merged 13 commits

## Summary

Hey team! I was cleaning up some of my old PRs and noticed this repo hasn't had much dependency love recently. Ruby 3.2 hit EOL back in March 2025, and bundle-audit was flagging a few CVEs, so I figured it was time for a thorough refresh.

### Ruby & Gem Updates

- **Ruby 3.2.2 → 3.4.9** — back on a supported, actively maintained version (3.2 has b…
[Read more](https://github.com/KennaSecurity/toolkit/pull/607)

[milla-jovovich/mempalace](https://github.com/milla-jovovich/mempalace)

The highest-scoring AI memory system ever benchmarked. And it's free.

Python [35.6k](https://github.com/milla-jovovich/mempalace/stargazers)

---

[safishamsi/graphify](https://github.com/safishamsi/graphify)

AI coding assistant skill (Claude Code, Codex, OpenCode, Cursor, Gemini CLI, OpenClaw, Factory Droid, Trae). Turn any folder of code, docs, papers, or images into a queryable knowledge graph

Python [17.6k](https://github.com/safishamsi/graphify/stargazers)

[microsoft/VibeVoice](https://github.com/microsoft/VibeVoice)

Open-Source Frontier Voice AI

Python [38.1k](https://github.com/microsoft/VibeVoice/stargazers)

[![@jgamblin profile](https://avatars.githubusercontent.com/u/8428124?s=80&v=4)](https://github.com/jgamblin)

### jgamblin contributed to jgamblin/CVElk

#### 7 hours ago

### fix: update vulnerable Python dependencies #49

Merged merged 1 commit

## Summary

Updates 6 Python packages to resolve 14 Dependabot alerts (1 critical, 5 high, 8 moderate).

Adds explicit minimum version constraints for transitive dependencies in `pyproject.toml` to prevent resolution to vulnerable versions.

## Changes

- Pillow >= 10.3.0
- certifi >= 2023.7.22
- urllib3 >= 2.5.0
- requests >= 2.32.4
- fonttools >= 4.60.2
- idna >= 3.7
[Read more](https://github.com/jgamblin/CVElk/pull/49)

[![@jgamblin profile](https://avatars.githubusercontent.com/u/8428124?s=80&v=4)](https://github.com/jgamblin)

### jgamblin contributed to jgamblin/NCAA-Prediction

#### 7 hours ago

### fix: update vulnerable NPM dependencies #18

Merged merged 1 commit

## Summary

- Adds `frontend/package-lock.json` to pin all transitive dependencies to safe versions
- Resolves 2 Dependabot alerts (1 high, 1 moderate):
	- **@remix-run/router** (XSS via open redirects): no longer in dependency tree since `react-router-dom` v7 dropped it
		- **esbuild** (dev server request forgery): pinned at 0.27.7, well above the 0.25.0 fix threshold
[Read more](https://github.com/jgamblin/NCAA-Prediction/pull/18)

[![@jgamblin profile](https://avatars.githubusercontent.com/u/8428124?s=80&v=4)](https://github.com/jgamblin)

### jgamblin contributed to jgamblin/RiskAnalyzer

#### 12 hours ago

### fix(security): bump vite to 8.0.8 — resolve 3 CVEs #9

Merged merged 1 commit

## Summary

- Bump `vite` from 8.0.1 to 8.0.8 to resolve 3 Dependabot security alerts

## Vulnerabilities Fixed

| GHSA | Severity | Description |
| --- | --- | --- |
| [GHSA-v2wj-q39q-566r](https://github.com/advisories/GHSA-v2wj-q39q-566r "GHSA-v2wj-q39q-566r") | **HIGH** | `server.fs.deny` bypassed with queries |
| [GHSA-p9ff-h696-f583](https://github.com/advisories/GHSA-p9ff-h696-f583 "GHSA-p9ff-h696-f583") | **HIGH** | Arbitrary file read via Vite Dev Server WebSocket |
| [GHSA-4w7w-66w2-5vf9](https://github.com/advisories/GHSA-4w7w-66w2-5vf9 "GHSA-4w7w-66w2-5vf9") | **MODERATE** | Path traversal in optimized deps `.map` hand… |

[Read more](https://github.com/jgamblin/RiskAnalyzer/pull/9)

[![@tangxiaofeng7 profile](https://avatars.githubusercontent.com/u/45926593?s=80&v=4)](https://github.com/tangxiaofeng7)

### tangxiaofeng7 starred a repository

#### 12 hours ago

[Tencent/AI-Infra-Guard](https://github.com/Tencent/AI-Infra-Guard)

A full-stack AI Red Teaming platform securing AI ecosystems via OpenClaw Security Scan, Agent Scan, Skills Scan, MCP scan, AI Infra scan and LLM jailbreak evaluation.

Python [3.4k](https://github.com/Tencent/AI-Infra-Guard/stargazers)

[![@openfindbearings profile](https://avatars.githubusercontent.com/u/255456289?s=80&v=4)](https://github.com/openfindbearings)

### openfindbearings contributed to openfindbearings/OpenFindBearings.Api

#### 13 hours ago

### fix(repository): 修正轴承类型导航属性引用 #44

Merged merged 1 commit

修正了BearingInterchangeRepository和MerchantBearingRepository中 对轴承类型导航属性的错误引用，将BearingType更正为  
BearingTypeNavigation以匹配实际的实体模型结构。

[openclaw/openclaw](https://github.com/openclaw/openclaw)

Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞

TypeScript [353k](https://github.com/openclaw/openclaw/stargazers)

[![@hackstoic profile](https://avatars.githubusercontent.com/u/7455951?s=80&v=4)](https://github.com/hackstoic)

### hackstoic starred a repository

#### 13 hours ago

[freestylefly/wechat-cli](https://github.com/freestylefly/wechat-cli)

A CLI tool to query your local WeChat data — chat history, contacts, sessions, favorites, and more. Designed for LLM integration.

Python [381](https://github.com/freestylefly/wechat-cli/stargazers)

[![@tangxiaofeng7 profile](https://avatars.githubusercontent.com/u/45926593?s=80&v=4)](https://github.com/tangxiaofeng7)

### tangxiaofeng7 starred a repository

#### 15 hours ago

[affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)

The agent harness performance optimization system. Skills, instincts, memory, security, and research-first development for Claude Code, Codex, Opencode, Cursor and beyond.

JavaScript [149k](https://github.com/affaan-m/everything-claude-code/stargazers)

[![@NanmiCoder profile](https://avatars.githubusercontent.com/u/47178017?s=80&v=4)](https://github.com/NanmiCoder)

### NanmiCoder added a repository to SKILLS

#### 2 days ago

[titanwings/colleague-skill](https://github.com/titanwings/colleague-skill)

将冰冷的离别化为温暖的 Skill，欢迎加入数字生命1.0！Transforming cold farewells into warm skills? It's giving rebirth era. Welcome to Digital Life 1.0. 🫶

Python [11.9k](https://github.com/titanwings/colleague-skill/stargazers)

[tw93/Mole](https://github.com/tw93/Mole)

🐹 Deep clean and optimize your Mac.

Shell [45.9k](https://github.com/tw93/Mole/stargazers)