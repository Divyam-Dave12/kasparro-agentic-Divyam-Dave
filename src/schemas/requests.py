from pydantic import BaseModel, Field


class UserRequest(BaseModel):
    """
    Entry-point request schema.
    Defines the contract for external inputs into the system.
    """

    user_input: str = Field(
        ...,
        description="Raw natural language request from the user"
    )
