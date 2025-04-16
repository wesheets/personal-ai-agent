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
import { FiSettings, FiUser, FiShield, FiGlobe } from 'react-icons/fi';

const BrandSettings = ({
  title = 'Settings',
  sections = [],
  activeSection = null,
  onSectionChange = () => {},
  children,
  ...props
}) => {
  // Default sections if none provided
  const defaultSections = [
    { id: 'general', label: 'General', icon: FiSettings },
    { id: 'account', label: 'Account', icon: FiUser },
    { id: 'security', label: 'Security', icon: FiShield },
    { id: 'preferences', label: 'Preferences', icon: FiGlobe }
  ];

  const settingsSections = sections.length > 0 ? sections : defaultSections;

  // Colors
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const sidebarBg = useColorModeValue('gray.50', 'gray.900');
  const activeBg = useColorModeValue('brand.50', 'brand.900');
  const activeColor = useColorModeValue('brand.700', 'brand.200');
  const hoverBg = useColorModeValue('gray.100', 'gray.700');

  return (
    <Box borderWidth="1px" borderRadius="lg" borderColor={borderColor} overflow="hidden" {...props}>
      <Box p={4} borderBottomWidth="1px" borderColor={borderColor} bg={bgColor}>
        <Text fontSize="lg" fontWeight="bold">
          {title}
        </Text>
      </Box>

      <Flex>
        {/* Sidebar */}
        <Box w="250px" bg={sidebarBg} borderRightWidth="1px" borderColor={borderColor} p={4}>
          <VStack spacing={2} align="stretch">
            {settingsSections.map((section) => (
              <Button
                key={section.id}
                variant="ghost"
                justifyContent="flex-start"
                leftIcon={<Icon as={section.icon} />}
                bg={activeSection === section.id ? activeBg : 'transparent'}
                color={activeSection === section.id ? activeColor : undefined}
                _hover={{ bg: activeSection === section.id ? activeBg : hoverBg }}
                onClick={() => onSectionChange(section.id)}
                size="md"
                borderRadius="md"
                w="full"
              >
                {section.label}
              </Button>
            ))}
          </VStack>
        </Box>

        {/* Content */}
        <Box flex={1} p={6} bg={bgColor}>
          {children}
        </Box>
      </Flex>
    </Box>
  );
};

export default BrandSettings;
