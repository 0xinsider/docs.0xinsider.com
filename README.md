# 0xinsider API Documentation

Documentation for the [0xinsider API](https://docs.0xinsider.com) — prediction market intelligence for AI agents, trading bots, and research tools.

## What is 0xinsider?

0xinsider provides trader grades, whale trade signals, smart money flow analysis, and insider detection across Polymarket and Kalshi.

The API gives you programmatic access to the same intelligence powering the [0xinsider terminal](https://0xinsider.com).

## API endpoints

- **Trader** — grades (S through F), P&L, win rate, strategy detection
- **Leaderboard** — top traders ranked by score with cursor pagination
- **Whale Trades** — large trades with signal scoring, filterable by grade and category
- **Explore Markets** — browse whale-active titled markets by category, platform, status, and sort order
- **Market Intel** — smart money flow direction, buy/sell volumes, top positions
- **Search Markets** — find markets by keyword with category and status filters
- **Insider Radar** — suspicious trading patterns and pre-resolution accumulation

## MCP Server

Connect AI agents to 0xinsider via the Model Context Protocol:

```bash
npx -y @0xinsider/mcp init
```

Supports Claude Code, Cursor, Codex, Gemini CLI, and other stdio-compatible MCP clients.

See the [MCP docs](https://docs.0xinsider.com/mcp) and the [npm package](https://www.npmjs.com/package/@0xinsider/mcp) for setup details.

## Local development

Install [Mintlify CLI](https://www.npmjs.com/package/mint):

```bash
npm i -g mint
```

Preview locally:

```bash
mint dev
```

Open `http://localhost:3000`.

## Links

- [API docs](https://docs.0xinsider.com)
- [API changelog](https://docs.0xinsider.com/changelog)
- [Terminal](https://0xinsider.com)
- [Product changelog](https://0xinsider.com/changelog)
- [Support](mailto:support@0xinsider.com)
