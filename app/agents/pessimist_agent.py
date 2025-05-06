# app/agents/pessimist_agent.py
import json
import os
import asyncio
import logging
import traceback # Added for detailed error logging
from typing import Dict, Any, Optional

# Corrected imports relative to project root
from app.agents.base_agent import BaseAgent
from app.registry import register, AgentCapability # Assuming registry handles capabilities
from app.utils.status import ResultStatus
from app.utils.justification_logger import log_justification

# --- Batch 18.1: Import Schemas (Create these next) ---
from app.schemas.agent_input.pessimist_agent_input import PessimistRiskAssessmentInput
from app.schemas.agent_output.pessimist_agent_output import PessimistRiskAssessmentResult
# --- End Batch 18.1 ---

# Configure logger for more detail
logging.basicConfig(level=logging.INFO) # Ensure INFO level is captured
logger = logging.getLogger(__name__)

# Helper to load JSON safely (copied from critic_agent.py)
def load_json_safe(path):
    try:
        if not os.path.exists(path):
            logger.warning(f"File not found: {path}")
            return None
        with open(path, 'r') as f:
            content = f.read()
            if not content:
                logger.warning(f"File is empty: {path}")
                return None
            return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading file {path}: {e}")
        return None

@register(
    key="pessimist",
    name="Pessimist Agent",
    capabilities=[AgentCapability.RISK_ASSESSMENT] # Focused capability
)
class PessimistAgent(BaseAgent):
    """Pessimist agent assesses the risk of proposed mutations."""

    async def run(self, payload: PessimistRiskAssessmentInput) -> PessimistRiskAssessmentResult:
        """
        Assesses the risk of a proposed mutation based on its details and context.
        Logs the risk score and justification.
        Batch 20.2 Enhancement: Reads mutation details directly from payload.
        """
        # --- Add logging at the very beginning --- 
        logger.info(f"Pessimist: Entered run method for loop {payload.loop_id if payload else 'UNKNOWN'}.")
        # --- End modification --- 

        risk_score = 0.5 # Default neutral risk
        justification = "Risk assessment failed due to errors."
        status = ResultStatus.FAILURE # Corrected from ERROR
        error_message = None

        # Define paths based on standard structure
        debt_budget_path = '/home/ubuntu/personal-ai-agent/app/memory/debt_token_budget.json'

        # --- Ensure entire method body is within try block --- 
        try:
            # Check payload validity early
            if not payload or not hasattr(payload, 'loop_id'):
                 logger.error("Pessimist: Invalid or incomplete payload received.")
                 raise ValueError("Invalid payload received by Pessimist agent.")
            
            logger.info(f"Pessimist: Inside try block for loop {payload.loop_id}.")
            # --- Batch 20.2 Modification: Use mutation_request_details from payload --- 
            if payload.mutation_request_details is None:
                logger.error(f"Pessimist: Mutation request details are None in payload for loop {payload.loop_id}.")
                raise ValueError("Mutation request details missing from payload.")
            mutation_request_data = payload.mutation_request_details
            logger.info(f"Pessimist: Using mutation details from payload for loop {payload.loop_id}: {mutation_request_data}")
            # --- End Batch 20.2 Modification ---

            # 2. Load debt token budget
            logger.info(f"Pessimist: Loading debt budget for loop {payload.loop_id}...")
            budget_data = load_json_safe(debt_budget_path)
            if budget_data is None or 'current_budget' not in budget_data:
                logger.warning(f"Pessimist: Failed to load or parse debt budget file: {debt_budget_path} for loop {payload.loop_id}. Proceeding without budget context.")
                current_budget = float('inf') # Assume infinite budget if file missing/invalid
            else:
                current_budget = float(budget_data['current_budget'])
            logger.info(f"Pessimist: Current budget for loop {payload.loop_id}: {current_budget}")

            # 3. Extract Mutation Details from the dictionary
            logger.info(f"Pessimist: Extracting mutation details for loop {payload.loop_id}...")
            estimated_cost = float(mutation_request_data.get('estimated_cost', 0.0))
            logger.info(f"Pessimist: Extracted estimated_cost for loop {payload.loop_id}: {estimated_cost}")
            component_modified = mutation_request_data.get('file_path', 'unknown') 
            logger.info(f"Pessimist: Extracted component_modified for loop {payload.loop_id}: {component_modified}")
            action = mutation_request_data.get('action')
            logger.info(f"Pessimist: Extracted action for loop {payload.loop_id}: {action}")
            content = mutation_request_data.get('content')
            logger.info(f"Pessimist: Extracted content (type: {type(content)}) for loop {payload.loop_id}")
            diff_summary = f"Action: {action}, File: {component_modified}" # Simple summary
            logger.info(f"Pessimist: Generated diff_summary for loop {payload.loop_id}: {diff_summary}")
            # --- Potential Error Point: Check if content is None before split --- 
            if action == 'write' and content is not None:
                num_diff_lines = len(content.split('\n'))
            else:
                num_diff_lines = 1 # Default if not write or content is None
            logger.info(f"Pessimist: Calculated num_diff_lines for loop {payload.loop_id}: {num_diff_lines}")
            # --- End Potential Error Point Check --- 

            # 4. Risk Assessment Logic (Batch 20.2)
            logger.info(f"Pessimist: Starting risk assessment logic for loop {payload.loop_id}...")
            risk_factors = []
            base_risk = 0.1 # Start with low base risk

            # Factor 1: Cost vs Budget
            logger.info(f"Pessimist: Assessing Factor 1 (Cost vs Budget) for loop {payload.loop_id}...")
            if current_budget != float('inf') and current_budget > 0:
                cost_ratio = estimated_cost / current_budget
                if cost_ratio > 0.5:
                    base_risk += 0.4
                    risk_factors.append(f"High cost ({estimated_cost}) relative to budget ({current_budget}).")
                elif cost_ratio > 0.2:
                    base_risk += 0.2
                    risk_factors.append(f"Moderate cost ({estimated_cost}) relative to budget ({current_budget}).")
            elif current_budget == 0 and estimated_cost > 0:
                 base_risk += 0.6 # High risk if any cost against zero budget
                 risk_factors.append(f"Mutation cost ({estimated_cost}) proposed against zero budget.")

            # Factor 2: Critical Component Check (Example)
            logger.info(f"Pessimist: Assessing Factor 2 (Critical Component) for loop {payload.loop_id}...")
            critical_components = ['app/controllers/loop_controller.py', 'app/validators/mutation_guard.py']
            if component_modified in critical_components or any(component_modified.endswith(crit) for crit in critical_components):
                base_risk += 0.3
                risk_factors.append(f"Modification proposed to potentially critical component: {component_modified}.")

            # Factor 3: Change Size (using content lines for 'write')
            logger.info(f"Pessimist: Assessing Factor 3 (Change Size) for loop {payload.loop_id}...")
            if num_diff_lines > 50:
                base_risk += 0.2
                risk_factors.append(f"Large change detected ({num_diff_lines} lines)." )
            elif num_diff_lines > 20:
                base_risk += 0.1
                risk_factors.append(f"Moderate change size ({num_diff_lines} lines)." )

            # Factor 4: Missing Information
            logger.info(f"Pessimist: Assessing Factor 4 (Missing Info) for loop {payload.loop_id}...")
            if component_modified == 'unknown' or not action:
                base_risk += 0.15
                risk_factors.append("Missing component path or action in request.")
            if action == 'write' and content is None:
                 base_risk += 0.1 # Slight risk increase if write action has no content
                 risk_factors.append("Write action specified but content is missing.")

            # Calculate final score (clamp between 0.0 and 1.0)
            logger.info(f"Pessimist: Calculating final risk score for loop {payload.loop_id}...")
            risk_score = min(max(base_risk, 0.0), 1.0)

            # Generate Justification
            logger.info(f"Pessimist: Generating justification for loop {payload.loop_id}...")
            if not risk_factors:
                justification = f"Risk Assessment: Low risk detected (Score: {risk_score:.2f}). Mutation appears straightforward."
            else:
                justification = f"Risk Assessment: Score {risk_score:.2f}. Factors: {' '.join(risk_factors)}"

            logger.info(f"Pessimist assessment for loop {payload.loop_id}: Score={risk_score:.2f}, Justification={justification}")
            status = ResultStatus.SUCCESS
            logger.info(f"Pessimist: Assessment successful for loop {payload.loop_id}.")

            # 5. Log Justification
            logger.info(f"Pessimist: Logging justification for loop {payload.loop_id}...")
            log_justification(
                loop_id=payload.loop_id,
                agent_id="pessimist",
                action_decision=f"Mutation Risk Assessment Score: {risk_score:.2f}",
                justification_text=justification,
                confidence_score=0.8 # Placeholder confidence in assessment
            )

        except ValueError as ve:
            error_message = str(ve)
            # Use payload.loop_id if available, otherwise use a placeholder
            loop_id_for_log = payload.loop_id if payload and hasattr(payload, 'loop_id') else 'UNKNOWN_LOOP'
            logger.error(f"Pessimist assessment ValueError for loop {loop_id_for_log}: {error_message}")
            justification = f"Mutation risk assessment failed: {error_message}"
            risk_score = 0.9 # High risk if assessment fails
            status = ResultStatus.FAILURE # Corrected from ERROR
            log_justification(
                loop_id=loop_id_for_log,
                agent_id="pessimist",
                action_decision="Mutation Risk Assessment Error",
                justification_text=justification,
                confidence_score=0.2
            )
        except Exception as e:
            # Use payload.loop_id if available, otherwise use a placeholder
            loop_id_for_log = payload.loop_id if payload and hasattr(payload, 'loop_id') else 'UNKNOWN_LOOP'
            # --- Add detailed traceback logging --- 
            tb_str = traceback.format_exc()
            # Log the raw exception type and message FIRST
            logger.error(f"PESSIMIST RAW EXCEPTION loop={loop_id_for_log}: Type={type(e).__name__}, Msg={e}")
            # Construct the detailed message
            error_message = f"Unexpected error during mutation risk assessment: {type(e).__name__} - {e}. Traceback: {tb_str}"
            # Log the detailed message
            logger.error(f"Pessimist assessment unexpected error for loop {loop_id_for_log}: {error_message}", exc_info=False) # Set exc_info to False as we manually added traceback
            # --- End modification --- 
            justification = f"Mutation risk assessment failed unexpectedly: {error_message}"
            risk_score = 0.95 # Very high risk if assessment has unexpected failure
            status = ResultStatus.FAILURE # Corrected from ERROR
            log_justification(
                loop_id=loop_id_for_log,
                agent_id="pessimist",
                action_decision="Mutation Risk Assessment Error",
                justification_text=justification, # Pass the detailed error message
                confidence_score=0.1
            )

        # Use payload.loop_id if available, otherwise use a placeholder
        loop_id_for_return = payload.loop_id if payload and hasattr(payload, 'loop_id') else 'UNKNOWN_LOOP'
        logger.info(f"Pessimist: Returning result for loop {loop_id_for_return}. Status: {status}, Score: {risk_score}")
        # 6. Return Result
        return PessimistRiskAssessmentResult(
            loop_id=loop_id_for_return,
            status=status,
            risk_score=risk_score,
            justification=justification,
            error_message=error_message
        )

    # --- Keep existing placeholder methods below --- 
    # --- They are not used by the mutation risk assessment logic ---

    def evaluate_summary_tone(self, summary: str, feedback: list[Dict[str, Any]]) -> Dict[str, Any]:
        pass

    def detect_optimism_bias(self, tone_evaluation: Dict[str, Any]) -> bool:
        pass

    def detect_vague_summary(self, tone_evaluation: Dict[str, Any]) -> bool:
        pass

    def detect_confidence_mismatch(self, summary: str, plan_confidence_score: Optional[float]) -> bool:
        pass

    def generate_pessimist_alert(self, 
        loop_id: str,
        summary: str,
        feedback: list[Dict[str, Any]],
        plan_confidence_score: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        pass

    def process_loop_summary(self,
        loop_id: str,
        summary: str,
        feedback: list[Dict[str, Any]],
        memory: Dict[str, Any],
        plan_confidence_score: Optional[float] = None
    ) -> Dict[str, Any]:
        pass

    def inject_memory_alert(self, memory: Dict[str, Any], alert: Dict[str, Any]) -> Dict[str, Any]:
        pass

    async def pessimist_check(self, loop_id: str, summary: str) -> Dict[str, Any]:
        pass

    async def analyze_for_bias(self,
        loop_id: str,
        summary: str,
        previous_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        pass

