# Building and Deploying a Secure MCP Server on Google Cloud Run

Demo companion for the **Build With AI 2026** talk by Gregory Tan (AI Security Engineer, YTL AI Labs), presented at Google Developer Group Kuala Lumpur.

## Overview

This repo demonstrates how to build a production-ready MCP (Model Context Protocol) server for a ShopApp e-commerce use case, and how to secure it when deployed on Google Cloud Run. It covers three key security concerns that affect real-world MCP deployments: authentication, authorization, and tenant isolation.

## Project Structure

```
.
├── mcp_server.py       # FastMCP server exposing ShopApp tools
├── mcp_client.ipynb    # Live demo notebook (all 5 sections)
├── Dockerfile          # Container definition for Cloud Run deployment
├── requirements.txt    # Python dependencies
└── README.md
```

## Demo Sections

| # | Section | What it covers |
|---|---------|----------------|
| 1 | Direct MCP Client | Connect to MCP server, list tools, invoke them directly |
| 2 | AI Agent (Google ADK) | Gemini-powered agent interacting with MCP tools conversationally |
| 3 | Authentication | Secure MCP server with Google Cloud Run IAM (`--no-allow-unauthenticated`) |
| 4 | Authorization | Least-privilege RBAC using `tool_filter` to scope agents to specific tools |
| 5 | Tenant Isolation | Per-tenant data isolation using SPIFFE identity via Vertex AI Agent Engine |

## MCP Tools

The server (`mcp_server.py`) exposes three tools on a SQLite-backed ShopApp:

- `search_products(query)` — search the product catalogue
- `get_user(user_id)` — retrieve a user profile
- `place_order(user_id, product_id, quantity)` — place a product order

## Prerequisites

- Python 3.11+
- [Google Cloud SDK (`gcloud`)](https://cloud.google.com/sdk/docs/install) authenticated and configured
- A GCP project with the following APIs enabled:
  - Cloud Run
  - Vertex AI
  - IAM
  - Cloud Resource Manager
  - Cloud Build

## Setup

### Option 1: Run locally

```bash
jupyter notebook mcp_client.ipynb
```

### Option 2: Run on Google Colab

1. Go to [colab.research.google.com](https://colab.research.google.com)
2. Click **File > Open notebook > GitHub**
3. Paste this repo's URL and select `mcp_client.ipynb`

---

The notebook handles everything — installing dependencies, starting the MCP server, deploying to Cloud Run, and managing teardown. Just run the cells top to bottom.

> Fill in your GCP project details in Section 2 (cell `04 Configuration`) before running the cloud sections.

## Security Architecture

```
AI Agent
   │  + Identity Token (Google IAM)
   │  + SPIFFE Certificate (Vertex AI Agent Engine)
   ▼
Google Cloud Run  ──── verifies token with Google IAM
   │
   ▼
MCP Server  ──── tool_filter enforces per-agent tool access
                 SPIFFE cert enforces per-tenant data isolation
```

## Resources

- [MCP Specification](https://modelcontextprotocol.io)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [Google ADK](https://google.github.io/adk-docs/)
- [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
- [Cloud Run IAM Authentication](https://cloud.google.com/run/docs/authenticating/overview)
