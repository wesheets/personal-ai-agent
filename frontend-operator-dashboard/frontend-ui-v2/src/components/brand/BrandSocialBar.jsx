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
import BrandLogo from './BrandLogo';
import { FiGithub, FiTwitter, FiLinkedin, FiMail } from 'react-icons/fi';

const BrandSocialBar = ({
  showGithub = true,
  showTwitter = true,
  showLinkedin = true,
  showEmail = true,
  githubUrl = 'https://github.com/promethios-ai',
  twitterUrl = 'https://twitter.com/promethios_ai',
  linkedinUrl = 'https://linkedin.com/company/promethios-ai',
  emailAddress = 'contact@promethios.ai',
  variant = 'default',
  ...props
}) => {
  // Variants
  const variants = {
    default: {
      bg: useColorModeValue('white', 'gray.800'),
      borderColor: useColorModeValue('gray.200', 'gray.700'),
      textColor: useColorModeValue('gray.600', 'gray.400'),
      iconColor: useColorModeValue('brand.500', 'brand.400'),
      hoverBg: useColorModeValue('gray.50', 'gray.700')
    },
    primary: {
      bg: useColorModeValue('brand.50', 'brand.900'),
      borderColor: useColorModeValue('brand.200', 'brand.700'),
      textColor: useColorModeValue('brand.600', 'brand.400'),
      iconColor: useColorModeValue('brand.500', 'brand.400'),
      hoverBg: useColorModeValue('brand.100', 'brand.800')
    },
    transparent: {
      bg: 'transparent',
      borderColor: 'transparent',
      textColor: useColorModeValue('gray.600', 'gray.400'),
      iconColor: useColorModeValue('brand.500', 'brand.400'),
      hoverBg: useColorModeValue('blackAlpha.50', 'whiteAlpha.50')
    }
  };

  const { bg, borderColor, textColor, iconColor, hoverBg } = variants[variant] || variants.default;

  const socialLinks = [
    {
      show: showGithub,
      icon: FiGithub,
      url: githubUrl,
      label: 'GitHub'
    },
    {
      show: showTwitter,
      icon: FiTwitter,
      url: twitterUrl,
      label: 'Twitter'
    },
    {
      show: showLinkedin,
      icon: FiLinkedin,
      url: linkedinUrl,
      label: 'LinkedIn'
    },
    {
      show: showEmail,
      icon: FiMail,
      url: `mailto:${emailAddress}`,
      label: 'Email'
    }
  ].filter((link) => link.show);

  return (
    <Box
      py={3}
      px={4}
      bg={bg}
      borderWidth="1px"
      borderRadius="lg"
      borderColor={borderColor}
      {...props}
    >
      <Flex
        justify="space-between"
        align="center"
        direction={{ base: 'column', sm: 'row' }}
        gap={{ base: 4, sm: 0 }}
      >
        <BrandLogo size="sm" />

        <HStack spacing={2}>
          {socialLinks.map((link, index) => (
            <Button
              key={index}
              as="a"
              href={link.url}
              target="_blank"
              rel="noopener noreferrer"
              aria-label={link.label}
              variant="ghost"
              size="sm"
              color={textColor}
              _hover={{ bg: hoverBg }}
              leftIcon={<Icon as={link.icon} color={iconColor} />}
            >
              <Text display={{ base: 'none', md: 'block' }}>{link.label}</Text>
            </Button>
          ))}
        </HStack>
      </Flex>
    </Box>
  );
};

export default BrandSocialBar;
