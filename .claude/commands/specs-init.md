# kiro-init
Initialize Claude Code with Kiro-style steering documents for enhanced context awareness.

## Usage
After running `/specs-create`, use this command to reload Claude's context with the new steering documents:

1. Clear Claude's context: `/clear`
2. Initialize with steering docs: `/specs-init`
3. Test the setup: Ask Claude "List the loaded steering docs."

## What This Does
- Clears Claude's working memory to start fresh
- Loads all 6 steering and specification documents into context
- Prioritizes steering documents (product, tech, structure) for maximum weight
- Makes Claude aware of current project state, constraints, and priorities

## Expected Response
Claude should acknowledge loading:
- `.claude/steering/product.md` - Product vision and business goals
- `.claude/steering/tech.md` - Technical constraints and approved stack  
- `.claude/steering/structure.md` - Code organization and naming conventions
- `specs/design.md` - Architecture and implementation details
- `specs/requirements.md` - User stories and acceptance criteria
- `specs/tasks.md` - Current sprint priorities and progress

## Benefits After Setup
- Code suggestions match approved tech stack
- New features align with product vision
- File organization follows established patterns
- Implementation considers current priorities
- Business context informs technical decisions

## Troubleshooting
If Claude doesn't acknowledge the documents:
1. Verify all files exist in the correct locations
2. Check CLAUDE.md has the steering document references at the top
3. Try `/clear` followed by `/init` again
4. Manually reference specific documents with `@.claude/steering/product.md`