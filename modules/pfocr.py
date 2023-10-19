import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import io
from collections import defaultdict



def pfocr2genes(column,keyword):
    # PFOCR table webpage
    url = "https://pfocr.wikipathways.org/browse/table.html"

    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find the table on the page
        table = soup.find("table")
        # print(table)

        pathway_titles = []
        
        # Loop through the rows of the table
        for row in table.find_all("tr"):
            # Find the cells in each row
            cells = row.find_all("td")
            
            # Check if there are at least 3 cells (3 columns)
            if len(cells) >= 3:
                if column == 0:
                    # Extract the pathway title from the first column
                    pathway_title = cells[column].text.strip()                   
                    # Check if the pathway title contains the keyword, and the number of characters in pathway_title is less than 2000
                    if re.search(keyword, pathway_title, re.IGNORECASE) and len(pathway_title) < 2000:
                        # Add the pathway title to the list
                        pathway_titles.append(pathway_title)
                else:
                    # if the column 2 is chosen, taxonomy name is searched and if true, pathway title is obtained.
                    if re.search(keyword, cells[column].text.strip(), re.IGNORECASE):
                        pathway_title = cells[0].text.strip()
                        pathway_titles.append(pathway_title)
            else:
                continue

        print(f"the number of pathway figures:{len(pathway_titles)}")
    else:
        print("Failed to retrieve PFOCR webpage.")

    for i in pathway_titles:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            link = soup.find("a", string=i)
            link_url = link.get("href")
            pre_pmcid = link_url.split("__")[0]
            pmcid = pre_pmcid.split("s/")[1]
            # print(pmcid)
            # Construct the pathway page url
            page_url = f"https://pfocr.wikipathways.org/{link_url}"
            # Send an HTTP GET request to the pathway page url
            response = requests.get(page_url)
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Parse the HTML content of the page using BeautifulSoup
                soup_link = BeautifulSoup(response.content, "html.parser")
                # Find all the links on the page
                links = soup_link.find_all("a")
                for link in links:
                    if link.get("href").startswith("https://raw.githubusercontent.com/wikipathways/pfocr-database/main/_data/PMC") and link.get("href").endswith("-genes.tsv"):
                        link_download_genetsv = link.get("href")
                        response_link = requests.get(link_download_genetsv)
                        # Aceess the link and download the file
                        if response_link.status_code == 200:
                            # parse the HTML content of the page using BeautifulSoup
                            soup_link_download = BeautifulSoup(response_link.content, "html.parser")
                            # get the content of the file
                            content2 = soup_link_download.text
                            # make a dataframe from the content
                            df = pd.read_csv(io.StringIO(content2), sep='\t')
                            # make a new column named "PMCID" and add the pmcid to the column
                            df["PMCID"] = pmcid
                            # save the dataframe to a file
                            df.to_csv("./results/pre_pfocr_genes.tsv", mode='a', header=False, sep="\t")
    return print("PFOCR gene extraction is done. Move to the next step")
                        # # save the content to a file
                        # with open(f"test.txt", "a") as f:
                        #     f.write(content2)
                        


def genes2ensg(filepath,taxonomy):
    data_list = []
    ensg_list = []
    # read each line of test.csv
    with open(filepath) as f:
        for line in f:
            et = line.split("\t")
            if et[2] == taxonomy:
                geneid = et[7]
                if geneid.endswith(".0"):
                    geneid = geneid.replace(".0","")
                else:
                    geneid = geneid  
                pmcid = et[12].replace("\n","")
                # print({"geneid":geneid,"pmcid":pmcid})
                data_list.append({"geneid":geneid,"pmcid":pmcid})
        # Remove duplicates by converting dictionaries to tuples
        unique_tuples = {tuple(sorted(d.items())) for d in data_list}
        # Convert tuples back to dictionaries
        unique_dicts = [dict(t) for t in unique_tuples]
        # print(len(unique_dicts))
        grouped_data = defaultdict(lambda:{"pmcid":[]})
        for i in unique_dicts:
            grouped_data[i["geneid"]]["pmcid"].append(str(i["pmcid"]))
        gdata_result = [{"geneid":k,"pmcid":','.join(v["pmcid"])} for k,v in grouped_data.items()]
        print(gdata_result)
        print(len(gdata_result))
        for i in gdata_result:
            geneid = i["geneid"]
            pmcid = i["pmcid"]
            pmc_convert_api_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=my_email@example.com&ids={pmcid}&format=json"
            r = requests.get(pmc_convert_api_url)
            data = r.json()
            pmid = data["records"][0]["pmid"]
            print(f"\ngeneid:{geneid},pmid:{pmid}")
            if geneid == "":
                continue
            else:  
                r = requests.post(
                url='https://biit.cs.ut.ee/gprofiler/api/convert/convert/',
                json={
                    'organism':'hsapiens',
                    'target':'ENSG',
                    'query':geneid,
                }
                )
                resultlist = r.json()['result']
                for result in resultlist:
                    if result['converted'].startswith('ENSG'):
                        ensg_list.append({"gene":result['converted'],"PMID_PMCID":pmid,"evidence":"PFOCR"})
                        print({"gene":result['converted'],"PMID_PMCID":pmid,"evidence":"PFOCR"})
                    else:
                        continue
    return ensg_list    