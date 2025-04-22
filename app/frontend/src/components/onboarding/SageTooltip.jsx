import React from 'react';
import { Box, Text, Tooltip, useColorModeValue, Popover, PopoverTrigger, PopoverContent, PopoverHeader, PopoverBody, PopoverArrow, PopoverCloseButton, Icon } from '@chakra-ui/react';
import { FaQuestionCircle } from 'react-icons/fa';
import tooltipRegistry from '../../config/TourStepRegistry.json';

/**
 * SageTooltip Component
 * 
 * Wraps any UI component with contextual help tooltips.
 * Pulls text from TooltipRegistry.json and supports different SAGE quote tones.
 * 
 * @param {Object} props
 * @param {string} props.componentId - ID of the component to get tooltip content from registry
 * @param {React.ReactNode} props.children - Component to wrap with tooltip
 * @param {boolean} props.showIcon - Whether to show the question mark icon (default: true)
 * @param {string} props.placement - Tooltip placement (default: 'top')
 * @param {boolean} props.usePopover - Whether to use Popover instead of Tooltip for more content (default: false)
 * @param {string} props.iconColor - Color of the question mark icon
 * @param {string} props.iconSize - Size of the question mark icon (default: 'sm')
 */
const SageTooltip = ({ 
  componentId, 
  children, 
  showIcon = true, 
  placement = 'top', 
  usePopover = false,
  iconColor,
  iconSize = 'sm'
}) => {
  const tooltipBg = useColorModeValue('blue.700', 'blue.900');
  const tooltipColor = useColorModeValue('white', 'gray.100');
  const iconDefaultColor = useColorModeValue('blue.500', 'blue.300');
  const actualIconColor = iconColor || iconDefaultColor;
  
  // Get tooltip content from registry
  const tooltipData = tooltipRegistry.tooltips[componentId];
  
  if (!tooltipData) {
    console.warn(`No tooltip data found for component: ${componentId}`);
    return children;
  }
  
  // Get sage quote based on tone
  const getSageQuote = () => {
    if (!tooltipData.sageQuote) return null;
    
    let quoteText = '';
    switch (tooltipData.sageQuote) {
      case 'reflective':
        quoteText = "I observe that this helps you understand the system's state.";
        break;
      case 'confident':
        quoteText = "This is essential for effective operation of the system.";
        break;
      case 'wise':
        quoteText = "Understanding this element reveals deeper cognitive patterns.";
        break;
      default:
        quoteText = "This component serves an important purpose in the system.";
    }
    
    return (
      <Text fontSize="xs" fontStyle="italic" mt={2} color="gray.200">
        {quoteText}
      </Text>
    );
  };
  
  // Icon sizes
  const getIconSize = () => {
    switch (iconSize) {
      case 'xs': return '12px';
      case 'sm': return '14px';
      case 'md': return '16px';
      case 'lg': return '20px';
      default: return '14px';
    }
  };
  
  // Render with Popover for more detailed content
  if (usePopover) {
    return (
      <Box position="relative" display="inline-block">
        {children}
        {showIcon && (
          <Popover placement={placement} trigger="hover">
            <PopoverTrigger>
              <Box 
                position="absolute" 
                top="2px" 
                right="2px" 
                cursor="pointer"
                zIndex={1}
              >
                <Icon 
                  as={FaQuestionCircle} 
                  color={actualIconColor} 
                  w={getIconSize()} 
                  h={getIconSize()} 
                />
              </Box>
            </PopoverTrigger>
            <PopoverContent bg={tooltipBg} color={tooltipColor} borderColor={tooltipBg}>
              <PopoverArrow bg={tooltipBg} />
              <PopoverCloseButton color={tooltipColor} />
              <PopoverHeader fontWeight="bold" borderBottomWidth="0">
                {tooltipData.title}
              </PopoverHeader>
              <PopoverBody>
                <Text>{tooltipData.content}</Text>
                {getSageQuote()}
              </PopoverBody>
            </PopoverContent>
          </Popover>
        )}
      </Box>
    );
  }
  
  // Render with simple Tooltip
  return (
    <Box position="relative" display="inline-block">
      <Tooltip 
        label={
          <Box>
            <Text fontWeight="bold">{tooltipData.title}</Text>
            <Text>{tooltipData.content}</Text>
          </Box>
        }
        bg={tooltipBg}
        color={tooltipColor}
        placement={placement}
        hasArrow
      >
        {children}
      </Tooltip>
      {showIcon && (
        <Box 
          position="absolute" 
          top="2px" 
          right="2px" 
          cursor="pointer"
          zIndex={1}
        >
          <Icon 
            as={FaQuestionCircle} 
            color={actualIconColor} 
            w={getIconSize()} 
            h={getIconSize()} 
          />
        </Box>
      )}
    </Box>
  );
};

export default SageTooltip;
