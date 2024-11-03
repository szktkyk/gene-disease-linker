import pandas as pd
import argparse
import os
import datetime
from modules import gene2pubmed, get_evidence_otp
import yaml

t_delta = datetime.timedelta(hours=9)
JST = datetime.timezone(t_delta, "JST")
now = datetime.datetime.now(JST)
date = now.strftime("%Y%m%d")



def main(config):
    with open(f'./{config}','r') as yml:
        config = yaml.safe_load(yml)
    mygenes = config["TEXT_FILE_WITH_ENSEMBL_GENE_IDs"] 
    efoid = config["EXPERIMENTAL_FACTOR_ONTOLOGY_ID"]
    output_prefix = config["OUTPUT_PREFIX"]
    if os.path.exists(f"./results/{date}/{output_prefix}_output.tsv"):
        return print("The output file already exist.")
    gene2pubmed.download_file()
    # read a txt file and make a list
    with open(mygenes) as f:
        gene_list = f.read().splitlines()
    with open("./results/otp_genes.txt") as f:
        otp_list = f.read().splitlines()
    common_genes = list(set(gene_list) & set(otp_list))
        
    # Get the evidence from OpenTargets
    otp_df = get_evidence_otp.get_evidence_otp(common_genes,efoid,2000)
    otp_df.to_csv(f"./results/otp_genes.tsv", sep='\t',index=False)
    # otp_df = pd.read_csv("./results/otp_genes.tsv",sep="\t")
    try:
        mirtex_df = pd.read_csv("./results/mirtex_genes.tsv",sep="\t")
    except:
        mirtex_df = pd.DataFrame(columns=["gene","PMID_PMCID","evidence"])
    rnadisease_df = pd.read_csv("./results/rnadisease_genes.tsv", sep="\t")
    try:
        disgenet_df = pd.read_csv("./results/disgenet_genes.tsv", sep="\t")
    except:
        disgenet_df = pd.DataFrame(columns=["gene","PMID_PMCID","evidence"])
    pubchem_df = pd.read_csv("./results/pubchem_genes.tsv", sep="\t")

    if not os.path.exists(f"./results/{output_prefix}_bib_genes.tsv"):
        bib_df = pd.concat([otp_df,mirtex_df,rnadisease_df,disgenet_df,pubchem_df],ignore_index=True)
        bib_df["PMID_PMCID"] = bib_df["PMID_PMCID"].astype(str)
        bib_df = bib_df.groupby('gene').agg({'PMID_PMCID':','.join,'evidence':','.join}).reset_index()
        bib_df = bib_df.reset_index().rename(columns={"gene":"gene","PMID_PMCID":"PMID_PMCID","evidence":"evidence"})
        bib_df = bib_df.drop("index",axis=1)
        # delete the duplicated PMIDs
        bib_df["PMID_PMCID"] = bib_df["PMID_PMCID"].apply(lambda x: ",".join(pd.unique(str(x).split(","))) if pd.notna(x) else x)
        # print(len(bib_df))
        bib_df.to_csv(f"./results/{output_prefix}_bib_genes.tsv", sep='\t',index=False)
        print("bib_genes.tsv has been created.")

    else:
        bib_df = pd.read_csv(f"./results/{output_prefix}_bib_genes.tsv",sep="\t")
        print("bib_genes.tsv already exists. the tsv file has been loaded")
        
    # make a empty dataframe
    new_df = pd.DataFrame(columns=["ensembl_ID","ncbi_geneid","gene_name","availability_association","evidence","count_of_PMIDs_from_evidence","count_of_PMIDs_from_gene2pubmed","PMIDs_from_evidence","PMIDs_from_gene2pubmed"])

    new_gene_list = gene2pubmed.search_pmids(gene_list)

    for gene in gene_list:
        if gene in bib_df["gene"].values:
            reported_row = bib_df[bib_df["gene"]==gene].to_dict(orient="records")[0]
            pmids_evidence = reported_row["PMID_PMCID"]
            # make a space after each comma
            pmids_evidence = pmids_evidence.replace(",",", ")
            for new_gene in new_gene_list:
                if new_gene["ensg"] == gene:
                    counts = new_gene["count"]
                    gene_name = new_gene["gene_name"]
                    g2p_pmids = new_gene["pmids"]
                    g2p_pmids = g2p_pmids.replace(",",", ")
                    ncbi_geneid = new_gene["ncbi_geneid"]
                    reportedgene_dict = {"ensembl_ID":gene,
                                         "ncbi_geneid":ncbi_geneid,
                                         "gene_name":gene_name,
                                         "availability_association":"yes",
                                         "evidence":reported_row["evidence"],
                                         "count_of_PMIDs_from_evidence":len(reported_row["PMID_PMCID"].split(",")),
                                         "count_of_PMIDs_from_gene2pubmed":counts,
                                         "PMIDs_from_evidence":pmids_evidence,
                                         "PMIDs_from_gene2pubmed":g2p_pmids}
                    print(reportedgene_dict)
                    new_df = new_df._append(reportedgene_dict,ignore_index=True)
                    continue
                else:
                    pass

        else:
            for new_gene in new_gene_list:
                if new_gene["ensg"] == gene:
                    counts = new_gene["count"]
                    gene_name = new_gene["gene_name"]
                    g2p_pmids = new_gene["pmids"]
                    g2p_pmids = g2p_pmids.replace(",",", ")
                    ncbi_geneid = new_gene["ncbi_geneid"]
                    a_row = {"ensembl_ID":gene,
                             "ncbi_geneid":ncbi_geneid,
                             "gene_name":gene_name,
                             "availability_association":"no",
                             "evidence":"-",
                             "count_of_PMIDs_from_evidence":0,
                             "count_of_PMIDs_from_gene2pubmed":counts,
                             "PMIDs_from_evidence":"-",
                             "PMIDs_from_gene2pubmed":g2p_pmids}
                    new_df = new_df._append(a_row,ignore_index=True)
                    continue
                else:
                    pass
    
    # make a new directory in results directory if it doesn't exist
    if not os.path.exists(f"./results/{date}"):
        os.mkdir(f"./results/{date}")

    new_df = new_df.sort_values("count_of_PMIDs_from_gene2pubmed",ascending=True)
    new_df.to_csv(f"./results/{date}/{output_prefix}_output.tsv",sep="\t",index=False)
    

if __name__ == "__main__":
    main("config.yml")