# StayEasy workspace

Shared toolbox for Adam, Claude and Codex. Rules and roles are in `AGENTS.md`.

| Folder | Purpose |
| --- | --- |
| `templates/client_kit/` | Template copied for every new client |
| `skills/` | Step-by-step procedures (start with `stayeasy-new-client`) |
| `docs/` | Client information system and file naming standard |
| `research/` | Data and notes Codex collects for Claude to analyse |
| `tools/` | Codex's research scripts |
| `clients/` | Not used: client folders stay on the Mac |

## Everyday use

- **New client:** tell Claude "new client: <name>" and paste the diagnostic form. The skill copies `templates/client_kit/` into `~/Documents/Projects/Stayeasy/clients/onboarding/<client_slug>/`.
- **Need data:** tell Claude what you need. Claude opens a `research_request` issue, Codex delivers a PR, Claude reviews it, you merge.

## On your Mac

```bash
cd ~/Documents/Projects
git clone https://github.com/kisamaadam0-max/stayeasy-workspace.git
```

Pull before each work session: `git -C ~/Documents/Projects/stayeasy-workspace pull`.
