import os
import json
import sqlite3
from pathlib import Path
from typing import Optional

# Path to the SQLite question bank
DB_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH = DB_DIR / "question_bank.db"


def get_db_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initializes the questions and keyword_index tables in SQLite."""
    conn = get_db_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            subtopic TEXT DEFAULT '',
            difficulty INTEGER DEFAULT 2 CHECK(difficulty BETWEEN 1 AND 5),
            stage TEXT DEFAULT 'easy', -- 'easy' (1-2), 'medium' (3), 'hard' (4-5)
            question_text TEXT NOT NULL,
            model_answer TEXT NOT NULL,
            keywords TEXT NOT NULL,       -- JSON list: ["r_squared", "regression"]
            related_concepts TEXT DEFAULT '[]', -- JSON list
            times_used INTEGER DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS keyword_index (
            keyword TEXT NOT NULL,
            question_id TEXT NOT NULL,
            weight REAL DEFAULT 1.0,
            PRIMARY KEY (keyword, question_id)
        )
    """)

    c.execute("CREATE INDEX IF NOT EXISTS idx_keyword ON keyword_index(keyword)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_topic ON questions(topic)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_difficulty ON questions(difficulty)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_stage ON questions(stage)")

    conn.commit()
    conn.close()


def get_stage_for_difficulty(difficulty: int) -> str:
    if difficulty <= 2:
        return "easy"
    elif difficulty == 3:
        return "medium"
    else:
        return "hard"


# Comprehensive, interconnected seed questions across domains
SEED_QUESTIONS = [
    # ══════════════════════════════════════════════════════════════════════════
    # MACHINE LEARNING — EASY (Levels 1 - 2) [Turns 1 - 5 target]
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "ml_easy_001",
        "topic": "machine_learning",
        "subtopic": "regression",
        "difficulty": 2,
        "question_text": "What is Linear Regression and how does it work?",
        "model_answer": "Linear Regression is a supervised machine learning algorithm used to model the relationship between a dependent continuous variable and one or more independent variables. It fits a straight line using the equation Y = mx + b (or Y = beta_0 + beta_1 * X), where m is the slope and b is the intercept. The algorithm finds the best-fitting line by minimizing the sum of squared residuals using Ordinary Least Squares (OLS). It can be evaluated using metrics like R-squared (R2 score), Mean Squared Error (MSE), and Mean Absolute Error (MAE).",
        "keywords": [
            "linear_regression", "supervised_learning", "regression", "y_equals_mx_plus_b",
            "slope", "intercept", "least_squares", "r_squared", "mse", "continuous_variable",
            "residuals", "mae"
        ],
        "related_concepts": ["r_squared", "mse", "multiple_regression", "gradient_descent", "overfitting"]
    },
    {
        "id": "ml_easy_002",
        "topic": "machine_learning",
        "subtopic": "evaluation",
        "difficulty": 2,
        "question_text": "What is R-squared (R2) score and what does an R2 value indicate?",
        "model_answer": "R-squared, also called the coefficient of determination, measures the proportion of variance in the target dependent variable that is predictable from the independent variables. It is calculated as R2 = 1 - (SS_res / SS_tot). An R2 value of 1.0 indicates a perfect fit, while 0.0 means the model performs no better than predicting the mean. However, standard R-squared can be misleading because adding arbitrary features always increases or maintains R2, which can disguise overfitting. For this reason, Adjusted R-squared is often used.",
        "keywords": [
            "r_squared", "coefficient_of_determination", "variance", "ss_res", "ss_tot",
            "residuals", "goodness_of_fit", "adjusted_r_squared", "overfitting", "model_evaluation"
        ],
        "related_concepts": ["adjusted_r_squared", "overfitting", "mse", "residuals", "multicollinearity"]
    },
    {
        "id": "ml_easy_003",
        "topic": "machine_learning",
        "subtopic": "loss_functions",
        "difficulty": 2,
        "question_text": "What is Mean Squared Error (MSE) and how does it differ from Mean Absolute Error (MAE)?",
        "model_answer": "Mean Squared Error (MSE) calculates the average of the squared differences between predicted and actual values: MSE = (1/n) * sum((y_true - y_pred)^2). Mean Absolute Error (MAE) measures the average of the absolute differences. MSE heavily penalizes large errors and outliers because the differences are squared, which makes it sensitive to extreme values. MAE treats all errors proportionally and is more robust to outliers. Root Mean Squared Error (RMSE) takes the square root of MSE to express errors in the original units.",
        "keywords": [
            "mse", "mae", "rmse", "mean_squared_error", "outliers", "loss_function",
            "residuals", "penalization", "error_metric", "regression_metrics"
        ],
        "related_concepts": ["outliers", "loss_function", "gradient_descent", "linear_regression", "robust_regression"]
    },
    {
        "id": "ml_easy_004",
        "topic": "machine_learning",
        "subtopic": "classification",
        "difficulty": 2,
        "question_text": "What is Logistic Regression and why is it used for classification instead of Linear Regression?",
        "model_answer": "Despite its name, Logistic Regression is a supervised classification algorithm used for predicting categorical outcomes (such as binary 0 or 1). While Linear Regression outputs continuous values that can range from -infinity to +infinity, Logistic Regression passes linear predictions through the Sigmoid activation function (1 / (1 + e^-z)) to map outputs into a probability range strictly between 0 and 1. It uses Log-Loss (Binary Cross-Entropy) rather than Mean Squared Error to optimize parameters.",
        "keywords": [
            "logistic_regression", "classification", "sigmoid", "probability", "binary_classification",
            "cross_entropy", "log_loss", "decision_boundary", "supervised_learning"
        ],
        "related_concepts": ["sigmoid", "cross_entropy", "precision", "recall", "confusion_matrix"]
    },
    {
        "id": "ml_easy_005",
        "topic": "machine_learning",
        "subtopic": "data_preparation",
        "difficulty": 2,
        "question_text": "What is the purpose of train-test split and cross-validation in machine learning?",
        "model_answer": "Train-test split divides data into distinct subsets: training data to fit model parameters, and test data to evaluate generalization on unseen data. Evaluating only on training data causes data leakage and obscures overfitting. Cross-validation (like K-Fold cross-validation) splits the dataset into k folds, iteratively training on k-1 folds and validating on the remaining fold. This ensures every data point is tested, providing a more reliable estimate of model performance and variance.",
        "keywords": [
            "train_test_split", "cross_validation", "k_fold", "generalization", "overfitting",
            "data_leakage", "validation_set", "hyperparameter_tuning"
        ],
        "related_concepts": ["k_fold", "overfitting", "data_leakage", "stratified_k_fold", "bias_variance"]
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MACHINE LEARNING — MEDIUM (Level 3) [Turns 6 - 12 target]
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "ml_med_001",
        "topic": "machine_learning",
        "subtopic": "overfitting",
        "difficulty": 3,
        "question_text": "What is overfitting in machine learning, and what techniques do you use to detect and prevent it?",
        "model_answer": "Overfitting happens when a model learns noise, random variations, and specific training samples rather than the underlying pattern, resulting in high training accuracy but poor generalization to test data. It is detected when training loss continues decreasing while validation loss begins to increase. Prevention techniques include: (1) Regularization (L1 Lasso, L2 Ridge), (2) Cross-validation, (3) Pruning in decision trees or Dropout in neural networks, (4) Early stopping during training, (5) Feature selection to remove redundant predictors, and (6) Gathering more diverse training data.",
        "keywords": [
            "overfitting", "generalization", "validation_loss", "regularization", "l1_lasso",
            "l2_ridge", "cross_validation", "dropout", "early_stopping", "pruning", "feature_selection", "bias_variance"
        ],
        "related_concepts": ["l1_lasso", "l2_ridge", "regularization", "bias_variance", "cross_validation"]
    },
    {
        "id": "ml_med_002",
        "topic": "machine_learning",
        "subtopic": "regularization",
        "difficulty": 3,
        "question_text": "How do L1 (Lasso) and L2 (Ridge) regularization work to prevent overfitting?",
        "model_answer": "Both L1 and L2 regularization add a penalty term to the loss function to constrain model weights. L1 Regularization (Lasso) adds the sum of absolute values of coefficients (lambda * sum(|w|)). Because of the diamond geometry of L1 constraints, it shrinks non-essential coefficients to exactly zero, functioning as built-in feature selection. L2 Regularization (Ridge) adds the sum of squared coefficients (lambda * sum(w^2)), shrinking coefficients toward zero without making them exactly zero. Elastic Net combines both L1 and L2 penalties.",
        "keywords": [
            "l1_lasso", "l2_ridge", "regularization", "penalty", "coefficients", "shrinkage",
            "feature_selection", "elastic_net", "lambda", "loss_function", "overfitting"
        ],
        "related_concepts": ["elastic_net", "hyperparameter_tuning", "gradient_descent", "sparsity"]
    },
    {
        "id": "ml_med_003",
        "topic": "machine_learning",
        "subtopic": "optimization",
        "difficulty": 3,
        "question_text": "Explain how Gradient Descent works and compare Batch, Stochastic, and Mini-batch Gradient Descent.",
        "model_answer": "Gradient Descent is a first-order optimization algorithm used to minimize a loss function by iteratively taking steps proportional to the negative gradient: w = w - alpha * grad(L). Batch Gradient Descent computes the gradient over the entire dataset before updating weights (slow, high memory, but smooth convergence). Stochastic Gradient Descent (SGD) updates weights after every single training example (fast, frequent updates, noisy oscillations that help escape local minima). Mini-batch Gradient Descent computes gradients over small batches (e.g. 32 to 256 samples), combining vectorization efficiency with stable stochastic convergence.",
        "keywords": [
            "gradient_descent", "optimization", "learning_rate", "batch_gd", "stochastic_gd",
            "sgd", "mini_batch", "loss_function", "convergence", "local_minima", "backpropagation"
        ],
        "related_concepts": ["learning_rate", "adam", "rmsprop", "momentum", "backpropagation"]
    },
    {
        "id": "ml_med_004",
        "topic": "machine_learning",
        "subtopic": "metrics",
        "difficulty": 3,
        "question_text": "Explain Precision, Recall, and F1-score. When is High Recall preferred over High Precision?",
        "model_answer": "In classification, Precision is True Positives divided by all Predicted Positives (TP / (TP + FP)), measuring how many of the positively predicted instances were correct. Recall (Sensitivity) is True Positives divided by all Actual Positives (TP / (TP + FN)), measuring the ability to find all positive instances. F1-score is the harmonic mean of Precision and Recall: 2 * (Precision * Recall) / (Precision + Recall). High Recall is preferred when false negatives carry severe consequences, such as medical diagnostics (missing a tumor is critical) or fraud detection. High Precision is preferred when false positives cause high disruption, like spam filtering.",
        "keywords": [
            "precision", "recall", "f1_score", "true_positive", "false_positive", "false_negative",
            "confusion_matrix", "auc_roc", "imbalanced_data", "classification_metrics"
        ],
        "related_concepts": ["confusion_matrix", "auc_roc", "class_imbalance", "threshold_tuning"]
    },
    {
        "id": "ml_med_005",
        "topic": "machine_learning",
        "subtopic": "decision_trees",
        "difficulty": 3,
        "question_text": "How do Decision Trees choose split points, and what are Gini Impurity and Entropy?",
        "model_answer": "Decision Trees partition data by selecting features and threshold values that maximize information gain or homogeneity at each node. For classification, two main split criteria are used: Gini Impurity and Entropy (Information Gain). Gini Impurity measures the probability of misclassifying a randomly chosen element: Gini = 1 - sum(p_i^2). Entropy measures disorder: Entropy = -sum(p_i * log2(p_i)). Information Gain is the reduction in entropy achieved by a split. While both produce similar trees, Gini is computationally faster because it avoids logarithmic operations.",
        "keywords": [
            "decision_tree", "gini_impurity", "entropy", "information_gain", "split_criterion",
            "random_forest", "pruning", "homogeneous_nodes", "overfitting"
        ],
        "related_concepts": ["random_forest", "information_gain", "ensemble", "boosting", "pruning"]
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MACHINE LEARNING — HARD (Levels 4 - 5) [Turns 13+ target]
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "ml_hard_001",
        "topic": "machine_learning",
        "subtopic": "bias_variance",
        "difficulty": 4,
        "question_text": "Decompose total prediction error into the Bias-Variance tradeoff and explain how ensemble techniques alter this decomposition.",
        "model_answer": "Total Expected Prediction Error can be mathematically decomposed into: Error = Bias^2 + Variance + Irreducible Error (sigma^2). Bias represents error from simplifying assumptions in the learning algorithm, leading to underfitting. Variance represents sensitivity to specific training sample variations, leading to overfitting. Bagging (Bootstrap Aggregation, like Random Forests) trains independent complex models in parallel on bootstrapped samples and averages predictions; this reduces Variance without increasing Bias. Boosting (like XGBoost, LightGBM) trains sequential weak learners where each corrects the residual errors of its predecessor; this primarily reduces Bias.",
        "keywords": [
            "bias_variance", "bias_variance_tradeoff", "irreducible_error", "bagging", "boosting",
            "random_forest", "xgboost", "variance_reduction", "bias_reduction", "bootstrap_aggregation", "ensemble_learning"
        ],
        "related_concepts": ["xgboost", "random_forest", "ensemble_learning", "cross_validation", "gradient_boosting"]
    },
    {
        "id": "ml_hard_002",
        "topic": "machine_learning",
        "subtopic": "optimizers",
        "difficulty": 4,
        "question_text": "How does the Adam optimizer combine Momentum and RMSprop, and why is bias correction necessary?",
        "model_answer": "Adam (Adaptive Moment Estimation) computes adaptive learning rates for each parameter by maintaining exponentially decaying averages of both past gradients (first moment, estimating the mean via Momentum) and past squared gradients (second raw moment, estimating uncentered variance via RMSprop): m_t = beta_1 * m_{t-1} + (1-beta_1) * g_t, and v_t = beta_2 * v_{t-1} + (1-beta_2) * g_t^2. Because m and v are initialized to zero vectors, they are biased toward zero during early steps. Adam applies bias correction: m_hat = m_t / (1 - beta_1^t) and v_hat = v_t / (1 - beta_2^t). Parameter update is: theta = theta - (alpha / (sqrt(v_hat) + eps)) * m_hat.",
        "keywords": [
            "adam", "momentum", "rmsprop", "optimizers", "exponential_decay", "learning_rate",
            "bias_correction", "gradient_descent", "first_moment", "second_moment", "backpropagation"
        ],
        "related_concepts": ["backpropagation", "learning_rate", "gradient_descent", "vanishing_gradient"]
    },
    {
        "id": "ml_hard_003",
        "topic": "machine_learning",
        "subtopic": "neural_networks",
        "difficulty": 5,
        "question_text": "What causes the Vanishing and Exploding Gradient problems in deep networks, and what mathematical architectural mechanisms solve them?",
        "model_answer": "During backpropagation, gradients are propagated backward through repeated matrix multiplications using the chain rule: dL/dw = prod(W_i * sigma'(z_i)). If activation derivatives are less than 1 (such as Sigmoid with max derivative 0.25) or weight eigenvalues are < 1, gradients decay exponentially as layers increase, preventing early layers from updating. Conversely, weights > 1 cause exploding gradients. Solutions: (1) Non-saturating activations (ReLU, Leaky ReLU, GELU), (2) Xavier/Glorot or He weight initialization preserving activation variance across layers, (3) Residual skip connections (ResNet) allowing gradients to flow directly: a_{l+1} = F(a_l) + a_l, and (4) Layer Normalization and Batch Normalization.",
        "keywords": [
            "vanishing_gradient", "exploding_gradient", "backpropagation", "chain_rule", "residual_connections",
            "resnet", "relu", "he_initialization", "batch_normalization", "layer_normalization", "eigenvalues"
        ],
        "related_concepts": ["resnet", "backpropagation", "adam", "layer_normalization", "transformers"]
    },

    # ══════════════════════════════════════════════════════════════════════════
    # DATA STRUCTURES & ALGORITHMS — EASY (Levels 1 - 2) [Turns 1 - 5 target]
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "dsa_easy_001",
        "topic": "data_structures",
        "subtopic": "arrays_vs_linkedlists",
        "difficulty": 2,
        "question_text": "Compare Arrays and Singly Linked Lists in terms of memory layout, indexing, and insertion complexity.",
        "model_answer": "Arrays allocate contiguous blocks of memory, allowing constant O(1) time random access using index arithmetic: address = base + (index * element_size). However, insertion and deletion require shifting elements, yielding O(n) time unless done at the end of a dynamic array with spare capacity. Linked Lists allocate nodes dynamically across arbitrary memory locations linked by pointers. Indexing requires sequential traversal with O(n) time. Insertion and deletion at a given node pointer take O(1) time by pointer updates. Arrays offer superior CPU cache locality due to spatial contiguity.",
        "keywords": [
            "array", "linked_list", "contiguous_memory", "random_access", "pointers", "cache_locality",
            "time_complexity", "o_1_lookup", "insertion", "dynamic_array"
        ],
        "related_concepts": ["cache_locality", "doubly_linked_list", "dynamic_array", "hash_table"]
    },
    {
        "id": "dsa_easy_002",
        "topic": "data_structures",
        "subtopic": "hash_table",
        "difficulty": 2,
        "question_text": "What is a Hash Table, how does hash function indexing work, and what is a hash collision?",
        "model_answer": "A Hash Table is an associative data structure providing average O(1) time complexity for insert, lookup, and delete operations. It uses a hash function to transform a key into an integer index within an underlying bucket array. A hash collision occurs when two distinct keys produce the same hash index. Common resolution strategies include Separate Chaining (each bucket points to a linked list or balanced tree) and Open Addressing (Linear Probing, Quadratic Probing, or Double Hashing).",
        "keywords": [
            "hash_table", "hash_function", "collision", "chaining", "open_addressing",
            "linear_probing", "o_1_lookup", "bucket_array", "dictionary", "hashmap"
        ],
        "related_concepts": ["open_addressing", "load_factor", "rehashing", "balanced_tree"]
    },
    {
        "id": "dsa_easy_003",
        "topic": "data_structures",
        "subtopic": "stacks_queues",
        "difficulty": 2,
        "question_text": "What are Stacks and Queues? What are their fundamental operations and real-world applications?",
        "model_answer": "A Stack is a Linear LIFO (Last-In, First-Out) data structure supporting push, pop, and peek operations in O(1) time. Applications include the function call stack, undo/redo mechanisms, and syntax parsing. A Queue is a FIFO (First-In, First-Out) data structure supporting enqueue and dequeue operations in O(1) time. Applications include CPU task scheduling, breadth-first search (BFS), and message queues (e.g. RabbitMQ, Kafka).",
        "keywords": [
            "stack", "queue", "lifo", "fifo", "push", "pop", "enqueue", "dequeue",
            "call_stack", "bfs", "breadth_first_search", "time_complexity"
        ],
        "related_concepts": ["bfs", "call_stack", "priority_queue", "deque"]
    },

    # ══════════════════════════════════════════════════════════════════════════
    # DATA STRUCTURES & ALGORITHMS — MEDIUM (Level 3) [Turns 6 - 12 target]
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "dsa_med_001",
        "topic": "data_structures",
        "subtopic": "trees",
        "difficulty": 3,
        "question_text": "Explain Binary Search Trees (BST) and how unbalanced trees degrade time complexity.",
        "model_answer": "A Binary Search Tree (BST) is a hierarchical node structure where for every node, keys in the left subtree are smaller and keys in the right subtree are greater. In a balanced BST, lookup, insertion, and deletion take O(log n) time proportional to tree height. If elements are inserted in sorted or reverse order, the tree degenerates into a linked list with height O(n), causing operations to degrade to O(n) linear search. Self-balancing trees such as AVL Trees and Red-Black Trees maintain logarithmic height through tree rotations.",
        "keywords": [
            "binary_search_tree", "bst", "balanced_tree", "avl_tree", "red_black_tree", "tree_rotations",
            "time_complexity", "log_n", "tree_height", "inorder_traversal"
        ],
        "related_concepts": ["avl_tree", "red_black_tree", "tree_rotations", "dfs", "recursion"]
    },
    {
        "id": "dsa_med_002",
        "topic": "data_structures",
        "subtopic": "graphs",
        "difficulty": 3,
        "question_text": "Compare Breadth-First Search (BFS) and Depth-First Search (DFS) for graph traversal.",
        "model_answer": "BFS visits neighbor vertices layer by layer using a FIFO Queue, exploring all vertices at depth d before moving to depth d+1. It guarantees the shortest path on unweighted graphs with O(V + E) time. DFS explores as deep as possible along each branch using a LIFO Stack or recursion before backtracking. Applications of DFS include topological sorting, cycle detection, and connected components. Both require a visited set to avoid infinite loops in cyclic graphs.",
        "keywords": [
            "bfs", "dfs", "graph_traversal", "breadth_first_search", "depth_first_search",
            "queue", "stack", "shortest_path", "topological_sort", "cycle_detection", "adjacency_list"
        ],
        "related_concepts": ["topological_sort", "dijkstra", "cycle_detection", "recursion"]
    },
    {
        "id": "dsa_med_003",
        "topic": "algorithms",
        "subtopic": "sorting",
        "difficulty": 3,
        "question_text": "How does QuickSort work and what pivot selection strategies avoid its O(n^2) worst-case?",
        "model_answer": "QuickSort is a divide-and-conquer algorithm. It selects a pivot element, partitions the array into elements smaller than the pivot and elements greater than the pivot, then recursively sorts the sub-arrays. Average time complexity is O(n log n) with in-place O(log n) space. The worst-case is O(n^2), which occurs when the chosen pivot is repeatedly the extreme element (e.g. already sorted array with first element pivot). Mitigations include choosing a random pivot, or using the Median-of-Three strategy (median of first, middle, last elements).",
        "keywords": [
            "quicksort", "divide_and_conquer", "pivot_selection", "partitioning", "median_of_three",
            "time_complexity", "worst_case", "in_place_sort", "recursion", "n_log_n"
        ],
        "related_concepts": ["mergesort", "median_of_three", "time_complexity", "recursion"]
    },

    # ══════════════════════════════════════════════════════════════════════════
    # DATA STRUCTURES & ALGORITHMS — HARD (Levels 4 - 5) [Turns 13+ target]
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "dsa_hard_001",
        "topic": "algorithms",
        "subtopic": "dynamic_programming",
        "difficulty": 4,
        "question_text": "What are the two core properties required for Dynamic Programming, and how does Memoization differ from Tabulation?",
        "model_answer": "Dynamic Programming applies to optimization problems exhibiting two properties: (1) Optimal Substructure (an optimal solution contains optimal solutions to subproblems), and (2) Overlapping Subproblems (the same subproblems are solved repeatedly). Memoization is Top-Down: it uses recursion with an auxiliary lookup table/hash map to cache subproblem solutions, only computing needed states. Tabulation is Bottom-Up: it builds solutions iteratively starting from base cases, eliminating recursion stack overhead and frequently allowing space optimization by maintaining only recent state transitions.",
        "keywords": [
            "dynamic_programming", "optimal_substructure", "overlapping_subproblems", "memoization",
            "tabulation", "top_down", "bottom_up", "recursion", "state_transition", "space_optimization"
        ],
        "related_concepts": ["space_optimization", "recursion", "knapsack", "bellman_ford"]
    },
    {
        "id": "dsa_hard_002",
        "topic": "data_structures",
        "subtopic": "advanced_trees",
        "difficulty": 5,
        "question_text": "Explain the invariant properties of Red-Black Trees and why they are preferred over AVL trees in production standard libraries.",
        "model_answer": "A Red-Black Tree is a self-balancing BST maintaining five invariants: (1) Every node is red or black, (2) The root is black, (3) All leaves (NIL) are black, (4) If a node is red, both children are black (no consecutive red nodes), (5) Every path from a node to descendant NIL leaves contains the same number of black nodes (black-height). AVL trees enforce stricter balance (height difference <= 1), yielding faster O(log n) lookups. Red-Black trees permit a path length up to twice another, requiring fewer tree rotations upon insertions and deletions (at most 2 rotations on insert, 3 on delete). Consequently, Red-Black Trees are standard in Java TreeMap and C++ std::map.",
        "keywords": [
            "red_black_tree", "avl_tree", "tree_rotations", "black_height", "balancing_invariants",
            "self_balancing_bst", "worst_case", "standard_template_library", "std_map"
        ],
        "related_concepts": ["avl_tree", "tree_rotations", "binary_search_tree", "b_tree"]
    },

    # ══════════════════════════════════════════════════════════════════════════
    # PYTHON & BACKEND — EASY (Levels 1 - 2) [Turns 1 - 5 target]
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "py_easy_001",
        "topic": "python",
        "subtopic": "data_types",
        "difficulty": 1,
        "question_text": "What is the difference between mutable and immutable types in Python, and how does it affect function arguments?",
        "model_answer": "In Python, immutable objects (int, float, str, tuple, frozenset) cannot be modified after creation; any operation that modifies them returns a new object. Mutable objects (list, dict, set) can be altered in-place. In Python, arguments are passed by object reference (call-by-sharing). If you pass a mutable object to a function and modify it inside, the caller's object is altered. A common pitfall is using a mutable default argument like def func(items=[]), where the default list persists across calls.",
        "keywords": [
            "mutable", "immutable", "call_by_sharing", "pass_by_reference", "tuples", "lists",
            "default_arguments", "memory_id", "python_types"
        ],
        "related_concepts": ["call_by_sharing", "default_arguments", "shallow_copy", "deep_copy"]
    },
    {
        "id": "py_easy_002",
        "topic": "python",
        "subtopic": "lists_dicts",
        "difficulty": 2,
        "question_text": "How do List Comprehensions work in Python, and how do they compare to using map() and filter()?",
        "model_answer": "List comprehensions provide a concise syntax for creating new lists from iterables: [expression for item in iterable if condition]. They are more readable than map() and filter() and avoid lambda function overhead in standard loops. Under the hood, Python bytecode executes list comprehensions in optimized C-level iteration loops. For massive datasets where full memory allocation is impractical, Generator Expressions (using parentheses) are preferred for lazy evaluation.",
        "keywords": [
            "list_comprehension", "generators", "generator_expression", "map_filter", "lambda",
            "lazy_evaluation", "iterables", "bytecode_optimization"
        ],
        "related_concepts": ["generators", "lazy_evaluation", "lambda", "iterators"]
    },

    # ══════════════════════════════════════════════════════════════════════════
    # PYTHON & BACKEND — MEDIUM (Level 3) [Turns 6 - 12 target]
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "py_med_001",
        "topic": "python",
        "subtopic": "decorators",
        "difficulty": 3,
        "question_text": "What are Python decorators, and how do closures enable decorator functionality?",
        "model_answer": "A decorator is a callable that takes a function as input, extends its behavior without modifying its code, and returns a callable. Decorators rely on Closures — inner functions that capture and retain references to variables from their enclosing lexical scope even after the outer function has returned. Syntax @decorator is syntactic sugar for func = decorator(func). Using functools.wraps on the wrapper function is essential to preserve the original function's name, docstrings, and parameter signature.",
        "keywords": [
            "decorator", "closure", "higher_order_function", "functools_wraps", "wrapper_function",
            "lexical_scoping", "syntactic_sugar", "first_class_functions"
        ],
        "related_concepts": ["closure", "functools_wraps", "generators", "context_managers"]
    },
    {
        "id": "py_med_002",
        "topic": "python",
        "subtopic": "concurrency",
        "difficulty": 3,
        "question_text": "What is Python's Global Interpreter Lock (GIL) and how does it affect multithreading vs multiprocessing?",
        "model_answer": "The Global Interpreter Lock (GIL) is a mutex in CPython that prevents multiple native threads from executing Python bytecode simultaneously in a single process. It protects CPython's reference-counting memory management from race conditions. Because of the GIL, multithreading does not achieve CPU-bound parallelism across multi-core processors, though it works well for I/O-bound operations (networking, disk I/O) where threads release the GIL while waiting. For CPU-bound tasks, the multiprocessing module is required to spawn separate OS processes with independent memory and GIL instances.",
        "keywords": [
            "gil", "global_interpreter_lock", "cpython", "multithreading", "multiprocessing",
            "cpu_bound", "io_bound", "race_conditions", "reference_counting", "concurrency"
        ],
        "related_concepts": ["asyncio", "multiprocessing", "reference_counting", "event_loop"]
    },

    # ══════════════════════════════════════════════════════════════════════════
    # PYTHON & BACKEND — HARD (Levels 4 - 5) [Turns 13+ target]
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "py_hard_001",
        "topic": "python",
        "subtopic": "asyncio",
        "difficulty": 4,
        "question_text": "How does the asyncio Event Loop work under the hood, and how do Coroutines yield control?",
        "model_answer": "Asyncio is single-threaded cooperative multitasking built around an Event Loop. Coroutines are defined with async def and use await to suspend execution and yield control back to the event loop. Under the hood, Python coroutines are enhanced generators that yield Future or Task objects. The event loop uses OS-level I/O multiplexers (such as epoll on Linux, kqueue on macOS, or IOCP on Windows) to monitor file descriptors for readiness without thread context-switching overhead. If CPU-heavy code blocks the event loop without yielding, it halts all concurrent tasks.",
        "keywords": [
            "asyncio", "event_loop", "coroutines", "await", "cooperative_multitasking",
            "epoll", "future_tasks", "io_multiplexing", "non_blocking"
        ],
        "related_concepts": ["event_loop", "epoll", "generators", "concurrency"]
    },

    # ══════════════════════════════════════════════════════════════════════════
    # EXPANSION: MACHINE LEARNING & DEEP LEARNING (Diverse Tracks)
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "ml_easy_006",
        "topic": "machine_learning",
        "subtopic": "clustering_vs_classification",
        "difficulty": 1,
        "question_text": "What is the key difference between Supervised and Unsupervised learning? Give an example of each.",
        "model_answer": "Supervised learning trains models on labeled input-output pairs (ground truth targets y provided), learning a mapping function to predict targets on unseen data. Examples include Linear Regression for continuous pricing or Logistic Regression for spam classification. Unsupervised learning discovers latent patterns, groupings, or distributions in unlabeled data without target guidance. Examples include K-Means clustering for customer segmentation and Principal Component Analysis (PCA) for dimensionality reduction.",
        "keywords": [
            "supervised_learning", "unsupervised_learning", "clustering", "classification", "labels",
            "ground_truth", "k_means", "pca", "continuous_variable", "dimensionality_reduction"
        ],
        "related_concepts": ["k_means", "pca", "classification", "regression", "reinforcement_learning"]
    },
    {
        "id": "ml_easy_007",
        "topic": "machine_learning",
        "subtopic": "knn",
        "difficulty": 2,
        "question_text": "How does the K-Nearest Neighbors (KNN) algorithm work, and why is feature scaling necessary for it?",
        "model_answer": "K-Nearest Neighbors (KNN) is a non-parametric, lazy learning algorithm that classifies new data points based on the majority class of its k nearest neighbors in the feature space (or averages values for regression). It relies on distance metrics like Euclidean or Manhattan distance. Feature scaling (such as standardization or min-max normalization) is essential because features with larger numerical magnitudes will disproportionately dominate the distance calculation.",
        "keywords": [
            "knn", "k_nearest_neighbors", "euclidean_distance", "manhattan_distance", "feature_scaling",
            "normalization", "standardization", "lazy_learning", "distance_metrics"
        ],
        "related_concepts": ["feature_scaling", "normalization", "curse_of_dimensionality", "classification"]
    },
    {
        "id": "ml_med_006",
        "topic": "machine_learning",
        "subtopic": "svm",
        "difficulty": 3,
        "question_text": "What is a Support Vector Machine (SVM) and how does the Kernel Trick handle non-linearly separable data?",
        "model_answer": "Support Vector Machines (SVM) find an optimal hyperplane that maximizes the margin of separation between classes in feature space. The margin is defined by the closest data points, called Support Vectors. When data is non-linearly separable in the input space, the Kernel Trick maps inputs into higher-dimensional Hilbert spaces where a linear hyperplane can separate them, without explicitly computing the high-dimensional coordinates: K(x, z) = phi(x) . phi(z). Common kernels include Radial Basis Function (RBF/Gaussian), Polynomial, and Sigmoid.",
        "keywords": [
            "svm", "support_vector_machine", "kernel_trick", "rbf_kernel", "hyperplane",
            "margin_maximization", "support_vectors", "polynomial_kernel", "classification"
        ],
        "related_concepts": ["rbf_kernel", "margin_maximization", "logistic_regression", "convex_optimization"]
    },
    {
        "id": "ml_med_007",
        "topic": "machine_learning",
        "subtopic": "pca",
        "difficulty": 3,
        "question_text": "How does Principal Component Analysis (PCA) work for dimensionality reduction, and what do Eigenvectors represent?",
        "model_answer": "PCA is an unsupervised linear dimensionality reduction technique that transforms correlated features into a smaller set of linearly uncorrelated components called Principal Components. It computes the covariance matrix of standardized features and extracts its Eigenvalues and Eigenvectors. The Eigenvectors represent the directions of maximum variance (principal axes), while the corresponding Eigenvalues indicate the amount of variance explained along each axis. Projecting data onto top eigenvectors reduces dimensionality while preserving maximum information.",
        "keywords": [
            "pca", "principal_component_analysis", "dimensionality_reduction", "eigenvalues", "eigenvectors",
            "covariance_matrix", "variance", "orthogonal_projections", "standardization"
        ],
        "related_concepts": ["eigenvalues", "eigenvectors", "unsupervised_learning", "svd"]
    },
    {
        "id": "ml_hard_004",
        "topic": "machine_learning",
        "subtopic": "transformers",
        "difficulty": 5,
        "question_text": "Explain the Multi-Head Self-Attention mechanism in Transformer models. What is the mathematical role of Q, K, and V matrices?",
        "model_answer": "Self-attention enables tokens in a sequence to dynamically attend to and weigh all other tokens regardless of distance. Given input embeddings X, linear projections produce Query (Q), Key (K), and Value (V) matrices. Scaled Dot-Product Attention is computed as: Attention(Q, K, V) = softmax( (Q * K^T) / sqrt(d_k) ) * V. The scaling factor 1/sqrt(d_k) prevents dot-product values from growing excessively large, which would push softmax into regions with vanishing gradients. Multi-Head Attention runs h parallel attention heads with different learned projection matrices, allowing the model to jointly attend to information from different representation subspaces.",
        "keywords": [
            "transformers", "self_attention", "multi_head_attention", "query_key_value", "softmax",
            "scaled_dot_product", "attention_mechanism", "nlp", "representation_learning"
        ],
        "related_concepts": ["self_attention", "deep_learning", "nlp", "vanishing_gradient"]
    },

    # ══════════════════════════════════════════════════════════════════════════
    # EXPANSION: DATA STRUCTURES & ALGORITHMS (Diverse Tracks)
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "dsa_easy_004",
        "topic": "algorithms",
        "subtopic": "binary_search",
        "difficulty": 2,
        "question_text": "What is Binary Search, what prerequisite must the data satisfy, and what is its time complexity?",
        "model_answer": "Binary Search is an efficient search algorithm that repeatedly halves the search space to find a target value. The data MUST be sorted in advance. By comparing the target with the middle element, it eliminates half the remaining elements in each step: if target < mid, search left; if target > mid, search right. Time complexity is O(log n) because the problem size halves at each step. Space complexity is O(1) for the iterative implementation and O(log n) for recursive calls.",
        "keywords": [
            "binary_search", "divide_and_conquer", "sorted_array", "log_n", "time_complexity",
            "search_algorithm", "o_log_n", "pointers"
        ],
        "related_concepts": ["divide_and_conquer", "two_pointers", "time_complexity", "quicksort"]
    },
    {
        "id": "dsa_med_004",
        "topic": "data_structures",
        "subtopic": "heaps",
        "difficulty": 3,
        "question_text": "What is a Binary Heap and how does a Priority Queue utilize Min-Heap or Max-Heap properties?",
        "model_answer": "A Binary Heap is a complete binary tree that satisfies the heap property: in a Min-Heap, every parent node is less than or equal to its children (minimum element at root); in a Max-Heap, every parent is greater than or equal to its children. Because it is a complete tree, it can be represented compactly as an array where children of index i are at 2i+1 and 2i+2. Priority Queues use heaps to provide O(1) retrieval of the highest-priority element, with O(log n) insert (heapify-up) and extract-min/max (heapify-down). Building a heap from an arbitrary array takes O(n) time.",
        "keywords": [
            "binary_heap", "heap", "priority_queue", "min_heap", "max_heap", "heapify",
            "complete_binary_tree", "time_complexity", "log_n", "array_representation"
        ],
        "related_concepts": ["priority_queue", "dijkstra", "complete_binary_tree", "heapsort"]
    },
    {
        "id": "dsa_med_005",
        "topic": "data_structures",
        "subtopic": "trie",
        "difficulty": 3,
        "question_text": "What is a Trie (Prefix Tree) and why is it preferred over a Hash Table for autocomplete and dictionary prefix search?",
        "model_answer": "A Trie is a tree-like data structure where each node represents a common prefix of string keys, with edges corresponding to characters. Unlike a Hash Table where searching for all words starting with a prefix requires scanning the entire key space in O(N * L) time, a Trie retrieves all prefix matches in O(L) time where L is prefix length, independent of dictionary size. Tries avoid hash collision overhead and naturally maintain lexicographical order, making them ideal for search engine autocomplete, spell checkers, and IP routing tables.",
        "keywords": [
            "trie", "prefix_tree", "autocomplete", "string_algorithms", "hash_table",
            "time_complexity", "lexicographical_order", "prefix_search", "dictionary"
        ],
        "related_concepts": ["hash_table", "prefix_search", "string_algorithms", "binary_search_tree"]
    },
    {
        "id": "dsa_hard_003",
        "topic": "data_structures",
        "subtopic": "lru_cache",
        "difficulty": 4,
        "question_text": "How do you design a Least Recently Used (LRU) Cache with O(1) get and put operations?",
        "model_answer": "An LRU Cache achieves O(1) time complexity for both get(key) and put(key, value) by combining a Hash Map with a Doubly Linked List. The Hash Map stores keys mapping directly to nodes in the doubly linked list, enabling O(1) lookup. The Doubly Linked List maintains access order: the most recently used item is moved to the head, while the least recently used item sits at the tail. When the cache hits capacity on a put operation, the tail node is removed in O(1) time and deleted from the hash map.",
        "keywords": [
            "lru_cache", "doubly_linked_list", "hash_map", "hash_table", "o_1_lookup",
            "cache_eviction", "system_design", "pointers", "capacity"
        ],
        "related_concepts": ["doubly_linked_list", "hash_table", "caching", "time_complexity"]
    },

    # ══════════════════════════════════════════════════════════════════════════
    # EXPANSION: DATABASES & SYSTEM CONCEPTS
    # ══════════════════════════════════════════════════════════════════════════
    {
        "id": "db_easy_001",
        "topic": "database",
        "subtopic": "joins",
        "difficulty": 2,
        "question_text": "Explain the difference between INNER JOIN, LEFT JOIN, and FULL OUTER JOIN in SQL with examples.",
        "model_answer": "An INNER JOIN returns only rows where there is a matching key in both tables. A LEFT JOIN (Left Outer Join) returns all rows from the left table, along with matching rows from the right table; if no match exists, NULL values are populated for right-table columns. A FULL OUTER JOIN returns all rows from both tables, populating NULL whenever a record in either table lacks a counterpart. For example, joining an Employees table with a Departments table via department_id using LEFT JOIN ensures employees without an assigned department are still retrieved.",
        "keywords": [
            "sql", "inner_join", "left_join", "full_outer_join", "sql_joins", "null_values",
            "relational_database", "primary_key", "foreign_key", "query_optimization"
        ],
        "related_concepts": ["relational_database", "foreign_key", "indexing", "sql"]
    },
    {
        "id": "db_med_001",
        "topic": "database",
        "subtopic": "acid",
        "difficulty": 3,
        "question_text": "What are the ACID properties in relational database transactions, and why are they critical?",
        "model_answer": "ACID guarantees transactional integrity in database management systems: (1) Atomicity: all operations in a transaction succeed or all fail together (all-or-nothing rollback). (2) Consistency: transactions transition the database from one valid state to another, enforcing all schema constraints. (3) Isolation: concurrent transactions execute without interfering with one another, preventing dirty reads and phantom reads using isolation levels (Read Committed, Serializable). (4) Durability: committed changes survive power failures or crashes via write-ahead logging (WAL).",
        "keywords": [
            "acid", "atomicity", "consistency", "isolation", "durability", "transactions",
            "write_ahead_log", "dirty_reads", "rollback", "relational_database", "concurrency"
        ],
        "related_concepts": ["transactions", "write_ahead_log", "concurrency", "relational_database"]
    },
    {
        "id": "db_med_002",
        "topic": "database",
        "subtopic": "indexing",
        "difficulty": 3,
        "question_text": "How do B-Tree indexes accelerate SQL queries, and what is the write performance penalty of indexing?",
        "model_answer": "A B-Tree index is a balanced multi-way search tree where data pointers or row IDs are stored in sorted order across disk blocks. Searching an index takes O(log n) disk I/O reads instead of an O(n) full table scan. However, indexes impose a write penalty: every INSERT, UPDATE, and DELETE operation must update both the base table and all associated B-Tree index structures, potentially triggering page splits and rebalancing overhead. Over-indexing tables with high write frequency severely degrades ingestion throughput.",
        "keywords": [
            "b_tree", "indexing", "sql", "full_table_scan", "query_optimization", "write_penalty",
            "disk_io", "database_performance", "page_split", "relational_database"
        ],
        "related_concepts": ["b_tree", "query_optimization", "hash_table", "relational_database"]
    }
]


def seed_database():
    """Populates the SQLite database and builds the inverted index."""
    init_database()
    conn = get_db_connection()
    c = conn.cursor()

    for q in SEED_QUESTIONS:
        stage = get_stage_for_difficulty(q["difficulty"])
        c.execute("""
            INSERT OR REPLACE INTO questions
            (id, topic, subtopic, difficulty, stage, question_text, model_answer, keywords, related_concepts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            q["id"], q["topic"], q["subtopic"], q["difficulty"], stage,
            q["question_text"], q["model_answer"],
            json.dumps(q["keywords"]),
            json.dumps(q["related_concepts"])
        ))

        # Index all primary keywords with weight 1.0
        for kw in q["keywords"]:
            c.execute("""
                INSERT OR REPLACE INTO keyword_index (keyword, question_id, weight)
                VALUES (?, ?, 1.0)
            """, (kw.lower(), q["id"]))

        # Index related concepts with weight 0.6
        for kw in q["related_concepts"]:
            c.execute("""
                INSERT OR IGNORE INTO keyword_index (keyword, question_id, weight)
                VALUES (?, ?, 0.6)
            """, (kw.lower(), q["id"]))

    conn.commit()
    conn.close()
    print(f"[QuestionBank] Seeded {len(SEED_QUESTIONS)} verified questions into {DB_PATH}")


if __name__ == "__main__":
    seed_database()
