from pydantic import BaseModel, Field


class ClaudeModel(BaseModel):
    """
    Docstring for ClaudeModel
    """
    display_name: str = Field(
        ..., 
        min_length=1, 
        description="Display name of the Anthropic model"
        )
    
    id: str = Field(
        ..., 
        min_length=1, 
        pattern=r"^claude-", 
        description="Anthropic model ID"
        )


class OpenAIModel(BaseModel):
    """
    Docstring for OpenAIModel
    """
    display_name: str = Field(
        ..., 
        min_length=0, 
        description="Display name of the OpenAI model. Intentionally left blank to keep in line with ClaudeModel"
        )

    id: str = Field(
        ...,
        min_length=1,
        description="OpenAI model ID"
    )


class DisplayModel(BaseModel):
    """
    Docstring for DisplayModel
    """
    provider: str = Field(
        ..., 
        min_length=1, 
        description="Provider. Either Anthropic or OpenAI",
        examples=["Anthropic", "OpenAI"]
        )
    display_name: str = Field(
        ..., 
        min_length=0, 
        description="Display name of the model. Can be blank."
        )
    id: str = Field(
        ...,
        min_length=1,
        description="Model ID"
    )