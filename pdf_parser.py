import os
import json
import base64
import argparse
import csv
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm
from model_config import get_model_info, list_available_models
from cost_monitor import CostMonitor
from pydantic import BaseModel
# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def encode_pdf_to_base64(file_path: str) -> str:
    """Encode PDF file to base64 string."""
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode("utf-8")

def process_single_pdf(pdf_path: str, model_name: str, cost_monitor: CostMonitor) -> Dict[str, Any]:
    """Process a single PDF file using GPT API."""
    base64_string = encode_pdf_to_base64(pdf_path)
    model_info = get_model_info(model_name)
    
    
    class StructuralProperties(BaseModel):
        aromatic_ring_count: int
        fused_ring_presence: int
        linkage_type: str
        steric_bulk: str
        degree_of_sulfonation_or_grafting: str
        cation_type: str
        acidic_proton: int
        acidic_proton_position: str

    class MorphologicalProperties(BaseModel):
        water_uptake_percent: str
        koh_uptake_percent: str
        free_volume_nm3_per_g: str
        swelling_degree_alkaline: str
        porosity_description: str

    class ConductivityProperties(BaseModel):
        conductivity_oh_mS_per_cm: float
        temperature_conductivity_tested: int
        koh_concentration_tested_M: str
        aging_time_in_alkaline_conditions: int

    class PolymerData(BaseModel):
        sample_id: str
        aromatic_ring_count: int
        fused_ring_presence: int
        linkage_type: str
        steric_bulk: str
        degree_of_sulfonation_or_grafting: str
        cation_type: str
        acidic_proton: int
        acidic_proton_position: str
        water_uptake_percent: str
        koh_uptake_percent: str
        free_volume_nm3_per_g: str
        swelling_degree_alkaline: str
        porosity_description: str
        conductivity_oh_mS_per_cm: float
        temperature_conductivity_tested: int
        koh_concentration_tested_M: str
        aging_time_in_alkaline_conditions: int

    class PolymerDataResponse(BaseModel):
        data: list[PolymerData]

    
    
    prompt = """Extract the data from the text in this paper, but extract the fields below as columns and tabulate them.
    
🔸 Structural
	•	aromatic_ring_count: count of aromatic rings in the polymer structure
	•	fused_ring_presence: presence of fused aromatic rings in the structure
	•	linkage_type: type of chemical bonds connecting polymer units
	•	steric_bulk: presence of bulky substituents affecting molecular structure
	•	degree_of_sulfonation_or_grafting: extent of sulfonation or grafting modifications
	•	cation_type ✅: type of cation present in the polymer
	•	acidic_proton ✅: presence of acidic protons in the structure
	•	acidic_proton_position ✅: location of acidic protons in the structure

🔸 Morphological & Environmental
	•	water_uptake_percent: percentage of water absorbed by the material
	•	koh_uptake_percent: percentage of KOH solution absorbed
	•	free_volume_nm3_per_g: free volume per gram in cubic nanometers
	•	swelling_degree_alkaline: extent of swelling in alkaline conditions
	•	porosity_description: description of material's porous structure

🔸 Conductivity
	•	conductivity_oh_mS_per_cm: ionic conductivity in millisiemens per centimeter
	•	temperature_conductivity_tested: temperature range for conductivity testing
	•	koh_concentration_tested_M: KOH concentration used in testing (molarity)
	•	aging_time_in_alkaline_conditions: duration of aging in alkaline environment
    
Please extract dataset and return it in the format of the PolymerDataResponse model.
Even if it's the same sample, if the values are different, organize them into separate rows.

Here is an example of the output data format:
Sample ID,aromatic_ring_count,fused_ring_presence,linkage_type,steric_bulk,degree_of_sulfonation_or_grafting,cation_type,acidic_proton,acidic_proton_position,water_uptake_percent,koh_uptake_percent,free_volume_nm3_per_g,swelling_degree_alkaline,porosity_description,conductivity_oh_mS_per_cm,temperature_conductivity_tested,koh_concentration_tested_M,aging_time_in_alkaline_conditions
TTT-PEMP,3,0,C–S,1,UV-cured,None,0,NA,N/A,N/A,N/A,Low,Gel-like,0.589,30,~1,0
TTT-PEMP,3,0,C–S,1,UV-cured,None,0,NA,N/A,N/A,N/A,Low,Gel-like,1.55,60,~1,0
TTT-PEMP-PEGDA,3,0,C–S,0,UV-cured,None,0,NA,N/A,N/A,N/A,Moderate,Gel-like,1.74,90,~1,0
TTT-PEMP-PDMS,3,0,C–S,Partial,UV-cured,None,0,NA,N/A,N/A,N/A,Moderate,Gel-like,0.442,30,~1,0
TTT-PEMP-PDMS,3,0,C–S,Partial,UV-cured,None,0,NA,N/A,N/A,N/A,Moderate,Gel-like,1.11,60,~1,0

"""

    try:
        response = client.responses.parse(
            model=model_name,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_file",
                            "filename": os.path.basename(pdf_path),
                            "file_data": f"data:application/pdf;base64,{base64_string}",
                        },
                        {
                            "type": "input_text",
                            "text": prompt,
                        },
                    ],
                }
            ],
            text_format=PolymerDataResponse,
        )
        
        # Calculate and log cost
        input_tokens = len(prompt.split())  # Approximate token count
        output_tokens = len(response.output_text.split())  # Approximate token count
        cost = cost_monitor.log_request(model_name, pdf_path, input_tokens, output_tokens, model_info=model_info)
        
        # Use the parsed response directly
        if response.output_parsed:
            result = {
                "data": response.output_parsed.data,
                "cost": cost
            }
        else:
            result = {
                "error": "No data parsed from response",
                "raw_response": response.output_text,
                "cost": cost
            }
        
        return result
    
    except Exception as e:
        return {
            "error": str(e),
            "file": pdf_path
        }

def process_pdfs(pdf_paths: List[str], model_name: str, output_file: str = "results.csv"):
    """Process multiple PDF files and save results to a CSV file."""
    results = []
    cost_monitor = CostMonitor()
    
    for pdf_path in tqdm(pdf_paths, desc="Processing PDFs"):
        result = process_single_pdf(pdf_path, model_name, cost_monitor)
        
        if "error" not in result:
            # Get the parsed data from the response
            polymer_data = result.get("data", [])
            
            # Write results to CSV file
            output_file_with_prefix = f"{os.path.splitext(os.path.basename(pdf_path))[0]}_{output_file}"
            
            # Get field names from the first row if available
            if polymer_data:
                # Convert Pydantic models to dictionaries
                data_to_write = [item.model_dump() for item in polymer_data]
                fieldnames = list(data_to_write[0].keys())
                
                with open(output_file_with_prefix, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data_to_write)
                
                print(f"CSV file saved: {output_file_with_prefix}")
            else:
                print(f"No data extracted from {pdf_path}")
        else:
            print(f"Error processing {pdf_path}: {result['error']}")
    
    # Save cost summary
    cost_monitor.save_summary()
    
    return results

def parse_csv_to_markdown(csv_file: str, markdown_file: str):
    """Parse CSV results into a markdown table and save it as a markdown file."""
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            if not fieldnames:
                print(f"No data found in {csv_file}")
                return
            
            # Create the markdown table header
            markdown_content = "| " + " | ".join(fieldnames) + " |\n"
            markdown_content += "| " + " | ".join(["---"] * len(fieldnames)) + " |\n"
            
            # Add each row to the markdown table
            for row in reader:
                markdown_content += "| " + " | ".join(str(row.get(field, "")) for field in fieldnames) + " |\n"
        
        # Use ChatGPT API to interpret the results in Korean
        prompt = f"Interpret the following data in Korean and summarize it in a markdown table format:\n{markdown_content}"
        try:
            response = client.responses.create(
                model="gpt-4.1-nano",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": prompt,
                            },
                        ],
                    }
                ]
            )
            
            # Write the interpreted markdown content to the markdown file
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(response.output_text)
            
            print(f"Markdown report saved to {markdown_file}")
        except Exception as e:
            print(f"Error interpreting results: {e}")
            
    except Exception as e:
        print(f"Error reading CSV file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Process PDF files using ChatGPT API")
    parser.add_argument("--model", type=str, default="gpt-4.1-nano",
                      help="Model to use for processing")
    parser.add_argument("--list-models", action="store_true",
                      help="List available models and exit")
    parser.add_argument("--enable-report", action="store_true",
                      help="Enable markdown report generation")
    parser.add_argument("files", nargs="*", help="PDF files to process")
    
    args = parser.parse_args()
    
    if args.list_models:
        print("🤖 사용 가능한 모델:")
        for name, desc in list_available_models().items():
            print(f"📌 {name}: {desc}")
        return
    
    # Get PDF files from command line arguments or use default
    if args.files:
        pdf_paths = args.files
    else:
        # Use all PDF files in the current directory
        pdf_paths = list(Path('.').glob('*.pdf'))
    
    if not pdf_paths:
        print("⚠️ PDF 파일을 찾을 수 없습니다. 파일 경로를 인자로 제공해주세요.")
        return
    
    # Process PDFs and save results
    results = process_pdfs(pdf_paths, args.model)
    
    # Parse each CSV file to markdown if enabled
    if args.enable_report:
        for pdf_path in pdf_paths:
            csv_file = f"{os.path.splitext(os.path.basename(pdf_path))[0]}_results.csv"
            markdown_file = f"{os.path.splitext(os.path.basename(pdf_path))[0]}_results.md"
            parse_csv_to_markdown(csv_file, markdown_file)

if __name__ == "__main__":
    main() 