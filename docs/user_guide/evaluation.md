# Performance Evaluation

Evaluating FDR control methods requires careful measurement of statistical performance, computational efficiency, and robustness. This guide covers the evaluation utilities and best practices for assessing method performance.

## Core Evaluation Metrics

### False Discovery Rate (FDR)

The primary metric for multiple testing correction:

$$\text{FDR} = \mathbb{E}\left[\frac{V}{R \vee 1}\right]$$

where $V$ = false discoveries, $R$ = total discoveries.

```python
from online_fdr.core.utils import calculate_sfdr

# Example evaluation
true_positives = 45   # Correctly rejected nulls
false_positives = 5   # Incorrectly rejected nulls
total_discoveries = true_positives + false_positives

# Calculate smoothed FDR (handles R=0 case)
empirical_fdr = calculate_sfdr(true_positives, false_positives)

print(f"Discoveries: {total_discoveries}")
print(f"False discoveries: {false_positives}")
print(f"Empirical FDR: {empirical_fdr:.3f}")
print(f"Target FDR: 0.05")
print(f"FDR controlled: {'yes' if empirical_fdr <= 0.05 else 'no'}")
```

### Statistical Power

The proportion of true alternatives correctly identified:

$$\text{Power} = \mathbb{E}\left[\frac{\text{True Positives}}{\text{Total Alternatives}}\right]$$

```python
from online_fdr.core.utils import calculate_power

# Power calculation
true_positives = 45
false_negatives = 15  # Missed true alternatives
total_alternatives = true_positives + false_negatives

power = calculate_power(true_positives, false_negatives)

print(f"True alternatives: {total_alternatives}")
print(f"Correctly identified: {true_positives}")
print(f"Statistical power: {power:.3f}")
```

### Comprehensive Performance Assessment

```python
def evaluate_method_performance(decisions, true_labels, alpha=0.05):
    """Comprehensive performance evaluation."""
    
    from online_fdr.core.utils import calculate_sfdr, calculate_power
    
    # Convert to boolean arrays if needed
    decisions = [bool(d) for d in decisions]
    true_labels = [bool(t) for t in true_labels]
    
    # Calculate confusion matrix elements
    true_positives = sum(d and t for d, t in zip(decisions, true_labels))
    false_positives = sum(d and not t for d, t in zip(decisions, true_labels))
    true_negatives = sum(not d and not t for d, t in zip(decisions, true_labels))
    false_negatives = sum(not d and t for d, t in zip(decisions, true_labels))
    
    # Primary metrics
    total_discoveries = true_positives + false_positives
    total_alternatives = true_positives + false_negatives
    total_nulls = false_positives + true_negatives
    
    empirical_fdr = calculate_sfdr(true_positives, false_positives)
    power = calculate_power(true_positives, false_negatives)
    
    # Additional metrics
    precision = true_positives / max(total_discoveries, 1)
    specificity = true_negatives / max(total_nulls, 1)
    
    results = {
        'total_tests': len(decisions),
        'total_discoveries': total_discoveries,
        'total_alternatives': total_alternatives,
        'true_positives': true_positives,
        'false_positives': false_positives,
        'true_negatives': true_negatives,
        'false_negatives': false_negatives,
        'empirical_fdr': empirical_fdr,
        'power': power,
        'precision': precision,
        'specificity': specificity,
        'fdr_controlled': empirical_fdr <= alpha * 1.1,  # 10% tolerance
        'discovery_rate': total_discoveries / len(decisions)
    }
    
    return results

# Example usage
decisions = [True, False, True, True, False, False, True, False]
true_labels = [True, False, False, True, True, False, True, False]

performance = evaluate_method_performance(decisions, true_labels, alpha=0.1)

print("Performance Evaluation Results:")
print("=" * 40)
for metric, value in performance.items():
    if isinstance(value, float):
        print(f"{metric:>20}: {value:.3f}")
    elif isinstance(value, bool):
        print(f"{metric:>20}: {'yes' if value else 'no'}")
    else:
        print(f"{metric:>20}: {value}")
```

## Online-Specific Metrics

### Temporal FDR Control

For sequential testing, we can monitor FDR over time:

```python
class OnlineFDRTracker:
    """Track FDR control during sequential testing."""
    
    def __init__(self):
        self.decisions = []
        self.true_labels = []
        self.fdr_history = []
        self.power_history = []
    
    def update(self, decision, true_label):
        """Update with new test result."""
        self.decisions.append(decision)
        self.true_labels.append(true_label)
        
        # Calculate current FDR and power
        tp = sum(d and t for d, t in zip(self.decisions, self.true_labels))
        fp = sum(d and not t for d, t in zip(self.decisions, self.true_labels))
        fn = sum(not d and t for d, t in zip(self.decisions, self.true_labels))
        
        current_fdr = fp / max(tp + fp, 1)
        current_power = tp / max(tp + fn, 1)
        
        self.fdr_history.append(current_fdr)
        self.power_history.append(current_power)
        
        return current_fdr, current_power
    
    def plot_history(self):
        """Plot FDR and power over time."""
        try:
            import matplotlib.pyplot as plt
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            # FDR over time
            ax1.plot(self.fdr_history, 'b-', label='Empirical FDR')
            ax1.axhline(y=0.05, color='r', linestyle='--', label='Target FDR')
            ax1.set_ylabel('FDR')
            ax1.set_title('FDR Control Over Time')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Power over time
            ax2.plot(self.power_history, 'g-', label='Power')
            ax2.set_xlabel('Test Number')
            ax2.set_ylabel('Power')
            ax2.set_title('Power Over Time')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            print("Matplotlib not available for plotting")

# Example usage with sequential testing
from online_fdr.p_values import Addis
from online_fdr.core.utils import DataGenerator, GaussianLocationModel

# Set up simulation
dgp = GaussianLocationModel(alt_mean=2.0, alt_std=1.0, one_sided=True)
generator = DataGenerator(n=200, pi0=0.9, dgp=dgp)
addis = Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5)

# Track performance over time
tracker = OnlineFDRTracker()

print("Sequential FDR Tracking:")
for i in range(50):
    p_value, is_alternative = generator.sample_one()
    decision = addis.test_one(p_value)
    
    current_fdr, current_power = tracker.update(decision, is_alternative)
    
    if decision:
        print(f"Test {i+1}: Discovery: FDR={current_fdr:.3f}, Power={current_power:.3f}")

print(f"\nFinal FDR: {tracker.fdr_history[-1]:.3f}")
print(f"Final Power: {tracker.power_history[-1]:.3f}")
```

### Memory-Decay FDR

For non-stationary sequences, use memory-decay FDR:

```python
from online_fdr.core.utils import MemoryDecayFDR

# Memory-decay FDR with forgetting factor
memory_fdr = MemoryDecayFDR(delta=0.99, offset=0)

print("Memory-Decay FDR Evaluation:")

# Simulate a sequence with time-varying signal
decisions = [True, False, True, False, False, True, True, False]
true_labels = [True, False, False, False, True, True, True, False]

for i, (decision, true_label) in enumerate(zip(decisions, true_labels)):
    current_fdr = memory_fdr.score_one(decision, true_label)
    print(f"Test {i+1}: Decision={decision}, FDR={current_fdr:.4f}")

print(f"Final memory-decay FDR: {current_fdr:.4f}")
```

## Method Comparison Framework

### Simulation-Based Comparison

```python
def compare_methods_simulation(methods, simulation_configs, n_reps=100):
    """Comprehensive method comparison via simulation."""
    
    from online_fdr.core.utils import DataGenerator, GaussianLocationModel
    import random
    
    results = {name: [] for name in methods.keys()}
    
    print(f"Method Comparison Study ({n_reps} replications)")
    print("=" * 50)
    
    for rep in range(n_reps):
        if (rep + 1) % 20 == 0:
            print(f"Replication {rep + 1}/{n_reps}")
        
        # Generate data for this replication
        dgp = GaussianLocationModel(**simulation_configs['dgp_params'])
        generator = DataGenerator(**simulation_configs['generator_params'], dgp=dgp)
        
        p_values = []
        true_labels = []
        
        for _ in range(simulation_configs['n_tests']):
            p_val, is_alt = generator.sample_one()
            p_values.append(p_val)
            true_labels.append(is_alt)
        
        # Test each method
        for method_name, method_class in methods.items():
            # Create fresh instance for each replication
            method = method_class()
            
            # Apply method
            if hasattr(method, 'test_batch'):
                decisions = method.test_batch(p_values)
            else:
                decisions = [method.test_one(p) for p in p_values]
            
            # Evaluate performance
            performance = evaluate_method_performance(
                decisions, true_labels, 
                alpha=simulation_configs.get('alpha', 0.05)
            )
            
            results[method_name].append(performance)
    
    # Aggregate results
    print("\nAggregated Results:")
    print("=" * 50)
    
    summary = {}
    
    for method_name, rep_results in results.items():
        # Calculate means and standard errors
        fdr_values = [r['empirical_fdr'] for r in rep_results]
        power_values = [r['power'] for r in rep_results]
        discovery_values = [r['total_discoveries'] for r in rep_results]
        
        mean_fdr = sum(fdr_values) / len(fdr_values)
        se_fdr = (sum((x - mean_fdr)**2 for x in fdr_values) / len(fdr_values))**0.5 / len(fdr_values)**0.5
        
        mean_power = sum(power_values) / len(power_values)
        se_power = (sum((x - mean_power)**2 for x in power_values) / len(power_values))**0.5 / len(power_values)**0.5
        
        mean_discoveries = sum(discovery_values) / len(discovery_values)
        
        fdr_control_rate = sum(1 for r in rep_results if r['fdr_controlled']) / len(rep_results)
        
        summary[method_name] = {
            'mean_fdr': mean_fdr,
            'se_fdr': se_fdr,
            'mean_power': mean_power,
            'se_power': se_power,
            'mean_discoveries': mean_discoveries,
            'fdr_control_rate': fdr_control_rate
        }
        
        print(f"{method_name:>12}: FDR={mean_fdr:.3f} +/- {se_fdr:.3f}, "
              f"Power={mean_power:.3f} +/- {se_power:.3f}, "
              f"Discoveries={mean_discoveries:.1f}, "
              f"Control={fdr_control_rate:.0%}")
    
    return summary

# Example comparison
from online_fdr.p_values import Addis
from online_fdr.p_values import LordThree
from online_fdr.p_values import BatchBH

methods_to_compare = {
    'ADDIS': lambda: Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5),
    'LORD3': lambda: LordThree(alpha=0.05, wealth=0.025, reward=0.025),
    'BatchBH': lambda: BatchBH(alpha=0.05)
}

sim_config = {
    'n_tests': 500,
    'alpha': 0.05,
    'dgp_params': {'alt_mean': 2.0, 'alt_std': 1.0, 'one_sided': True},
    'generator_params': {'n': 500, 'pi0': 0.9}
}

comparison_results = compare_methods_simulation(
    methods_to_compare, sim_config, n_reps=50
)
```

## Computational Performance Evaluation

### Speed and Memory Benchmarks

```python
import time
import sys

def benchmark_method_performance(method_factory, p_values, n_runs=10):
    """Benchmark computational performance."""

    sample_method = method_factory()
    print(f"Benchmarking {sample_method.__class__.__name__}:")
    
    # Time benchmarking
    times = []
    
    for run in range(n_runs):
        # Create fresh instance for fair timing
        fresh_method = method_factory()
        
        start_time = time.time()
        
        # Run method
        if hasattr(fresh_method, 'test_batch'):
            results = fresh_method.test_batch(p_values)
        else:
            results = [fresh_method.test_one(p) for p in p_values]
        
        end_time = time.time()
        times.append(end_time - start_time)
    
    # Calculate statistics
    mean_time = sum(times) / len(times)
    std_time = (sum((t - mean_time)**2 for t in times) / len(times))**0.5
    
    # Memory usage (rough estimate)
    memory_usage = sys.getsizeof(sample_method) + sys.getsizeof(p_values)
    
    # Throughput
    throughput = len(p_values) / mean_time
    
    print(f"  Mean time: {mean_time:.4f} +/- {std_time:.4f} seconds")
    print(f"  Throughput: {throughput:.0f} tests/second")
    print(f"  Memory usage: {memory_usage/1024:.1f} KB")
    print(f"  Time per test: {mean_time/len(p_values)*1000:.3f} ms")
    
    return {
        'mean_time': mean_time,
        'std_time': std_time,
        'throughput': throughput,
        'memory_usage': memory_usage
    }

# Benchmark different methods
import random
random.seed(42)
test_p_values = [random.uniform(0, 1) for _ in range(1000)]

print("Performance Benchmarks:")
print("=" * 30)

# Benchmark ADDIS
addis_perf = benchmark_method_performance(
    lambda: Addis(alpha=0.05, wealth=0.025, lambda_=0.25, tau=0.5),
    test_p_values,
)

print()

# Benchmark BatchBH
bh_perf = benchmark_method_performance(
    lambda: BatchBH(alpha=0.05),
    test_p_values,
)

print(f"\nSpeedup: {addis_perf['mean_time'] / bh_perf['mean_time']:.1f}x "
      f"({'BatchBH' if bh_perf['mean_time'] < addis_perf['mean_time'] else 'ADDIS'} faster)")
```

## Robustness Testing

### Parameter Sensitivity Analysis

```python
def parameter_sensitivity_analysis(method_class, param_grid, base_params):
    """Analyze method sensitivity to parameter changes."""
    
    from online_fdr.core.utils import DataGenerator, GaussianLocationModel
    
    print("Parameter Sensitivity Analysis:")
    print("=" * 40)
    
    # Generate fixed test data
    dgp = GaussianLocationModel(alt_mean=2.0, alt_std=1.0, one_sided=True)
    generator = DataGenerator(n=200, pi0=0.9, dgp=dgp)
    
    p_values = []
    true_labels = []
    for _ in range(200):
        p_val, is_alt = generator.sample_one()
        p_values.append(p_val)
        true_labels.append(is_alt)
    
    results = {}
    
    for param_name, param_values in param_grid.items():
        print(f"\nTesting {param_name}:")
        param_results = []
        
        for param_value in param_values:
            # Create method with modified parameter
            test_params = base_params.copy()
            test_params[param_name] = param_value
            
            method = method_class(**test_params)
            
            # Test method
            decisions = [method.test_one(p) for p in p_values]
            
            # Evaluate
            performance = evaluate_method_performance(decisions, true_labels)
            param_results.append({
                'param_value': param_value,
                'fdr': performance['empirical_fdr'],
                'power': performance['power'],
                'discoveries': performance['total_discoveries']
            })
            
            print(f"  {param_name}={param_value}: "
                  f"FDR={performance['empirical_fdr']:.3f}, "
                  f"Power={performance['power']:.3f}")
        
        results[param_name] = param_results
    
    return results

# Example: ADDIS parameter sensitivity
addis_param_grid = {
    'wealth': [0.01, 0.02, 0.025, 0.04],
    'lambda_': [0.1, 0.25, 0.5, 0.75],
    'tau': [0.3, 0.5, 0.7, 0.9]
}

addis_base_params = {
    'alpha': 0.05,
    'wealth': 0.025,
    'lambda_': 0.25,
    'tau': 0.5
}

sensitivity_results = parameter_sensitivity_analysis(
    Addis, addis_param_grid, addis_base_params
)
```

### Dependency Structure Robustness

```python
def test_dependency_robustness(method_factory, dependency_scenarios):
    """Test method robustness under different dependency structures."""
    
    import numpy as np
    
    print("Dependency Robustness Testing:")
    print("=" * 35)
    
    n_tests = 500
    n_alternatives = 50
    
    results = {}
    
    for scenario_name, correlation in dependency_scenarios.items():
        print(f"\nTesting {scenario_name} (rho={correlation}):")
        
        # Generate correlated test statistics
        if correlation == 0:
            # Independent case
            test_stats = np.random.normal(0, 1, n_tests)
        else:
            # Correlated case - use AR(1) structure
            test_stats = np.zeros(n_tests)
            test_stats[0] = np.random.normal(0, 1)
            
            for i in range(1, n_tests):
                test_stats[i] = (correlation * test_stats[i-1] + 
                               np.sqrt(1 - correlation**2) * np.random.normal(0, 1))
        
        # Add signal to some tests (alternatives)
        alt_indices = np.random.choice(n_tests, n_alternatives, replace=False)
        test_stats[alt_indices] += 2.0  # Add signal
        
        # Convert to p-values
        from scipy.stats import norm
        p_values = 2 * (1 - norm.cdf(np.abs(test_stats)))  # Two-sided
        true_labels = np.zeros(n_tests, dtype=bool)
        true_labels[alt_indices] = True
        
        # Test method
        method = method_factory()
        if hasattr(method, 'test_batch'):
            decisions = method.test_batch(p_values.tolist())
        else:
            decisions = [method.test_one(p) for p in p_values]
        
        # Evaluate
        performance = evaluate_method_performance(decisions, true_labels.tolist())
        
        results[scenario_name] = performance
        
        print(f"  FDR: {performance['empirical_fdr']:.3f}")
        print(f"  Power: {performance['power']:.3f}")
        print(f"  FDR controlled: {'yes' if performance['fdr_controlled'] else 'no'}")
    
    return results

# Test dependency robustness
dependency_scenarios = {
    'Independent': 0.0,
    'Weak positive': 0.3,
    'Moderate positive': 0.6,
    'Strong positive': 0.9
}

from online_fdr.p_values import BatchBH

dependency_results = test_dependency_robustness(
    lambda: BatchBH(alpha=0.05),
    dependency_scenarios
)
```

## Evaluation Best Practices

### Comprehensive Evaluation Checklist

!!! tip "Statistical Performance"
    - FDR control under null (empirical FDR <= alpha)
    - Power comparison across effect sizes
    - Robustness to parameter misspecification
    - Performance under different dependency structures

!!! tip "Computational Performance"  
    - Scalability to large numbers of tests
    - Memory efficiency
    - Real-time processing capability (for online methods)

!!! tip "Practical Considerations"
    - Parameter sensitivity analysis
    - Robustness to model misspecification
    - Performance with realistic effect sizes
    - Behavior in edge cases (no discoveries, all discoveries)

### Reporting Guidelines

```python
def generate_evaluation_report(results, method_name, simulation_config):
    """Generate standardized evaluation report."""
    
    report = f"""
Method Evaluation Report: {method_name}
{'='*50}

Simulation Configuration:
- Number of tests: {simulation_config.get('n_tests', 'Unknown')}
- Null proportion (pi0): {simulation_config.get('pi0', 'Unknown')}
- Effect size: {simulation_config.get('effect_size', 'Unknown')}
- Target FDR (alpha): {simulation_config.get('alpha', 'Unknown')}
- Replications: {simulation_config.get('n_reps', 'Unknown')}

Performance Results:
- Empirical FDR: {results.get('mean_fdr', 0):.3f} +/- {results.get('se_fdr', 0):.3f}
- Statistical Power: {results.get('mean_power', 0):.3f} +/- {results.get('se_power', 0):.3f}
- Average Discoveries: {results.get('mean_discoveries', 0):.1f}
- FDR Control Rate: {results.get('fdr_control_rate', 0):.1%}

Interpretation:
"""
    
    # Add interpretation
    fdr_controlled = results.get('mean_fdr', 1) <= simulation_config.get('alpha', 0.05) * 1.1
    if fdr_controlled:
        report += "FDR is successfully controlled\n"
    else:
        report += "FDR control violation detected\n"
    
    power = results.get('mean_power', 0)
    if power >= 0.8:
        report += "High statistical power achieved\n"
    elif power >= 0.5:
        report += "Moderate statistical power\n"
    else:
        report += "Low statistical power\n"
    
    control_rate = results.get('fdr_control_rate', 0)
    if control_rate >= 0.95:
        report += "Consistent FDR control across replications\n"
    else:
        report += f"FDR control inconsistent ({control_rate:.0%} of replications)\n"
    
    return report

# Example report generation
sample_results = {
    'mean_fdr': 0.047,
    'se_fdr': 0.012,
    'mean_power': 0.73,
    'se_power': 0.05,
    'mean_discoveries': 42.3,
    'fdr_control_rate': 0.96
}

sample_config = {
    'n_tests': 500,
    'pi0': 0.9,
    'effect_size': 2.0,
    'alpha': 0.05,
    'n_reps': 100
}

print(generate_evaluation_report(sample_results, "ADDIS", sample_config))
```

## References

1. **Storey, J. D.** (2003). "The positive false discovery rate: a Bayesian interpretation and the q-value." *Annals of Statistics*, 31(6):2013-2035.

2. **Genovese, C., and L. Wasserman** (2002). "Operating characteristics and extensions of the false discovery rate procedure." *Journal of the Royal Statistical Society*, Series B, 64(3):499-517.

3. **Efron, B.** (2010). "Large-scale inference: empirical Bayes methods for estimation, testing, and prediction." Cambridge University Press.

4. **Yekutieli, D., and Y. Benjamini** (1999). "Resampling-based false discovery rate controlling multiple test procedures for correlated test statistics." *Journal of Statistical Planning and Inference*, 82(1-2):171-196.

## Next Steps

- **Apply evaluation techniques in [examples](../examples/comparison.md)**
- **Learn about [data generation](data_generation.md)** for simulation studies  
- **Explore [theory](../theory/guarantee_matrix.md)** for method-specific guarantee assumptions
