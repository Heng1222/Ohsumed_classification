import gzip
import rdflib
import pandas as pd
import random
from collections import defaultdict

# --- 配置 ---
LOCAL_NT_FILE = "nt_data/mesh2026.nt.gz"
OUTPUT_CSV_FILE = "mesh_dataset.csv"
SAMPLING_QUANTITY = 5000 # 預設取樣數量，可由使用者更改

# MeSH 命名空間
MESH = rdflib.Namespace("http://id.nlm.nih.gov/mesh/")
MESH_VOCAB = rdflib.Namespace("http://id.nlm.nih.gov/mesh/vocab#")
RDFS = rdflib.Namespace("http://www.w3.org/2000/01/rdf-schema#")

class MeshNode:
    def __init__(self, tree_number, descriptor_uri, terms=None):
        self.tree_number = tree_number
        self.descriptor_uri = descriptor_uri
        self.terms = set(terms) if terms else set() # 使用集合來儲存唯一的術語
        self.children = []
        self.parent = None
        self.depth = None # 稍後計算

    def add_child(self, child_node):
        self.children.append(child_node)
        child_node.parent = self

    def __repr__(self):
        return f"MeshNode(TreeNumber='{self.tree_number}', Terms={list(self.terms)})"

    def __hash__(self):
        return hash(self.tree_number)

    def __eq__(self, other):
        if not isinstance(other, MeshNode):
            return NotImplemented
        return self.tree_number == other.tree_number

def parse_mesh_rdf(nt_file):
    g = rdflib.Graph()
    print(f"--- 步驟 1: 解析 RDF 檔案 ---")
    print(f"正在解析 {nt_file}...")
    try:
        if nt_file.endswith(".gz"):
            with gzip.open(nt_file, 'rb') as f:
                g.parse(f, format="nt")
        else:
            g.parse(nt_file, format="nt")
    except Exception as e:
        print(f"解析 RDF 檔案時發生錯誤: {e}")
        raise # 印出錯誤後重新引發異常
    print(f"解析完成。總三元組數: {len(g)}")
    return g

def extract_data_from_graph(g):
    print("\n--- 步驟 2: 從 RDF 圖譜中提取資料 ---")
    descriptor_to_terms = defaultdict(set)
    tree_number_to_descriptor = defaultdict(list)
    
    print("正在提取 TreeNumber 到 Descriptor 的對應關係...")
    # 一個描述符 (s) 通過 vocab#treeNumber (p) 連結到一個 TreeNumber URI (o)
    for s, p, o in g.triples((None, MESH_VOCAB.treeNumber, None)):
        descriptor_uri = s
        tree_number_uri = str(o)
        tree_number = tree_number_uri.split('/')[-1]
        tree_number_to_descriptor[tree_number].append(descriptor_uri)
        
    print(f"找到 {len(tree_number_to_descriptor)} 個唯一的 TreeNumbers 對應到 Descriptors。")
    # 印出一些範例
    print("  範例 TreeNumber -> Descriptor 對應:")
    count = 0
    # 使用 items() 迭代鍵值對
    for tn, uris in tree_number_to_descriptor.items():
        if count >= 3: break
        print(f"    '{tn}' -> {[str(u) for u in uris]}")
        count += 1

    print("\n正在提取 Descriptor 到 Term 的對應關係...")
    all_descriptors_with_tn = {desc for descs in tree_number_to_descriptor.values() for desc in descs}

    if not all_descriptors_with_tn:
        print("警告: 找不到任何與 tree number 連結的 descriptor。術語提取可能為空。")

    processed_descriptors_count = 0
    for desc_uri in all_descriptors_with_tn:
        # 路徑: Descriptor -> Concept -> Term -> Label
        # 1. Descriptor -> Concept
        for concept_uri in g.objects(desc_uri, MESH_VOCAB.concept):
            # 2. Concept -> Term (使用 'term' 和 'preferredTerm')
            term_uris = set(g.objects(concept_uri, MESH_VOCAB.term))
            term_uris.update(g.objects(concept_uri, MESH_VOCAB.preferredTerm))

            for term_uri in term_uris:
                # 3. Term -> Label (使用 rdfs:label 和 vocab:prefLabel)，並移除雙引號
                for label in g.objects(term_uri, RDFS.label):
                    descriptor_to_terms[desc_uri].add(str(label).strip('"'))
                for label in g.objects(term_uri, MESH_VOCAB.prefLabel):
                    descriptor_to_terms[desc_uri].add(str(label).strip('"'))

        processed_descriptors_count += 1
        if processed_descriptors_count % 5000 == 0:
            print(f"  已處理 {processed_descriptors_count}/{len(all_descriptors_with_tn)} 個 descriptors 的術語提取...")

    print(f"完成 descriptors 的處理。")
    print(f"找到 {len(descriptor_to_terms)} 個具有關聯術語的 Descriptors。")
    # 印出一些範例
    print("  範例 Descriptor -> Terms 對應:")
    count = 0
    for desc, terms in descriptor_to_terms.items():
        if count >= 3: break
        if terms:
            print(f"    '{str(desc)}' -> {list(terms)[:3]}...")
            count += 1

    # 整合: TreeNumber 到 (Descriptor URI, Terms)
    tree_number_to_all_terms = defaultdict(set)
    tree_number_to_descriptor_uri_map = {} # 追蹤每個 TreeNumber 的一個主要 descriptor URI

    print("\n正在整合 TreeNumber 到 Terms 的對應關係...")
    for tn, descriptor_uris in tree_number_to_descriptor.items():
        if descriptor_uris:
            primary_descriptor_uri = descriptor_uris[0] 
            tree_number_to_descriptor_uri_map[tn] = primary_descriptor_uri
            if primary_descriptor_uri in descriptor_to_terms:
                tree_number_to_all_terms[tn].update(descriptor_to_terms[primary_descriptor_uri])
    print(f"已整合 {len(tree_number_to_all_terms)} 個具有術語的 TreeNumbers。")
    print("  範例 TreeNumber -> Terms 對應 (整合後):")
    count = 0
    for tn, terms in tree_number_to_all_terms.items():
        if count >= 3: break
        if terms:
            print(f"    '{tn}' -> {list(terms)[:3]}...")
            count += 1
    
    return tree_number_to_all_terms, tree_number_to_descriptor_uri_map, descriptor_to_terms

def build_disease_tree(tree_number_to_all_terms, tree_number_to_descriptor_uri_map, descriptor_to_terms, g):
    print("\n--- 步驟 3: 建立 'Diseases [C]' 樹狀結構 ---")
    
    # 1. 從資料中獲取所有以 'C' 開頭的顯式樹狀編號
    explicit_disease_tns = {tn for tn in tree_number_to_all_terms if tn.startswith('C')}
    print(f"找到 {len(explicit_disease_tns)} 個以 'C' 開頭的顯式樹狀編號。")

    # 2. 產生所有隱含的父層樹狀編號
    all_required_tns = set(explicit_disease_tns)
    for tn in explicit_disease_tns:
        parts = tn.split('.')
        for i in range(1, len(parts)):
            parent_tn = ".".join(parts[:i])
            all_required_tns.add(parent_tn)
    all_required_tns.add('C') # 確保根節點 'C' 被包含
    
    print(f"總共需要建立的節點數 (顯式 + 隱式): {len(all_required_tns)}")

    # 3. 為每個需要的樹狀編號建立 MeshNode 物件
    nodes = {}
    for tn in all_required_tns:
        descriptor_uri = tree_number_to_descriptor_uri_map.get(tn)
        terms_from_concepts = tree_number_to_all_terms.get(tn) # 取所有Term為內容
        nodes[tn] = MeshNode(tn, descriptor_uri, terms_from_concepts)
    
    # 如果 'C' 節點沒有術語，進行特殊處理
    if 'C' in nodes and not nodes['C'].terms:
        print("根節點 'C' 沒有術語，嘗試從 descriptor D004194 填入。")
        diseases_descriptor_uri = MESH.D004194
        if diseases_descriptor_uri in descriptor_to_terms:
            nodes['C'].terms.update(descriptor_to_terms[diseases_descriptor_uri])
            print("已從現有的 descriptor 資料填入 'C' 節點的術語。")
        if not nodes['C'].terms: # 如果仍然沒有術語
            nodes['C'].terms.add('Diseases')
            print("使用備用術語 'Diseases' 建立 'C' 節點。")

    # 新增：確保每個節點都包含其 Descriptor 的 rdfs:label (如果存在)
    print("正在為所有節點新增 Descriptor 的 rdfs:label (如果存在)...")
    descriptors_labels_added = 0
    for tn, node in nodes.items():
        if node.descriptor_uri:
            # 嘗試從 descriptor 的 rdfs:label 取得術語
            for label in g.objects(node.descriptor_uri, RDFS.label):
                node.terms.add(str(label).strip('"'))
                descriptors_labels_added += 1
                break # We only need one
    if descriptors_labels_added > 0:
        print(f"已為 {descriptors_labels_added} 個節點新增了 Descriptor 的 rdfs:label。")

    # 新增：確保每個節點至少有一個術語 (針對仍無術語的節點，使用 Tree Number 作為備用)
    print("正在檢查並確保所有節點都至少有一個術語 (備用方案)...")
    nodes_fixed_with_treenum = 0
    for tn, node in nodes.items():
        if not node.terms: # This condition now means 'after adding concept terms and descriptor label'
            node.terms.add(tn)
            nodes_fixed_with_treenum += 1
    if nodes_fixed_with_treenum > 0:
        print(f"已為 {nodes_fixed_with_treenum} 個節點新增了 tree number 作為術語 (最終備用)。")


    print(f"已建立 {len(nodes)} 個 MeshNode 物件。")

    # 4. 將子節點連結到父節點並計算深度
    print("正在將節點連結成樹狀結構並設定深度...")
    all_tn_sorted = sorted(nodes.keys(), key=lambda x: x.count('.')) # 按點的數量排序以確保父節點先處理

    for tn in all_tn_sorted:
        node = nodes[tn]
        node.depth = get_depth(tn) # 使用新的全域 get_depth 函數

        # --- 連結至父節點 ---
        if tn == 'C':
            continue # C 是根，沒有父節點

        # 判斷父節點
        is_top_level_cat = '.' not in tn
        parent_tn = "C" if is_top_level_cat else ".".join(tn.split('.')[:-1])

        if parent_tn in nodes:
            parent_node = nodes[parent_tn]
            parent_node.add_child(node)
        else:
             print(f"嚴重警告: 節點 '{tn}' 的父節點 '{parent_tn}' 不存在。跳過此連結。")
    
    print("樹狀結構連結完成。")
    if 'C' in nodes:
        print(f"  根節點 'C' 有 {len(nodes['C'].children)} 個直接子節點。")

    return nodes.get('C'), nodes

def print_subtree_info(node, level=0):
    """遞迴地印出一個節點及其所有子節點的詳細資訊。"""
    indent = "  " * level
    parent_tn = node.parent.tree_number if node.parent else "None"
    
    print(f"{indent}--- Node: {node.tree_number} ---")
    print(f"{indent}  - 深度 (Depth): {node.depth}")
    print(f"{indent}  - 父節點 (Parent): {parent_tn}")
    print(f"{indent}  - 子節點數量 (Children): {len(node.children)}")
    print(f"{indent}  - 描述符 URI (Descriptor): {node.descriptor_uri}")
    print(f"{indent}  - 術語 (Terms): {node.terms if node.terms else '{}'}")
    
    for child in sorted(node.children, key=lambda n: n.tree_number):
        print_subtree_info(child, level + 1)

def get_depth(tree_number):
    """根據使用者規則計算'C'類別下的節點深度。"""
    # 規則: C=1, C01=2, C01.123=3
    if not tree_number:
        return 0
    
    if not tree_number.startswith('C'):
        return tree_number.count('.') + 1 # For non-'C' categories

    if '.' not in tree_number:
        # C -> 1, C01 -> 2
        return 1 if tree_number == 'C' else 2
    else:
        # C01.123 -> count('.') is 1 -> 1 + 2 = 3
        return tree_number.count('.') + 2

def get_lcs_path_and_depth(tn1, tn2):
    """找到兩個樹狀編號的最低共同上層 (LCS) 的路徑和深度。"""
    path1 = get_path_components(tn1)
    path2 = get_path_components(tn2)

    lcs_tn_components = []
    min_len = min(len(path1), len(path2))
    for i in range(min_len):
        if path1[i] == path2[i]:
            lcs_tn_components.append(path1[i])
        else:
            break
    
    if not lcs_tn_components:
        # 如果沒有共同路徑，且兩者都是疾病，則 LCS 為根節點 'C'
        if tn1.startswith('C') and tn2.startswith('C'):
            return 'C', 1
        return "", 0

    lcs_tree_number = lcs_tn_components[-1]
    lcs_depth = get_depth(lcs_tree_number)
    return lcs_tree_number, lcs_depth

def get_path_components(tree_number):
    """返回祖先樹狀編號組件的列表。"""
    if not tree_number:
        return []

    path = []
    # 加入根節點 C
    if tree_number.startswith('C') and tree_number != 'C':
        path.append('C')

    parts = tree_number.split('.')
    current_path_parts = []
    for part in parts:
        current_path_parts.append(part)
        path.append(".".join(current_path_parts))
    # 找 tree_number 往上所有父節點的唯一路徑
    unique_path = []
    for p in path:
        if p not in unique_path:
            unique_path.append(p)
    return unique_path

def wup_similarity(tn1, tn2, log_example=False):
    """計算兩個樹狀編號之間的 Wu-Palmer 相似度。"""
    if tn1 == tn2:
        return 1.0

    depth1 = get_depth(tn1)
    depth2 = get_depth(tn2)

    if depth1 == 0 or depth2 == 0:
        return 0.0

    lcs_tn, depth_lcs = get_lcs_path_and_depth(tn1, tn2)

    if depth_lcs == 0:
        return 0.0
    
    # Wu-Palmer 公式
    similarity = (2.0 * depth_lcs) / (depth1 + depth2)
    
    if log_example:
        print(f"    - Sim('{tn1}', '{tn2}')")
        print(f"      - Depth1: {depth1}, Depth2: {depth2}")
        print(f"      - LCS: '{lcs_tn}' (Depth: {depth_lcs})")
        print(f"      - Similarity: (2 * {depth_lcs}) / ({depth1} + {depth2}) = {similarity:.4f}")

    return similarity

def main():
    # --- 第 1 部分: 資料處理與樹狀結構 ---
    g = parse_mesh_rdf(LOCAL_NT_FILE)
    tree_number_to_all_terms, tree_number_to_descriptor_uri_map, descriptor_to_terms = extract_data_from_graph(g)

    disease_root, all_disease_nodes = build_disease_tree(tree_number_to_all_terms, tree_number_to_descriptor_uri_map, descriptor_to_terms, g)

    if not disease_root:
        print("建立 'Diseases [C]' 樹失敗。正在結束程式。")
        return

    # 新增：印出所有深度為 2 的節點及其子節點數量
    print("\n--- 節點資訊：深度為 2 的節點 ---")
    nodes_at_depth_2 = [n for n in all_disease_nodes.values() if n.depth == 2]
    if nodes_at_depth_2:
        for node in sorted(nodes_at_depth_2, key=lambda n: n.tree_number):
            print(f"  - 節點: {node.tree_number} (深度 {node.depth}), 子節點數量: {len(node.children)}")
    else:
        print("  找不到深度為 2 的節點。")

    total_nodes = len(all_disease_nodes)
    all_terms_in_tree = set()
    for node in all_disease_nodes.values():
        all_terms_in_tree.update(node.terms)
    total_unique_terms = len(all_terms_in_tree)

    print(f"\n--- 步驟 4: 最終樹狀結構摘要 ---")
    max_samples = total_unique_terms * (total_unique_terms - 1) // 2
    print(f"'C' 類別中的總節點數: {total_nodes}")
    print(f"'C' 類別中的總唯一術語數: {total_unique_terms}")
    print(f"基於唯一的術語對，理論上最多可產生 {max_samples:,} 個樣本。")

    # --- 印出 C21 子樹的詳細資訊 ---
    print("\n--- C21 子樹詳細資訊 (便於檢查) ---")
    if 'C21' in all_disease_nodes:
        print_subtree_info(all_disease_nodes['C21'])
    else:
        print("在資料中找不到 C21 節點。")


    # --- 第 2 部分: 取樣與相似度計算 ---
    print(f"\n--- 步驟 5: 為 CSV 檔案產生 {SAMPLING_QUANTITY} 個樣本 ---")
    
    valid_sampling_nodes = [node for node in all_disease_nodes.values() if node.terms and len(node.terms) > 0]
    print(f"找到 {len(valid_sampling_nodes)} 個可用於取樣的節點。")
    if len(valid_sampling_nodes) < 2:
        print("沒有足夠的節點來進行取樣。正在結束程式。")
        return

    sampled_pairs_data = []
    seen_term_pairs = set() # 用於確保 (term_i, term_j) 的組合是唯一的

    attempts = 0
    max_attempts = SAMPLING_QUANTITY * 20 # 防止因唯一配對稀少而導致無限迴圈

    print("開始取樣過程...")
    while len(sampled_pairs_data) < SAMPLING_QUANTITY and attempts < max_attempts:
        attempts += 1
        
        # 修改：允許重複取樣節點
        node1, node2 = random.choices(valid_sampling_nodes, k=2)

        if not node1.terms or not node2.terms:
            continue

        term_i = random.choice(list(node1.terms))
        term_j = random.choice(list(node2.terms))

        if term_i == term_j:
            continue # 術語必須不同

        current_term_pair = frozenset({term_i, term_j})
        if current_term_pair in seen_term_pairs:
            continue
            
        # 詳細記錄前 20 個成功的樣本
        log_this_sample = len(sampled_pairs_data) < 20
        
        similarity = wup_similarity(node1.tree_number, node2.tree_number, log_this_sample)
        
        if log_this_sample:
            print(f"  - 樣本 #{len(sampled_pairs_data) + 1}:")
            print(f"    - Node1: '{node1.tree_number}' | Term: '{term_i}'")
            print(f"    - Node2: '{node2.tree_number}' | Term: '{term_j}'")

        # 將相似度四捨五入到小數點後兩位
        rounded_similarity = round(similarity, 2)
        
        sampled_pairs_data.append({"word_i": term_i, "word_j": term_j, "wup_similarity": rounded_similarity})
        seen_term_pairs.add(current_term_pair)
        
        if (len(sampled_pairs_data) % 100 == 0) and not log_this_sample:
            print(f"  已產生 {len(sampled_pairs_data)}/{SAMPLING_QUANTITY} 個樣本...")

    print("取樣完成。")
    if len(sampled_pairs_data) < SAMPLING_QUANTITY:
        print(f"警告: 在 {attempts} 次嘗試後，只能產生 {len(sampled_pairs_data)} 個唯一樣本（要求為 {SAMPLING_QUANTITY}）。")

    df = pd.DataFrame(sampled_pairs_data)
    df.to_csv(OUTPUT_CSV_FILE, index=False)
    print(f"\n--- 步驟 6: 輸出 ---")
    print(f"已產生 {len(df)} 個樣本並儲存至 {OUTPUT_CSV_FILE}")
    print("輸出檔案的前 5 列:")
    print(df.head())

if __name__ == "__main__":
    main()
