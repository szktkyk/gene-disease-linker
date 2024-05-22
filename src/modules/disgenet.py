from SPARQLWrapper import SPARQLWrapper
import requests

def disgenet2list(dctermID,score,limit):
    """
    dctermID: disease ID defined in ncit
    score: threshold of score
    limit: limit of the number of pmids for each gene
    """
    sparql = SPARQLWrapper(endpoint='http://rdf.disgenet.org/sparql/', returnFormat='json')
    query_disease = f"""
        SELECT DISTINCT ?gene str(?geneName) as ?name ?score 
        WHERE {{ 
            ?gda sio:SIO_000628 ?gene,?disease ; 
                sio:SIO_000216 ?scoreIRI . 
            ?gene rdf:type ncit:C16612 ;
                dcterms:title ?geneName . 
            ?disease rdf:type ncit:C7057 
                FILTER (?disease=<http://linkedlifedata.com/resource/umls/id/{dctermID}>) . 
            ?scoreIRI sio:SIO_000300 ?score . 
            FILTER (?score >= {score}) 
        }} ORDER BY DESC(?score)
    """
    print(query_disease)
    sparql.setQuery(query_disease)
    gene_list = []
    results = sparql.query().convert()
    for r in results["results"]["bindings"]:
        gene_list.append(r["gene"]["value"])

    pre_list = []
    for gene in gene_list:
        print(f"gene: {gene}")
        query_pmid = f"""        
            SELECT DISTINCT ?gda
            <http://linkedlifedata.com/resource/umls/id/{dctermID}> as ?disease
            <{gene}> as ?gene 
            ?score ?source ?associationType	?pmid  ?sentence
            WHERE {{
                ?gda sio:SIO_000628
                    <http://linkedlifedata.com/resource/umls/id/{dctermID}>,
                    <{gene}> ;
                    rdf:type ?associationType ;
                    sio:SIO_000216 ?scoreIRI ;
                    sio:SIO_000253 ?source .
                ?scoreIRI sio:SIO_000300 ?score .
                OPTIONAL {{
                    ?gda sio:SIO_000772 ?pmid .
                    ?gda dcterms:description ?sentence .
                }}
            }}
            LIMIT {limit}
        """
        print(query_pmid)
        sparql.setQuery(query_pmid)
        pmid_tmp_list = []
        results_evidence = sparql.query().convert()
        for i in results_evidence["results"]["bindings"]:
            try:
                pmid_url = i["pmid"]["value"]
                pmid_tmp_list.append(pmid_url.split('pubmed/')[-1])
            except:
                continue
        pmids = ",".join(pmid_tmp_list)

        geneid = gene.split('ncbigene/')[-1]
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
                pre_list.append({"gene":result['converted'],"PMID_PMCID":pmids,"evidence":"DisGeNET"})
                print({"gene":result['converted'],"PMID_PMCID":pmids,"evidence":"DisGeNET"})
            else:
                continue

    return pre_list