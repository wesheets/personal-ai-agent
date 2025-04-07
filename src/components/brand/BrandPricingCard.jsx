import React from 'react';
import { Box, Flex, Text, useColorModeValue, Button, Icon, HStack, VStack, Divider } from '@chakra-ui/react';
import { FiCheck } from 'react-icons/fi';

const BrandPricingCard = ({ 
  title, 
  price, 
  period = 'month',
  description, 
  features = [],
  isPopular = false,
  actionText = 'Get Started',
  actionUrl = '#',
  variant = 'default',
  ...props 
}) => {
  // Variants
  const variants = {
    default: {
      bg: useColorModeValue('white', 'gray.800'),
      borderColor: useColorModeValue('gray.200', 'gray.700'),
      titleColor: useColorModeValue('gray.800', 'white'),
      priceColor: useColorModeValue('brand.600', 'brand.400'),
      descColor: useColorModeValue('gray.600', 'gray.400'),
      buttonVariant: 'outline',
      buttonColorScheme: 'brand',
    },
    primary: {
      bg: useColorModeValue('brand.50', 'brand.900'),
      borderColor: useColorModeValue('brand.200', 'brand.700'),
      titleColor: useColorModeValue('brand.800', 'white'),
      priceColor: useColorModeValue('brand.600', 'brand.400'),
      descColor: useColorModeValue('brand.600', 'brand.400'),
      buttonVariant: 'solid',
      buttonColorScheme: 'brand',
    },
    secondary: {
      bg: useColorModeValue('secondary.50', 'secondary.900'),
      borderColor: useColorModeValue('secondary.200', 'secondary.700'),
      titleColor: useColorModeValue('secondary.800', 'white'),
      priceColor: useColorModeValue('secondary.600', 'secondary.400'),
      descColor: useColorModeValue('secondary.600', 'secondary.400'),
      buttonVariant: 'solid',
      buttonColorScheme: 'secondary',
    },
  };
  
  const {
    bg,
    borderColor,
    titleColor,
    priceColor,
    descColor,
    buttonVariant,
    buttonColorScheme,
  } = variants[variant] || variants.default;
  
  // Popular badge styles
  const popularBadgeBg = useColorModeValue('accent.500', 'accent.500');
  const popularBadgeColor = useColorModeValue('white', 'white');
  
  return (
    <Box
      position="relative"
      p={6}
      borderWidth="1px"
      borderRadius="lg"
      bg={bg}
      borderColor={isPopular ? `${buttonColorScheme}.400` : borderColor}
      boxShadow={isPopular ? 'md' : 'sm'}
      transition="all 0.2s"
      _hover={{ boxShadow: 'lg', transform: 'translateY(-4px)' }}
      {...props}
    >
      {isPopular && (
        <Box
          position="absolute"
          top="-3"
          right="50%"
          transform="translateX(50%)"
          px={3}
          py={1}
          bg={popularBadgeBg}
          color={popularBadgeColor}
          fontSize="xs"
          fontWeight="bold"
          borderRadius="full"
          boxShadow="sm"
        >
          Most Popular
        </Box>
      )}
      
      <VStack spacing={4} align="center">
        <Text fontSize="xl" fontWeight="bold" color={titleColor}>
          {title}
        </Text>
        
        <HStack spacing={1} align="baseline">
          <Text fontSize="4xl" fontWeight="extrabold" color={priceColor}>
            ${price}
          </Text>
          <Text fontSize="md" color={descColor}>
            /{period}
          </Text>
        </HStack>
        
        <Text fontSize="sm" color={descColor} textAlign="center">
          {description}
        </Text>
        
        <Divider my={2} />
        
        <VStack spacing={3} align="start" w="full">
          {features.map((feature, index) => (
            <HStack key={index} spacing={2}>
              <Icon as={FiCheck} color={`${buttonColorScheme}.500`} />
              <Text fontSize="sm" color={descColor}>
                {feature}
              </Text>
            </HStack>
          ))}
        </VStack>
        
        <Button
          as="a"
          href={actionUrl}
          variant={buttonVariant}
          colorScheme={buttonColorScheme}
          size="md"
          w="full"
          mt={4}
        >
          {actionText}
        </Button>
      </VStack>
    </Box>
  );
};

export default BrandPricingCard;
