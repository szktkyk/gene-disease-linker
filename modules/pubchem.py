from SPARQLWrapper import SPARQLWrapper
import requests

def pubchem2list(pubchem_diseaseID):
    """
    """
    sparql = SPARQLWrapper(endpoint='https://rdfportal.org/pubchem/sparql', returnFormat='json')
    query_disease = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX disease: <http://rdf.ncbi.nlm.nih.gov/pubchem/disease/>
    select distinct ?gene ?score  {{
    VALUES ?disease {{disease:{pubchem_diseaseID}}}
    graph <http://rdf.ncbi.nlm.nih.gov/pubchem/cooccurrence> {{
        ?s a sio:SIO_000983 ;
        sio:SIO_000300 ?score;
        rdf:subject ?disease ;
        rdf:object ?gene .
        }}
    }}
    order by desc(?score)
    """
    print(query_disease)
    sparql.setQuery(query_disease)
    gene_list = []
    results = sparql.query().convert()
    for r in results["results"]["bindings"]:
        gene_list.append(r["gene"]["value"])
    print(len(gene_list))

    pre_list = []
    for gene in gene_list:
        print(f"gene: {gene}")
        query_pmid = f"""        
        PREFIX prism: <http://prismstandard.org/namespaces/basic/3.0/>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX pcvocab: <http://rdf.ncbi.nlm.nih.gov/pubchem/vocabulary#>
        PREFIX disease: <http://rdf.ncbi.nlm.nih.gov/pubchem/disease/>
        PREFIX gene: <http://rdf.ncbi.nlm.nih.gov/pubchem/gene/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?ref, ?pmid
        FROM <http://rdf.ncbi.nlm.nih.gov/pubchem/reference>
        WHERE {{
        ?ref pcvocab:discussesAsDerivedByTextMining <{gene}> .
        ?ref pcvocab:discussesAsDerivedByTextMining disease:DZID8805 .
        ?ref dcterms:identifier ?pmid .
        FILTER (STRSTARTS(STR(?pmid), "https://pubmed.ncbi.nlm.nih.gov/") && !CONTAINS(STR(?pmid), "PMC"))
        }}
        """
        # print(query_pmid)
        sparql.setQuery(query_pmid)
        pmid_tmp_list = []
        results_evidence = sparql.query().convert()
        # print(results_evidence)
        for i in results_evidence["results"]["bindings"]:
            try:
                pmid_url = i["pmid"]["value"]
                pmid_tmp_list.append(pmid_url.split('.nlm.nih.gov/')[-1])
            except:
                continue
        pmids = ",".join(pmid_tmp_list)

        geneid = gene.split('/pubchem/gene/')[-1]
        print(geneid)
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
                pre_list.append({"gene":result['converted'],"PMID_PMCID":pmids,"evidence":"PubChem"})
                print({"gene":result['converted'],"PMID_PMCID":pmids,"evidence":"PubChem"})
            else:
                continue

    return pre_list

