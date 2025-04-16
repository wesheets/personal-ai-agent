import React from 'react';
import {
  Box,
  Flex,
  Text,
  useColorModeValue,
  Button,
  Icon,
  HStack,
  VStack,
  Image
} from '@chakra-ui/react';
import { FiExternalLink } from 'react-icons/fi';

const BrandCard = ({
  title,
  description,
  image,
  actionText = 'Learn More',
  actionUrl = '#',
  variant = 'default',
  ...props
}) => {
  // Variants
  const variants = {
    default: {
      bg: useColorModeValue('white', 'gray.800'),
      borderColor: useColorModeValue('gray.200', 'gray.700'),
      titleColor: useColorModeValue('brand.700', 'brand.300'),
      descColor: useColorModeValue('gray.600', 'gray.400'),
      buttonVariant: 'outline',
      buttonColorScheme: 'brand'
    },
    primary: {
      bg: useColorModeValue('brand.50', 'brand.900'),
      borderColor: useColorModeValue('brand.200', 'brand.700'),
      titleColor: useColorModeValue('brand.700', 'brand.300'),
      descColor: useColorModeValue('brand.600', 'brand.400'),
      buttonVariant: 'solid',
      buttonColorScheme: 'brand'
    },
    secondary: {
      bg: useColorModeValue('secondary.50', 'secondary.900'),
      borderColor: useColorModeValue('secondary.200', 'secondary.700'),
      titleColor: useColorModeValue('secondary.700', 'secondary.300'),
      descColor: useColorModeValue('secondary.600', 'secondary.400'),
      buttonVariant: 'solid',
      buttonColorScheme: 'secondary'
    },
    accent: {
      bg: useColorModeValue('accent.50', 'accent.900'),
      borderColor: useColorModeValue('accent.200', 'accent.700'),
      titleColor: useColorModeValue('accent.700', 'accent.300'),
      descColor: useColorModeValue('accent.600', 'accent.400'),
      buttonVariant: 'solid',
      buttonColorScheme: 'accent'
    }
  };

  const { bg, borderColor, titleColor, descColor, buttonVariant, buttonColorScheme } =
    variants[variant] || variants.default;

  return (
    <Box
      p={5}
      borderWidth="1px"
      borderRadius="lg"
      bg={bg}
      borderColor={borderColor}
      boxShadow="sm"
      transition="all 0.2s"
      _hover={{ boxShadow: 'md', transform: 'translateY(-2px)' }}
      {...props}
    >
      <VStack spacing={4} align="flex-start">
        {image && (
          <Box w="full" h="160px" borderRadius="md" overflow="hidden" mb={2}>
            <Image
              src={image}
              alt={title}
              w="full"
              h="full"
              objectFit="cover"
              fallback={
                <Box
                  w="full"
                  h="full"
                  bg={`${buttonColorScheme}.100`}
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                >
                  <Text color={`${buttonColorScheme}.500`} fontWeight="bold">
                    {title?.charAt(0) || 'P'}
                  </Text>
                </Box>
              }
            />
          </Box>
        )}

        <Text fontSize="xl" fontWeight="bold" color={titleColor}>
          {title}
        </Text>

        <Text fontSize="md" color={descColor}>
          {description}
        </Text>

        <Button
          as="a"
          href={actionUrl}
          target="_blank"
          rel="noopener noreferrer"
          variant={buttonVariant}
          colorScheme={buttonColorScheme}
          size="sm"
          rightIcon={<Icon as={FiExternalLink} />}
          mt={2}
        >
          {actionText}
        </Button>
      </VStack>
    </Box>
  );
};

export default BrandCard;
