# app/agents/pessimist_agent.py
import json
import os
import asyncio
import logging
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
    capabilities=[AgentCapability.RISK_ASSESSMENT, AgentCapability.PLANNING] # Example capabilities
)
class PessimistAgent(BaseAgent):
    """Pessimist agent assesses the risk of proposed plans."""

    async def run(self, payload: PessimistRiskAssessmentInput) -> PessimistRiskAssessmentResult:
        """
        Assesses the risk of a proposed plan based on its content and context.
        Logs the risk score and justification.
        """
        logger.info(f"Pessimist agent received risk assessment request for loop: {payload.loop_id}")
        
        risk_score = 0.5 # Default neutral risk
        justification = "Risk assessment failed due to errors."
        status = ResultStatus.ERROR
        error_message = None

        try:
            # 1. Load the proposed plan
            plan_data = load_json_safe(payload.plan_file_path)
            if plan_data is None:
                raise ValueError(f"Failed to load or parse plan file: {payload.plan_file_path}")

            # 2. Load context (beliefs, creed) - Optional, if needed for risk assessment
            # belief_data = load_json_safe(payload.belief_surface_path) if payload.belief_surface_path else None
            # creed_data = load_json_safe(payload.promethios_creed_path) if payload.promethios_creed_path else None

            # 3. Placeholder Risk Assessment Logic
            # Simple check: Higher risk for longer plans?
            # In future, analyze steps for complexity, dependencies, potential failures.
            num_steps = len(plan_data) if isinstance(plan_data, list) else 0
            
            if num_steps == 0:
                risk_score = 0.8 # High risk for empty plan
                justification = "Risk Assessment: High risk due to empty or invalid plan structure."
                logger.warning(f"Pessimist: High risk assessed for empty/invalid plan {payload.plan_file_path}")
            elif num_steps > 5:
                risk_score = 0.7 # Higher risk for longer plans
                justification = f"Risk Assessment: Elevated risk due to plan complexity ({num_steps} steps)."
                logger.info(f"Pessimist: Elevated risk assessed for plan {payload.plan_file_path} ({num_steps} steps)." )
            else:
                risk_score = 0.3 # Lower risk for shorter plans
                justification = f"Risk Assessment: Low risk assessed for plan with {num_steps} steps."
                logger.info(f"Pessimist: Low risk assessed for plan {payload.plan_file_path} ({num_steps} steps)." )
                
            status = ResultStatus.SUCCESS

            # 4. Log Justification
            log_justification(
                loop_id=payload.loop_id,
                agent_id="pessimist",
                action_decision=f"Risk Assessment Score: {risk_score:.2f}",
                justification_text=justification,
                confidence_score=0.8 # Placeholder confidence in assessment
            )

        except ValueError as ve:
            error_message = str(ve)
            logger.error(f"Pessimist assessment error for loop {payload.loop_id}: {error_message}")
            justification = f"Risk assessment failed: {error_message}"
            risk_score = 0.9 # High risk if assessment fails
            status = ResultStatus.ERROR
            log_justification(
                loop_id=payload.loop_id,
                agent_id="pessimist",
                action_decision="Risk Assessment Error",
                justification_text=justification,
                confidence_score=0.2
            )
        except Exception as e:
            error_message = f"Unexpected error during risk assessment: {e}"
            logger.error(f"Pessimist assessment unexpected error for loop {payload.loop_id}: {error_message}", exc_info=True)
            justification = f"Risk assessment failed unexpectedly: {error_message}"
            risk_score = 0.95 # Very high risk if assessment has unexpected failure
            status = ResultStatus.ERROR
            log_justification(
                loop_id=payload.loop_id,
                agent_id="pessimist",
                action_decision="Risk Assessment Error",
                justification_text=justification,
                confidence_score=0.1
            )

        # 5. Return Result
        return PessimistRiskAssessmentResult(
            loop_id=payload.loop_id,
            status=status,
            risk_score=risk_score,
            justification=justification,
            error_message=error_message
        )

    # --- Keep existing methods below for potential future use or refactoring ---
    # --- but they are not directly used by the new `run` method for Batch 18.1 ---
    
    def evaluate_summary_tone(self, summary: str, feedback: List[Dict[str, Any]]) -> Dict[str, Any]:
        # ... (existing implementation) ...
        pass

    def detect_optimism_bias(self, tone_evaluation: Dict[str, Any]) -> bool:
        # ... (existing implementation) ...
        pass

    def detect_vague_summary(self, tone_evaluation: Dict[str, Any]) -> bool:
        # ... (existing implementation) ...
        pass

    def detect_confidence_mismatch(self, summary: str, plan_confidence_score: Optional[float]) -> bool:
        # ... (existing implementation) ...
        pass

    def generate_pessimist_alert(self, 
        loop_id: str,
        summary: str,
        feedback: List[Dict[str, Any]],
        plan_confidence_score: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        # ... (existing implementation) ...
        pass

    def process_loop_summary(self,
        loop_id: str,
        summary: str,
        feedback: List[Dict[str, Any]],
        memory: Dict[str, Any],
        plan_confidence_score: Optional[float] = None
    ) -> Dict[str, Any]:
        # ... (existing implementation) ...
        pass

    def inject_memory_alert(self, memory: Dict[str, Any], alert: Dict[str, Any]) -> Dict[str, Any]:
        # ... (existing implementation) ...
        pass

    async def pessimist_check(self, loop_id: str, summary: str) -> Dict[str, Any]:
        # ... (existing implementation) ...
        pass

    async def analyze_for_bias(self,
        loop_id: str,
        summary: str,
        previous_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # ... (existing implementation) ...
        pass

