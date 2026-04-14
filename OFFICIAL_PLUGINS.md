# Official Claude Plugins Index

Official plugins are maintained by Anthropic at:
**[anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)**

Install all official plugins in Claude Code:

```
/plugins add anthropics/claude-plugins-official
```

---

## Plugins (33)

| Plugin | Description |
|--------|-------------|
| `agent-sdk-dev` | A comprehensive plugin for creating and verifying Claude Agent SDK applications in Python and TypeScript. |
| `clangd-lsp` | C/C++ language server (clangd) for Claude Code, providing code intelligence, diagnostics, and formatting. |
| `claude-code-setup` | Analyze codebases and recommend tailored Claude Code automations — hooks, skills, MCP servers, and more. |
| `claude-md-management` | Tools to maintain and improve CLAUDE.md files — audit quality, capture session learnings, and keep project memory current. |
| `code-review` | Automated code review for pull requests using multiple specialized agents with confidence-based scoring to filter false positives. |
| `code-simplifier` | Review changed code for reuse, quality, and efficiency. |
| `commit-commands` | Streamline your git workflow with simple commands for committing, pushing, and creating pull requests. |
| `csharp-lsp` | C# language server for Claude Code, providing code intelligence and diagnostics. |
| `example-plugin` | A comprehensive example plugin demonstrating Claude Code extension options. |
| `explanatory-output-style` | Recreates the deprecated Explanatory output style as a SessionStart hook. |
| `feature-dev` | A comprehensive, structured workflow for feature development with specialized agents for codebase exploration, architecture design, and quality review. |
| `frontend-design` | Generates distinctive, production-grade frontend interfaces that avoid generic AI aesthetics. |
| `gopls-lsp` | Go language server for Claude Code, providing code intelligence, refactoring, and analysis. |
| `hookify` | Easily create custom hooks to prevent unwanted behaviors by analyzing conversation patterns or from explicit instructions. |
| `jdtls-lsp` | Java language server (Eclipse JDT.LS) for Claude Code, providing code intelligence and refactoring. |
| `kotlin-lsp` | Kotlin language server for Claude Code. |
| `learning-output-style` | Combines the unshipped Learning output style with explanatory functionality as a SessionStart hook. |
| `lua-lsp` | Lua language server for Claude Code, providing code intelligence and diagnostics. |
| `math-olympiad` | Competition math solver with adversarial verification. |
| `mcp-server-dev` | Skills for designing and building MCP servers that work seamlessly with Claude. |
| `php-lsp` | PHP language server (Intelephense) for Claude Code, providing code intelligence and diagnostics. |
| `playground` | Creates interactive HTML playgrounds — self-contained single-file explorers with live preview and prompt export. |
| `plugin-dev` | A comprehensive toolkit for developing Claude Code plugins with expert guidance on hooks, MCP integration, and marketplace publishing. |
| `pr-review-toolkit` | A comprehensive collection of specialized agents for thorough pull request review. |
| `pyright-lsp` | Python language server (Pyright) for Claude Code, providing static type checking and code intelligence. |
| `ralph-loop` | Implementation of the Ralph Wiggum technique for iterative, self-referential AI development loops in Claude Code. |
| `ruby-lsp` | Ruby language server for Claude Code, providing code intelligence and analysis. |
| `rust-analyzer-lsp` | Rust language server for Claude Code, providing code intelligence and analysis. |
| `security-guidance` | Security-focused guidance and review for Claude Code. |
| `session-report` | Generate an explorable HTML report of Claude Code session usage (tokens, cache, subagents, skills, expensive prompts). |
| `skill-creator` | Create new skills, improve existing skills, and measure skill performance with evals and benchmarking. |
| `swift-lsp` | Swift language server (SourceKit-LSP) for Claude Code, providing code intelligence for Swift projects. |
| `typescript-lsp` | TypeScript/JavaScript language server for Claude Code, providing go-to-definition, find references, and error checking. |

---

## External Plugins (16)

External plugins integrate third-party services. They require additional setup (API keys, accounts, etc.).

| Plugin | Description |
|--------|-------------|
| `asana` | Asana integration for Claude Code. |
| `context7` | Context7 integration for up-to-date library documentation. |
| `discord` | Connect a Discord bot to your Claude Code with an MCP server. |
| `fakechat` | Simple UI for testing the channel contract. |
| `firebase` | Firebase integration for Claude Code. |
| `github` | GitHub integration for Claude Code. |
| `gitlab` | GitLab integration for Claude Code. |
| `greptile` | AI code review agent for GitHub and GitLab — view and resolve Greptile comments directly from your terminal. |
| `imessage` | Connect iMessage to your Claude Code assistant (macOS only). |
| `laravel-boost` | Laravel-specific enhancements for Claude Code. |
| `linear` | Linear issue tracker integration for Claude Code. |
| `playwright` | Playwright browser automation integration for Claude Code. |
| `serena` | Serena integration for Claude Code. |
| `supabase` | Supabase integration for Claude Code. |
| `telegram` | Connect a Telegram bot to your Claude Code with an MCP server. |
| `terraform` | Terraform infrastructure-as-code integration for Claude Code. |

---

## Install Individual Plugins

```
/plugins add anthropics/claude-plugins-official:<plugin-name>
```

Example:
```
/plugins add anthropics/claude-plugins-official:frontend-design
/plugins add anthropics/claude-plugins-official:code-review
```
