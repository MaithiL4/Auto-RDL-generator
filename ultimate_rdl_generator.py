
import streamlit as st
import sys
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom

# --- XML and RDL Generation Logic ---
# This section contains the core functions for creating the RDL file.
# It uses the robust ElementTree library for safe and reliable XML manipulation.

# Register the RDL namespace to keep the output XML clean.
ET.register_namespace('', "http://schemas.microsoft.com/sqlserver/reporting/2003/10/reportdefinition")

def map_db_type_to_rdl_type(db_type: str) -> str:
    """
    Converts database data types (like 'integer' or 'character varying')
    into their corresponding RDL data types ('Integer', 'String').
    """
    db_type_lower = db_type.lower()
    if db_type_lower == 'integer':
        return 'Integer'
    if 'char' in db_type_lower:
        return 'String'
    if db_type_lower == 'refcursor':
        return 'cursor'
    # Default to capitalizing the type if no specific mapping is found.
    return db_type.capitalize()

def create_header_cell(field_name: str, ns_map: dict) -> ET.Element:
    """
    Creates the XML for a table header cell for a given field.
    Returns an ElementTree element.
    """
    # Convert snake_case to Title Case with spaces, and handle CamelCase
    header_text = field_name.replace('_', ' ')
    header_text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', header_text).title()

    cell_xml = f'''
    <TableCell xmlns="{ns_map['rdl']}">
        <ReportItems>
            <Textbox Name="Header{field_name}">
                <Style>
                    <FontFamily>Calibri</FontFamily>
                    <FontSize>11pt</FontSize>
                    <Color>#666666</Color>
                    <TextAlign>Center</TextAlign>
                    <PaddingLeft>8pt</PaddingLeft>
                    <PaddingRight>5pt</PaddingRight>
                    <PaddingTop>5pt</PaddingTop>
                    <PaddingBottom>5pt</PaddingBottom>
                    <FontWeight>700</FontWeight>
                    <BackgroundColor>#FAFAFA</BackgroundColor>
                    <BorderColor>
                        <Bottom>#dfdfdf</Bottom>
                        <Left>#dfdfdf</Left>
                        <Top>#dfdfdf</Top>
                        <Right>#dfdfdf</Right>
                    </BorderColor>
                    <BorderStyle>
                        <Bottom/>
                        <Left/>
                        <Top/>
                        <Right/>
                    </BorderStyle>
                </Style>
                <Top>.3in</Top>
                <Left>.3in</Left>
                <Height>0in</Height>
                <Width>2pt</Width>
                <CanGrow>true</CanGrow>
                <Value>{header_text}</Value>
            </Textbox>
        </ReportItems>
    </TableCell>
    '''
    return ET.fromstring(cell_xml)

def create_details_cell(field_name: str, ns_map: dict, first_field: str) -> ET.Element:
    """
    Creates the XML for a table data cell for a given field.
    The `first_field` is used for a conditional formatting rule in the template.
    Returns an ElementTree element.
    """
    cell_xml = f'''
    <TableCell xmlns="{ns_map['rdl']}">
        <ReportItems>
            <Textbox Name="Details{field_name}">
                <Style>
                    <FontFamily>Verdana, Arial, Helvetica</FontFamily>
                    <FontSize>10pt</FontSize>
                    <TextAlign>Center</TextAlign>
                    <PaddingLeft>8pt</PaddingLeft>
                    <PaddingRight>2pt</PaddingRight>
                    <PaddingTop>10pt</PaddingTop>
                    <PaddingBottom>10pt</PaddingBottom>
                    <BorderColor>
                        <Right>#dfdfdf</Right>
                        <Top>#dfdfdf</Top>
                        <Bottom>#dfdfdf</Bottom>
                        <Left>#dfdfdf</Left>
                    </BorderColor>
                    <BorderStyle/>
                    <BackgroundColor>=iif(RowNumber(Nothing) Mod 2, "#FFFFFF","#FFFFFF")</BackgroundColor>
                    <Color>=iif(Fields!{first_field}.Value < 0, "#000000","#222222")</Color>
                </Style>
                <Top>0in</Top>
                <Left>0in</Left>
                <Height>.25in</Height>
                <Width>0pt</Width>
                <CanGrow>true</CanGrow>
                <Value>=Fields!{field_name}.Value</Value>
            </Textbox>
        </ReportItems>
    </TableCell>
    '''
    return ET.fromstring(cell_xml)

def generate_rdl_from_parsed_info(sp_name: str, params: dict, fields: list, table_name: str) -> str:
    """
    The main generation function. It takes the parsed SP information,
    loads the 'rdl_template.xml', and injects the new data.
    """
    try:
        # Read the template file as a string and parse it.
        with open('rdl_template_clean.xml', 'r', encoding='utf-8') as f:
            rdl_template_content = f.read()
        root = ET.fromstring(rdl_template_content)
        ns = {'rdl': 'http://schemas.microsoft.com/sqlserver/reporting/2003/10/reportdefinition'}

        # --- Update Stored Procedure Name ---
        command_text_element = root.find('.//rdl:CommandText', ns)
        if command_text_element is not None:
            command_text_element.text = sp_name

        # --- Update Query Parameters ---
        query_params_element = root.find('.//rdl:QueryParameters', ns)
        if query_params_element is not None:
            query_params_element.clear()  # Remove existing parameters
            for name in params:
                if name.lower() != 'p_refcur':
                    qp = ET.SubElement(query_params_element, 'QueryParameter')
                    qp.set('Name', f'@{name}')
                    val = ET.SubElement(qp, 'Value')
                    val.text = f'=Parameters!{name}.Value'
            # Add the required 'refcursor' parameter
            qp_ref = ET.SubElement(query_params_element, 'QueryParameter')
            qp_ref.set('Name', 'refcursor')
            ET.SubElement(qp_ref, 'Value')

        # --- Update Fields ---
        fields_element = root.find('.//rdl:Fields', ns)
        if fields_element is not None:
            fields_element.clear()  # Remove existing fields
            for name in fields:
                field = ET.SubElement(fields_element, 'Field')
                field.set('Name', name)
                df = ET.SubElement(field, 'DataField')
                df.text = name
                # Default all fields to String type for simplicity, as this is the most common case.
                tn = ET.SubElement(field, 'TypeName')
                tn.text = 'System.String'

        # --- Update Report Parameters ---
        report_params_element = root.find('.//rdl:ReportParameters', ns)
        if report_params_element is not None:
            report_params_element.clear()  # Remove existing report parameters
            for name, data_type in params.items():
                rp = ET.SubElement(report_params_element, 'ReportParameter')
                rp.set('Name', name)
                dt = ET.SubElement(rp, 'DataType')
                dt.text = map_db_type_to_rdl_type(data_type)
                dv = ET.SubElement(rp, 'DefaultValue')
                vs = ET.SubElement(dv, 'Values')
                v = ET.SubElement(vs, 'Value')
                v.text = '-1'  # Default value for all parameters

        # --- Update Table Name ---
        table_element = root.find('.//rdl:Table', ns)
        if table_element is not None:
            table_element.set('Name', table_name)

        # --- Update Table Columns ---
        table_columns_element = root.find('.//rdl:TableColumns', ns)
        if table_columns_element is not None:
            table_columns_element.clear()
            for _ in fields:
                tc = ET.SubElement(table_columns_element, 'TableColumn')
                w = ET.SubElement(tc, 'Width')
                w.text = '0pt' # Use 0pt width as per your reference files

        # --- Update Header Cells ---
        header_cells_element = root.find('.//rdl:Header//rdl:TableCells', ns)
        if header_cells_element is not None:
            header_cells_element.clear()
            for name in fields:
                header_cells_element.append(create_header_cell(name, ns))

        # --- Update Details Cells ---
        details_cells_element = root.find('.//rdl:Details//rdl:TableCells', ns)
        if details_cells_element is not None:
            details_cells_element.clear()
            first_field = fields[0] if fields else "dummy_field"
            for name in fields:
                details_cells_element.append(create_details_cell(name, ns, first_field))

        # --- Finalize XML Output ---
        # Convert the ElementTree object to a string.
        rough_string = ET.tostring(root, 'utf-8')
        # Use minidom to "prettify" the XML with proper indentation.
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="\t", encoding="utf-8").decode('utf-8')

        # Clean up extra newlines and ensure the CDATA section for the connection string is correct.
        final_xml = '\n'.join(line for line in pretty_xml.splitlines() if line.strip())
        return final_xml.replace('<ConnectString>##CONNECTION_STRING##</ConnectString>', '<ConnectString><![CDATA[##CONNECTION_STRING##]]></ConnectString>')

    except FileNotFoundError:
        return "Error: rdl_template.xml not found. Please make sure it's in the same directory."
    except Exception as e:
        return f"An unexpected error occurred during RDL generation: {e}"


# --- SQL Parsing Logic ---
# This function uses regular expressions to "intelligently" parse the
# CREATE PROCEDURE script and extract the necessary metadata.

def parse_sp_definition(sp_text: str) -> tuple:
    """
    Parses the 'CREATE PROCEDURE' T-SQL script to extract the
    procedure name, its parameters, and the output fields from the SELECT query.
    """
    # Extract procedure name
    sp_name_match = re.search(r'PROCEDURE\s+([\w\.]+)', sp_text, re.IGNORECASE)
    sp_name = sp_name_match.group(1) if sp_name_match else 'Unknown_SP'

    # Extract parameters from the procedure definition
    params = {}
    param_block_match = re.search(r'CREATE(?: OR REPLACE)? PROCEDURE[\s\w\.]*\((.*?)\)', sp_text, re.DOTALL | re.IGNORECASE)
    if param_block_match:
        param_text = param_block_match.group(1)
        # Find all 'IN' or 'INOUT' parameters and their types
        param_matches = re.findall(r'IN(?:OUT)?\s+(\w+)\s+([\w\s]+(?:varying)?)', param_text, re.IGNORECASE)
        for match in param_matches:
            params[match[0]] = match[1].strip()

    # Extract fields from the 'sql_query' variable within the procedure
    fields = []
    sql_query = None

    # Try to find the query in a 'sql_query' variable
    sql_query_match = re.search(r'sql_query\s*:=\s*\'(.*?)\';', sp_text, re.DOTALL | re.IGNORECASE)
    if sql_query_match:
        sql_query = sql_query_match.group(1)
    else:
        # If not found, try to find the query in an 'OPEN ... FOR' statement
        open_for_match = re.search(r'OPEN\s+\w+\s+FOR\s+(.*?);', sp_text, re.DOTALL | re.IGNORECASE)
        if open_for_match:
            sql_query = open_for_match.group(1)

    if sql_query:
        # This regex is simplified to find any 'AS alias' pattern.
        aliases = re.findall(r'AS\s+(\w+)', sql_query, re.IGNORECASE)
        fields = aliases

    return sp_name, params, fields


# --- Streamlit User Interface ---
# This is the main function that runs the web UI.

def main():
    """
    Defines and runs the Streamlit web application.
    """
    st.set_page_config(page_title="Ultimate RDL Generator", layout="wide")
    st.title("📄 Ultimate RDL Generator")
    st.markdown("Paste your `CREATE PROCEDURE` script below. The script will automatically detect the procedure name, parameters, and fields to generate a ready-to-use RDL file.")

    # Text area for user to paste their SQL script
    sql_script = st.text_area("Enter SQL Script Here:", height=350, placeholder="CREATE OR REPLACE PROCEDURE...")

    if not sql_script:
        st.info("Waiting for you to paste a SQL script. 📝")
        st.stop()

    try:
        # Parse the script to get the metadata
        sp_name, params, fields = parse_sp_definition(sql_script)

        # Display the information that was automatically detected
        with st.expander("✅ Auto-Detected Information", expanded=True):
            st.write(f"**Procedure Name:** `{sp_name}`")
            st.write(f"**Parameters:** `{params}`")
            st.write(f"**Detected Fields:** `{fields}`")

        # Allow user to manually override fields if detection fails
        if not fields:
            st.warning("Could not automatically detect output fields from the query.")
            fields_str = st.text_input("Please enter the fields manually, separated by commas (e.g., field1,field2):")
            if fields_str:
                fields = [f.strip() for f in fields_str.split(',') if f.strip()]

        # Suggest a default table name based on the SP name
        default_table_name = sp_name.split('.')[-1].replace('_', ' ').title()
        table_name = st.text_input("Enter a name for the report table:", value=default_table_name)
        
        st.markdown("---")

        # The main generation button
        if st.button("🚀 Generate RDL File", use_container_width=True):
            if not fields:
                st.error("Cannot generate RDL without fields. Please enter them manually above.")
            elif not table_name:
                st.error("Table name cannot be empty.")
            else:
                with st.spinner('Building your RDL file... Please wait.'):
                    # Call the generation function
                    generated_rdl_content = generate_rdl_from_parsed_info(sp_name, params, fields, table_name)
                
                if generated_rdl_content.startswith('Error') or generated_rdl_content.startswith('An unexpected error'):
                    st.error(generated_rdl_content)
                else:
                    st.success(f"RDL file content generated successfully!")
                    output_file_name = f"{sp_name.split('.')[-1]}.rdl"
                    
                    # Add a download button for the generated file
                    st.download_button(
                        label="📥 Download .rdl File",
                        data=generated_rdl_content.encode('utf-8'),
                        file_name=output_file_name,
                        mime='application/xml',
                        use_container_width=True
                    )
                    # Display the generated XML in a code block
                    st.code(generated_rdl_content, language='xml', line_numbers=True)

    except Exception as e:
        st.error(f"An error occurred while parsing the script: {e}")

# --- Entry Point ---
# This allows the script to be run directly from the command line.
if __name__ == "__main__":
    # Check if Streamlit is installed. If not, provide instructions.
    try:
        import streamlit
    except ImportError:
        print("---")
        print("Error: Streamlit is not installed.")
        print("Please install it by running: pip install streamlit")
        print("Then run this script again with: streamlit run ultimate_rdl_generator.py")
        print("---")
        sys.exit(1)
        
    main()
