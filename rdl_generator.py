import xml.etree.ElementTree as ET
from xml.dom import minidom
import re

# Register the default namespace to avoid long namespace prefixes in the output
ET.register_namespace('', "http://schemas.microsoft.com/sqlserver/reporting/2003/10/reportdefinition")

def map_db_type_to_rdl_type(db_type):
    """Maps common database data types to RDL data types."""
    db_type_lower = db_type.lower()
    if db_type_lower == 'integer':
        return 'Integer'
    if db_type_lower == 'character varying':
        return 'String'
    if db_type_lower == 'refcursor':
        return 'cursor' # Keep this special type as is
    # Default to returning the original type if no specific mapping is found
    return db_type

def create_header_cell(field_name, ns_map):
    """Creates the XML for a header TableCell as an ET element."""
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
                <Value>{field_name}</Value>
            </Textbox>
        </ReportItems>
    </TableCell>'''
    return ET.fromstring(cell_xml)

def create_details_cell(field_name, ns_map):
    """Creates the XML for a details TableCell as an ET element."""
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
                    <Color>=iif(Fields!leadid.Value &lt; 0, "#000000","#222222")</Color>
                </Style>
                <Top>0in</Top>
                <Left>0in</Left>
                <Height>.25in</Height>
                <Width>0pt</Width>
                <CanGrow>true</CanGrow>
                <Value>=Fields!{field_name}.Value</Value>
            </Textbox>
        </ReportItems>
    </TableCell>'''
    return ET.fromstring(cell_xml)

def generate_rdl(sp_name: str, params: dict, fields: dict, table_name: str) -> str:
    """
    Generates a new RDL file string by parsing the template and modifying the XML tree.
    """
    try:
        tree = ET.parse('rdl_template.xml')
        root = tree.getroot()
        ns = {'rdl': 'http://schemas.microsoft.com/sqlserver/reporting/2003/10/reportdefinition'}

        # 1. Update Stored Procedure Name
        command_text_element = root.find('.//rdl:CommandText', ns)
        if command_text_element is not None:
            command_text_element.text = sp_name

        # 2. Update Query Parameters
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

        # 3. Update Fields
        fields_element = root.find('.//rdl:Fields', ns)
        if fields_element is not None:
            fields_element.clear()
            for name, data_type in fields.items():
                field = ET.SubElement(fields_element, 'Field')
                field.set('Name', name)
                df = ET.SubElement(field, 'DataField')
                df.text = name
                tn = ET.SubElement(field, 'TypeName')
                tn.text = data_type

        # 4. Update Report Parameters
        report_params_element = root.find('.//rdl:ReportParameters', ns)
        if report_params_element is not None:
            report_params_element.clear()
            for name, data_type in params.items():
                rp = ET.SubElement(report_params_element, 'ReportParameter')
                rp.set('Name', name)
                dt = ET.SubElement(rp, 'DataType')
                dt.text = map_db_type_to_rdl_type(data_type) # Use the mapping function
                dv = ET.SubElement(rp, 'DefaultValue')
                vs = ET.SubElement(dv, 'Values')
                v = ET.SubElement(vs, 'Value')
                v.text = '-1'

        # 5. Update Table Name
        table_element = root.find('.//rdl:Table', ns)
        if table_element is not None:
            table_element.set('Name', table_name)

        # 6. Update Table Columns
        table_columns_element = root.find('.//rdl:TableColumns', ns)
        if table_columns_element is not None:
            table_columns_element.clear()
            for _ in fields:
                tc = ET.SubElement(table_columns_element, 'TableColumn')
                w = ET.SubElement(tc, 'Width')
                w.text = '1in'

        # 7. Update Header Cells
        header_cells_element = root.find('.//rdl:Header//rdl:TableCells', ns)
        if header_cells_element is not None:
            header_cells_element.clear()
            for name in fields:
                cell_element = create_header_cell(name, ns)
                header_cells_element.append(cell_element)

        # 8. Update Details Cells
        details_cells_element = root.find('.//rdl:Details//rdl:TableCells', ns)
        if details_cells_element is not None:
            details_cells_element.clear()
            for name in fields:
                cell_element = create_details_cell(name, ns)
                details_cells_element.append(cell_element)

        # Convert the XML tree to a string and prettify it
        rough_string = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="\t", encoding="utf-8").decode('utf-8')
        
        # Remove extra blank lines and fix the connection string CDATA
        final_xml = '\n'.join(line for line in pretty_xml.splitlines() if line.strip())
        final_xml = final_xml.replace('<ConnectString>##CONNECTION_STRING##</ConnectString>', '<ConnectString><![CDATA[##CONNECTION_STRING##]]></ConnectString>')
        return final_xml

    except FileNotFoundError:
        return "Error: rdl_template.xml not found."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

if __name__ == "__main__":
    print("--- RDL Generator (Final Version) ---")
    
    def parse_input_string(input_str):
        result_dict = {}
        items = [item.strip() for item in input_str.split(',') if item.strip()]
        for item in items:
            parts = []
            if ':' in item:
                parts = [p.strip() for p in item.split(':', 1)]
            else:
                # Find the first space to separate name and type
                first_space_index = item.find(' ')
                if first_space_index != -1:
                    name = item[:first_space_index].strip()
                    type_val = item[first_space_index+1:].strip()
                    parts = [name, type_val]
            
            if len(parts) == 2:
                result_dict[parts[0]] = parts[1]
            else:
                raise ValueError(f"Invalid format for item: '{item}'. Please use 'name:type' or 'name type'.")
        return result_dict

    # Get inputs from the user
    new_sp_name = input("\nEnter the stored procedure name: ")
    
    print("\nEnter the parameters, separated by commas.")
    print("Use 'name:type' or 'name type' format (e.g., ownerid:Integer, filter character varying)")
    params_str = input("Parameters: ")
    
    try:
        new_params = parse_input_string(params_str)
    except ValueError as e:
        print(f"\nError parsing parameters: {e}")
        exit()

    print("\nEnter the fields, separated by commas.")
    print("Use 'name:type' or 'name type' format (e.g., product_name:System.String, region String)")
    fields_str = input("Fields: ")

    try:
        new_fields = parse_input_string(fields_str)
    except ValueError as e:
        print(f"\nError parsing fields: {e}")
        print("Please check your input and try again.")
        exit()

    new_table_name = input("\nEnter the table name for the report: ")
    output_file_name = input("Enter the desired output file name (e.g., my_report.rdl): ")

    # Generate the RDL file content
    generated_rdl_content = generate_rdl(new_sp_name, new_params, new_fields, new_table_name)

    if generated_rdl_content.startswith('Error') or generated_rdl_content.startswith('An unexpected error'):
        print(f"\n{generated_rdl_content}")
    else:
        with open(output_file_name, 'w', encoding='utf-8') as f:
            f.write(generated_rdl_content)
        print(f"\nRDL file '{output_file_name}' has been successfully created.")