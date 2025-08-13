# Refresh Documentation (Quick Update)

Execute a quick documentation refresh after code changes.

## Quick Action Steps

1. **Analyze Recent Changes**:
   - Check last 10 commits: `git log --oneline -10`
   - Review modified files: `git diff --name-status HEAD~5..HEAD`
   - Scan package.json for new dependencies

2. **Update Key Documents**:
   - Read and update `.claude/steering/tech.md` with new technologies
   - Update `.claude/steering/structure.md` with structural changes
   - Refresh `specs/tasks.md` with current development status

3. **Quick Validation**:
   - Verify CLAUDE.md context references are still accurate
   - Check that steering documents reflect current tech stack
   - Ensure spec documents match implemented features

## Focus Areas
- New dependencies or tools
- Structural/architectural changes  
- Feature implementation status
- Updated development priorities

Use `/update-docs` for comprehensive updates. Use this command for routine maintenance after smaller changes.