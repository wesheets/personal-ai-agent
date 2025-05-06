import re

class ArchetypeClassifier:
    """
    Classifies a loop intent into one of the predefined archetypes.
    """

    ARCHETYPES = {
        "Explore": {
            "keywords": ["research", "find information", "investigate", "discover", "survey"],
            "description_patterns": [r"gather new information", r"understand a new domain", r"broadly search for solutions"],
            "tool_patterns": ["info_search_web", "browser_navigate"] # Example tools
        },
        "Optimize": {
            "keywords": ["refine", "improve performance", "reduce cost", "tune", "enhance", "optimize"],
            "description_patterns": [r"refining an existing solution", r"iterative improvements", r"parameter tuning"]
        },
        "Refactor": {
            "keywords": ["refactor", "restructure", "improve code readability", "consolidate schemas", "maintainability"],
            "description_patterns": [r"improve the internal structure", r"improve maintainability", r"clarity of an existing system"]
        },
        "Implement": {
            "keywords": ["implement", "build", "create", "develop", "construct", "add feature"],
            "description_patterns": [r"create or build a new component", r"based on a relatively well-defined specification"]
        },
        "Validate_Verify": {
            "keywords": ["validate", "verify", "test", "check consistency", "confirm accuracy", "assert"],
            "description_patterns": [r"check if a system.*conforms to specifications", r"testing, checking consistency"]
        },
        "Debug_Remediate": {
            "keywords": ["debug", "remediate", "fix error", "resolve issue", "troubleshoot", "patch"],
            "description_patterns": [r"identifying and fixing errors", r"reactive process to a known problem"]
        }
    }

    DEFAULT_ARCHETYPE = "Unknown"

    def classify_intent(self, intent_description: str, target_components: list = None, parameters: dict = None, tools_used: list = None) -> str:
        """
        Classifies the loop intent based on its description, target components, parameters, and tools used.

        Args:
            intent_description: The natural language description of the intent.
            target_components: A list of components targeted by the intent.
            parameters: A dictionary of parameters for the intent.
            tools_used: A list of tools planned or used in the loop.

        Returns:
            The classified archetype string.
        """
        if not intent_description:
            return self.DEFAULT_ARCHETYPE

        # Convert intent description to lowercase for case-insensitive matching
        lower_intent_description = intent_description.lower()

        # Prioritize keyword matching
        for archetype, criteria in self.ARCHETYPES.items():
            if "keywords" in criteria:
                for keyword in criteria["keywords"]:
                    if keyword in lower_intent_description:
                        return archetype
        
        # Then try description patterns
        for archetype, criteria in self.ARCHETYPES.items():
            if "description_patterns" in criteria:
                for pattern in criteria["description_patterns"]:
                    if re.search(pattern, lower_intent_description, re.IGNORECASE):
                        return archetype

        # Example: Check for tool usage if other methods don't yield a result
        if tools_used:
            for archetype, criteria in self.ARCHETYPES.items():
                if "tool_patterns" in criteria:
                    for tool_pattern in criteria["tool_patterns"]:
                        if any(tool_pattern in tool for tool in tools_used):
                            return archetype
                            
        # Fallback if no specific archetype is matched
        # More sophisticated logic could be added here, e.g., based on target_components or parameters
        # For now, if keywords or patterns don't match, it's Unknown

        return self.DEFAULT_ARCHETYPE

if __name__ == '__main__':
    classifier = ArchetypeClassifier()

    # Test cases based on phase22_schema_surface_identification.md
    test_intents = [
        {"desc": "Research the latest advancements in quantum computing", "tools": ["info_search_web"]},
        {"desc": "Find information about the Manu civilization"},
        {"desc": "Refine the sorting algorithm for better time complexity"},
        {"desc": "Improve performance of the database query"},
        {"desc": "Refactor the user authentication module to use a new library"},
        {"desc": "Improve code readability of the main controller"},
        {"desc": "Implement the new user profile page as per the design document"},
        {"desc": "Build a module for data export in CSV format"},
        {"desc": "Validate the input data against the new schema version"},
        {"desc": "Test the functionality of the payment gateway integration"},
        {"desc": "Debug the null pointer exception occurring in the reporting service"},
        {"desc": "Fix an error in the user login flow"},
        {"desc": "Analyze the stock market trends for the last quarter"} # Potentially Explore or a new 'Analyze' archetype
    ]

    print("Archetype Classification Test Results:")
    for i, intent_data in enumerate(test_intents):
        desc = intent_data["desc"]
        tools = intent_data.get("tools")
        archetype = classifier.classify_intent(intent_description=desc, tools_used=tools)
        print(f"Intent {i+1}: '{desc}' -> Archetype: {archetype}")

