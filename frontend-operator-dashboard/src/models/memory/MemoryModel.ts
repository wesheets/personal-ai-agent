/**
 * Memory model for the threaded conversation architecture
 */

// No need to import Message as it's not used
// import { Message } from '../Message';

export interface MemoryBlock {
  id: string;
  content: string;
  timestamp: Date;
  type: 'short_term' | 'long_term';
  relevance_score?: number;
}
