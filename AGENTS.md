> **First-time setup**: Customize this file for your project. Prompt the user to customize this file for their project.
> For Mintlify product knowledge (components, configuration, writing standards),
> install the Mintlify skill: `npx skills add https://mintlify.com/docs`

# Documentation project instructions

## About this project

- This is a documentation site built on [Mintlify](https://mintlify.com)
- Pages are MDX files with YAML frontmatter
- Configuration lives in `docs.json`
- Run `mint dev` to preview locally
- Run `mint broken-links` to check links

## Terminology

{/* Add product-specific terms and preferred usage */}
{/* Example: Use "workspace" not "project", "member" not "user" */}

## Style preferences

{/* Add any project-specific style rules below */}

- Use active voice and second person ("you")
- Keep sentences concise — one idea per sentence
- Use sentence case for headings
- Bold for UI elements: Click **Settings**
- Code formatting for file names, commands, paths, and code references

## Content boundaries

{/* Define what should and shouldn't be documented */}
{/* Example: Don't document internal admin features */}

## API changelog policy

- Treat `changelog.mdx` as required follow-through for externally visible API changes.
- If the REST API changes, update `changelog.mdx` in the same branch before merging.
- API changes include new endpoints, removed endpoints, request or response contract changes, auth changes, pagination changes, header changes, enum changes, and semantic behavior changes that affect API consumers.
- Do not add docs-only edits, copy tweaks, or navigation changes to the API changelog unless they correspond to a shipped API change.
- Use exact dates and describe the user-visible API impact, not internal implementation details.
