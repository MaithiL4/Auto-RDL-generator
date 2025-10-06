import requests
import json
import os

def generate_rdl_with_ai(sp_name: str, params: dict, fields: dict, table_name: str, connection_string: str, mistral_api_key: str, model_id: str) -> str:
    """
    Generates a new RDL file string using a Mistral AI model.
    """
    # Load the RDL template from a file
    try:
        with open('rdl_template.xml', 'r') as file:
            rdl_template_content = file.read()
    except FileNotFoundError:
        return "Error: rdl_template.xml not found."
    
    # Prepare the prompt for the AI model
    prompt = f"""
You are an expert at generating RDL XML based on a provided template.
Your task is to take the provided RDL template and replace specific sections with new data. Do not change any other parts of the template, including styling, layout, or static text. Provide only the complete RDL XML file in your response.

Stored Procedure Details:
- Stored Procedure Name: {sp_name}
- Parameters: {json.dumps(params)}
- Fields: {json.dumps(fields)}
- Table Name: {table_name}
- Connection String: {connection_string}

Base RDL Template to modify:
{rdl_template_content}
"""
    
    messages = [
        {"role": "user", "content": prompt}
    ]

    headers = {
        "Authorization": f"Bearer {mistral_api_key}",
        "Content-Type": "application/json",
    }
    
    data = {
        "model": model_id,
        "messages": messages,
    }
    
    try:
        # Use the correct Mistral API endpoint
        response = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        
        ai_response = response.json()
        generated_text = ai_response['choices'][0]['message']['content'].strip()

        return generated_text

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - {response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error calling Mistral AI API: {e}")
        return None

# --- Example Usage ---
# WARNING: Do not hardcode your API key in production. Use environment variables.
mistral_api_key = "UFac9Xn6AVKVs7Y2BW6UJylqEu6VqfuB"
your_model_id = "mistral-medium"

# Inputs for your new RDL file
new_sp_name = "new_inventory_report_sp"
new_params = {
    "product_id": "Integer",
    "warehouse_id": "Integer",
    "p_refcur": "cursor",
}
new_fields = {
    "product_name": "System.String",
    "quantity": "System.Decimal",
    "location": "System.String",
}
new_table_name = "Inventory Details"
connection_string = "Server=your_server;Database=your_database;"

# Generate the RDL file content using the AI agent
generated_rdl_content = generate_rdl_with_ai(new_sp_name, new_params, new_fields, new_table_name, connection_string, mistral_api_key, your_model_id)

if generated_rdl_content:
    file_name = f'{new_sp_name}.rdl'
    with open(file_name, 'w') as f:
        f.write(generated_rdl_content)
    
    print(f"RDL file '{file_name}' has been successfully created. 🎉")
else:
    print("Failed to generate RDL.")