from xml.dom import minidom

def generate_rdl_from_template(sp_name: str, params: dict, fields: dict, table_name: str, connection_string: str) -> str:
    """
    Generates a new RDL file string from a template by replacing stored procedure details.

    Args:
        sp_name (str): The new stored procedure name.
        params (dict): Dictionary of parameters (e.g., {"ownerid": "Integer", "userid": "Integer"}).
        fields (dict): Dictionary of fields (e.g., {"rn": "System.String", "Status": "System.String"}).
        table_name (str): The name for the report table.
        connection_string (str): The database connection string.

    Returns:
        str: The complete, updated RDL file as a string.
    """
    # Load your RDL template
    with open('rdl_template_modified.xml', 'r') as file:
        rdl_content = file.read()

    # --- Perform substitutions ---
    connection_properties = f'''<ConnectionProperties>
				<DataProvider>NPGSQL</DataProvider>
				<ConnectString><![CDATA[{connection_string}]]></ConnectString>
				<IntegratedSecurity>true</IntegratedSecurity>
			</ConnectionProperties>'''
    rdl_content = rdl_content.replace('<!--CONNECTION_PROPERTIES-->', connection_properties)
    
    rdl_content = rdl_content.replace('<!--SP_NAME-->', sp_name)
    rdl_content = rdl_content.replace('##TABLE_NAME##', table_name)

    # Generate and replace query parameters
    query_params_xml = "".join([f'<QueryParameter Name="@{name}"><Value>=Parameters!{name}.Value</Value></QueryParameter>' for name in params.keys() if name != 'p_refcur'])
    query_params_xml += '<QueryParameter Name="refcursor"><Value/></QueryParameter>'
    rdl_content = rdl_content.replace('<!--QUERY_PARAMETERS-->', query_params_xml)

    # Generate and replace fields
    fields_xml = "".join([f'<Field Name="{name}"><DataField>{name}</DataField><TypeName>{data_type}</TypeName></Field>' for name, data_type in fields.items()])
    rdl_content = rdl_content.replace('<!--FIELDS-->', fields_xml)

    # Generate and replace report parameters
    report_params_xml = "".join([f'<ReportParameter Name="{name}"><DataType>{data_type}</DataType><DefaultValue><Values><Value>-1</Value></Values></DefaultValue></ReportParameter>' for name, data_type in params.items()])
    rdl_content = rdl_content.replace('<!--REPORT_PARAMETERS-->', report_params_xml)

    # Generate and replace table columns
    table_columns_xml = "".join([f'<TableColumn><Width>0pt</Width></TableColumn>' for _ in fields])
    rdl_content = rdl_content.replace('<!--TABLE_COLUMNS-->', table_columns_xml)

    # Generate and replace header cells
    header_cells_xml = "".join([f'<TableCell><ReportItems><Textbox Name="Header{name}"><Style><FontFamily>Calibri</FontFamily><FontSize>11pt</FontSize><Color>#666666</Color><TextAlign>Center</TextAlign><PaddingLeft>8pt</PaddingLeft><PaddingRight>5pt</PaddingRight><PaddingTop>5pt</PaddingTop><PaddingBottom>5pt</PaddingBottom><FontWeight>700</FontWeight><BackgroundColor>#FAFAFA</BackgroundColor><BorderColor><Bottom>#dfdfdf</Bottom><Left>#dfdfdf</Left><Top>#dfdfdf</Top><Right>#dfdfdf</Right></BorderColor><BorderStyle><Bottom/><Left/><Top/><Right/></BorderStyle></Style><Top>.3in</Top><Left>.3in</Left><Height>0in</Height><Width>2pt</Width><CanGrow>true</CanGrow><Value>{name}</Value></Textbox></ReportItems></TableCell>' for name in fields.keys()])
    rdl_content = rdl_content.replace('<!--HEADER_CELLS-->', header_cells_xml)

    # Generate and replace details cells
    details_cells_xml = "".join([f'<TableCell><ReportItems><Textbox Name="Details{name}"><Style><FontFamily>Verdana, Arial, Helvetica</FontFamily><FontSize>10pt</FontSize><TextAlign>Center</TextAlign><PaddingLeft>8pt</PaddingLeft><PaddingRight>2pt</PaddingRight><PaddingTop>10pt</PaddingTop><PaddingBottom>10pt</PaddingBottom><BorderColor><Right>#dfdfdf</Right><Top>#dfdfdf</Top><Bottom>#dfdfdf</Bottom><Left>#dfdfdf</Left></BorderColor><BorderStyle/><BackgroundColor>=iif(RowNumber(Nothing) Mod 2, "#FFFFFF","#FFFFFF")</BackgroundColor><Color>=iif(Fields!leadid.Value < 0, "#000000","#222222")</Color></Style><Top>0in</Top><Left>0in</Left><Height>.25in</Height><Width>0pt</Width><CanGrow>true</CanGrow><Value>=Fields!{name}.Value</Value></Textbox></ReportItems></TableCell>' for name in fields.keys()])
    rdl_content = rdl_content.replace('<!--DETAILS_CELLS-->', details_cells_xml)

    try:
        dom = minidom.parseString(rdl_content)
        # The toprettyxml method adds its own xml declaration, so we remove it.
        pretty_rdl_content = '\n'.join(dom.toprettyxml(indent="\t").split('\n')[1:])
        # Prepend the original declaration
        final_rdl = f'<?xml version="1.0" encoding="utf-8"?>\n{pretty_rdl_content}'
        return final_rdl
    except Exception as e:
        print(f"Warning: Could not prettify the RDL XML. Error: {e}")
        return rdl_content

if __name__ == "__main__":
    print("--- RDL Generator ---")
    
    def parse_input_string(input_str):
        result_dict = {}
        for item in input_str.split(','):
            item = item.strip()
            if not item:
                continue
            
            parts = []
            if ':' in item:
                parts = item.split(':', 1)
            else:
                first_space_index = item.find(' ')
                if first_space_index != -1:
                    name = item[:first_space_index].strip()
                    type = item[first_space_index+1:].strip()
                    parts = [name, type]
                else:
                    raise ValueError(f"Invalid format: '{item}'")

            if len(parts) == 2:
                result_dict[parts[0].strip()] = parts[1].strip()
            else:
                raise ValueError(f"Invalid format: '{item}'")
        return result_dict

    # Get inputs from the user
    new_sp_name = input("\nEnter the stored procedure name: ")
    
    print("\nEnter the parameters, separated by commas.")
    print("Use 'name:type' or 'name type' format.")
    print("Example: ownerid:Integer, userid integer, p_refcur:cursor")
    params_str = input("Parameters: ")
    
    try:
        new_params = parse_input_string(params_str)
    except ValueError as e:
        print(f"\nError parsing parameters: {e}")
        print("Please check your input and try again.")
        exit()

    print("\nEnter the fields, separated by commas.")
    print("Use 'name:type' or 'name type' format.")
    print("Example: product_name:System.String, sales_total System.Decimal")
    fields_str = input("Fields: ")

    try:
        new_fields = parse_input_string(fields_str)
    except ValueError as e:
        print(f"\nError parsing fields: {e}")
        print("Please check your input and try again.")
        exit()

    new_table_name = input("\nEnter the table name for the report: ")
    connection_string = input("Enter the database connection string: ")
    output_file_name = input("Enter the desired output file name (e.g., my_report.rdl): ")

    # Generate the RDL file content
    generated_rdl_content = generate_rdl_from_template(new_sp_name, new_params, new_fields, new_table_name, connection_string)

    # Save the generated RDL to a file
    with open(output_file_name, 'w') as f:
        f.write(generated_rdl_content)
    
    print(f"\nRDL file '{output_file_name}' has been successfully created.")