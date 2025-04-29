from enum import Enum

class StepType(str, Enum):
    BUILD = "build"
    PLAN = "plan"
    REFLECT = "reflect"
    VALIDATE = "validate"
    PATCH = "patch"
    REVIEW = "review"
    END = "end"
