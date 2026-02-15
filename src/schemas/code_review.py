from enum import Enum
from typing import Optional
from pydantic import Field, BaseModel, field_validator



class Severity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


class CodeIssue(BaseModel):
    line : int = Field(ge = 1)
    severity : Severity
    description : str = Field(min_length = 10)
    suggested_fix: Optional[str] = Field(default=None)


class CodeReviewResult(BaseModel):
    overall_score : int = Field(ge = 1, le = 10)
    issues : list[CodeIssue]
    summary : str = Field(min_length=20)
    @field_validator("issues")
    @classmethod
    def validate_issues(cls, v):
        for issue in v:
            if issue.severity == Severity.CRITICAL and not issue.suggested_fix:
                raise ValueError("Critical issues must have a suggested fix.")
        return v
    
    