import React from 'react';
import { 
  Box, 
  SimpleGrid, 
  Stat, 
  StatLabel, 
  StatNumber, 
  StatHelpText, 
  StatArrow, 
  Icon, 
  Flex,
  useColorModeValue
} from '@chakra-ui/react';
import { FiUsers, FiMessageCircle, FiCpu, FiDatabase } from 'react-icons/fi';

const StatCard = ({ title, value, icon, helpText, trend, trendValue, ...rest }) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const iconBg = useColorModeValue('blue.100', 'blue.900');
  const iconColor = useColorModeValue('blue.700', 'blue.200');
  
  return (
    <Box
      p={5}
      bg={bgColor}
      borderRadius="lg"
      boxShadow="sm"
      borderWidth="1px"
      borderColor={borderColor}
      {...rest}
    >
      <Flex justifyContent="space-between">
        <Stat>
          <StatLabel fontWeight="medium">{title}</StatLabel>
          <StatNumber fontSize="2xl" fontWeight="bold" my={2}>
            {value}
          </StatNumber>
          {helpText && (
            <StatHelpText>
              {trend && <StatArrow type={trend} />}
              {helpText}
            </StatHelpText>
          )}
        </Stat>
        <Flex
          w={12}
          h={12}
          alignItems="center"
          justifyContent="center"
          borderRadius="md"
          bg={iconBg}
          color={iconColor}
        >
          <Icon as={icon} boxSize={6} />
        </Flex>
      </Flex>
    </Box>
  );
};

const DashboardStats = ({ stats = [] }) => {
  // Default stats if none provided
  const defaultStats = [
    {
      title: 'Active Agents',
      value: '3',
      icon: FiUsers,
      helpText: '2 system agents',
    },
    {
      title: 'Conversations',
      value: '24',
      icon: FiMessageCircle,
      helpText: '12 this week',
      trend: 'increase',
    },
    {
      title: 'Memory Entries',
      value: '156',
      icon: FiDatabase,
      helpText: 'Last updated 2h ago',
    },
    {
      title: 'System Status',
      value: 'Operational',
      icon: FiCpu,
      helpText: 'All systems normal',
    },
  ];

  const displayStats = stats.length > 0 ? stats : defaultStats;

  return (
    <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
      {displayStats.map((stat, index) => (
        <StatCard key={index} {...stat} />
      ))}
    </SimpleGrid>
  );
};

export default DashboardStats;
