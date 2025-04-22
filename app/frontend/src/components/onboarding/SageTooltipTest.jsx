import React from 'react';
import { Box } from '@chakra-ui/react';
import SageTooltip from './SageTooltip';

/**
 * Test component for SageTooltip
 * This component demonstrates how to use SageTooltip with different configurations
 */
const SageTooltipTest = () => {
  return (
    <Box p={4}>
      <Box mb={4}>
        <SageTooltip componentId="OperatorHUDBar" showIcon={true} placement="bottom">
          <Box p={3} bg="blue.100" borderRadius="md">
            Hover me to see a basic tooltip with icon
          </Box>
        </SageTooltip>
      </Box>
      
      <Box mb={4}>
        <SageTooltip componentId="ProjectContextSwitcher" usePopover={true} placement="right">
          <Box p={3} bg="green.100" borderRadius="md">
            Hover me to see a popover with more content
          </Box>
        </SageTooltip>
      </Box>
      
      <Box mb={4}>
        <SageTooltip componentId="OrchestratorModePanel" showIcon={false} placement="top">
          <Box p={3} bg="purple.100" borderRadius="md">
            Hover me to see a tooltip without icon
          </Box>
        </SageTooltip>
      </Box>
      
      <Box mb={4}>
        <SageTooltip componentId="AgentPanel" iconColor="red.500" iconSize="lg" usePopover={true}>
          <Box p={3} bg="yellow.100" borderRadius="md">
            Hover me to see a popover with custom icon styling
          </Box>
        </SageTooltip>
      </Box>
    </Box>
  );
};

export default SageTooltipTest;
