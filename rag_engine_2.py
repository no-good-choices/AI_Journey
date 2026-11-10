import numpy as np

# Local text blocks matching the exact nodes in your UI
COMPONENT_KNOWLEDGE = {
    "tsiata_hypercar_root": "The root workspace directory contains the baseline mechanical engineering parameter matrix and tracking specifications for the TSIATA hypercar platform.",
    "assembly_manifest.json": "The assembly manifest configuration defines the structural file schema linkages between FreeCAD geometry inputs, Blender assets, and SQLite data logs.",
    "chassis_system": "The monocoque chassis is built from advanced pre-preg carbon fiber weave, forming a 340 kg core survival cell matching the 1250 kg total hypercar weight target.",
    "powertrain_unit": "The powertrain unit is a custom twin-turbo V8 hybrid implementation producing 2000 horsepower and 1800 lb-ft of torque, utilizing a highly advanced active AWD layout.",
    "aero_surfaces": "Aerodynamic packages feature active front and rear wing profiles generating 2500+ lbs of downforce at 250 mph to ensure stabilization up to a targeted 520+ MPH."
}

def normalize_and_tokenize(text):
    """Slices raw text strings into manageable numeric token arrays."""
    return text.lower().replace(".", "").replace(",", "").replace("(", "").replace(")", "").split()

def get_term_frequency_vector(text, vocabulary):
    """Maps words directly to a localized term-frequency matrix coordinate."""
    tokens = normalize_and_tokenize(text)
    vector = np.zeros(len(vocabulary))
    for token in tokens:
        if token in vocabulary:
            idx = vocabulary[token]
            vector[idx] += 1
            
    magnitude = np.linalg.norm(vector)
    if magnitude == 0:
        return vector
    return vector / magnitude

def compute_ui_similarity(selected_node):
    """Executes a pure NumPy dot-product vector matrix calculation locally."""
    if selected_node not in COMPONENT_KNOWLEDGE:
        return f"No vector matrix baseline mapped for node: {selected_node}"
        
    doc_text = COMPONENT_KNOWLEDGE[selected_node]
    
    # Form a unique vocabulary grid for this specific document slice
    words = sorted(list(set(normalize_and_tokenize(doc_text))))
    vocabulary = {word: idx for idx, word in enumerate(words)}
    
    # Vectorize both the document and a dynamic matching search target query
    doc_vector = get_term_frequency_vector(doc_text, vocabulary)
    query_text = f"engineering data metrics for the active {selected_node.replace('_', ' ')}"
    query_vector = get_term_frequency_vector(query_text, vocabulary)
    
    # Calculate directional Cosine Match Score via strict NumPy Dot Product matrix math
    dot_product_score = float(np.dot(doc_vector, query_vector))
    
    return (
        f"<b>Backend Engine Matrix:</b> Local NumPy Dot-Product Executed<br>"
        f"<b>Cosine Similarity Metric:</b> <span style='color: #0A5C96;'>{dot_product_score:.4f}</span><br>"
        f"<b>Vocabulary Workspace Size:</b> {len(vocabulary)} dimensions<br><br>"
        f"<b>Extracted Knowledge Base Chunk:</b><br>\"{doc_text}\""
    )
