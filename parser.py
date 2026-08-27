from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

class LearningStage(BaseModel):
    name: str = Field(
        description="Name of this learning stage."
    )

    topics: list[str] = Field(
        description="Important topics to learn in this stage, in logical order."
    )


class LearningPath(BaseModel):
    learning_stages: list[LearningStage] = Field(
        description="Ordered learning stages that form the complete learning roadmap."
    )

    learning_goal_summary: str = Field(
        description="A concise summary of what the learner should understand or accomplish after completing the roadmap."
    )
    
def create_parser()->PydanticOutputParser:
    """
    Create and return the Pydantic output parser.
    """
    return PydanticOutputParser(pydantic_object=LearningPath)    