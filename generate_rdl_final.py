def generate_rdl_final(sp_name: str, params: dict, fields: dict, table_name: str, connection_string: str) -> str:
    """
    Generates a new RDL file string from a template using robust string replacement.
    """
    with open('rdl_template.xml', 'r') as file:
        rdl_content = file.read()

    # 1. Replace Connection String
    rdl_content = rdl_content.replace('##CONNECTION_STRING##', connection_string)

    # 2. Replace Stored Procedure Name
    rdl_content = rdl_content.replace('<CommandText>hspl_Status_SubStatus_master_report</CommandText>', f'<CommandText>{sp_name}</CommandText>')

    # 3. Replace Fields
    new_fields_xml = "".join([f'\n\t\t\t\t<Field Name="{name}"><DataField>{name}</DataField><TypeName>{data_type}</TypeName></Field>' for name, data_type in fields.items()])
    start_fields = rdl_content.find('<Fields>') + len('<Fields>')
    end_fields = rdl_content.find('</Fields>')
    rdl_content = rdl_content[:start_fields] + new_fields_xml + '\n\t\t\t' + rdl_content[end_fields:]

    # 4. Replace Query Parameters
    new_query_params_xml = "".join([f'\n\t\t\t\t\t<QueryParameter Name="@{name}"><Value>=Parameters!{name}.Value</Value></QueryParameter>' for name in params.keys() if name != 'p_refcur'])
    new_query_params_xml += '\n\t\t\t\t\t<QueryParameter Name="refcursor"><Value/></QueryParameter>\n\t\t\t\t'
    start_q_params = rdl_content.find('<QueryParameters>') + len('<QueryParameters>')
    end_q_params = rdl_content.find('</QueryParameters>')
    rdl_content = rdl_content[:start_q_params] + new_query_params_xml + rdl_content[end_q_params:]

    # 5. Replace Report Parameters
    new_report_params_xml = "".join([f'\n\t\t<ReportParameter Name="{name}"><DataType>{data_type}</DataType><DefaultValue><Values><Value>-1</Value></Values></DefaultValue></ReportParameter>' for name, data_type in params.items()])
    start_r_params = rdl_content.find('<ReportParameters>') + len('<ReportParameters>')
    end_r_params = rdl_content.find('</ReportParameters>')
    rdl_content = rdl_content[:start_r_params] + new_report_params_xml + '\n\t' + rdl_content[end_r_params:]

    # 6. Replace Table Name
    rdl_content = rdl_content.replace('<Table Name="Status SubStatus Master">', f'<Table Name="{table_name}">')

    # 7. Replace Table Columns
    new_columns_xml = "".join([f'\n\t\t\t\t\t<TableColumn><Width>0pt</Width></TableColumn>' for _ in fields])
    start_cols = rdl_content.find('<TableColumns>') + len('<TableColumns>')
    end_cols = rdl_content.find('</TableColumns>')
    rdl_content = rdl_content[:start_cols] + new_columns_xml + '\n\t\t\t\t' + rdl_content[end_cols:]

    # 8. Replace Header Cells
    header_start_str = '''<Header>\n\t\t\t\t\t<RepeatOnNewPage>true</RepeatOnNewPage>\n\t\t\t\t\t<TableRows>\n\t\t\t\t\t\t<TableRow>\n\t\t\t\t\t\t\t<Height>.35in</Height>\n\t\t\t\t\t\t\t<TableCells>'''
    header_end_str = '''</TableCells>\n\t\t\t\t\t\t</TableRow>\n\t\t\t\t\t</TableRows>\n\t\t\t\t</Header>'''
    new_header_xml = "".join([f'\n\t\t\t\t\t\t\t\t<TableCell><ReportItems><Textbox Name="Header{name}"><Style><FontFamily>Calibri</FontFamily><FontSize>11pt</FontSize><Color>#666666</Color><TextAlign>Center</TextAlign><PaddingLeft>8pt</PaddingLeft><PaddingRight>5pt</PaddingRight><PaddingTop>5pt</PaddingTop><PaddingBottom>5pt</PaddingBottom><FontWeight>700</FontWeight><BackgroundColor>#FAFAFA</BackgroundColor><BorderColor><Bottom>#dfdfdf</Bottom><Left>#dfdfdf</Left><Top>#dfdfdf</Top><Right>#dfdfdf</Right></BorderColor><BorderStyle><Bottom/><Left/><Top/><Right/></BorderStyle></Style><Top>.3in</Top><Left>.3in</Left><Height>0in</Height><Width>2pt</Width><CanGrow>true</CanGrow><Value>{name}</Value></Textbox></ReportItems></TableCell>' for name in fields.keys()])
    start_h_cells = rdl_content.find(header_start_str) + len(header_start_str)
    end_h_cells = rdl_content.find(header_end_str)
    rdl_content = rdl_content[:start_h_cells] + new_header_xml + '\n\t\t\t\t\t\t\t' + rdl_content[end_h_cells:]

    # 9. Replace Details Cells
    details_start_str = '''<Details>\n\t\t\t\t\t<TableRows>\n\t\t\t\t\t\t<TableRow>\n\t\t\t\t\t\t\t<Height>.25in</Height>\n\t\t\t\t\t\t\t<TableCells>'''
    details_end_str = '''</TableCells>\n\t\t\t\t\t\t</TableRow>\n\t\t\t\t\t</TableRows>\n\t\t\t\t</Details>'''
    new_detail_xml = "".join([f'\n\t\t\t\t\t\t\t\t<TableCell><ReportItems><Textbox Name="Details{name}"><Style><FontFamily>Verdana, Arial, Helvetica</FontFamily><FontSize>10pt</FontSize><TextAlign>Center</TextAlign><PaddingLeft>8pt</PaddingLeft><PaddingRight>2pt</PaddingRight><PaddingTop>10pt</PaddingTop><PaddingBottom>10pt</PaddingBottom><BorderColor><Right>#dfdfdf</Right><Top>#dfdfdf</Top><Bottom>#dfdfdf</Bottom><Left>#dfdfdf</Left></BorderColor><BorderStyle/><BackgroundColor>=iif(RowNumber(Nothing) Mod 2, "#FFFFFF","#FFFFFF")</BackgroundColor><Color>=iif(Fields!leadid.Value &lt; 0, "#000000","#222222")</Color></Style><Top>0in</Top><Left>0in</Left><Height>.25in</Height><Width>0pt</Width><CanGrow>true</CanGrow><Value>=Fields!{name}.Value</Value></Textbox></ReportItems></TableCell>' for name in fields.keys()])
    start_d_cells = rdl_content.find(details_start_str) + len(details_start_str)
    end_d_cells = rdl_content.find(details_end_str)
    rdl_content = rdl_content[:start_d_cells] + new_detail_xml + '\n\t\t\t\t\t\t\t' + rdl_content[end_d_cells:]

    return rdl_content

if __name__ == "__main__":
    print("--- RDL Generator (Final) ---")
    
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

    new_sp_name = input("\nEnter the stored procedure name: ")
    print("\nEnter the parameters, separated by commas (e.g., ownerid:Integer, userid integer):")
    params_str = input("Parameters: ")
    try:
        new_params = parse_input_string(params_str)
    except ValueError as e:
        print(f"\nError parsing parameters: {e}")
        exit()

    print("\nEnter the fields, separated by commas (e.g., product_name:System.String, sales_total System.Decimal):")
    fields_str = input("Fields: ")
    try:
        new_fields = parse_input_string(fields_str)
    except ValueError as e:
        print(f"\nError parsing fields: {e}")
        exit()

    new_table_name = input("\nEnter the table name for the report: ")
    connection_string = input("Enter the database connection string: ")
    output_file_name = input("Enter the desired output file name (e.g., my_report.rdl): ")

    generated_rdl_content = generate_rdl_final(new_sp_name, new_params, new_fields, new_table_name, connection_string)

    with open(output_file_name, 'w') as f:
        f.write(generated_rdl_content)
    
    print(f"\nRDL file '{output_file_name}' has been successfully created.")