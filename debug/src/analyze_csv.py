#!/usr/bin/env python3
"""
CSV Pattern Analyzer for Score Following Debug Data

Analyzes the flattened CSV files to identify patterns that lead to no-match/mismatch scenarios.
Provides statistical analysis and pattern identification for debugging algorithm failures.
"""

import pandas as pd
import numpy as np
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
from tqdm import tqdm

# Optional matplotlib/seaborn for future plotting capabilities
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False

from utils import setup_logging

logger = setup_logging(__name__)


class CSVPatternAnalyzer:
    """Analyzes flattened CSV data to identify failure patterns."""
    
    def __init__(self, csv_file: Path):
        self.csv_file = csv_file
        self.df = None
        self.analysis_results = {}
        
    def load_data(self):
        """Load and validate CSV data."""
        logger.info(f"Loading CSV data from {self.csv_file}")
        
        if not self.csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_file}")
        
        # Get file size for progress estimation
        file_size = self.csv_file.stat().st_size
        logger.info(f"Loading CSV file ({file_size / 1024 / 1024:.1f} MB)...")
        
        # Load with progress indication for large files
        if file_size > 10 * 1024 * 1024:  # Show progress for files > 10MB
            # Count rows first for progress bar
            with open(self.csv_file, 'r') as f:
                total_rows = sum(1 for _ in f) - 1  # Subtract header
            
            # Load in chunks with progress bar
            chunk_size = 10000
            chunks = []
            with tqdm(total=total_rows, desc="Loading CSV", unit="rows", 
                     bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as pbar:
                for chunk in pd.read_csv(self.csv_file, chunksize=chunk_size):
                    chunks.append(chunk)
                    pbar.update(len(chunk))
            
            self.df = pd.concat(chunks, ignore_index=True)
        else:
            self.df = pd.read_csv(self.csv_file)
        
        logger.info(f"Loaded {len(self.df)} entries with {len(self.df.columns)} columns")
        
        # Basic validation
        required_columns = ['input_column', 'input_pitch', 'input_perf_time', 'dp_row', 'result_type', 'hrule_match_type']
        missing_columns = set(required_columns) - set(self.df.columns)
        if missing_columns:
            logger.warning(f"Missing expected columns: {missing_columns}")
        
        return self.df
    
    def analyze_failure_patterns(self) -> Dict[str, Any]:
        """Comprehensive analysis of failure patterns."""
        logger.info("Analyzing failure patterns")
        
        results = {}
        
        # Analysis steps with progress tracking
        analysis_steps = [
            ("Basic statistics", self._analyze_basic_stats),
            ("Result types", self._analyze_result_types),
            ("Match type patterns", self._analyze_match_types),
            ("Timing patterns", self._analyze_timing_patterns),
            ("Algorithm bugs", self._analyze_algorithm_bugs),
            ("Score patterns", self._analyze_score_patterns),
            ("Ornament patterns", self._analyze_ornament_patterns),
            ("Sequence patterns", self._analyze_failure_sequences)
        ]
        
        with tqdm(analysis_steps, desc="Analyzing patterns", unit="step") as pbar:
            for step_name, analysis_func in pbar:
                pbar.set_description(f"Analyzing {step_name}")
                step_key = step_name.replace(" ", "_").lower()
                results[step_key] = analysis_func()
        
        self.analysis_results = results
        return results
    
    def _analyze_basic_stats(self) -> Dict[str, Any]:
        """Basic statistical analysis."""
        stats = {
            'total_entries': len(self.df),
            'unique_columns': self.df['input_column'].nunique(),
            'unique_rows': self.df['dp_row'].nunique(),
            'time_range': {
                'min_perf_time': self.df['input_perf_time'].min(),
                'max_perf_time': self.df['input_perf_time'].max(),
                'duration': self.df['input_perf_time'].max() - self.df['input_perf_time'].min()
            },
            'pitch_range': {
                'min_pitch': self.df['input_pitch'].min(),
                'max_pitch': self.df['input_pitch'].max(),
                'unique_pitches': self.df['input_pitch'].nunique()
            }
        }
        return stats
    
    def _analyze_result_types(self) -> Dict[str, Any]:
        """Analyze distribution of result types."""
        result_counts = self.df['result_type'].value_counts()
        result_percentages = (result_counts / len(self.df) * 100).round(2)
        
        return {
            'counts': result_counts.to_dict(),
            'percentages': result_percentages.to_dict(),
            'no_match_rate': result_percentages.get('no_match', 0),
            'match_rate': result_percentages.get('match', 0)
        }
    
    def _analyze_match_types(self) -> Dict[str, Any]:
        """Analyze match type patterns for failures."""
        match_type_counts = self.df['hrule_match_type'].value_counts()
        
        # Analyze match types by result
        match_type_by_result = self.df.groupby(['result_type', 'hrule_match_type']).size().unstack(fill_value=0)
        
        # Find problematic match types
        no_match_df = self.df[self.df['result_type'] == 'no_match']
        problematic_types = no_match_df['hrule_match_type'].value_counts()
        
        return {
            'overall_distribution': match_type_counts.to_dict(),
            'by_result_type': match_type_by_result.to_dict(),
            'problematic_match_types': problematic_types.to_dict()
        }
    
    def _analyze_timing_patterns(self) -> Dict[str, Any]:
        """Analyze timing-related failure patterns."""
        # Filter out algorithm bugs for clean timing analysis
        clean_df = self.df[self.df['bug_has_timing_bug'] != True]
        
        timing_stats = {
            'ioi_stats': {
                'mean': clean_df['hrule_ioi'].mean(),
                'median': clean_df['hrule_ioi'].median(),
                'std': clean_df['hrule_ioi'].std(),
                'max': clean_df['hrule_ioi'].max(),
                'min': clean_df['hrule_ioi'].min()
            },
            'timing_failures': len(clean_df[clean_df['timing_pass'] == 'nil']),
            'timing_pass_rate': len(clean_df[clean_df['timing_pass'] == 't']) / len(clean_df) * 100
        }
        
        # Analyze timing failures by constraint type
        timing_failures = clean_df[clean_df['timing_pass'] == 'nil']
        if len(timing_failures) > 0:
            timing_stats['failure_by_constraint'] = timing_failures['timing_constraint_type'].value_counts().to_dict()
            timing_stats['failure_ioi_stats'] = {
                'mean': timing_failures['hrule_ioi'].mean(),
                'median': timing_failures['hrule_ioi'].median(),
                'max': timing_failures['hrule_ioi'].max()
            }
        
        return timing_stats
    
    def _analyze_algorithm_bugs(self) -> Dict[str, Any]:
        """Analyze algorithm bugs and their impact."""
        bug_entries = self.df[self.df['bug_has_timing_bug'] == True]
        
        return {
            'total_bug_entries': len(bug_entries),
            'bug_percentage': len(bug_entries) / len(self.df) * 100,
            'bug_impact_on_failures': len(bug_entries[bug_entries['result_type'] == 'no_match']) / len(bug_entries) * 100 if len(bug_entries) > 0 else 0,
            'bug_descriptions': bug_entries['bug_description'].value_counts().to_dict() if len(bug_entries) > 0 else {}
        }
    
    def _analyze_score_patterns(self) -> Dict[str, Any]:
        """Analyze score progression and competition patterns."""
        score_stats = {
            'final_value_stats': {
                'mean': self.df['dp_final_value'].mean(),
                'median': self.df['dp_final_value'].median(),
                'std': self.df['dp_final_value'].std()
            },
            'top_score_progression': {
                'mean': self.df['score_top_score'].mean(),
                'max': self.df['score_top_score'].max(),
                'final': self.df['score_top_score'].iloc[-1] if len(self.df) > 0 else 0
            },
            'beats_top_rate': len(self.df[self.df['score_beats_top'] == 't']) / len(self.df) * 100,
            'confidence_stats': {
                'mean': self.df['score_confidence'].mean(),
                'median': self.df['score_confidence'].median(),
                'low_confidence_rate': len(self.df[self.df['score_confidence'] < 0.5]) / len(self.df) * 100
            }
        }
        
        return score_stats
    
    def _analyze_ornament_patterns(self) -> Dict[str, Any]:
        """Analyze ornament-related patterns."""
        ornament_entries = self.df[self.df['cevent_ornament_count'] > 0]
        
        ornament_stats = {
            'entries_with_ornaments': len(ornament_entries),
            'ornament_percentage': len(ornament_entries) / len(self.df) * 100,
            'ornament_failure_rate': len(ornament_entries[ornament_entries['result_type'] == 'no_match']) / len(ornament_entries) * 100 if len(ornament_entries) > 0 else 0
        }
        
        # Analyze ornament types
        if len(ornament_entries) > 0:
            ornament_stats['ornament_types'] = ornament_entries['ornament_type'].value_counts().to_dict()
            ornament_stats['ornament_count_distribution'] = ornament_entries['cevent_ornament_count'].value_counts().to_dict()
        
        return ornament_stats
    
    def _analyze_failure_sequences(self) -> Dict[str, Any]:
        """Analyze sequences leading to failures."""
        # Group by column to analyze sequences
        sequences = []
        
        for column in self.df['input_column'].unique():
            column_data = self.df[self.df['input_column'] == column].sort_values('dp_row')
            
            # Find failures in this column
            failures = column_data[column_data['result_type'] == 'no_match']
            
            for _, failure in failures.iterrows():
                # Get preceding context (last 3 decisions before failure)
                preceding = column_data[column_data['dp_row'] < failure['dp_row']].tail(3)
                
                if len(preceding) > 0:
                    sequence = {
                        'failure_row': failure['dp_row'],
                        'failure_pitch': failure['input_pitch'],
                        'preceding_match_types': preceding['hrule_match_type'].tolist(),
                        'preceding_timing_pass': preceding['hrule_timing_pass'].tolist(),
                        'preceding_scores': preceding['dp_final_value'].tolist()
                    }
                    sequences.append(sequence)
        
        # Analyze common patterns in sequences
        pattern_analysis = {}
        if sequences:
            # Most common preceding match types
            all_preceding_types = []
            for seq in sequences:
                all_preceding_types.extend(seq['preceding_match_types'])
            
            if all_preceding_types:
                pattern_analysis['common_preceding_types'] = pd.Series(all_preceding_types).value_counts().to_dict()
            
            # Timing patterns before failures
            timing_before_failure = []
            for seq in sequences:
                timing_before_failure.extend(seq['preceding_timing_pass'])
            
            if timing_before_failure:
                pattern_analysis['timing_before_failure'] = pd.Series(timing_before_failure).value_counts().to_dict()
        
        return {
            'total_failure_sequences': len(sequences),
            'patterns': pattern_analysis
        }
    
    def generate_report(self, output_file: Optional[Path] = None) -> str:
        """Generate a comprehensive analysis report."""
        if not self.analysis_results:
            self.analyze_failure_patterns()
        
        report_lines = []
        report_lines.append("# Score Following Algorithm Failure Pattern Analysis")
        report_lines.append("="*60)
        report_lines.append(f"Data source: {self.csv_file}")
        report_lines.append(f"Analysis timestamp: {pd.Timestamp.now()}")
        report_lines.append("")
        
        # Basic Statistics
        basic = self.analysis_results['basic_stats']
        report_lines.append("## Basic Statistics")
        report_lines.append(f"Total entries: {basic['total_entries']:,}")
        report_lines.append(f"Performance duration: {basic['time_range']['duration']:.2f} seconds")
        report_lines.append(f"Pitch range: {basic['pitch_range']['min_pitch']}-{basic['pitch_range']['max_pitch']} ({basic['pitch_range']['unique_pitches']} unique)")
        report_lines.append("")
        
        # Result Types
        results = self.analysis_results['result_types']
        report_lines.append("## Result Type Analysis")
        report_lines.append(f"Match rate: {results['match_rate']:.1f}%")
        report_lines.append(f"No-match rate: {results['no_match_rate']:.1f}%")
        report_lines.append("Distribution:")
        for result_type, percentage in results['percentages'].items():
            report_lines.append(f"  {result_type}: {percentage:.1f}%")
        report_lines.append("")
        
        # Match Types
        match_types = self.analysis_results['match_types']
        report_lines.append("## Match Type Patterns")
        report_lines.append("Most problematic match types (leading to no-match):")
        for match_type, count in list(match_types['problematic_match_types'].items())[:5]:
            report_lines.append(f"  {match_type}: {count} failures")
        report_lines.append("")
        
        # Timing Analysis
        timing = self.analysis_results['timing_patterns']
        report_lines.append("## Timing Analysis")
        report_lines.append(f"Timing pass rate: {timing['timing_pass_rate']:.1f}%")
        report_lines.append(f"Mean IOI: {timing['ioi_stats']['mean']:.3f}s")
        report_lines.append(f"Max IOI: {timing['ioi_stats']['max']:.3f}s")
        if 'failure_by_constraint' in timing:
            report_lines.append("Timing failures by constraint type:")
            for constraint, count in timing['failure_by_constraint'].items():
                report_lines.append(f"  {constraint}: {count}")
        report_lines.append("")
        
        # Algorithm Bugs
        bugs = self.analysis_results['algorithm_bugs']
        report_lines.append("## Algorithm Bug Analysis")
        report_lines.append(f"Entries with timing bugs: {bugs['total_bug_entries']} ({bugs['bug_percentage']:.1f}%)")
        if bugs['total_bug_entries'] > 0:
            report_lines.append(f"Bug impact on failures: {bugs['bug_impact_on_failures']:.1f}%")
        report_lines.append("")
        
        # Ornament Analysis
        ornaments = self.analysis_results['ornament_patterns']
        report_lines.append("## Ornament Impact Analysis")
        report_lines.append(f"Entries with ornaments: {ornaments['entries_with_ornaments']} ({ornaments['ornament_percentage']:.1f}%)")
        if ornaments['entries_with_ornaments'] > 0:
            report_lines.append(f"Ornament failure rate: {ornaments['ornament_failure_rate']:.1f}%")
        report_lines.append("")
        
        # Key Findings
        report_lines.append("## Key Findings and Recommendations")
        findings = self._generate_key_findings()
        for finding in findings:
            report_lines.append(f"- {finding}")
        
        report_text = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            logger.info(f"Report saved to {output_file}")
        
        return report_text
    
    def _generate_key_findings(self) -> List[str]:
        """Generate key findings based on analysis."""
        findings = []
        
        results = self.analysis_results
        
        # High no-match rate
        if results['result_types']['no_match_rate'] > 20:
            findings.append(f"High no-match rate ({results['result_types']['no_match_rate']:.1f}%) indicates significant tracking issues")
        
        # Algorithm bugs
        if results['algorithm_bugs']['bug_percentage'] > 5:
            findings.append(f"Algorithm bugs present in {results['algorithm_bugs']['bug_percentage']:.1f}% of entries - fix Cell initialization (-1 time bug)")
        
        # Timing issues
        if results['timing_patterns']['timing_pass_rate'] < 80:
            findings.append(f"Low timing pass rate ({results['timing_patterns']['timing_pass_rate']:.1f}%) suggests timing constraints may be too strict")
        
        # Ornament impact
        if results['ornament_patterns']['ornament_failure_rate'] > results['result_types']['no_match_rate']:
            findings.append("Ornaments show higher failure rate than average - ornament handling needs improvement")
        
        # Score progression
        if results['score_patterns']['confidence_stats']['low_confidence_rate'] > 30:
            findings.append(f"High low-confidence rate ({results['score_patterns']['confidence_stats']['low_confidence_rate']:.1f}%) indicates uncertain matching")
        
        return findings


def main():
    """Main entry point for CSV analysis."""
    parser = argparse.ArgumentParser(description="Analyze flattened score following CSV data")
    parser.add_argument("csv_file", help="Path to flattened CSV file")
    parser.add_argument("--output", "-o", help="Output report file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    csv_file = Path(args.csv_file)
    if not csv_file.exists():
        logger.error(f"CSV file not found: {csv_file}")
        return 1
    
    # Create analyzer
    analyzer = CSVPatternAnalyzer(csv_file)
    
    try:
        # Load and analyze data
        analyzer.load_data()
        results = analyzer.analyze_failure_patterns()
        
        # Generate report
        output_file = Path(args.output) if args.output else csv_file.with_suffix('.analysis.md')
        report = analyzer.generate_report(output_file)
        
        print(report)
        print(f"\nDetailed analysis saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    import logging
    sys.exit(main())