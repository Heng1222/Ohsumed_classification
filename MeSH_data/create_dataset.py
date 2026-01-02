import rdflib
import networkx as nx
import pandas as pd
import random

def process_mesh_with_names(input_file, output_file="mesh_dataset.csv", sample_pairs=100):
    print("正在載入 RDF 資料...")
    g = rdflib.Graph()
    g.parse(input_file, format="nt")

    tree_graph = nx.DiGraph()
    
    # 建立兩個對照表
    tn_to_descriptor = {}  # TreeNumber -> DescriptorURI
    desc_to_label = {}     # DescriptorURI -> Human Label

    MESHV = rdflib.Namespace("http://id.nlm.nih.gov/mesh/vocab#")
    RDFS = rdflib.RDFS

    print("正在建立名詞映射表與樹狀結構...")
    for s, p, o in g:
        # 1. 構建樹的邊
        if p == MESHV.parentTreeNumber:
            tree_graph.add_edge(str(o), str(s))
        
        # 2. 建立 TreeNumber 到 Descriptor 的連結
        # 在 MeSH 中，Descriptor 會透過 meshv:treeNumber 連結到 TreeNumber
        elif p == MESHV.treeNumber:
            # s 是 Descriptor (如 D00123), o 是 TreeNumber (如 A01.123)
            tn_to_descriptor[str(o)] = str(s)
        
        # 3. 建立 Descriptor 到文字 Label 的連結
        elif p == RDFS.label:
            desc_to_label[str(s)] = str(o)

    # 預計算深度
    roots = [n for n, d in tree_graph.in_degree() if d == 0]
    for r in roots: tree_graph.add_edge("root", r)
    depths = nx.shortest_path_length(tree_graph, source="root")

    results = []
    nodes = [n for n in tree_graph.nodes() if n != "root"]

    print("開始生成帶有名稱的詞對...")
    while len(results) < sample_pairs:
        u, v = random.sample(nodes, 2)
        
        # 只有當這兩個編號都能對應到真實名詞時才計算
        if u in tn_to_descriptor and v in tn_to_descriptor:
            desc_u = tn_to_descriptor[u]
            desc_v = tn_to_descriptor[v]
            
            if desc_u in desc_to_label and desc_v in desc_to_label:
                name_u = desc_to_label[desc_u]
                name_v = desc_to_label[desc_v]
                
                # 計算 WUP
                try:
                    lca = nx.lowest_common_ancestor(tree_graph, u, v)
                    wup = (2.0 * depths[lca]) / (depths[u] + depths[v])
                    
                    results.append({
                        "word_i": name_u,
                        "word_j": name_v,
                        "wup_similarity": round(wup, 4)
                    })
                except:
                    continue

    df = pd.DataFrame(results).drop_duplicates()
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"成功輸出含有名詞的資料至 {output_file}！")

if __name__ == "__main__":
    process_mesh_with_names("mesh2025.nt")