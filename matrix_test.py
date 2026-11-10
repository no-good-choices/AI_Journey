import numpy as np

# 1. Define two 1D vectors (e.g., conceptual coordinates for two words)
word_a_vector = np.array([0.2, 0.8, -0.4])  # e.g., representing "Technology"
word_b_vector = np.array([0.1, 0.9, -0.3])  # e.g., representing "Software"

# 2. Calculate the dot product (multiplying matching elements and adding them up)
similarity_score = np.dot(word_a_vector, word_b_vector)

# 3. Print the geometric results to the terminal
print("--- AI Linear Algebra Test ---")
print(f"Mathematical Similarity Score: {similarity_score:.4f}")
