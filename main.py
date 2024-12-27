from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, confloat, conint
from typing import Annotated, Literal

app = FastAPI(
    title="MDRD GFR Calculator Tool",
    description="API to calculate the estimated Glomerular Filtration Rate (eGFR) using the MDRD equation.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MDRDGFRResult(BaseModel):
    egfr: str = Field(..., title="eGFR", description="Calculated estimated Glomerular Filtration Rate using the MDRD equation.")

def calculate_mdrd_gfr(sex: str, serum_creatinine: float, age: int, race: str) -> float:
    sex_factor = 0.742 if sex == 'female' else 1.0
    race_factor = 1.212 if race == 'black' else 1.0

    gfr = 175 * (serum_creatinine ** -1.154) * (age ** -0.203) * race_factor * sex_factor
    return round(gfr, 1)

@app.post("/calculate_mdrd_gfr", response_model=MDRDGFRResult)
async def calculate_mdrd_gfr_endpoint(
    serum_creatinine: Annotated[confloat(ge=0.01, le=40.0), Form(title="Serum Creatinine (mg/dL)", description="Enter the serum creatinine level in mg/dL. Must be between 0.01 and 40.")] = 1.0,
    age: Annotated[conint(ge=1, le=120), Form(title="Age (years)", description="Enter the age in years. Must be between 1 and 120.")] = 30,
    sex: Annotated[Literal["male", "female"], Form(title="Sex", description="Select the sex. Must be 'male' or 'female'.")] = "male",
    race: Annotated[Literal["black", "non-black", "N/A"], Form(title="Race", description="Select the race. Must be 'black', 'non-black', or 'N/A'.")] = "N/A"
):
    """Calculate eGFR using the MDRD equation based on serum creatinine, age, sex, and race."""
    
    # Adjust race_factor based on the race input if not "N/A"
    race_factor = 1.212 if race == 'black' else 1.0

    gfr = calculate_mdrd_gfr(sex, serum_creatinine, age, race)
    return MDRDGFRResult(egfr=f'{gfr} ml/min/1.73 m² (Estimated GFR by MDRD)')
