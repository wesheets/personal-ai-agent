/**
 * SAGE Belief Map Visualization
 * 
 * This module provides visualization components for SAGE belief maps,
 * displaying belief scores and emotional weights in an interactive format.
 */

// Initialize visualization when document is ready
document.addEventListener('DOMContentLoaded', () => {
  initializeBeliefMap();
});

/**
 * Initialize the belief map visualization
 */
async function initializeBeliefMap() {
  const container = document.getElementById('belief-map-container');
  if (!container) {
    console.error('Belief map container not found');
    return;
  }

  // Show loading indicator
  container.innerHTML = '<div class="loading">Loading belief data...</div>';

  try {
    // Fetch belief data from API
    const response = await fetch('/dashboard/sage/beliefs');
    if (!response.ok) {
      throw new Error(`Failed to fetch belief data: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    // Check if we have belief data
    if (!data.belief_data_list || data.belief_data_list.length === 0) {
      container.innerHTML = '<div class="no-data">No belief data available. Run SAGE in cascade mode to generate belief maps.</div>';
      return;
    }

    // Clear loading indicator
    container.innerHTML = '';

    // Create belief map for each loop
    data.belief_data_list.forEach(item => {
      createBeliefMapForLoop(container, item.loop_id, item.belief_data);
    });

    // Add event listeners for interactive elements
    addEventListeners();

  } catch (error) {
    console.error('Error initializing belief map:', error);
    container.innerHTML = `<div class="error">Error loading belief data: ${error.message}</div>`;
  }
}

/**
 * Create a belief map visualization for a specific loop
 * 
 * @param {HTMLElement} container - The container element
 * @param {string} loopId - The loop identifier
 * @param {Object} beliefData - The belief data for the loop
 */
function createBeliefMapForLoop(container, loopId, beliefData) {
  // Create loop section
  const loopSection = document.createElement('div');
  loopSection.className = 'loop-section';
  loopSection.id = `loop-${loopId}`;

  // Create header
  const header = document.createElement('h2');
  header.textContent = `Loop: ${loopId}`;
  header.className = 'loop-header';
  loopSection.appendChild(header);

  // Create timestamp
  if (beliefData.timestamp) {
    const timestamp = document.createElement('div');
    timestamp.className = 'timestamp';
    timestamp.textContent = `Generated: ${new Date(beliefData.timestamp).toLocaleString()}`;
    loopSection.appendChild(timestamp);
  }

  // Create reflection section if available
  if (beliefData.reflection_text) {
    const reflection = document.createElement('div');
    reflection.className = 'reflection';
    reflection.innerHTML = `<h3>Reflection</h3><p>${beliefData.reflection_text}</p>`;
    loopSection.appendChild(reflection);
  }

  // Create belief map visualization
  const beliefMap = document.createElement('div');
  beliefMap.className = 'belief-map';
  
  // Check if we have belief scores
  if (beliefData.belief_scores && beliefData.belief_scores.length > 0) {
    // Create belief cards
    beliefData.belief_scores.forEach((score, index) => {
      const beliefCard = createBeliefCard(score, index);
      beliefMap.appendChild(beliefCard);
    });
  } else {
    beliefMap.innerHTML = '<div class="no-beliefs">No beliefs found for this loop</div>';
  }
  
  loopSection.appendChild(beliefMap);
  container.appendChild(loopSection);
}

/**
 * Create a belief card for a single belief score
 * 
 * @param {Object} score - The belief score object
 * @param {number} index - The index of the belief
 * @returns {HTMLElement} The belief card element
 */
function createBeliefCard(score, index) {
  const card = document.createElement('div');
  card.className = 'belief-card';
  card.dataset.index = index;
  
  // Calculate color based on confidence
  const confidenceColor = getConfidenceColor(score.confidence);
  
  // Calculate border color based on emotional weight
  let borderColor = '#888'; // Neutral gray
  if (score.emotional_weight !== null && score.emotional_weight !== undefined) {
    borderColor = getEmotionalColor(score.emotional_weight);
  }
  
  // Set card styles
  card.style.backgroundColor = confidenceColor;
  card.style.borderColor = borderColor;
  
  // Create belief text
  const beliefText = document.createElement('div');
  beliefText.className = 'belief-text';
  beliefText.textContent = score.belief;
  card.appendChild(beliefText);
  
  // Create confidence indicator
  const confidenceIndicator = document.createElement('div');
  confidenceIndicator.className = 'confidence-indicator';
  confidenceIndicator.textContent = `Confidence: ${Math.round(score.confidence * 100)}%`;
  card.appendChild(confidenceIndicator);
  
  // Create emotional weight indicator if available
  if (score.emotional_weight !== null && score.emotional_weight !== undefined) {
    const emotionalIndicator = document.createElement('div');
    emotionalIndicator.className = 'emotional-indicator';
    const emotionLabel = score.emotional_weight > 0 ? 'Positive' : 
                         score.emotional_weight < 0 ? 'Negative' : 'Neutral';
    emotionalIndicator.textContent = `Emotional Weight: ${emotionLabel} (${score.emotional_weight.toFixed(2)})`;
    card.appendChild(emotionalIndicator);
  }
  
  return card;
}

/**
 * Get color for confidence value
 * 
 * @param {number} confidence - Confidence value (0-1)
 * @returns {string} CSS color value
 */
function getConfidenceColor(confidence) {
  // Use a gradient from light to dark blue based on confidence
  const lightness = 90 - (confidence * 40); // Higher confidence = darker blue
  return `hsl(210, 70%, ${lightness}%)`;
}

/**
 * Get color for emotional weight
 * 
 * @param {number} weight - Emotional weight (-1 to 1)
 * @returns {string} CSS color value
 */
function getEmotionalColor(weight) {
  if (weight > 0) {
    // Positive: green
    const intensity = Math.min(weight * 100, 100);
    return `hsl(120, ${intensity}%, 40%)`;
  } else if (weight < 0) {
    // Negative: red
    const intensity = Math.min(Math.abs(weight) * 100, 100);
    return `hsl(0, ${intensity}%, 50%)`;
  } else {
    // Neutral: gray
    return '#888';
  }
}

/**
 * Add event listeners for interactive elements
 */
function addEventListeners() {
  // Add click event for belief cards to show details
  const beliefCards = document.querySelectorAll('.belief-card');
  beliefCards.forEach(card => {
    card.addEventListener('click', () => {
      // Toggle selected state
      card.classList.toggle('selected');
    });
  });
  
  // Add filter functionality
  const filterInput = document.getElementById('belief-filter');
  if (filterInput) {
    filterInput.addEventListener('input', event => {
      const filterText = event.target.value.toLowerCase();
      const cards = document.querySelectorAll('.belief-card');
      
      cards.forEach(card => {
        const beliefText = card.querySelector('.belief-text').textContent.toLowerCase();
        if (beliefText.includes(filterText)) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    });
  }
}

/**
 * Load belief data for a specific loop
 * 
 * @param {string} loopId - The loop identifier
 */
async function loadBeliefDataForLoop(loopId) {
  const container = document.getElementById('belief-map-container');
  if (!container) {
    console.error('Belief map container not found');
    return;
  }

  try {
    // Show loading indicator
    container.innerHTML = '<div class="loading">Loading belief data...</div>';
    
    // Fetch belief data for specific loop
    const response = await fetch(`/dashboard/sage/beliefs?loop_id=${loopId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch belief data: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    // Clear container
    container.innerHTML = '';
    
    // Create belief map
    createBeliefMapForLoop(container, data.loop_id, data.belief_data);
    
    // Add event listeners
    addEventListeners();
    
  } catch (error) {
    console.error(`Error loading belief data for loop ${loopId}:`, error);
    container.innerHTML = `<div class="error">Error loading belief data: ${error.message}</div>`;
  }
}
