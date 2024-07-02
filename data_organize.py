

import json
def buildVar(filename):
    from bs4 import BeautifulSoup
    import re

    reponse_data = {}
    with open(filename, 'r') as file:
        # Read the entire contents of the file into a string variable
        file_contents = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(file_contents, 'html.parser')

    # Find the table in the HTML (adjust the slector as needed)
    table_rows = soup.select('table')
    reports = table_rows[1].select('tr')
    reports = reports[2:]
    for report in reports:
        data = report.find_all('td')
        date = re.search(r'\d{2}/\d{2}',data[0].text).group(0)
        report_in = data[4].text
        report_out = data[5].text
        if date not in reponse_data:
            reponse_data[date] = []
            
        reponse_data[date].append({"in": report_in, "out": report_out})
    return reponse_data
    # table_rows = table.find_all('tr')
    # Extract table rows
    #rows = {}
    #for row in table_rows:
    #    cells = row.select('td:nth-child(1)')
    #    print(cells)
        #cells = [cell.text for cell in cells]
        #rows.append(cells)

print(json.dumps(buildVar('test.xls')))
