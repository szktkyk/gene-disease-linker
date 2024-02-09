import pandas as pd
import argparse
import os
import datetime
from modules import gene2pubmed, get_evidence_otp

t_delta = datetime.timedelta(hours=9)
JST = datetime.timezone(t_delta, "JST")
now = datetime.datetime.now(JST)
date = now.strftime("%Y%m%d")

parser = argparse.ArgumentParser(description="This script takes a list of ensembl genes in a text file, and links your gene set with the collected information (gene-disease associations and evidences)")
parser.add_argument("path_to_your_genes", help="path to your genes in a text file")
parser.add_argument("efoID",type=str, help="efo ontology ID")
parser.add_argument("output", help="Add this to the output file name")


args = parser.parse_args()

def main():
    gene2pubmed.download_file()
    # read a txt file and make a list
    with open(args.path_to_your_genes) as f:
        gene_list = f.read().splitlines()
    with open("./results/otp_genes.txt") as f:
        otp_list = f.read().splitlines()
    common_genes = list(set(gene_list) & set(otp_list))
        
    # Get the evidence from OpenTargets
    otp_df = get_evidence_otp.get_evidence_otp(common_genes,args.efoID,2000)
    otp_df.to_csv(f"./results/otp_genes.tsv", sep='\t',index=False)
    # otp_df = pd.read_csv("./results/otp_genes.tsv",sep="\t")
    mirtex_df = pd.read_csv("./results/mirtex_genes.tsv",sep="\t")
    rnadisease_df = pd.read_csv("./results/rnadisease_genes.tsv", sep="\t")
    disgenet_df = pd.read_csv("./results/disgenet_genes.tsv", sep="\t")
    pubchem_df = pd.read_csv("./results/pubchem_genes.tsv", sep="\t")


    bib_df = pd.concat([otp_df,mirtex_df,rnadisease_df,disgenet_df,pubchem_df],ignore_index=True)
    bib_df["PMID_PMCID"] = bib_df["PMID_PMCID"].astype(str)
    bib_df = bib_df.groupby('gene').agg({'PMID_PMCID':','.join,'evidence':','.join}).reset_index()
    bib_df = bib_df.reset_index().rename(columns={"gene":"gene","PMID_PMCID":"PMID_PMCID","evidence":"evidence"})
    bib_df = bib_df.drop("index",axis=1)
    # delete the duplicated PMIDs
    bib_df["PMID_PMCID"] = bib_df["PMID_PMCID"].apply(lambda x: ",".join(pd.unique(str(x).split(","))) if pd.notna(x) else x)
    # print(len(bib_df))
    bib_df.to_csv(f"./results/{args.output}_bib_genes.tsv", sep='\t',index=False)


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
    new_df.to_csv(f"./results/{date}/{args.output}_output.tsv",sep="\t",index=False)
    

if __name__ == "__main__":
    main()