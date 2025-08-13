# create-specs
Generate Kiro IDE-style steering and specification documents to improve Claude Code's context awareness and code generation accuracy.

## Overview
This command creates 6 essential documents that guide Claude Code's understanding of your project:
- 3 steering documents (product, tech, structure) 
- 3 specification documents (design, requirements, tasks)

It also updates CLAUDE.md to reference these documents, ensuring they're loaded into context for every prompt.

## Steps

1. **Analyze the codebase** using to understand:
   - Project architecture and tech stack
   - Business domain and features
   - Code organization patterns
   - Existing documentation (PRD.md, TODO.md, etc.)

2. **Create steering documents** in `.claude/steering/`:
   - `product.md` - Product vision, users, features, business goals
   - `tech.md` - Approved stack, libraries, constraints
   - `structure.md` - Folder layout, naming conventions, patterns

3. **Create specification documents** in `specs/`:
   - `design.md` - Technical architecture and implementation details
   - `requirements.md` - User stories and acceptance criteria
   - `tasks.md` - Discrete coding steps (imported from TODO.md)

4. **Update CLAUDE.md** by adding document references at the TOP (for maximum weight)

5. **Verify** the setup by asking Claude to list loaded steering docs

## Usage
Run this command when:
- Starting a new project with Claude Code
- Wanting better context awareness and code consistency
- Migrating from manual documentation to structured steering docs

After running, use `/clear` → `/init` to reload Claude's context with the new documents.

## Note
Keep tasks.md manageable to avoid excessive token usage. Regularly archive completed tasks.