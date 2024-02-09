import pandas as pd
import requests
import gzip
import shutil
import os
import xml.etree.ElementTree as ET
import subprocess
import datetime
import json

t_delta = datetime.timedelta(hours=9)
JST = datetime.timezone(t_delta, "JST")
now = datetime.datetime.now(JST)
date = now.strftime("%Y%m%d")

def download_file():
    if not os.path.exists(f"./results/gene2pubmed_{date}"):
        print("gene2pubmed is downloading...")
        outputpath = f"./results/gene2pubmed_{date}.gz"
        url = "https://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2pubmed.gz"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(outputpath, 'wb') as file:
                    file.write(response.content)           
                with gzip.open(f"./results/gene2pubmed_{date}.gz", mode="rb") as gzip_file:
                    with open(f"./results/gene2pubmed_{date}", mode="wb") as decompressed_file:
                        shutil.copyfileobj(gzip_file, decompressed_file)
                    # delete the zip file  
                    os.remove(f"./results/gene2pubmed_{date}.gz")
                    print(f"Downloaded {url} to {outputpath}")
            else:
                print(f"Failed to download. Status code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("gene2pubmed file exists. Move to the next step")


def search_pmids(genes_ensgs):
    """
    """
    # read the file and make a dataframe with the data type of string
    df_gene2pubmed = pd.read_csv(f"./results/gene2pubmed_{date}", sep="\t", dtype=str)
    # convert ensgs to ncbi geneids
    new_list = []
    for ensg in genes_ensgs:
        r = requests.post(
        url='https://biit.cs.ut.ee/gprofiler/api/convert/convert/',
        json={
            'organism':'hsapiens',
            'target':'ENTREZGENE_ACC',
            'query':ensg,
        }
        )
        ncbi_geneid = r.json()['result'][0]['converted']
        gene_name = r.json()['result'][0]['name']
        # search the ncbi_geneid in the column "GeneID"
        df_searched = df_gene2pubmed[df_gene2pubmed["GeneID"] == str(ncbi_geneid)]
        count = len(df_searched)
        # make a list of the column "PubMed_ID"
        pmids = df_searched["PubMed_ID"].tolist()
        pmids_str = ",".join(pmids)
        new_list.append({"ensg":ensg,"ncbi_geneid":ncbi_geneid, "gene_name":gene_name,"count":count,"pmids":pmids_str})
        print({"ensg":ensg,"ncbi_geneid":ncbi_geneid, "gene_name":gene_name,"count":count,"pmids":pmids_str})
    return new_list



