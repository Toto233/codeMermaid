# Update Documentation Command

You are tasked with updating the steering documents and specification files after major changes or new features have been added to the THOTH Portal application.

## Objective
Systematically review the current codebase state and update all documentation files to reflect the current architecture, features, and development status.

## Process

### 1. Codebase Analysis
- **Review Recent Changes**: Check git log for recent commits, new features, and architectural changes
- **Analyze Current Structure**: Examine the file structure, new components, routes, and backend functions
- **Identify New Technologies**: Look for new dependencies, libraries, or patterns that have been introduced
- **Assess Feature Status**: Check what features have been implemented, are in progress, or are planned

### 2. Steering Documents Update

#### `.claude/steering/product.md`
- Update product vision and roadmap based on implemented features
- Refresh target user personas with current understanding
- Update business goals and competitive differentiation
- Reflect any pivots or strategic changes in product direction

#### `.claude/steering/structure.md` 
- Update code organization patterns based on current file structure
- Document new architecture patterns or conventions that have emerged
- Update naming conventions and folder structures
- Reflect any refactoring or structural improvements

#### `.claude/steering/tech.md`
- Update technology stack with new dependencies or tools
- Document any technical constraints that have been discovered
- Update approved libraries, frameworks, and development tools
- Reflect performance requirements and technical decisions

### 3. Specification Documents Update

#### `specs/design.md`
- Update technical architecture diagrams and descriptions
- Document new feature designs and implementation approaches
- Update API specifications and data flow patterns
- Reflect current database schema and relationships

#### `specs/requirements.md` 
- Update user stories based on implemented and planned features
- Refresh acceptance criteria for current development phase
- Document functional requirements that have evolved
- Update priority and status of requirements

#### `specs/tasks.md`
- Update current development tasks and their status
- Refresh sprint planning and progress tracking
- Document completed tasks and lessons learned
- Update task priorities and dependencies

### 4. Implementation Steps

1. **Start with Git Analysis**:
   ```bash
   git log --oneline -20
   git diff --name-status HEAD~10..HEAD
   ```

2. **Analyze Package Changes**:
   - Check `package.json` for new dependencies
   - Review `convex/schema.ts` for database changes
   - Examine new routes and components

3. **Review Current Features**:
   - List all implemented features
   - Identify features in development
   - Note deprecated or removed functionality

4. **Update Each Document Systematically**:
   - Read current content
   - Identify outdated information
   - Add new information based on codebase analysis
   - Ensure consistency across all documents

5. **Cross-Reference and Validate**:
   - Ensure CLAUDE.md references are accurate
   - Verify all links and references work
   - Check that technical details match implementation

### 5. Quality Checks

Before completing the update:
- [ ] All steering documents reflect current product state
- [ ] All spec documents align with implemented features  
- [ ] Technology stack is accurately documented
- [ ] File structure documentation matches actual structure
- [ ] Requirements reflect current development priorities
- [ ] Task tracking is up-to-date with real progress
- [ ] All cross-references between documents are valid
- [ ] CLAUDE.md context loading directives are accurate

### 6. Execution Guidelines

- **Be Comprehensive**: Don't just add new items, review and update existing content
- **Be Accurate**: Ensure all technical details match the actual implementation
- **Be Current**: Remove outdated information and deprecated features
- **Be Consistent**: Maintain consistent terminology and formatting across all documents
- **Be Forward-Looking**: Include planned features and known technical debt

### 7. User Input Requirements

When running this command, gather information about:
- What major changes or features were recently added?
- Are there any strategic shifts or new requirements?
- What technical decisions or constraints should be documented?
- Are there any performance issues or architectural concerns?
- What are the current development priorities and timeline?

### 8. Success Criteria

The documentation update is complete when:
- All documents accurately reflect the current state of the application
- New features and architectural changes are properly documented
- Development team can use the docs for onboarding and decision-making
- Documentation provides clear guidance for future development
- All stakeholders have accurate information about product status and direction

## Usage
Run this command after:
- Major feature releases
- Architectural refactoring
- New technology integration
- Sprint completion
- Significant requirement changes
- Team onboarding preparation

This command ensures that your documentation stays synchronized with your rapidly evolving codebase and maintains its value as a source of truth for the project.