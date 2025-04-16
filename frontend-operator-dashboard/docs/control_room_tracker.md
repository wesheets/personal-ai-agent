# Control Room Integration Tracker (Phase 6 UI Sync)

This document tracks the status of various features and their UI integration needs for the Control Room interface.

## Control Registry Endpoint

The system provides a dedicated endpoint for retrieving the current status of all UI components:

```
GET /control/registry
```

This endpoint returns a comprehensive JSON structure containing:

- List of all modules with their routes, UI types, and implementation status
- UI component descriptions and requirements
- Integration status definitions
- Last updated timestamp

This endpoint can be used to power dynamic UI menus, developer dashboards, and Control Room builder screens.

## Feature Integration Status

| Feature             | Endpoint / Module     | UI Type             | Status      | Notes                        |
| ------------------- | --------------------- | ------------------- | ----------- | ---------------------------- |
| Scope Planner       | `/orchestrator/scope` | Markdown viewer     | needs_ui    | Show project blueprint       |
| Delegate Executor   | `/delegate`           | Payload button      | needs_ui    | Agent-to-agent ops           |
| Summary Viewer      | `/summarize`          | Markdown text panel | needs_ui    | Show reflection              |
| Project Selector    | `/projects`           | Sidebar dropdown    | built       | For selecting context        |
| Tone Configurator   | `agent_manifest.json` | Editable table      | future      | Persona + skills             |
| Loop Controller     | `/loop`               | Status panel        | needs_ui    | Cognitive loop visualization |
| Reflection Viewer   | `/reflect`            | Text panel          | needs_ui    | Agent reflection display     |
| Memory Browser      | `/read`               | Searchable table    | in_progress | Browse and filter memories   |
| Agent Registry      | `/agents`             | Card grid           | needs_ui    | View available agents        |
| System Caps Monitor | `system_caps.json`    | Settings panel      | future      | Configure system limits      |

## Integration Priority

1. **High Priority**

   - Scope Planner
   - Delegate Executor
   - Summary Viewer

2. **Medium Priority**

   - Loop Controller
   - Reflection Viewer
   - Memory Browser

3. **Low Priority**
   - Agent Registry
   - System Caps Monitor
   - Tone Configurator

## UI Component Requirements

### Markdown Viewer

- Support for full Markdown syntax
- Code block highlighting
- Table rendering
- Collapsible sections

### Payload Button

- JSON payload editor
- Request history
- Response viewer
- Error handling

### Text Panel

- Formatted text display
- Copy functionality
- Search within text
- Export options

### Sidebar Dropdown

- Hierarchical organization
- Search functionality
- Recent selections
- Favorites

### Editable Table

- Inline editing
- Validation
- Revert/commit changes
- Export/import

## Implementation Notes

- All UI components should follow the design system guidelines
- Components should be responsive and mobile-friendly
- Accessibility requirements must be met for all UI elements
- Dark mode support is required for all components
