import numpy as np
import os
import json
import time
from sklearn.metrics import f1_score, mean_squared_error
from fuzzy_system import FuzzyAcademicRiskSystem
from config import Config

class RealCodedGeneticAlgorithm:
    """
    Real-Coded Genetic Algorithm (RCGA) for Fuzzy Membership Function Optimization.
    Optimizes continuous membership function parameters to minimize RMSE and maximize F1-score on training data.
    """
    def __init__(self,
                 pop_size=30,
                 generations=25,
                 crossover_rate=0.8,
                 mutation_rate=0.15,
                 elite_count=2,
                 random_seed=42):
        self.pop_size = pop_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elite_count = elite_count
        self.random_seed = random_seed
        
        np.random.seed(random_seed)
        self.base_fuzzy = FuzzyAcademicRiskSystem()
        self.initial_chromosome, self.meta = self.base_fuzzy.export_parameters_vector()
        self.chromosome_length = len(self.initial_chromosome)
        
        self.best_chromosome = None
        self.best_fitness = -1.0
        self.history = {
            'generations': [],
            'best_fitness': [],
            'avg_fitness': [],
            'best_rmse': [],
            'best_f1': []
        }

    def _initialize_population(self):
        """Initializes population around baseline chromosome with bounded Gaussian noise."""
        population = []
        # Include baseline chromosome as index 0
        population.append(self.initial_chromosome.copy())
        
        for _ in range(1, self.pop_size):
            # Perturb initial chromosome by ~10%
            noise = np.random.normal(0, 0.08, size=self.chromosome_length)
            chrom = np.clip(self.initial_chromosome + noise, 0.0, 1.0)
            population.append(chrom)
            
        return np.array(population)

    def evaluate_fitness(self, chromosome, X_sample, y_sample_score, y_sample_cat):
        """
        Evaluates a chromosome on a training sample.
        Fitness = 0.5 * (100.0 / (100.0 + RMSE)) + 0.5 * F1_macro
        """
        eval_fuzzy = FuzzyAcademicRiskSystem()
        eval_fuzzy.import_parameters_vector(chromosome, self.meta)
        
        # Fast batch prediction
        pred_scores = eval_fuzzy.evaluate_batch(X_sample)
        
        # RMSE calculation
        rmse = np.sqrt(mean_squared_error(y_sample_score, pred_scores))
        rmse_fitness = 100.0 / (100.0 + rmse)
        
        # Map predicted continuous scores to risk categories (0-4)
        pred_cats = np.zeros(len(pred_scores), dtype=int)
        pred_cats[pred_scores <= 20.0] = 0
        pred_cats[(pred_scores > 20.0) & (pred_scores <= 40.0)] = 1
        pred_cats[(pred_scores > 40.0) & (pred_scores <= 60.0)] = 2
        pred_cats[(pred_scores > 60.0) & (pred_scores <= 80.0)] = 3
        pred_cats[pred_scores > 80.0] = 4
        
        f1 = f1_score(y_sample_cat, pred_cats, average='macro', zero_division=0)
        
        combined_fitness = 0.6 * f1 + 0.4 * rmse_fitness
        return combined_fitness, rmse, f1

    def _tournament_selection(self, population, fitnesses, k=3):
        """Selects parent using tournament selection."""
        selected_idx = np.random.choice(len(population), size=k, replace=False)
        best_idx = selected_idx[np.argmax(fitnesses[selected_idx])]
        return population[best_idx].copy()

    def _blend_crossover(self, parent1, parent2, alpha=0.5):
        """BLX-alpha real-coded crossover."""
        if np.random.rand() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
            
        child1 = np.zeros_like(parent1)
        child2 = np.zeros_like(parent2)
        
        for i in range(len(parent1)):
            x1, x2 = min(parent1[i], parent2[i]), max(parent1[i], parent2[i])
            diff = x2 - x1
            low = max(0.0, x1 - alpha * diff)
            high = min(1.0, x2 + alpha * diff)
            if high > low:
                child1[i] = np.random.uniform(low, high)
                child2[i] = np.random.uniform(low, high)
            else:
                child1[i], child2[i] = x1, x2
                
        return child1, child2

    def _gaussian_mutation(self, chromosome):
        """Applies Gaussian mutation to genes with probability mutation_rate."""
        mutated = chromosome.copy()
        for i in range(len(mutated)):
            if np.random.rand() < self.mutation_rate:
                mutation_val = np.random.normal(0, 0.05)
                mutated[i] = np.clip(mutated[i] + mutation_val, 0.0, 1.0)
        return mutated

    def optimize(self, X_train, y_train_score, y_train_cat, sample_size=1500):
        """
        Runs the RCGA optimization over training data.
        Uses a random sample per generation for fast convergence.
        """
        start_time = time.time()
        population = self._initialize_population()
        
        for gen in range(1, self.generations + 1):
            # Subsample training set for evaluation efficiency
            if len(X_train) > sample_size:
                idx = np.random.choice(len(X_train), size=sample_size, replace=False)
                X_sub = X_train.iloc[idx].reset_index(drop=True)
                y_sub_score = y_train_score.iloc[idx].reset_index(drop=True)
                y_sub_cat = y_train_cat.iloc[idx].reset_index(drop=True)
            else:
                X_sub, y_sub_score, y_sub_cat = X_train, y_train_score, y_train_cat
                
            # Evaluate population fitness
            fitnesses = []
            rmses = []
            f1s = []
            
            for chrom in population:
                fit, rmse, f1 = self.evaluate_fitness(chrom, X_sub, y_sub_score, y_sub_cat)
                fitnesses.append(fit)
                rmses.append(rmse)
                f1s.append(f1)
                
            fitnesses = np.array(fitnesses)
            
            # Identify best in generation
            best_gen_idx = np.argmax(fitnesses)
            best_gen_fit = fitnesses[best_gen_idx]
            
            if best_gen_fit > self.best_fitness:
                self.best_fitness = best_gen_fit
                self.best_chromosome = population[best_gen_idx].copy()
                
            # Log metrics
            self.history['generations'].append(gen)
            self.history['best_fitness'].append(round(float(best_gen_fit), 4))
            self.history['avg_fitness'].append(round(float(np.mean(fitnesses)), 4))
            self.history['best_rmse'].append(round(float(rmses[best_gen_idx]), 4))
            self.history['best_f1'].append(round(float(f1s[best_gen_idx]), 4))
            
            # Elitism: retain top elite_count individuals
            sorted_indices = np.argsort(fitnesses)[::-1]
            new_population = [population[i].copy() for i in sorted_indices[:self.elite_count]]
            
            # Generate offspring
            while len(new_population) < self.pop_size:
                p1 = self._tournament_selection(population, fitnesses)
                p2 = self._tournament_selection(population, fitnesses)
                c1, c2 = self._blend_crossover(p1, p2)
                c1 = self._gaussian_mutation(c1)
                c2 = self._gaussian_mutation(c2)
                new_population.append(c1)
                if len(new_population) < self.pop_size:
                    new_population.append(c2)
                    
            population = np.array(new_population)
            
        elapsed = round(time.time() - start_time, 2)
        
        # Save best parameters to optimized_parameters.json
        opt_fuzzy = FuzzyAcademicRiskSystem()
        opt_fuzzy.import_parameters_vector(self.best_chromosome, self.meta)
        opt_fuzzy.save_parameters()
        
        return {
            'elapsed_seconds': elapsed,
            'generations': self.generations,
            'pop_size': self.pop_size,
            'best_fitness': round(float(self.best_fitness), 4),
            'final_rmse': self.history['best_rmse'][-1],
            'final_f1': self.history['best_f1'][-1],
            'history': self.history
        }
