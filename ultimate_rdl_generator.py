import streamlit as st
import sys
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom

# --- Your Original Code (Functions) ---
# The only change is inside the generate_rdl_from_parsed_info function.

ET.register_namespace('', "http://schemas.microsoft.com/sqlserver/reporting/2003/10/reportdefinition")

def map_db_type_to_rdl_type(db_type):
    db_type_lower = db_type.lower()
    if db_type_lower == 'integer': return 'Integer'
    if 'char' in db_type_lower: return 'String'
    if db_type_lower == 'refcursor': return 'cursor'
    return db_type.capitalize()

def create_header_cell(field_name, ns_map):
    # This function is correct based on your reference file (Width 2pt, Height 0in)
    cell_xml = f'''<TableCell xmlns="{ns_map['rdl']}"><ReportItems><Textbox Name="Header{field_name}"><Style><FontFamily>Calibri</FontFamily><FontSize>11pt</FontSize><Color>#666666</Color><TextAlign>Center</TextAlign><PaddingLeft>8pt</PaddingLeft><PaddingRight>5pt</PaddingRight><PaddingTop>5pt</PaddingTop><PaddingBottom>5pt</PaddingBottom><FontWeight>700</FontWeight><BackgroundColor>#FAFAFA</BackgroundColor><BorderColor><Bottom>#dfdfdf</Bottom><Left>#dfdfdf</Left><Top>#dfdfdf</Top><Right>#dfdfdf</Right></BorderColor><BorderStyle><Bottom/><Left/><Top/><Right/></BorderStyle></Style><Top>.3in</Top><Left>.3in</Left><Height>0in</Height><Width>2pt</Width><CanGrow>true</CanGrow><Value>{field_name}</Value></Textbox></ReportItems></TableCell>'''
    return ET.fromstring(cell_xml)

def create_details_cell(field_name, ns_map, first_field):
    # This function is correct based on your reference file (Width 0pt, Height .25in)
    cell_xml = f'''<TableCell xmlns="{ns_map['rdl']}"><ReportItems><Textbox Name="Details{field_name}"><Style><FontFamily>Verdana, Arial, Helvetica</FontFamily><FontSize>10pt</FontSize><TextAlign>Center</TextAlign><PaddingLeft>8pt</PaddingLeft><PaddingRight>2pt</PaddingRight><PaddingTop>10pt</PaddingTop><PaddingBottom>10pt</PaddingBottom><BorderColor><Right>#dfdfdf</Right><Top>#dfdfdf</Top><Bottom>#dfdfdf</Bottom><Left>#dfdfdf</Left></BorderColor><BorderStyle/><BackgroundColor>=iif(RowNumber(Nothing) Mod 2, "#FFFFFF","#FFFFFF")</BackgroundColor><Color>=iif(Fields!{first_field}.Value &lt; 0, "#000000","#222222")</Color></Style><Top>0in</Top><Left>0in</Left><Height>.25in</Height><Width>0pt</Width><CanGrow>true</CanGrow><Value>=Fields!{field_name}.Value</Value></Textbox></ReportItems></TableCell>'''
    return ET.fromstring(cell_xml)

def generate_rdl_from_parsed_info(sp_name: str, params: dict, fields: list, table_name: str) -> str:
    try:
        tree = ET.parse('rdl_template.xml')
        root = tree.getroot()
        ns = {'rdl': 'http://schemas.microsoft.com/sqlserver/reporting/2003/10/reportdefinition'}

        command_text_element = root.find('.//rdl:CommandText', ns)
        if command_text_element is not None: command_text_element.text = sp_name

        query_params_element = root.find('.//rdl:QueryParameters', ns)
        if query_params_element is not None:
            query_params_element.clear()
            for name in params:
                if name.lower() != 'p_refcur':
                    qp = ET.SubElement(query_params_element, 'QueryParameter')
                    qp.set('Name', f'@{name}')
                    val = ET.SubElement(qp, 'Value')
                    val.text = f'=Parameters!{name}.Value'
            qp_ref = ET.SubElement(query_params_element, 'QueryParameter')
            qp_ref.set('Name', 'refcursor')
            ET.SubElement(qp_ref, 'Value')

        fields_element = root.find('.//rdl:Fields', ns)
        if fields_element is not None:
            fields_element.clear()
            for name in fields:
                field = ET.SubElement(fields_element, 'Field')
                field.set('Name', name)
                df = ET.SubElement(field, 'DataField')
                df.text = name
                tn = ET.SubElement(field, 'TypeName')
                tn.text = 'System.String' # Default to String as discussed

        report_params_element = root.find('.//rdl:ReportParameters', ns)
        if report_params_element is not None:
            report_params_element.clear()
            for name, data_type in params.items():
                rp = ET.SubElement(report_params_element, 'ReportParameter')
                rp.set('Name', name)
                dt = ET.SubElement(rp, 'DataType')
                dt.text = map_db_type_to_rdl_type(data_type)
                dv = ET.SubElement(rp, 'DefaultValue')
                vs = ET.SubElement(dv, 'Values')
                v = ET.SubElement(vs, 'Value')
                v.text = '-1'

        table_element = root.find('.//rdl:Table', ns)
        if table_element is not None: table_element.set('Name', table_name)

        #********************************************************#
        # THIS IS THE SECTION THAT HAS BEEN CHANGED              #
        #********************************************************#
        table_columns_element = root.find('.//rdl:TableColumns', ns)
        if table_columns_element is not None:
            table_columns_element.clear()
            for _ in fields:
                tc = ET.SubElement(table_columns_element, 'TableColumn')
                w = ET.SubElement(tc, 'Width')
                # Change made here to match your reference file
                w.text = '0pt'
        #********************************************************#
        # END OF CHANGES                                         #
        #********************************************************#

        header_cells_element = root.find('.//rdl:Header//rdl:TableCells', ns)
        if header_cells_element is not None:
            header_cells_element.clear()
            for name in fields:
                header_cells_element.append(create_header_cell(name, ns))

        details_cells_element = root.find('.//rdl:Details//rdl:TableCells', ns)
        if details_cells_element is not None:
            details_cells_element.clear()
            first_field = fields[0] if fields else "dummy_field"
            for name in fields:
                details_cells_element.append(create_details_cell(name, ns, first_field))

        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="\t", encoding="utf-8").decode('utf-8')

        final_xml = '\n'.join(line for line in pretty_xml.splitlines() if line.strip())
        return final_xml.replace('<ConnectString>##CONNECTION_STRING##</ConnectString>', '<ConnectString><![CDATA[##CONNECTION_STRING##]]></ConnectString>')

    except FileNotFoundError:
        return "Error: rdl_template.xml not found. Please make sure it's in the same directory as the app."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def parse_sp_definition(sp_text):
    """Parses the CREATE PROCEDURE text to extract metadata."""
    sp_name_match = re.search(r'PROCEDURE\s+([\w\.]+)', sp_text, re.IGNORECASE)
    sp_name = sp_name_match.group(1) if sp_name_match else 'Unknown_SP'

    params = {}
    param_block_match = re.search(r'CREATE OR REPLACE PROCEDURE[\s\w\.]*\((.*?)\)', sp_text, re.DOTALL | re.IGNORECASE)
    if param_block_match:
        param_text = param_block_match.group(1)
        param_matches = re.findall(r'IN(?:OUT)?\s+(\w+)\s+([\w\s]+(?:varying)?)', param_text, re.IGNORECASE)
        for match in param_matches:
            params[match[0]] = match[1].strip()

    fields = []
    sql_query = None

    sql_query_match = re.search(r'sql_query\s*:=\s*\'(.*?)\';', sp_text, re.DOTALL | re.IGNORECASE)
    if sql_query_match:
        sql_query = sql_query_match.group(1)
    else:
        open_for_match = re.search(r'OPEN\s+\w+\s+FOR\s+(.*?);', sp_text, re.DOTALL | re.IGNORECASE)
        if open_for_match:
            sql_query = open_for_match.group(1)

    if sql_query:
        # Remove comments
        sql_query = re.sub(r'--.*', '', sql_query)
        sql_query = re.sub(r'/\*.*?\*/', '', sql_query, flags=re.DOTALL)

        aliases = re.findall(r'AS\s+(\w+|\"[^\"]+\")', sql_query, re.IGNORECASE)
        # Clean up the aliases by removing quotes
        fields = [alias.replace('"', '') for alias in aliases]

    return sp_name, params, fields

# --- Streamlit UI Code (No changes here) ---

def main():
    st.set_page_config(page_title="RDL Generator", layout="wide")
    st.title("📄 Smart RDL Generator UI")
    st.markdown("Paste your `CREATE PROCEDURE` script into the text area below to generate an RDL file.")

    sql_script = st.text_area("Enter SQL Script Here:", height=300, placeholder="CREATE OR REPLACE PROCEDURE...")

    if not sql_script:
        st.info("Waiting for SQL script input.")
        st.stop()

    try:
        sp_name, params, fields = parse_sp_definition(sql_script)

        with st.expander("✅ Detected Information", expanded=True):
            st.write(f"**Procedure Name:** `{sp_name}`")
            st.write(f"**Parameters:** `{params}`")
            st.write(f"**Detected Fields:** `{fields}`")

        if not fields:
            st.warning("Could not automatically detect output fields.")
            fields_str = st.text_input("Please enter the fields manually, separated by commas (e.g., field1,field2):")
            if fields_str:
                fields = [f.strip() for f in fields_str.split(',') if f.strip()]

        default_table_name = sp_name.split('.')[-1].replace('_', ' ').title()
        table_name = st.text_input("Enter a name for the report table:", value=default_table_name)
        
        st.markdown("---")

        if st.button("🚀 Generate RDL File", use_container_width=True):
            if not fields:
                st.error("Cannot generate RDL without fields. Please enter them manually above.")
            elif not table_name:
                st.error("Table name cannot be empty.")
            else:
                with st.spinner('Generating RDL content...'):
                    generated_rdl_content = generate_rdl_from_parsed_info(sp_name, params, fields, table_name)
                
                if generated_rdl_content.startswith('Error') or generated_rdl_content.startswith('An unexpected error'):
                    st.error(generated_rdl_content)
                else:
                    st.success(f"RDL file content generated successfully!")
                    output_file_name = f"{sp_name.split('.')[-1]}.rdl"
                    
                    st.download_button(
                        label="📥 Download .rdl File",
                        data=generated_rdl_content.encode('utf-8'),
                        file_name=output_file_name,
                        mime='application/xml',
                        use_container_width=True
                    )
                    st.code(generated_rdl_content, language='xml', line_numbers=True)

    except Exception as e:
        st.error(f"An error occurred during parsing: {e}")

if __name__ == "__main__":
    main()