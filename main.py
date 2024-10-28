from typing import Annotated, Literal

from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="MDRD GFR Calculator Tool",
    description="API for calculating Glomerular Filtration Rate (GFR) using the MDRD equation.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GFRFormInput(BaseModel):
    """Form-based input schema for calculating MDRD GFR."""

    age: int = Field(
        title="Age",
        ge=18,
        le=120,
        examples=[45],
        description="Enter the patient's age in years. Must be between 18 and 120.",
    )
    serum_creatinine: float = Field(
        title="Serum Creatinine (mg/dL)",
        ge=0.1,
        le=15.0,
        examples=[1.2],
        description="Enter the patient's serum creatinine level in mg/dL. Must be between 0.1 and 15.0.",
    )
    biological_sex: Literal['male', 'female'] = Field(
        title="Biological Sex",
        description="Enter the patient's biological sex: 'male' or 'female'.",
        examples=["male"],
    )
    race_is_black: bool = Field(
        title="Race Indicator",
        description="Specify whether the patient is of Black or African American descent (True = Yes, False = No).",
        examples=[True],
    )


class GFRFormOutput(BaseModel):
    """Form-based output schema for MDRD GFR."""

    gfr: float = Field(
        title="Estimated Glomerular Filtration Rate (GFR)",
        examples=[60.0],
        description="Your calculated GFR in mL/min/1.73m².",
    )


@app.post(
    "/calculate",
    description="Calculate GFR based on MDRD equation using inputs like age, serum creatinine, gender, and race.",
    response_model=GFRFormOutput,
)
async def calculate_gfr(
    data: Annotated[GFRFormInput, Form()],
) -> GFRFormOutput:
    """Calculate GFR using the MDRD equation.

    Args:
        data (GFRFormInput): The input data containing age, serum creatinine, gender, and race.

    Returns:
        GFRFormOutput: The estimated GFR.
    """
    # Constants for MDRD equation
    gender_factor = 0.742 if data.biological_sex.lower() == "female" else 1.0
    race_factor = 1.212 if data.race_is_black else 1.0

    # MDRD equation: GFR = 175 × (Serum Creatinine)^-1.154 × (Age)^-0.203 × (Gender Factor) × (Race Factor)
    gfr_value = (
        175
        * (data.serum_creatinine ** -1.154)
        * (data.age ** -0.203)
        * gender_factor
        * race_factor
    )

    # Optionally, round the result to one decimal place
    gfr_value = round(gfr_value, 1)

    return GFRFormOutput(gfr=gfr_value)
