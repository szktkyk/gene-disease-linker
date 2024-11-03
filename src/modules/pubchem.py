from SPARQLWrapper import SPARQLWrapper
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
from urllib3.exceptions import MaxRetryError
from requests.exceptions import RequestException


def create_retry_session(retries=3, backoff_factor=0.3):
    """カスタムリトライ設定付きのセッションを作成"""
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        allowed_methods=["POST", "GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def convert_gene_id(session, geneid, max_retries=3):
    """遺伝子IDの変換を行う（リトライ処理付き）"""
    for attempt in range(max_retries):
        try:
            response = session.post(
                url='https://biit.cs.ut.ee/gprofiler/api/convert/convert/',
                json={
                    'organism': 'hsapiens',
                    'target': 'ENSG',
                    'query': geneid,
                },
                verify=False  # SSL検証を無効化
            )
            response.raise_for_status()
            return response.json()['result']
        except RequestException as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                print(f"Failed to convert gene ID after {max_retries} attempts")
                return []
            time.sleep(2 ** attempt)  # 指数バックオフ


def pubchem2list(pubchem_diseaseID):
    """
    PubChemからの遺伝子リストの取得と変換
    """
    sparql = SPARQLWrapper(endpoint='https://rdfportal.org/pubchem/sparql', returnFormat='json')
    session = create_retry_session()
    
    # SPARQL クエリ（変更なし）
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
    pre_list = []
    
    try:
        results = sparql.query().convert()
        for r in results["results"]["bindings"]:
            gene_list.append(r["gene"]["value"])
        print(f"the number of genes:{len(gene_list)}")

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
            ?ref pcvocab:discussesAsDerivedByTextMining disease:{pubchem_diseaseID} .
            ?ref dcterms:identifier ?pmid .
            FILTER (STRSTARTS(STR(?pmid), "https://pubmed.ncbi.nlm.nih.gov/") && !CONTAINS(STR(?pmid), "PMC"))
            }}
            """
            
            sparql.setQuery(query_pmid)
            pmid_tmp_list = []
            
            try:
                results_evidence = sparql.query().convert()
                for i in results_evidence["results"]["bindings"]:
                    try:
                        pmid_url = i["pmid"]["value"]
                        pmid_tmp_list.append(pmid_url.split('.nlm.nih.gov/')[-1])
                    except:
                        continue
                
                pmids = ",".join(pmid_tmp_list)
                geneid = gene.split('/pubchem/gene/')[-1]
                
                # 遺伝子ID変換の実行
                resultlist = convert_gene_id(session, geneid)
                
                for result in resultlist:
                    if result['converted'].startswith('ENSG'):
                        entry = {
                            "gene": result['converted'],
                            "PMID_PMCID": pmids,
                            "evidence": "PubChem"
                        }
                        pre_list.append(entry)
                        print(entry)
                    else:
                        print("No ENSG")
                        continue
                
                # レート制限対策の待機
                time.sleep(1)
                
            except Exception as e:
                print(f"Error processing gene {gene}: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error in main process: {str(e)}")
        
    return pre_list



# def pubchem2list(pubchem_diseaseID):
#     """
#     """
#     sparql = SPARQLWrapper(endpoint='https://rdfportal.org/pubchem/sparql', returnFormat='json')
#     query_disease = f"""
#     PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#     PREFIX sio: <http://semanticscience.org/resource/>
#     PREFIX disease: <http://rdf.ncbi.nlm.nih.gov/pubchem/disease/>
#     select distinct ?gene ?score  {{
#     VALUES ?disease {{disease:{pubchem_diseaseID}}}
#     graph <http://rdf.ncbi.nlm.nih.gov/pubchem/cooccurrence> {{
#         ?s a sio:SIO_000983 ;
#         sio:SIO_000300 ?score;
#         rdf:subject ?disease ;
#         rdf:object ?gene .
#         }}
#     }}
#     order by desc(?score)
#     """
#     print(query_disease)
#     sparql.setQuery(query_disease)
#     gene_list = []
#     results = sparql.query().convert()
#     for r in results["results"]["bindings"]:
#         gene_list.append(r["gene"]["value"])
#     print(f"the number of genes:{len(gene_list)}")

#     pre_list = []
#     for gene in gene_list:
#         print(f"gene: {gene}")
#         query_pmid = f"""        
#         PREFIX prism: <http://prismstandard.org/namespaces/basic/3.0/>
#         PREFIX dcterms: <http://purl.org/dc/terms/>
#         PREFIX pcvocab: <http://rdf.ncbi.nlm.nih.gov/pubchem/vocabulary#>
#         PREFIX disease: <http://rdf.ncbi.nlm.nih.gov/pubchem/disease/>
#         PREFIX gene: <http://rdf.ncbi.nlm.nih.gov/pubchem/gene/>
#         PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

#         SELECT ?ref, ?pmid
#         FROM <http://rdf.ncbi.nlm.nih.gov/pubchem/reference>
#         WHERE {{
#         ?ref pcvocab:discussesAsDerivedByTextMining <{gene}> .
#         ?ref pcvocab:discussesAsDerivedByTextMining disease:{pubchem_diseaseID} .
#         ?ref dcterms:identifier ?pmid .
#         FILTER (STRSTARTS(STR(?pmid), "https://pubmed.ncbi.nlm.nih.gov/") && !CONTAINS(STR(?pmid), "PMC"))
#         }}
#         """
#         # print(query_pmid)
#         sparql.setQuery(query_pmid)
#         pmid_tmp_list = []
#         results_evidence = sparql.query().convert()
#         # print(results_evidence)
#         for i in results_evidence["results"]["bindings"]:
#             try:
#                 pmid_url = i["pmid"]["value"]
#                 pmid_tmp_list.append(pmid_url.split('.nlm.nih.gov/')[-1])
#             except:
#                 continue
#         pmids = ",".join(pmid_tmp_list)

#         geneid = gene.split('/pubchem/gene/')[-1]
#         # print(geneid)
#         r = requests.post(
#         url='https://biit.cs.ut.ee/gprofiler/api/convert/convert/',
#         json={
#             'organism':'hsapiens',
#             'target':'ENSG',
#             'query':geneid,
#         }
#         )
#         resultlist = r.json()['result']
#         for result in resultlist:
#             if result['converted'].startswith('ENSG'):
#                 pre_list.append({"gene":result['converted'],"PMID_PMCID":pmids,"evidence":"PubChem"})
#                 print({"gene":result['converted'],"PMID_PMCID":pmids,"evidence":"PubChem"})
#             else:
#                 print("No ENSG")
#                 continue

#     return pre_list

