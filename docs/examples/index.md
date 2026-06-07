# Examples

This section provides practical, real-world examples of using **online-fdr** for various applications. Each example includes complete code, explanations, and interpretations to help you apply online FDR control in your domain.

## Example Categories

### [Basic Usage](basic_usage.md)
**Getting started with online FDR control**

- Simple sequential testing workflow
- Comparing methods on simulated data  
- Parameter tuning and sensitivity analysis
- Performance evaluation and metrics

### [Advanced Scenarios](advanced.md)
**Real-world applications and complex use cases**

- A/B testing in tech companies
- Genomic variant discovery
- Clinical trial interim analyses  
- Financial anomaly detection
- Web analytics and conversion optimization

### [Method Comparisons](comparison.md)
**Systematic comparison of different approaches**

- Online vs batch method performance
- Power and FDR trade-offs across methods
- Dependency structure effects
- Parameter sensitivity studies

### [E-Value Examples](e_values.md)
**Batch, online, and construction workflows for e-values**

- e-BH for fixed batches of valid e-values
- e-LOND for streaming e-values
- P-to-e calibration, e-value merging, and e-process stopping
- Gaussian likelihood-ratio e-value simulations

## Quick Start Examples

### 1. **Basic Online Testing**

```python
from online_fdr.p_values.investing.addis.addis import Addis

# Initialize method
addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)

# Your p-values from real experiments
p_values = [0.032, 0.001, 0.145, 0.003, 0.234, 0.089, 0.012]

# Test sequentially and collect results
significant_results = []
for i, p_val in enumerate(p_values):
    if addis.test_one(p_val):
        significant_results.append((i, p_val))
        print(f" Significant: Test {i+1} with p-value {p_val:.4f}")

print(f"\nFound {len(significant_results)} significant results out of {len(p_values)} tests")
```

### 2. **A/B Test Monitoring**

```python
from online_fdr.p_values.investing.addis.addis import Addis
import numpy as np

def ab_test_with_fdr_control(variants, control_data, alpha=0.05):
    """A/B test multiple variants with online FDR control."""
    
    method = Addis(alpha=alpha, wealth=alpha/2, lambda_=0.25, tau=0.5)
    
    results = {}
    
    for variant_name, variant_data in variants.items():
        # Perform statistical test (e.g., t-test)
        from scipy.stats import ttest_ind
        statistic, p_value = ttest_ind(variant_data, control_data)
        
        # Apply online FDR control
        is_significant = method.test_one(p_value)
        
        results[variant_name] = {
            'p_value': p_value,
            'statistic': statistic,
            'significant': is_significant,
            'effect_size': np.mean(variant_data) - np.mean(control_data)
        }
        
        if is_significant:
            print(f" {variant_name}: Significant effect detected!")
            print(f"   P-value: {p_value:.4f}, Effect: {results[variant_name]['effect_size']:.3f}")
    
    return results

# Example usage
np.random.seed(42)
control = np.random.normal(100, 15, 1000)  # Control group
variants = {
    'Variant_A': np.random.normal(105, 15, 1000),  # Small positive effect
    'Variant_B': np.random.normal(98, 15, 1000),   # Small negative effect  
    'Variant_C': np.random.normal(110, 15, 1000),  # Large positive effect
    'Variant_D': np.random.normal(101, 15, 1000),  # Minimal effect
}

results = ab_test_with_fdr_control(variants, control, alpha=0.1)
```

### 3. **Gene Expression Analysis**

```python
from online_fdr.p_values.investing.addis.addis import Addis
from scipy.stats import ttest_ind
import numpy as np

def differential_expression_analysis(gene_expression_data, group_labels, 
                                   alpha=0.05):
    """Identify differentially expressed genes with FDR control."""
    
    method = Addis(alpha=alpha, wealth=alpha/2, lambda_=0.25, tau=0.5)
    
    group1_mask = group_labels == 'treatment'
    group2_mask = group_labels == 'control'
    
    significant_genes = []
    
    for gene_id in range(gene_expression_data.shape[0]):
        group1_expr = gene_expression_data[gene_id, group1_mask]
        group2_expr = gene_expression_data[gene_id, group2_mask]
        
        # Perform t-test
        statistic, p_value = ttest_ind(group1_expr, group2_expr)
        
        # Apply online FDR control
        if method.test_one(p_value):
            fold_change = np.mean(group1_expr) / np.mean(group2_expr)
            significant_genes.append({
                'gene_id': gene_id,
                'p_value': p_value,
                'fold_change': fold_change,
                'log_fc': np.log2(fold_change)
            })
    
    return significant_genes

# Simulate gene expression data
np.random.seed(123)
n_genes, n_samples = 1000, 50
expression_data = np.random.lognormal(2, 1, (n_genes, n_samples))

# Add differential expression to some genes
diff_genes = np.random.choice(n_genes, 50, replace=False)
expression_data[diff_genes, :25] *= 1.5  # Treatment group upregulated

group_labels = np.array(['treatment'] * 25 + ['control'] * 25)

significant_genes = differential_expression_analysis(
    expression_data, group_labels, alpha=0.1
)

print(f"Found {len(significant_genes)} differentially expressed genes")
```

### 4. **Clinical Trial Interim Analysis**

```python
from online_fdr.p_values.investing.lord.three import LordThree
from scipy.stats import chi2_contingency
import numpy as np

def interim_analysis(endpoints, alpha=0.05):
    """Analyze multiple endpoints with interim monitoring."""
    
    # Use LORD3 for temporal correlation in sequential analyses
    method = LordThree(alpha=alpha, wealth=alpha/2, reward=alpha/2)
    
    results = {}
    
    for endpoint_name, (treatment_outcomes, control_outcomes) in endpoints.items():
        # Create contingency table
        treatment_success = np.sum(treatment_outcomes)
        treatment_total = len(treatment_outcomes)
        control_success = np.sum(control_outcomes) 
        control_total = len(control_outcomes)
        
        contingency_table = np.array([
            [treatment_success, treatment_total - treatment_success],
            [control_success, control_total - control_success]
        ])
        
        # Perform chi-square test
        chi2, p_value, dof, expected = chi2_contingency(contingency_table)
        
        # Apply online FDR control
        is_significant = method.test_one(p_value)
        
        # Calculate effect measures
        treatment_rate = treatment_success / treatment_total
        control_rate = control_success / control_total
        relative_risk = treatment_rate / control_rate if control_rate > 0 else np.inf
        
        results[endpoint_name] = {
            'p_value': p_value,
            'significant': is_significant,
            'treatment_rate': treatment_rate,
            'control_rate': control_rate,
            'relative_risk': relative_risk,
            'chi2_statistic': chi2
        }
        
        if is_significant:
            print(f" {endpoint_name}: Significant treatment effect!")
            print(f"   Treatment rate: {treatment_rate:.3f}")
            print(f"   Control rate: {control_rate:.3f}")
            print(f"   Relative risk: {relative_risk:.3f}")
    
    return results

# Simulate clinical trial data
np.random.seed(456)
endpoints = {
    'Primary_Efficacy': (
        np.random.binomial(1, 0.65, 200),    # Treatment group
        np.random.binomial(1, 0.50, 200)     # Control group  
    ),
    'Secondary_QoL': (
        np.random.binomial(1, 0.70, 200),
        np.random.binomial(1, 0.60, 200)
    ),
    'Safety_AE': (
        np.random.binomial(1, 0.15, 200),
        np.random.binomial(1, 0.12, 200)
    )
}

trial_results = interim_analysis(endpoints, alpha=0.1)
```

## Domain-Specific Applications

### Technology & Web

=== "A/B Testing"
    - Multi-variant testing with FDR control
    - Conversion rate optimization
    - Feature rollout decision making
    - Revenue impact assessment

=== "System Monitoring"  
    - Anomaly detection in metrics
    - Performance regression testing
    - Alert fatigue reduction
    - SLA violation analysis

### Life Sciences

=== "Genomics"
    - Differential gene expression
    - GWAS analysis
    - Variant prioritization  
    - Pathway enrichment

=== "Drug Discovery"
    - High-throughput screening
    - Biomarker identification
    - Toxicity testing
    - Clinical endpoint analysis

### Finance & Economics

=== "Risk Management"
    - Market anomaly detection
    - Portfolio optimization
    - Fraud detection
    - Credit scoring

=== "Algorithmic Trading"
    - Strategy backtesting
    - Factor discovery
    - Market regime detection
    - Risk factor analysis

### Research & Academia

=== "Psychology"
    - Experiment replication studies
    - Meta-analysis
    - Survey data analysis
    - Behavioral intervention studies

=== "Epidemiology" 
    - Disease outbreak detection
    - Risk factor identification
    - Treatment effectiveness
    - Public health surveillance

## Code Templates

### Template 1: Sequential Testing Pipeline

```python
def sequential_testing_pipeline(data_stream, method_class, method_params, 
                               statistical_test, significance_threshold=0.05):
    """Generic pipeline for sequential hypothesis testing."""
    
    # Initialize FDR method
    fdr_method = method_class(**method_params)
    
    results = {
        'decisions': [],
        'p_values': [],
        'test_statistics': [],
        'effect_sizes': [],
        'timestamps': []
    }
    
    for i, data_point in enumerate(data_stream):
        # Extract test data
        test_data = data_point['test_data']
        control_data = data_point['control_data']
        timestamp = data_point.get('timestamp', i)
        
        # Perform statistical test
        statistic, p_value = statistical_test(test_data, control_data)
        
        # Apply FDR control
        decision = fdr_method.test_one(p_value)
        
        # Calculate effect size
        effect_size = np.mean(test_data) - np.mean(control_data)
        
        # Store results
        results['decisions'].append(decision)
        results['p_values'].append(p_value)
        results['test_statistics'].append(statistic)
        results['effect_sizes'].append(effect_size)
        results['timestamps'].append(timestamp)
        
        # Optional: Early stopping condition
        if decision and effect_size < -0.5:  # Negative effect threshold
            print(f"Early stopping at test {i+1}: Large negative effect detected")
            break
    
    return results
```

### Template 2: Performance Evaluation

```python
def evaluate_fdr_method(method, p_values, true_labels, alpha=0.05):
    """Comprehensive evaluation of FDR method performance."""
    
    # Run the method
    decisions = []
    for p_val in p_values:
        decisions.append(method.test_one(p_val))
    
    # Calculate performance metrics
    decisions = np.array(decisions)
    true_labels = np.array(true_labels)  # True if alternative hypothesis
    
    # Confusion matrix components
    true_positives = np.sum(decisions & true_labels)
    false_positives = np.sum(decisions & ~true_labels)
    true_negatives = np.sum(~decisions & ~true_labels)
    false_negatives = np.sum(~decisions & true_labels)
    
    # Performance metrics
    total_discoveries = true_positives + false_positives
    empirical_fdr = false_positives / max(total_discoveries, 1)
    power = true_positives / np.sum(true_labels) if np.sum(true_labels) > 0 else 0
    precision = true_positives / max(total_discoveries, 1)
    recall = power  # Same as power
    
    results = {
        'total_tests': len(p_values),
        'total_discoveries': total_discoveries,
        'true_positives': true_positives,
        'false_positives': false_positives,
        'true_negatives': true_negatives,
        'false_negatives': false_negatives,
        'empirical_fdr': empirical_fdr,
        'power': power,
        'precision': precision,
        'recall': recall,
        'target_fdr': alpha,
        'fdr_controlled': empirical_fdr <= alpha * 1.1  # 10% tolerance
    }
    
    return results
```

## Visualization Examples

### Plotting FDR Control Over Time

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_fdr_control(p_values, true_labels, method, alpha=0.05):
    """Plot empirical FDR over time."""
    
    decisions = []
    cumulative_fdr = []
    true_pos = false_pos = 0
    
    for p_val, is_alt in zip(p_values, true_labels):
        decision = method.test_one(p_val)
        decisions.append(decision)
        
        if decision:
            if is_alt:
                true_pos += 1
            else:
                false_pos += 1
        
        # Calculate cumulative FDR
        total_discoveries = true_pos + false_pos
        current_fdr = false_pos / max(total_discoveries, 1)
        cumulative_fdr.append(current_fdr)
    
    # Create plot
    plt.figure(figsize=(12, 6))
    
    # Plot empirical FDR
    plt.subplot(1, 2, 1)
    plt.plot(cumulative_fdr, label='Empirical FDR', linewidth=2)
    plt.axhline(y=alpha, color='red', linestyle='--', 
               label=f'Target FDR (={alpha})')
    plt.xlabel('Test Number')
    plt.ylabel('Cumulative FDR')
    plt.title('FDR Control Over Time')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot discoveries
    plt.subplot(1, 2, 2)
    cumulative_discoveries = np.cumsum(decisions)
    plt.plot(cumulative_discoveries, label='Total Discoveries', linewidth=2)
    plt.fill_between(range(len(cumulative_discoveries)), 
                    cumulative_discoveries, alpha=0.3)
    plt.xlabel('Test Number')  
    plt.ylabel('Cumulative Discoveries')
    plt.title('Discoveries Over Time')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    return cumulative_fdr, cumulative_discoveries
```

## Next Steps

Ready to dive deeper? Choose an example category:

- **[Basic Usage](basic_usage.md)**: Start here if you're new to online FDR control
- **[Advanced Scenarios](advanced.md)**: Real-world applications and complex use cases  
- **[Method Comparisons](comparison.md)**: Systematic comparison studies

Or explore other sections:
- **[API Reference](../api/index.md)**: Detailed method documentation
- **[Theory](../theory/index.md)**: Mathematical foundations  
- **[User Guide](../user_guide/index.md)**: Concepts and best practices
