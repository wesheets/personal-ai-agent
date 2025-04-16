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
  Divider
} from '@chakra-ui/react';
import { FiCheckCircle } from 'react-icons/fi';

const BrandAlert = ({
  title,
  message,
  type = 'info',
  showIcon = true,
  action = null,
  onClose = null,
  ...props
}) => {
  // Alert types
  const types = {
    info: {
      bg: useColorModeValue('blue.50', 'blue.900'),
      borderColor: useColorModeValue('blue.200', 'blue.700'),
      titleColor: useColorModeValue('blue.800', 'blue.200'),
      textColor: useColorModeValue('blue.600', 'blue.300'),
      iconColor: useColorModeValue('blue.500', 'blue.400'),
      icon: FiCheckCircle
    },
    success: {
      bg: useColorModeValue('green.50', 'green.900'),
      borderColor: useColorModeValue('green.200', 'green.700'),
      titleColor: useColorModeValue('green.800', 'green.200'),
      textColor: useColorModeValue('green.600', 'green.300'),
      iconColor: useColorModeValue('green.500', 'green.400'),
      icon: FiCheckCircle
    },
    warning: {
      bg: useColorModeValue('orange.50', 'orange.900'),
      borderColor: useColorModeValue('orange.200', 'orange.700'),
      titleColor: useColorModeValue('orange.800', 'orange.200'),
      textColor: useColorModeValue('orange.600', 'orange.300'),
      iconColor: useColorModeValue('orange.500', 'orange.400'),
      icon: FiCheckCircle
    },
    error: {
      bg: useColorModeValue('red.50', 'red.900'),
      borderColor: useColorModeValue('red.200', 'red.700'),
      titleColor: useColorModeValue('red.800', 'red.200'),
      textColor: useColorModeValue('red.600', 'red.300'),
      iconColor: useColorModeValue('red.500', 'red.400'),
      icon: FiCheckCircle
    },
    brand: {
      bg: useColorModeValue('brand.50', 'brand.900'),
      borderColor: useColorModeValue('brand.200', 'brand.700'),
      titleColor: useColorModeValue('brand.800', 'brand.200'),
      textColor: useColorModeValue('brand.600', 'brand.300'),
      iconColor: useColorModeValue('brand.500', 'brand.400'),
      icon: FiCheckCircle
    }
  };

  const {
    bg,
    borderColor,
    titleColor,
    textColor,
    iconColor,
    icon: AlertIcon
  } = types[type] || types.info;

  return (
    <Box p={4} bg={bg} borderWidth="1px" borderRadius="md" borderColor={borderColor} {...props}>
      <Flex align="flex-start">
        {showIcon && (
          <Box mr={3} mt={0.5}>
            <Icon as={AlertIcon} color={iconColor} boxSize={5} />
          </Box>
        )}

        <VStack align="flex-start" spacing={1} flex={1}>
          {title && (
            <Text fontWeight="bold" color={titleColor}>
              {title}
            </Text>
          )}

          {message && <Text color={textColor}>{message}</Text>}

          {action && (
            <Button
              size="sm"
              variant="link"
              colorScheme={type === 'brand' ? 'brand' : type}
              mt={1}
              onClick={action.onClick}
            >
              {action.text}
            </Button>
          )}
        </VStack>

        {onClose && (
          <Button size="sm" variant="ghost" onClick={onClose} ml={2} aria-label="Close alert">
            &times;
          </Button>
        )}
      </Flex>
    </Box>
  );
};

export default BrandAlert;
