import React from 'react';
import { Box, Flex, Image, Text, useColorModeValue } from '@chakra-ui/react';

const BrandLogo = ({ size = 'md', withText = true, ...props }) => {
  // Size mappings
  const sizes = {
    xs: { logoSize: '16px', fontSize: 'xs', spacing: 1 },
    sm: { logoSize: '24px', fontSize: 'sm', spacing: 2 },
    md: { logoSize: '32px', fontSize: 'md', spacing: 3 },
    lg: { logoSize: '48px', fontSize: 'lg', spacing: 4 },
    xl: { logoSize: '64px', fontSize: 'xl', spacing: 5 },
  };
  
  const { logoSize, fontSize, spacing } = sizes[size] || sizes.md;
  
  // Colors
  const textColor = useColorModeValue('brand.800', 'brand.200');
  
  return (
    <Flex align="center" {...props}>
      <Box 
        w={logoSize} 
        h={logoSize} 
        borderRadius="md" 
        bg="brand.500" 
        display="flex" 
        alignItems="center" 
        justifyContent="center"
        overflow="hidden"
      >
        {/* Replace with actual logo image when available */}
        <Text color="white" fontWeight="bold" fontSize={`calc(${logoSize} * 0.5)`}>P</Text>
      </Box>
      
      {withText && (
        <Text 
          ml={spacing} 
          fontWeight="bold" 
          fontSize={fontSize} 
          color={textColor}
          letterSpacing="tight"
        >
          Promethios
        </Text>
      )}
    </Flex>
  );
};

export default BrandLogo;
