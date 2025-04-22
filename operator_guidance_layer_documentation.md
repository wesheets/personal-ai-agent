# Operator Guidance & Onboarding Layer Documentation

## Overview

The Operator Guidance & Onboarding Layer provides contextual help, guided tours, and onboarding information to make Promethios feel accessible, learnable, and empowering. This layer helps new users understand the system's capabilities and assists experienced operators in discovering advanced features.

## Components

### 1. SageTooltip

The `SageTooltip` component wraps any UI element with contextual help tooltips that provide information about the component's purpose and functionality.

#### Features:
- Pulls tooltip content from `TourStepRegistry.json`
- Supports both simple tooltips and more detailed popovers
- Includes optional SAGE quotes with different tones (reflective, confident, wise)
- Customizable icon appearance and placement

#### Usage:
```jsx
import SageTooltip from './components/onboarding/SageTooltip';

// Basic usage
<SageTooltip componentId="OperatorHUDBar">
  <YourComponent />
</SageTooltip>

// With popover for more detailed content
<SageTooltip componentId="ProjectContextSwitcher" usePopover={true} placement="right">
  <YourComponent />
</SageTooltip>

// Without question mark icon
<SageTooltip componentId="OrchestratorModePanel" showIcon={false}>
  <YourComponent />
</SageTooltip>

// With custom icon styling
<SageTooltip componentId="AgentPanel" iconColor="red.500" iconSize="lg">
  <YourComponent />
</SageTooltip>
```

#### Props:
- `componentId` (string, required): ID of the component to get tooltip content from registry
- `children` (React.ReactNode, required): Component to wrap with tooltip
- `showIcon` (boolean, default: true): Whether to show the question mark icon
- `placement` (string, default: 'top'): Tooltip placement
- `usePopover` (boolean, default: false): Whether to use Popover instead of Tooltip for more content
- `iconColor` (string): Color of the question mark icon
- `iconSize` (string, default: 'sm'): Size of the question mark icon

### 2. OnboardingPane

The `OnboardingPane` component provides a floating right-side pane that introduces users to Promethios concepts through a tabbed interface.

#### Features:
- Tabbed interface with sections for "What is Promethios?", "What is a loop?", and "How do I talk to an agent?"
- Responsive design that works on both desktop and mobile
- Includes SAGE wisdom quotes for deeper understanding
- Navigation between tabs with next/previous buttons

#### Usage:
```jsx
import OnboardingPane from './components/onboarding/OnboardingPane';

// Basic usage
const [isOpen, setIsOpen] = useState(false);

<Button onClick={() => setIsOpen(true)}>
  Open Help
</Button>

<OnboardingPane 
  isOpen={isOpen} 
  onClose={() => setIsOpen(false)} 
/>

// With specific initial tab
<OnboardingPane 
  isOpen={isOpen} 
  onClose={() => setIsOpen(false)} 
  initialTab="loops" // 'about', 'loops', or 'agents'
/>
```

#### Props:
- `isOpen` (boolean, default: true): Whether the pane is open
- `onClose` (function, required): Function to call when closing the pane
- `initialTab` (string, default: 'about'): Initial tab to show ('about', 'loops', or 'agents')

### 3. GuidedTourManager

The `GuidedTourManager` component provides guided tours of the Promethios UI using the react-joyride library and tour steps defined in `TourStepRegistry.json`.

#### Features:
- Multiple tour types (main, newUser, advancedFeatures)
- Tour progress is saved to localStorage for resuming later
- Controls for pausing, restarting, and skipping tours
- Customizable tooltips with SAGE quotes

#### Usage:
```jsx
import GuidedTourManager from './components/onboarding/GuidedTourManager';

// Basic usage
const [showTour, setShowTour] = useState(false);

<Button onClick={() => setShowTour(true)}>
  Start Tour
</Button>

{showTour && (
  <GuidedTourManager
    tourId="main"
    autoStart={true}
    onComplete={() => setShowTour(false)}
    onSkip={() => setShowTour(false)}
  />
)}

// With different tour and hidden controls
<GuidedTourManager
  tourId="newUser"
  autoStart={true}
  showControls={false}
  onComplete={handleComplete}
  onSkip={handleSkip}
/>
```

#### Props:
- `tourId` (string, default: 'main'): ID of the tour to run from TourStepRegistry
- `autoStart` (boolean, default: false): Whether to start the tour automatically
- `onComplete` (function): Callback when tour is completed
- `onSkip` (function): Callback when tour is skipped
- `showControls` (boolean, default: true): Whether to show tour controls

### 4. TourStepRegistry.json

The `TourStepRegistry.json` file contains all the tour steps and tooltip content used by the onboarding components.

#### Structure:
```json
{
  "tours": {
    "main": {
      "title": "Welcome to Promethios",
      "description": "Let's explore the key features of your cognitive system",
      "steps": [
        {
          "target": "#OperatorHUDBar",
          "title": "Operator HUD",
          "content": "This is your control center...",
          "position": "bottom",
          "sageQuote": "The interface between mind and machine begins with awareness..."
        },
        // More steps...
      ]
    },
    // More tours...
  },
  "tooltips": {
    "OperatorHUDBar": {
      "title": "Operator HUD",
      "content": "Your control center for Promethios...",
      "sageQuote": "reflective"
    },
    // More tooltips...
  }
}
```

## Integration

The Operator Guidance Layer is integrated with the Promethios UI in the following ways:

1. **SageTooltip Integration**:
   - All components in DashboardLayout.jsx are wrapped with SageTooltip
   - Tooltips appear when hovering over components

2. **OnboardingPane Integration**:
   - Added to the MODAL zone in UIZoneSchema.json
   - Accessible via the Help button in the bottom-right corner
   - Opens automatically for first-time users

3. **GuidedTourManager Integration**:
   - Integrated in DashboardLayout.jsx
   - Accessible via the Take Tour button in the bottom-right corner
   - Starts automatically for first-time users with the "newUser" tour
   - Uses localStorage to track tour progress

## First-Time User Experience

When a user visits Promethios for the first time:

1. The OnboardingPane automatically opens with an introduction to Promethios
2. After a short delay, the "newUser" guided tour starts
3. The tour highlights key components with step-by-step instructions
4. Tour progress is saved if the user skips or pauses
5. The first-time flag is set in localStorage to prevent repeating on subsequent visits

## Best Practices

1. **Adding New Tooltips**:
   - Add new component entries to the `tooltips` section of TourStepRegistry.json
   - Use appropriate SAGE quote tones based on the component's purpose

2. **Creating New Tours**:
   - Add new tour entries to the `tours` section of TourStepRegistry.json
   - Ensure all target elements have proper IDs in the DOM
   - Test tours thoroughly to ensure all steps are accessible

3. **Extending the Onboarding Pane**:
   - Add new tabs by modifying the OnboardingPane.jsx component
   - Keep content concise and focused on helping users understand key concepts

## Maintenance

The Operator Guidance Layer is designed to be maintainable by non-developers through the TourStepRegistry.json file. This allows content updates without code changes.

To update tooltip or tour content:
1. Edit the TourStepRegistry.json file
2. Update the relevant tooltip or tour step content
3. No code changes or recompilation is required

## Future Enhancements

Potential future enhancements for the Operator Guidance Layer:

1. User-specific onboarding based on role or experience level
2. Interactive tutorials with practice exercises
3. Context-aware help that appears based on user actions
4. Expanded SAGE wisdom quotes database
5. Video tutorials integrated into the OnboardingPane
