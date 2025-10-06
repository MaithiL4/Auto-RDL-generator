import xml.etree.ElementTree as ET

def generate_rdl(sp_name: str, params: dict, fields: dict, table_name: str, connection_string: str) -> str:
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
    with open('rdl_template.xml', 'r') as file:
        rdl_content = file.read()

    # --- Perform substitutions ---
    # Update Connection String
    rdl_content = rdl_content.replace('##CONNECTION_STRING##', connection_string)
    
    # Update Stored Procedure Name
    rdl_content = rdl_content.replace('<CommandText>hspl_Status_SubStatus_master_report</CommandText>', f'<CommandText>{sp_name}</CommandText>')
    
    # Update Fields
    new_fields_xml = "".join([f'<Field Name="{name}"><DataField>{name}</DataField><TypeName>{data_type}</TypeName></Field>' for name, data_type in fields.items()])
    rdl_content = rdl_content.replace('<Fields>\n\t\t\t\t<Field Name="rn">\n\t\t\t\t\t<DataField>rn</DataField>\n\t\t\t\t\t<TypeName>System.String</TypeName>\n\t\t\t\t</Field>\n\t\t\t\t<Field Name="Status">\n\t\t\t\t\t<DataField>Status</DataField>\n\t\t\t\t\t<TypeName>System.String</TypeName>\n\t\t\t\t</Field>\n\t\t\t\t<Field Name="SubStatus">\n\t\t\t\t\t<DataField>SubStatus</DataField>\n\t\t\t\t\t<TypeName>System.String</TypeName>\n\t\t\t\t</Field>\n\t\t\t</Fields>', f'<Fields>\n\t\t\t\t{new_fields_xml}\n\t\t\t</Fields>')

    # Update QueryParameters
    new_query_params_xml = "".join([f'<QueryParameter Name="@{name}"><Value>=Parameters!{name}.Value</Value></QueryParameter>' for name in params.keys() if name != 'p_refcur']) + '<QueryParameter Name="refcursor"><Value/></QueryParameter>'
    rdl_content = rdl_content.replace('<QueryParameters>\n\t\t\t\t\t<QueryParameter Name="@ownerid">\n\t\t\t\t\t\t<Value>=Parameters!ownerid.Value</Value>\n\t\t\t\t\t</QueryParameter>\n\t\t\t\t\t<QueryParameter Name="@userid">\n\t\t\t\t\t\t<Value>=Parameters!userid.Value</Value>\n\t\t\t\t\t</QueryParameter>\n\t\t\t\t\t<QueryParameter Name="@startindex">\n\t\t\t\t\t\t<Value>=Parameters!startindex.Value</Value>\n\t\t\t\t\t</QueryParameter>\n\t\t\t\t\t<QueryParameter Name="@endindex">\n\t\t\t\t\t\t<Value>=Parameters!endindex.Value</Value>\n\t\t\t\t\t</QueryParameter>\n\t\t\t\t\t<QueryParameter Name="@filter">\n\t\t\t\t\t\t<Value>=Parameters!filter.Value</Value>\n\t\t\t\t\t</QueryParameter>\n\t\t\t\t\t<QueryParameter Name="@filter1">\n\t\t\t\t\t\t<Value>=Parameters!filter1.Value</Value>\n\t\t\t\t\t</QueryParameter>\n\t\t\t\t\t<QueryParameter Name="@filter2">\n\t\t\t\t\t\t<Value>=Parameters!filter2.Value</Value>\n\t\t\t\t\t</QueryParameter>\n\t\t\t\t\t<QueryParameter Name="refcursor">\n\t\t\t\t\t\t<Value/>\n\t\t\t\t\t</QueryParameter>\n\t\t\t\t</QueryParameters>', f'<QueryParameters>\n\t\t\t\t\t{new_query_params_xml}\n\t\t\t\t</QueryParameters>')

    # Update ReportParameters
    new_report_params_xml = "".join([f'<ReportParameter Name="{name}"><DataType>{data_type}</DataType><DefaultValue><Values><Value>-1</Value></Values></DefaultValue></ReportParameter>' for name, data_type in params.items()])
    rdl_content = rdl_content.replace('<ReportParameters>\n\t\t<ReportParameter Name="ownerid">\n\t\t\t<DataType>Integer</DataType>\n\t\t\t<DefaultValue>\n\t\t\t\t<Values>\n\t\t\t\t\t<Value>-1</Value>\n\t\t\t\t</Values>\n\t\t\t</DefaultValue>\n\t\t</ReportParameter>\n\t\t<ReportParameter Name="userid">\n\t\t\t<DataType>Integer</DataType>\n\t\t\t<DefaultValue>\n\t\t\t\t<Values>\n\t\t\t\t\t<Value>-1</Value>\n\t\t\t\t</Values>\n\t\t\t</DefaultValue>\n\t\t</ReportParameter>\n\t\t<ReportParameter Name="startindex">\n\t\t\t<DataType>Integer</DataType>\n\t\t\t<DefaultValue>\n\t\t\t\t<Values>\n\t\t\t\t\t<Value>-1</Value>\n\t\t\t\t</Values>\n\t\t\t</DefaultValue>\n\t\t</ReportParameter>\n\t\t<ReportParameter Name="endindex">\n\t\t\t<DataType>Integer</DataType>\n\t\t\t<DefaultValue>\n\t\t\t\t<Values>\n\t\t\t\t\t<Value>-1</Value>\n\t\t\t\t</Values>\n\t\t\t</DefaultValue>\n\t\t</ReportParameter>\n\t\t<ReportParameter Name="filter">\n\t\t\t<DataType>String</DataType>\n\t\t\t<DefaultValue>\n\t\t\t\t<Values>\n\t\t\t\t\t<Value>-1</Value>\n\t\t\t\t</Values>\n\t\t\t</DefaultValue>\n\t\t</ReportParameter>\n\t\t<ReportParameter Name="filter1">\n\t\t\t<DataType>String</DataType>\n\t\t\t<DefaultValue>\n\t\t\t\t<Values>\n\t\t\t\t\t<Value>-1</Value>\n\t\t\t\t</Values>\n\t\t\t</DefaultValue>\n\t\t</ReportParameter>\n\t\t<ReportParameter Name="filter2">\n\t\t\t<DataType>String</DataType>\n\t\t\t<DefaultValue>\n\t\t\t\t<Values>\n\t\t\t\t\t<Value>-1</Value>\n\t\t\t\t</Values>\n\t\t\t</DefaultValue>\n\t\t</ReportParameter>\n\t\t<ReportParameter Name="p_refcur">\n\t\t\t<DataType>cursor</DataType>\n\t\t\t<DefaultValue>\n\t\t\t\t<Values>\n\t\t\t\t\t<Value>-1</Value>\n\t\t\t\t</Values>\n\t\t\t</DefaultValue>\n\t\t</ReportParameter>\n\t</ReportParameters>', f'<ReportParameters>\n\t\t{new_report_params_xml}\n\t</ReportParameters>')

    # Update Table Name
    rdl_content = rdl_content.replace('<Table Name="Status SubStatus Master">', f'<Table Name="{table_name}">')

    # Update Table Columns
    new_columns_xml = "".join([f'<TableColumn><Width>0pt</Width></TableColumn>' for _ in fields])
    rdl_content = rdl_content.replace('<TableColumns>\n\t\t\t\t\t<TableColumn>\n\t\t\t\t\t\t<Width>0pt</Width>\n\t\t\t\t\t</TableColumn>\n\t\t\t\t\t<TableColumn>\n\t\t\t\t\t\t<Width>0pt</Width>\n\t\t\t\t\t</TableColumn>\n\t\t\t\t</TableColumns>', f'<TableColumns>\n\t\t\t\t\t{new_columns_xml}\n\t\t\t\t</TableColumns>')

    # Update Header Textboxes
    new_header_xml = "".join([f'<TableCell><ReportItems><Textbox Name="Header{name}"><Style><FontFamily>Calibri</FontFamily><FontSize>11pt</FontSize><Color>#666666</Color><TextAlign>Center</TextAlign><PaddingLeft>8pt</PaddingLeft><PaddingRight>5pt</PaddingRight><PaddingTop>5pt</PaddingTop><PaddingBottom>5pt</PaddingBottom><FontWeight>700</FontWeight><BackgroundColor>#FAFAFA</BackgroundColor><BorderColor><Bottom>#dfdfdf</Bottom><Left>#dfdfdf</Left><Top>#dfdfdf</Top><Right>#dfdfdf</Right></BorderColor><BorderStyle><Bottom/><Left/><Top/><Right/></BorderStyle></Style><Top>.3in</Top><Left>.3in</Left><Height>0in</Height><Width>2pt</Width><CanGrow>true</CanGrow><Value>{name}</Value></Textbox></ReportItems></TableCell>' for name in fields.keys()])
    rdl_content = rdl_content.replace('<Header>\n\t\t\t\t\t<RepeatOnNewPage>true</RepeatOnNewPage>\n\t\t\t\t\t<TableRows>\n\t\t\t\t\t\t<TableRow>\n\t\t\t\t\t\t\t<Height>.35in</Height>\n\t\t\t\t\t\t\t<TableCells>\n\t\t\t\t\t\t\t\t<TableCell>\n\t\t\t\t\t\t\t\t\t<ReportItems>\n\t\t\t\t\t\t\t\t\t\t<Textbox Name="HeaderStatus">\n\t\t\t\t\t\t\t\t\t\t\t<Style>\n\t\t\t\t\t\t\t\t\t\t\t\t<FontFamily>Calibri</FontFamily>\n\t\t\t\t\t\t\t\t\t\t\t\t<FontSize>11pt</FontSize>\n\t\t\t\t\t\t\t\t\t\t\t\t<Color>#666666</Color>\n\t\t\t\t\t\t\t\t\t\t\t\t<TextAlign>Center</TextAlign>\n\t\t\t\t\t\t\t\t\t\t\t\t<PaddingLeft>8pt</PaddingLeft>\n\t\t\t\t\t\t\t\t\t\t\t\t<PaddingRight>5pt</PaddingRight>\n\t\t\t\t\t\t\t\t\t\t\t\t<PaddingTop>5pt</PaddingTop>\n\t\t\t\t\t\t\t\t\t\t\t\t<PaddingBottom>5pt</PaddingBottom>\n\t\t\t\t\t\t\t\t\t\t\t\t<FontWeight>700</FontWeight>\n\t\t\t\t\t\t\t\t\t\t\t\t<BackgroundColor>#FAFAFA</BackgroundColor>\n\t\t\t\t\t\t\t\t\t\t\t\t<BorderColor>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Bottom>#dfdfdf</Bottom>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Left>#dfdfdf</Left>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Top>#dfdfdf</Top>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Right>#dfdfdf</Right>\n\t\t\t\t\t\t\t\t\t\t\t\t</BorderColor>\n\t\t\t\t\t\t\t\t\t\t\t\t<BorderStyle>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Bottom/>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Left/>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Top/>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Right/>\n\t\t\t\t\t\t\t\t\t\t\t\t</BorderStyle>\n\t\t\t\t\t\t\t\t\t\t\t</Style>\n\t\t\t\t\t\t\t\t\t\t\t<Top>.3in</Top>\n\t\t\t\t\t\t\t\t\t\t\t<Left>.3in</Left>\n\t\t\t\t\t\t\t\t\t\t\t<Height>0in</Height>\n\t\t\t\t\t\t\t\t\t\t\t<Width>2pt</Width>\n\t\t\t\t\t\t\t\t\t\t\t<CanGrow>true</CanGrow>\n\t\t\t\t\t\t\t\t\t\t\t<Value>Status</Value>\n\t\t\t\t\t\t\t\t\t\t</Textbox>\n\t\t\t\t\t\t\t\t\t</ReportItems>\n\t\t\t\t\t\t\t\t</TableCell>\n\t\t\t\t\t\t\t\t<TableCell>\n\t\t\t\t\t\t\t\t\t<ReportItems>\n\t\t\t\t\t\t\t\t\t\t<Textbox Name="HeaderSubStatus">\n\t\t\t\t\t\t\t\t\t\t\t<Style>\n\t\t\t\t\t\t\t\t\t\t\t\t<FontFamily>Calibri</FontFamily>\n\t\t\t\t\t\t\t\t\t\t\t\t<FontSize>11pt</FontSize>\n\t\t\t\t\t\t\t\t\t\t\t\t<Color>#666666</Color>\n\t\t\t\t\t\t\t\t\t\t\t\t<TextAlign>Center</TextAlign>\n\t\t\t\t\t\t\t\t\t\t\t\t<PaddingLeft>8pt</PaddingLeft>\n\t\t\t\t\t\t\t\t\t\t\t\t<PaddingRight>5pt</PaddingRight>\n\t\t\t\t\t\t\t\t\t\t\t\t<PaddingTop>5pt</PaddingTop>\n\t\t\t\t\t\t\t\t\t\t\t\t<PaddingBottom>5pt</PaddingBottom>\n\t\t\t\t\t\t\t\t\t\t\t\t<FontWeight>700</FontWeight>\n\t\t\t\t\t\t\t\t\t\t\t\t<BackgroundColor>#FAFAFA</BackgroundColor>\n\t\t\t\t\t\t\t\t\t\t\t\t<BorderColor>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Bottom>#dfdfdf</Bottom>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Left>#dfdfdf</Left>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Top>#dfdfdf</Top>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Right>#dfdfdf</Right>\n\t\t\t\t\t\t\t\t\t\t\t\t</BorderColor>\n\t\t\t\t\t\t\t\t\t\t\t\t<BorderStyle>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Bottom/>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Left/>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Top/>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Right/>\n\t\t\t\t\t\t\t\t\t\t\t\t</BorderStyle>\n\t\t\t\t\t\t\t\t\t\t\t</Style>\n\t\t\t\t\t\t\t\t\t\t\t<Top>.3in</Top>\n\t\t\t\t\t\t\t\t\t\t\t<Left>.3in</Left>\n\t\t\t\t\t\t\t\t\t\t\t<Height>0in</Height>\n\t\t\t\t\t\t\t\t\t\t\t<Width>2pt</Width>\n\t\t\t\t\t\t\t\t\t\t\t<CanGrow>true</CanGrow>\n\t\t\t\t\t\t\t\t\t\t\t<Value>SubStatus</Value>\n\t\t\t\t\t\t\t\t\t\t</Textbox>\n\t\t\t\t\t\t\t\t\t</ReportItems>\n\t\t\t\t\t\t\t\t</TableCell>\n\t\t\t\t\t\t\t</TableCells>\n\t\t\t\t\t\t</TableRow>\n\t\t\t\t\t</TableRows>\n\t\t\t\t</Header>', f'<Header>\n\t\t\t\t\t<RepeatOnNewPage>true</RepeatOnNewPage>\n\t\t\t\t\t<TableRows>\n\t\t\t\t\t\t<TableRow>\n\t\t\t\t\t\t\t<Height>.35in</Height>\n\t\t\t\t\t\t\t<TableCells>{new_header_xml}</TableCells>\n\t\t\t\t\t\t</TableRow>\n\t\t\t\t\t</TableRows>\n\t\t\t\t</Header>')
    
    # Update Detail Textboxes
    new_detail_xml = "".join([f'<TableCell><ReportItems><Textbox Name="Details{name}"><Style><FontFamily>Verdana, Arial, Helvetica</FontFamily><FontSize>10pt</FontSize><TextAlign>Center</TextAlign><PaddingLeft>8pt</PaddingLeft><PaddingRight>2pt</PaddingRight><PaddingTop>10pt</PaddingTop><PaddingBottom>10pt</PaddingBottom><BorderColor><Right>#dfdfdf</Right><Top>#dfdfdf</Top><Bottom>#dfdfdf</Bottom><Left>#dfdfdf</Left></BorderColor><BorderStyle/><BackgroundColor>=iif(RowNumber(Nothing) Mod 2, "#FFFFFF","#FFFFFF")</BackgroundColor><Color>=iif(Fields!leadid.Value < 0, "#000000","#222222")</Color></Style><Top>0in</Top><Left>0in</Left><Height>.25in</Height><Width>0pt</Width><CanGrow>true</CanGrow><Value>=Fields!{name}.Value</Value></Textbox></ReportItems></TableCell>' for name in fields.keys()])
    rdl_content = rdl_content.replace('<Details>\n\t\t\t\t\t<TableRows>\n\t\t\t\t\t\t<TableRow>\n\t\t\t\t\t\t\t<Height>.25in</Height>\n\t\t\t\t\t\t\t<TableCells>\n\t\t\t\t\t\t\t\t<TableCell>\n\t\t\t\t\t\t\t\t\t<ReportItems>\n\t\t\t\t\t\t\t\t\t\t<Textbox Name="DetailsStatus">\n\t\t\t\t\t\t\t\t\t\t\t<Style>\n\t\t\t\t\t\t\t\t\t\t\t\t<FontFamily>Verdana, Arial, Helvetica</FontFamily>\n\t\t\t\t\t\t\t\t\t\t\t\t<FontSize>10pt</FontSize>\n\t\t\t\t\t\t\t\t\t\t\t\t<TextAlign>Center</TextAlign>\n\t\t\t\t\t\t\t\t\t\t\t\t<PaddingLeft>8pt</PaddingLeft>\n\t\t\t\t\t\t\t\t\t\t\t\t<PaddingRight>2pt</PaddingRight>\n\t\t\t\t\t\t\t\t\t\t\t\t<PaddingTop>10pt</PaddingTop>\n\t\t\t\t\t\t\t\t\t\t\t\t<PaddingBottom>10pt</PaddingBottom>\n\t\t\t\t\t\t\t\t\t\t\t\t<BorderColor>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Right>#dfdfdf</Right>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Top>#dfdfdf</Top>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Bottom>#dfdfdf</Bottom>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Left>#dfdfdf</Left>\n\t\t\t\t\t\t\t\t\t\t\t\t</BorderColor>\n\t\t\t\t\t\t\t\t\t\t\t\t<BorderStyle/>\n\t\t\t\t\t\t\t\t\t\t\t\t<BackgroundColor>=iif(RowNumber(Nothing) Mod 2, "#FFFFFF","#FFFFFF")</BackgroundColor>\n\t\t\t\t\t\t\t\t\t\t\t\t<Color>=iif(Fields!leadid.Value &lt; 0, "#000000","#222222")</Color>\n\t\t\t\t\t\t\t\t\t\t\t</Style>\n\t\t\t\t\t\t\t\t\t\t\t<Top>0in</Top>\n\t\t\t\t\t\t\t\t\t\t\t<Left>0in</Left>\n\t\t\t\t\t\t\t\t\t\t\t<Height>.25in</Height>\n\t\t\t\t\t\t\t\t\t\t\t<Width>0pt</Width>\n\t\t\t\t\t\t\t\t\t\t\t<CanGrow>true</CanGrow>\n\t\t\t\t\t\t\t\t\t\t\t<Value>=Fields!Status.Value</Value>\n\t\t\t\t\t\t\t\t\t\t</Textbox>\n\t\t\t\t\t\t\t\t\t</ReportItems>\n\t\t\t\t\t\t\t\t</TableCell>\n\t\t\t\t\t\t\t\t<TableCell>\n\t\t\t\t\t\t\t\t\t<ReportItems>\n\t\t\t\t\t\t\t\t\t\t<Textbox Name="DetailsSubStatus">\n\t\t\t\t\t\t\t\t\t\t\t<Style>\n\t\t\t\t\t\t\t\t\t\t\t\t<FontFamily>Verdana, Arial, Helvetica</FontFamily>\n\t\t\t\t\t\t\t\t\t\t\t\t<FontSize>10pt</FontSize>\n\t\t\t\t\t\t\t\t\t\t\t\t<TextAlign>Center</TextAlign>\n\t\t\t\t\t\t\t\t\t\t\t\t<PaddingLeft>8pt</PaddingLeft>\n\t\t\t\t\t\t\t\t\t\t\t\t<PaddingRight>2pt</PaddingRight>\n\t\t\t\t\t\t\t\t\t\t\t\t<PaddingTop>10pt</PaddingTop>\n\t\t\t\t\t\t\t\t\t\t\t\t<PaddingBottom>10pt</PaddingBottom>\n\t\t\t\t\t\t\t\t\t\t\t\t<BorderColor>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Right>#dfdfdf</Right>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Top>#dfdfdf</Top>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Bottom>#dfdfdf</Bottom>\n\t\t\t\t\t\t\t\t\t\t\t\t\t<Left>#dfdfdf</Left>\n\t\t\t\t\t\t\t\t\t\t\t\t</BorderColor>\n\t\t\t\t\t\t\t\t\t\t\t\t<BorderStyle/>\n\t\t\t\t\t\t\t\t\t\t\t\t<BackgroundColor>=iif(RowNumber(Nothing) Mod 2, "#FFFFFF","#FFFFFF")</BackgroundColor>\n\t\t\t\t\t\t\t\t\t\t\t\t<Color>=iif(Fields!leadid.Value &lt; 0, "#000000","#222222")</Color>\n\t\t\t\t\t\t\t\t\t\t\t</Style>\n\t\t\t\t\t\t\t\t\t\t\t<Top>0in</Top>\n\t\t\t\t\t\t\t\t\t\t\t<Left>0in</Left>\n\t\t\t\t\t\t\t\t\t\t\t<Height>.25in</Height>\n\t\t\t\t\t\t\t\t\t\t\t<Width>0pt</Width>\n\t\t\t\t\t\t\t\t\t\t\t<CanGrow>true</CanGrow>\n\t\t\t\t\t\t\t\t\t\t\t<Value>=Fields!SubStatus.Value</Value>\n\t\t\t\t\t\t\t\t\t\t</Textbox>\n\t\t\t\t\t\t\t\t\t</ReportItems>\n\t\t\t\t\t\t\t\t</TableCell>\n\t\t\t\t\t\t\t</TableCells>\n\t\t\t\t\t\t</TableRow>\n\t\t\t\t\t</TableRows>\n\t\t\t\t</Details>', f'<Details>\n\t\t\t\t\t<TableRows>\n\t\t\t\t\t\t<TableRow>\n\t\t\t\t\t\t\t<Height>.25in</Height>\n\t\t\t\t\t\t\t<TableCells>{new_detail_xml}</TableCells>\n\t\t\t\t\t\t</TableRow>\n\t\t\t\t\t</TableRows>\n\t\t\t\t</Details>')

    return rdl_content

# --- Example Usage ---
# Define the inputs for your new stored procedure
new_sp_name = "new_sales_report_sp"
new_params = {
    "start_date": "DateTime",
    "end_date": "DateTime",
    "p_refcur": "cursor",
}
new_fields = {
    "product_name": "System.String",
    "sales_total": "System.Decimal",
    "region": "System.String",
}
new_table_name = "Sales Report"
connection_string = "Server=myServer;Database=myNewDB;"

# Generate the RDL file content
generated_rdl_content = generate_rdl(new_sp_name, new_params, new_fields, new_table_name, connection_string)

# Save the generated RDL to a file
with open(f'{new_sp_name}.rdl', 'w') as f:
    f.write(generated_rdl_content)
    
print(f"RDL file '{new_sp_name}.rdl' has been successfully created.")