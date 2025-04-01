import React, { useState, useEffect, useMemo } from 'react';
import { Box, Text, Alert, Spinner } from '@chakra-ui/react';
import { AlertIcon } from '@chakra-ui/alert';

export default function InterruptControl() {
  const [loading, setLoading] = useState(true);
  const [interruptSystemOffline, setInterruptSystemOffline] = useState(false);
  
  // Check if getTaskState is safe to use at the top of the component
  const isSafe = useMemo(() => {
    const safeToUse = typeof window !== 'undefined' && typeof window.or?.getTaskState === 'function';
    if (!safeToUse) {
      console.warn('InterruptControl: getTaskState is not available. Skipping...');
    } else {
      console.log('InterruptControl: getTaskState is available and safe to use.');
    }
    return safeToUse;
  }, []);

  // Fetch system state on component mount
  useEffect(() => {
    const fetchSystemState = async () => {
      try {
        setLoading(true);
        console.log('InterruptControl: Starting to fetch system state...');
        
        // Apply safeguard before calling getTaskState
        const isSafeToCall = typeof window !== 'undefined' && typeof window.or?.getTaskState === 'function';
        
        if (isSafeToCall) {
          console.log('InterruptControl: Safe to call getTaskState, proceeding...');
          const state = await window.or.getTaskState();
          console.log('InterruptControl: Successfully fetched task state:', state);
          setInterruptSystemOffline(false);
        } else {
          console.warn('InterruptControl: getTaskState is not available. Skipping fetch...');
          setInterruptSystemOffline(true);
        }
      } catch (err) {
        console.error('InterruptControl: Error fetching task state:', err);
        setInterruptSystemOffline(true);
      } finally {
        // Ensure spinner unmounts cleanly in all cases
        console.log('InterruptControl: Unmounting spinner regardless of outcome');
        setLoading(false);
      }
    };

    fetchSystemState();
  }, []);

  return (
    <Box p={4} borderWidth="1px" borderRadius="lg">
      <Text fontWeight="bold" mb={2}>Interrupt Control</Text>
      
      {loading ? (
        <Box display="flex" alignItems="center">
          <Spinner size="sm" mr={2} />
          <Text>Loading control panel...</Text>
        </Box>
      ) : interruptSystemOffline ? (
        <Alert status="warning" variant="left-accent">
          <AlertIcon />
          Interrupt system offline – retrying soon
        </Alert>
      ) : (
        <Text>Control panel loaded.</Text>
      )}
    </Box>
  );
}
      
      {loading ? (
        <Box display="flex" alignItems="center">
          <Spinner size="sm" mr={2} />
          <Text>Loading control panel...</Text>
        </Box>
      ) : interruptSystemOffline ? (
        <Alert status="warning" variant="left-accent">
          <AlertIcon />
          Interrupt system offline – retrying soon
        </Alert>
      ) : (
        <Text>Control panel loaded.</Text>
      )}
    </Box>
  );
}
