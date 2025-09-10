# Data Generation

The **online-fdr** package provides comprehensive utilities for generating synthetic data to test and validate FDR control methods. This is essential for simulation studies, method comparison, and performance evaluation.

## Overview

Data generation involves creating realistic p-value sequences that mirror real-world testing scenarios. The package provides:

!!! info "Data Generation Components"
    - **Data Generating Processes (DGPs)**: Define how test statistics are distributed
    - **DataGenerator**: Orchestrates the generation process with null/alternative mixture
    - **Realistic Models**: Various statistical models for different domains

## Core Components

### DataGenerator Class

The main interface for generating p-value sequences:

```python
from online_fdr.utils.generation import DataGenerator, GaussianLocationModel

# Create a data generating process
dgp = GaussianLocationModel(alt_mean=2.0, alt_std=1.0, one_sided=True)

# Create data generator with mixture of nulls and alternatives
generator = DataGenerator(
    n=1000,        # Total number of tests
    pi0=0.9,       # Proportion of true nulls (90%)
    dgp=dgp        # Data generating process
)

# Generate individual p-values
for i in range(10):
    p_value, is_alternative = generator.sample_one()
    status = "ALT" if is_alternative else "NULL"
    print(f"Test {i+1}: p={p_value:.4f} ({status})")
```

### Available Data Generating Processes

#### GaussianLocationModel
**Best for**: General hypothesis testing, t-tests, regression

```python
from online_fdr.utils.generation import GaussianLocationModel

# Two-sided test (default)
dgp_two_sided = GaussianLocationModel(
    alt_mean=1.5,    # Effect size under alternative
    alt_std=1.0,     # Standard deviation
    one_sided=False  # Two-sided test
)

# One-sided test (more powerful)
dgp_one_sided = GaussianLocationModel(
    alt_mean=1.2,    # Smaller effect detectable
    alt_std=1.0,
    one_sided=True   # One-sided test
)

# Test both variants
print("Two-sided vs One-sided Power Comparison:")

generator_two = DataGenerator(n=100, pi0=0.8, dgp=dgp_two_sided)
generator_one = DataGenerator(n=100, pi0=0.8, dgp=dgp_one_sided)

# Sample some alternatives to compare
two_sided_alt_p = []
one_sided_alt_p = []

for _ in range(20):
    # Force generation of alternatives
    while True:
        p_val, is_alt = generator_two.sample_one()
        if is_alt:
            two_sided_alt_p.append(p_val)
            break
    
    while True:
        p_val, is_alt = generator_one.sample_one()
        if is_alt:
            one_sided_alt_p.append(p_val)
            break

print(f"Two-sided alternative p-values (mean): {sum(two_sided_alt_p)/len(two_sided_alt_p):.4f}")
print(f"One-sided alternative p-values (mean): {sum(one_sided_alt_p)/len(one_sided_alt_p):.4f}")
print("One-sided tests typically have smaller p-values (more power)")
```

#### BetaMixtureModel  
**Best for**: Genomics, when effect sizes vary widely

```python
from online_fdr.utils.generation import BetaMixtureModel

# Beta mixture model mimics genomics p-value distributions
dgp_beta = BetaMixtureModel(
    alt_alpha=0.5,   # Shape parameter (< 1 creates U-shape)
    alt_beta=10.0    # Shape parameter (skews toward 0)
)

generator_beta = DataGenerator(n=100, pi0=0.95, dgp=dgp_beta)

# Sample p-values to see distribution
alt_p_values = []
null_p_values = []

for _ in range(100):
    p_val, is_alt = generator_beta.sample_one()
    if is_alt:
        alt_p_values.append(p_val)
    else:
        null_p_values.append(p_val)

print("Beta Mixture Model Results:")
print(f"Alternative p-values: min={min(alt_p_values):.4f}, mean={sum(alt_p_values)/len(alt_p_values):.4f}")
print(f"Null p-values: min={min(null_p_values):.4f}, mean={sum(null_p_values)/len(null_p_values):.4f}")
```

#### ChiSquaredModel
**Best for**: Goodness-of-fit tests, variance testing

```python
from online_fdr.utils.generation import ChiSquaredModel

# Chi-squared model for variance-based tests
dgp_chi2 = ChiSquaredModel(
    df=1,           # Degrees of freedom  
    alt_scale=3.0   # Scale factor for alternatives
)

generator_chi2 = DataGenerator(n=100, pi0=0.85, dgp=dgp_chi2)

# Generate and examine p-values
chi2_p_values = [generator_chi2.sample_one()[0] for _ in range(50)]
print("Chi-squared Model Sample:")
print(f"First 10 p-values: {[f'{p:.3f}' for p in chi2_p_values[:10]]}")
```

#### SparseGaussianModel
**Best for**: High-dimensional testing, screening studies

```python
from online_fdr.utils.generation import SparseGaussianModel

# Sparse model with varying effect sizes
dgp_sparse = SparseGaussianModel(
    effect_dist="uniform",  # How effects are distributed
    min_effect=1.5,        # Minimum effect size
    max_effect=4.0         # Maximum effect size
)

generator_sparse = DataGenerator(n=100, pi0=0.98, dgp=dgp_sparse)

# Sample to see sparse nature
sparse_results = []
for _ in range(100):
    p_val, is_alt = generator_sparse.sample_one()
    sparse_results.append((p_val, is_alt))

alternatives = [(p, alt) for p, alt in sparse_results if alt]
print("Sparse Gaussian Model:")
print(f"Alternatives found: {len(alternatives)} out of 100")
print(f"Alternative p-values: {[f'{p:.4f}' for p, _ in alternatives[:5]]}")
```

## Realistic Simulation Scenarios

### A/B Testing Simulation

```python
def simulate_ab_testing_scenario(n_variants=5, n_tests_per_variant=100):
    """Simulate A/B testing with multiple variants."""
    
    from online_fdr.utils.generation import DataGenerator, GaussianLocationModel
    import random
    
    print(f"Simulating A/B test with {n_variants} variants:")
    
    # Different variants have different effect sizes
    effect_sizes = [0.0, 0.2, 0.0, 0.5, 0.1]  # Mix of null and alternative variants
    
    all_p_values = []
    all_labels = []
    all_variants = []
    
    for variant_id, effect_size in enumerate(effect_sizes):
        print(f"  Variant {variant_id + 1}: effect size = {effect_size}")
        
        if effect_size == 0.0:
            # Pure null variant
            dgp = GaussianLocationModel(alt_mean=0.0, alt_std=1.0, one_sided=False)
            generator = DataGenerator(n=n_tests_per_variant, pi0=1.0, dgp=dgp)
        else:
            # Variant with real effect
            dgp = GaussianLocationModel(alt_mean=effect_size, alt_std=1.0, one_sided=True)
            generator = DataGenerator(n=n_tests_per_variant, pi0=0.0, dgp=dgp)
        
        # Generate p-values for this variant
        variant_p_values = []
        variant_labels = []
        
        for _ in range(n_tests_per_variant):
            p_val, is_alt = generator.sample_one()
            variant_p_values.append(p_val)
            variant_labels.append(effect_size > 0)  # True if variant has effect
            
        all_p_values.extend(variant_p_values)
        all_labels.extend(variant_labels)
        all_variants.extend([f"Variant_{variant_id + 1}"] * n_tests_per_variant)
        
        mean_p = sum(variant_p_values) / len(variant_p_values)
        print(f"    Mean p-value: {mean_p:.4f}")
    
    return all_p_values, all_labels, all_variants

# Run A/B testing simulation
p_vals, labels, variants = simulate_ab_testing_scenario()
print(f"\nGenerated {len(p_vals)} total tests across variants")
```

### Time Series Simulation

```python
def simulate_time_series_scenario(n_time_points=200, trend_change_points=None):
    """Simulate time series with changing signal strength."""
    
    from online_fdr.utils.generation import DataGenerator, GaussianLocationModel
    import math
    
    if trend_change_points is None:
        trend_change_points = [50, 100, 150]
    
    print("Simulating time series with changing signal:")
    
    all_p_values = []
    all_time_points = []
    true_signal_strength = []
    
    current_effect = 0.0
    effect_levels = [0.0, 1.5, 0.0, 2.0, 0.5]  # Different phases
    
    for t in range(n_time_points):
        # Determine current effect size based on time
        phase = sum(1 for cp in trend_change_points if t >= cp)
        current_effect = effect_levels[phase] if phase < len(effect_levels) else 0.0
        
        # Add some noise to effect size
        noisy_effect = current_effect + 0.2 * math.sin(t / 20)  # Sinusoidal variation
        
        # Generate p-value for this time point
        dgp = GaussianLocationModel(alt_mean=abs(noisy_effect), alt_std=1.0, one_sided=True)
        
        if noisy_effect <= 0.1:  # Essentially null
            generator = DataGenerator(n=1, pi0=1.0, dgp=dgp)
        else:  # Alternative
            generator = DataGenerator(n=1, pi0=0.0, dgp=dgp)
        
        p_val, _ = generator.sample_one()
        
        all_p_values.append(p_val)
        all_time_points.append(t)
        true_signal_strength.append(current_effect)
        
        # Print phase changes
        if t in trend_change_points:
            print(f"  Time {t}: Signal strength changed to {current_effect}")
    
    return all_p_values, all_time_points, true_signal_strength

# Run time series simulation
ts_p_vals, time_points, signal_strength = simulate_time_series_scenario()
print(f"\nGenerated time series with {len(ts_p_vals)} time points")

# Show some statistics by phase
phases = [0, 50, 100, 150, 200]
for i in range(len(phases) - 1):
    start, end = phases[i], phases[i + 1]
    phase_p_vals = ts_p_vals[start:end]
    mean_p = sum(phase_p_vals) / len(phase_p_vals)
    print(f"Phase {i + 1} (t={start}-{end}): mean p-value = {mean_p:.4f}")
```

### Genomics-Style Simulation

```python
def simulate_genomics_scenario(n_genes=10000, n_significant=100):
    """Simulate genomics study with conservative nulls."""
    
    from online_fdr.utils.generation import DataGenerator, BetaMixtureModel
    import random
    
    print(f"Simulating genomics study: {n_genes} genes, {n_significant} truly significant")
    
    # Most genes are null with conservative p-values
    # (common in real genomics data due to correlation, batch effects, etc.)
    
    # Conservative nulls: Beta(1, 0.8) gives p-values skewed toward 1
    conservative_dgp = BetaMixtureModel(alt_alpha=1.0, alt_beta=0.8)
    
    # True alternatives: Beta(0.3, 5) gives small p-values
    alternative_dgp = BetaMixtureModel(alt_alpha=0.3, alt_beta=5.0)
    
    # Generate gene IDs and assign significance status
    gene_ids = [f"Gene_{i+1:05d}" for i in range(n_genes)]
    significant_genes = random.sample(range(n_genes), n_significant)
    
    all_p_values = []
    all_gene_ids = []
    all_is_significant = []
    
    print("Generating p-values...")
    for i, gene_id in enumerate(gene_ids):
        if i in significant_genes:
            # Generate from alternative distribution
            generator = DataGenerator(n=1, pi0=0.0, dgp=alternative_dgp)
        else:
            # Generate conservative null
            generator = DataGenerator(n=1, pi0=1.0, dgp=conservative_dgp)
        
        p_val, _ = generator.sample_one()
        
        all_p_values.append(p_val)
        all_gene_ids.append(gene_id)
        all_is_significant.append(i in significant_genes)
        
        # Show progress
        if (i + 1) % 2000 == 0:
            print(f"  Generated {i + 1}/{n_genes} p-values")
    
    # Analyze the generated data
    sig_p_values = [p for p, sig in zip(all_p_values, all_is_significant) if sig]
    null_p_values = [p for p, sig in zip(all_p_values, all_is_significant) if not sig]
    
    print(f"\nGenomics simulation results:")
    print(f"Significant genes - mean p-value: {sum(sig_p_values)/len(sig_p_values):.4f}")
    print(f"Null genes - mean p-value: {sum(null_p_values)/len(null_p_values):.4f}")
    print(f"Conservative nulls create higher mean p-value for nulls")
    
    return all_p_values, all_gene_ids, all_is_significant

# Run genomics simulation (smaller scale for demo)
genomics_p_vals, gene_ids, is_significant = simulate_genomics_scenario(
    n_genes=1000, n_significant=50
)
```

## Advanced Data Generation

### Custom Data Generating Process

```python
class CustomExponentialDGP:
    """Custom DGP for exponential survival-like data."""
    
    def __init__(self, null_rate=1.0, alt_rate=2.0):
        self.null_rate = null_rate
        self.alt_rate = alt_rate
    
    def generate_p_value(self, is_alternative):
        """Generate p-value from exponential model."""
        import random
        import math
        
        if is_alternative:
            # Alternative: faster rate (shorter survival)
            test_statistic = random.exponential(1/self.alt_rate)
            # Convert to p-value using null distribution
            p_value = math.exp(-self.null_rate * test_statistic)
        else:
            # Null: standard rate
            test_statistic = random.exponential(1/self.null_rate) 
            p_value = random.uniform(0, 1)  # Null p-values are uniform
            
        return min(p_value, 1.0)  # Ensure p-value ≤ 1

# Use custom DGP
custom_dgp = CustomExponentialDGP(null_rate=1.0, alt_rate=3.0)

# Manual generation (DataGenerator might not work with custom DGPs)
print("Custom Exponential DGP:")
for i in range(10):
    # Alternate between null and alternative for demo
    is_alt = i % 3 == 0  # Every 3rd is alternative
    p_val = custom_dgp.generate_p_value(is_alt)
    status = "ALT" if is_alt else "NULL"
    print(f"Test {i+1}: p={p_val:.4f} ({status})")
```

### Parameter Sensitivity Analysis

```python
def analyze_dgp_sensitivity():
    """Analyze how DGP parameters affect p-value distributions."""
    
    from online_fdr.utils.generation import DataGenerator, GaussianLocationModel
    
    # Test different effect sizes
    effect_sizes = [0.5, 1.0, 1.5, 2.0, 3.0]
    
    print("Effect Size Sensitivity Analysis:")
    print("=" * 50)
    
    results = {}
    
    for effect_size in effect_sizes:
        dgp = GaussianLocationModel(
            alt_mean=effect_size, 
            alt_std=1.0, 
            one_sided=True
        )
        
        generator = DataGenerator(n=100, pi0=0.0, dgp=dgp)  # Pure alternatives
        
        # Generate sample of p-values
        p_values = [generator.sample_one()[0] for _ in range(100)]
        
        # Calculate statistics
        mean_p = sum(p_values) / len(p_values)
        min_p = min(p_values)
        power_est = sum(1 for p in p_values if p <= 0.05) / len(p_values)
        
        results[effect_size] = {
            'mean_p': mean_p,
            'min_p': min_p,
            'power_05': power_est
        }
        
        print(f"Effect size {effect_size:3.1f}: mean p = {mean_p:.4f}, "
              f"power@0.05 = {power_est:.3f}")
    
    return results

# Run sensitivity analysis
sensitivity_results = analyze_dgp_sensitivity()
```

## Integration with FDR Methods

### Complete Simulation Pipeline

```python
def complete_simulation_study(method_configs, n_simulations=10):
    """Complete simulation study comparing FDR methods."""
    
    from online_fdr.investing.addis.addis import Addis
    from online_fdr.investing.lord.three import LordThree
    from online_fdr.batching.bh import BatchBH
    from online_fdr.utils.generation import DataGenerator, GaussianLocationModel
    
    print(f"Running complete simulation study ({n_simulations} replications)")
    
    # Simulation settings
    n_tests = 500
    pi0 = 0.9
    effect_size = 2.0
    
    # Create data generating process
    dgp = GaussianLocationModel(alt_mean=effect_size, alt_std=1.0, one_sided=True)
    
    # Initialize methods
    methods = {
        'ADDIS': Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5),
        'LORD3': LordThree(alpha=0.05, wealth=0.025, reward=0.05),
        'BatchBH': BatchBH(alpha=0.05)
    }
    
    # Storage for results
    all_results = {name: {'fdr': [], 'power': [], 'discoveries': []} 
                  for name in methods.keys()}
    
    print(f"Methods being compared: {list(methods.keys())}")
    
    for sim in range(n_simulations):
        if sim % 5 == 0:
            print(f"  Simulation {sim + 1}/{n_simulations}")
        
        # Generate data for this simulation
        generator = DataGenerator(n=n_tests, pi0=pi0, dgp=dgp)
        
        p_values = []
        true_labels = []
        
        for _ in range(n_tests):
            p_val, is_alt = generator.sample_one()
            p_values.append(p_val)
            true_labels.append(is_alt)
        
        # Test each method
        for method_name, method in methods.items():
            if method_name == 'BatchBH':
                # Batch method
                decisions = method.test_batch(p_values)
            else:
                # Sequential method - need fresh instance
                if method_name == 'ADDIS':
                    fresh_method = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)
                elif method_name == 'LORD3':
                    fresh_method = LordThree(alpha=0.05, wealth=0.025, reward=0.05)
                
                decisions = [fresh_method.test_one(p) for p in p_values]
            
            # Calculate performance metrics
            true_pos = sum(d and t for d, t in zip(decisions, true_labels))
            false_pos = sum(d and not t for d, t in zip(decisions, true_labels))
            total_discoveries = true_pos + false_pos
            
            empirical_fdr = false_pos / max(total_discoveries, 1)
            empirical_power = true_pos / sum(true_labels)
            
            # Store results
            all_results[method_name]['fdr'].append(empirical_fdr)
            all_results[method_name]['power'].append(empirical_power)
            all_results[method_name]['discoveries'].append(total_discoveries)
    
    # Summarize results
    print(f"\nSimulation Results (π₀={pi0}, effect size={effect_size}):")
    print("=" * 60)
    
    for method_name, results in all_results.items():
        mean_fdr = sum(results['fdr']) / len(results['fdr'])
        mean_power = sum(results['power']) / len(results['power'])
        mean_discoveries = sum(results['discoveries']) / len(results['discoveries'])
        
        print(f"{method_name:>8}: FDR={mean_fdr:.3f}, Power={mean_power:.3f}, "
              f"Discoveries={mean_discoveries:.1f}")
    
    return all_results

# Run complete simulation study
simulation_results = complete_simulation_study(
    method_configs={}, 
    n_simulations=20
)
```

## Best Practices

### Choosing Appropriate DGPs

!!! tip "Domain-Specific Guidelines"
    - **A/B Testing**: Use GaussianLocationModel with small effect sizes (0.1-0.5)
    - **Genomics**: Use BetaMixtureModel with conservative nulls
    - **Survival Analysis**: Use ChiSquaredModel or custom exponential DGPs
    - **High-dimensional**: Use SparseGaussianModel with very low π₁

### Simulation Design Principles

1. **Effect Size Realism**: Use effect sizes observed in real data
2. **Null Proportion**: Most real applications have π₀ > 0.8
3. **Sample Size**: Balance realism with computational cost  
4. **Replication**: Use ≥ 100 replications for stable estimates
5. **Multiple Scenarios**: Test various π₀ and effect size combinations

### Common Pitfalls

!!! warning "Avoid These Mistakes"
    - **Unrealistic effect sizes**: Don't use effect sizes > 3 standard deviations
    - **Too few replications**: < 50 simulations give unstable results
    - **Ignoring dependence**: Real data often has correlation structure
    - **Only uniform nulls**: Many applications have conservative nulls

## References

1. **Efron, B.** (2007). "Size, power and false discovery rates." *Annals of Statistics*, 35(4):1351-1377.

2. **Schwartzman, A., and X. Lin** (2011). "The effect of correlation in false discovery rate estimation." *Biometrika*, 98(1):199-214.

3. **Stephens, M.** (2017). "False discovery rates: a new deal." *Biostatistics*, 18(2):275-294.

## Next Steps

- **Apply data generation in [examples](../examples/basic_usage.md)**
- **Learn about [evaluation metrics](evaluation.md)**  
- **See [theory](../theory/fdr_control.md)** for mathematical foundations