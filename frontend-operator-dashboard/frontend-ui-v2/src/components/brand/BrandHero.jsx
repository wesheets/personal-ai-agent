import React from 'react';
import { Box, Flex, Text, useColorModeValue, Button, Icon, HStack, VStack, Divider, Image } from '@chakra-ui/react';
import { FiExternalLink } from 'react-icons/fi';

const BrandHero = ({ 
  title,
  subtitle,
  ctaText = 'Get Started',
  ctaUrl = '#',
  secondaryCtaText = 'Learn More',
  secondaryCtaUrl = '#',
  image = null,
  imageAlt = 'Hero Image',
  variant = 'default',
  ...props 
}) => {
  // Variants
  const variants = {
    default: {
      bg: useColorModeValue('white', 'gray.800'),
      titleColor: useColorModeValue('gray.800', 'white'),
      subtitleColor: useColorModeValue('gray.600', 'gray.400'),
      primaryButtonVariant: 'solid',
      primaryButtonColorScheme: 'brand',
      secondaryButtonVariant: 'outline',
      secondaryButtonColorScheme: 'brand',
    },
    primary: {
      bg: useColorModeValue('brand.50', 'brand.900'),
      titleColor: useColorModeValue('brand.800', 'white'),
      subtitleColor: useColorModeValue('brand.600', 'brand.300'),
      primaryButtonVariant: 'solid',
      primaryButtonColorScheme: 'brand',
      secondaryButtonVariant: 'outline',
      secondaryButtonColorScheme: 'brand',
    },
    secondary: {
      bg: useColorModeValue('secondary.50', 'secondary.900'),
      titleColor: useColorModeValue('secondary.800', 'white'),
      subtitleColor: useColorModeValue('secondary.600', 'secondary.300'),
      primaryButtonVariant: 'solid',
      primaryButtonColorScheme: 'secondary',
      secondaryButtonVariant: 'outline',
      secondaryButtonColorScheme: 'secondary',
    },
    dark: {
      bg: useColorModeValue('gray.800', 'gray.900'),
      titleColor: 'white',
      subtitleColor: 'gray.300',
      primaryButtonVariant: 'solid',
      primaryButtonColorScheme: 'brand',
      secondaryButtonVariant: 'outline',
      secondaryButtonColorScheme: 'whiteAlpha',
    },
  };
  
  const {
    bg,
    titleColor,
    subtitleColor,
    primaryButtonVariant,
    primaryButtonColorScheme,
    secondaryButtonVariant,
    secondaryButtonColorScheme,
  } = variants[variant] || variants.default;
  
  return (
    <Box
      py={12}
      px={8}
      bg={bg}
      borderRadius="lg"
      {...props}
    >
      <Flex 
        direction={{ base: 'column', lg: 'row' }}
        align="center"
        justify="space-between"
        gap={8}
      >
        <VStack 
          spacing={6} 
          align={{ base: 'center', lg: 'flex-start' }}
          textAlign={{ base: 'center', lg: 'left' }}
          maxW={{ base: 'full', lg: '50%' }}
        >
          <Text 
            fontSize={{ base: '3xl', md: '4xl', lg: '5xl' }}
            fontWeight="bold"
            lineHeight="shorter"
            color={titleColor}
          >
            {title}
          </Text>
          
          <Text 
            fontSize={{ base: 'md', md: 'lg' }}
            color={subtitleColor}
          >
            {subtitle}
          </Text>
          
          <HStack spacing={4}>
            <Button
              as="a"
              href={ctaUrl}
              size="lg"
              variant={primaryButtonVariant}
              colorScheme={primaryButtonColorScheme}
            >
              {ctaText}
            </Button>
            
            <Button
              as="a"
              href={secondaryCtaUrl}
              size="lg"
              variant={secondaryButtonVariant}
              colorScheme={secondaryButtonColorScheme}
              rightIcon={<Icon as={FiExternalLink} />}
            >
              {secondaryCtaText}
            </Button>
          </HStack>
        </VStack>
        
        {image && (
          <Box 
            maxW={{ base: 'full', lg: '50%' }}
            w={{ base: 'full', lg: 'auto' }}
          >
            <Image 
              src={image} 
              alt={imageAlt} 
              borderRadius="md"
              shadow="lg"
              maxH="400px"
              objectFit="contain"
            />
          </Box>
        )}
      </Flex>
    </Box>
  );
};

export default BrandHero;
