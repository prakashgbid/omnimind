#!/usr/bin/env python3
"""
Performance monitoring and profiling tools for OSA.

This module provides tools for monitoring performance, detecting
bottlenecks, and generating performance reports.
"""

import time
import psutil
import threading
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
import functools


@dataclass
class PerformanceMetric:
    """Represents a performance metric measurement."""
    
    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceReport:
    """Performance analysis report."""
    
    duration: float
    metrics: List[PerformanceMetric]
    bottlenecks: List[str]
    recommendations: List[str]
    summary: Dict[str, Any]


class PerformanceMonitor:
    """Real-time performance monitoring for OSA operations."""
    
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.start_time: Optional[float] = None
        
    def start_monitoring(self) -> None:
        """Start real-time performance monitoring."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.start_time = time.time()
        self.monitor_thread = threading.Thread(target=self._monitor_system)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logging.info("Performance monitoring started")
    
    def stop_monitoring(self) -> PerformanceReport:
        """Stop monitoring and generate report."""
        if not self.is_monitoring:
            raise RuntimeError("Monitoring not active")
        
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        
        duration = time.time() - (self.start_time or 0)
        report = self._generate_report(duration)
        
        logging.info(f"Performance monitoring stopped (duration: {duration:.2f}s)")
        return report
    
    def _monitor_system(self) -> None:
        """Monitor system resources in background thread."""
        while self.is_monitoring:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.metrics.append(PerformanceMetric(
                    name="cpu_usage",
                    value=cpu_percent,
                    unit="percent"
                ))
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.metrics.append(PerformanceMetric(
                    name="memory_usage",
                    value=memory.percent,
                    unit="percent"
                ))
                
                # Available memory
                self.metrics.append(PerformanceMetric(
                    name="memory_available",
                    value=memory.available / (1024**3),  # GB
                    unit="GB"
                ))
                
                # Disk I/O
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    self.metrics.append(PerformanceMetric(
                        name="disk_read_bytes",
                        value=disk_io.read_bytes / (1024**2),  # MB
                        unit="MB"
                    ))
                    self.metrics.append(PerformanceMetric(
                        name="disk_write_bytes", 
                        value=disk_io.write_bytes / (1024**2),  # MB
                        unit="MB"
                    ))
                
                # Network I/O
                net_io = psutil.net_io_counters()
                if net_io:
                    self.metrics.append(PerformanceMetric(
                        name="network_sent",
                        value=net_io.bytes_sent / (1024**2),  # MB
                        unit="MB"
                    ))
                    self.metrics.append(PerformanceMetric(
                        name="network_recv",
                        value=net_io.bytes_recv / (1024**2),  # MB
                        unit="MB"
                    ))
                
                time.sleep(1)  # Monitor every second
                
            except Exception as e:
                logging.error(f"Error in performance monitoring: {e}")
    
    def _generate_report(self, duration: float) -> PerformanceReport:
        """Generate performance analysis report."""
        bottlenecks = []
        recommendations = []
        
        # Analyze metrics for bottlenecks
        cpu_metrics = [m for m in self.metrics if m.name == "cpu_usage"]
        if cpu_metrics:
            avg_cpu = sum(m.value for m in cpu_metrics) / len(cpu_metrics)
            max_cpu = max(m.value for m in cpu_metrics)
            
            if avg_cpu > 80:
                bottlenecks.append(f"High average CPU usage: {avg_cpu:.1f}%")
                recommendations.append("Consider optimizing CPU-intensive operations")
            
            if max_cpu > 95:
                bottlenecks.append(f"CPU usage spike detected: {max_cpu:.1f}%")
                recommendations.append("Investigate CPU spikes and add rate limiting")
        
        # Memory analysis
        memory_metrics = [m for m in self.metrics if m.name == "memory_usage"]
        if memory_metrics:
            avg_memory = sum(m.value for m in memory_metrics) / len(memory_metrics)
            max_memory = max(m.value for m in memory_metrics)
            
            if avg_memory > 80:
                bottlenecks.append(f"High memory usage: {avg_memory:.1f}%")
                recommendations.append("Consider memory optimization and garbage collection")
            
            if max_memory > 90:
                bottlenecks.append(f"Memory usage critical: {max_memory:.1f}%")
                recommendations.append("Implement memory limits and monitoring")
        
        # Generate summary
        summary = {
            "duration": duration,
            "total_metrics": len(self.metrics),
            "avg_cpu": sum(m.value for m in cpu_metrics) / len(cpu_metrics) if cpu_metrics else 0,
            "avg_memory": sum(m.value for m in memory_metrics) / len(memory_metrics) if memory_metrics else 0,
            "bottlenecks_found": len(bottlenecks),
        }
        
        return PerformanceReport(
            duration=duration,
            metrics=self.metrics.copy(),
            bottlenecks=bottlenecks,
            recommendations=recommendations,
            summary=summary
        )
    
    def export_metrics(self, filepath: str) -> None:
        """Export metrics to JSON file."""
        data = {
            "metrics": [
                {
                    "name": m.name,
                    "value": m.value,
                    "unit": m.unit,
                    "timestamp": m.timestamp.isoformat(),
                    "metadata": m.metadata
                }
                for m in self.metrics
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


class PerformanceProfiler:
    """Code profiling utilities for OSA functions."""
    
    @staticmethod
    def profile_function(func: Callable) -> Callable:
        """Decorator to profile function execution time."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            logging.info(f"Function '{func.__name__}' took {execution_time:.4f} seconds")
            
            return result
        
        return wrapper
    
    @staticmethod
    def profile_async_function(func: Callable) -> Callable:
        """Decorator to profile async function execution time."""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = await func(*args, **kwargs)
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            logging.info(f"Async function '{func.__name__}' took {execution_time:.4f} seconds")
            
            return result
        
        return wrapper


class MemoryProfiler:
    """Memory usage profiling for OSA operations."""
    
    def __init__(self):
        self.snapshots: List[Dict[str, Any]] = []
    
    def take_snapshot(self, label: str = "") -> None:
        """Take a memory usage snapshot."""
        memory = psutil.virtual_memory()
        process = psutil.Process()
        
        snapshot = {
            "label": label,
            "timestamp": datetime.now().isoformat(),
            "system_memory": {
                "total": memory.total / (1024**3),  # GB
                "available": memory.available / (1024**3),  # GB
                "used": memory.used / (1024**3),  # GB
                "percent": memory.percent
            },
            "process_memory": {
                "rss": process.memory_info().rss / (1024**2),  # MB
                "vms": process.memory_info().vms / (1024**2),  # MB
                "percent": process.memory_percent()
            }
        }
        
        self.snapshots.append(snapshot)
        logging.info(f"Memory snapshot taken: {label}")
    
    def analyze_memory_usage(self) -> Dict[str, Any]:
        """Analyze memory usage patterns."""
        if len(self.snapshots) < 2:
            return {"error": "Need at least 2 snapshots for analysis"}
        
        first = self.snapshots[0]
        last = self.snapshots[-1]
        
        memory_growth = (
            last["process_memory"]["rss"] - first["process_memory"]["rss"]
        )
        
        max_memory = max(s["process_memory"]["rss"] for s in self.snapshots)
        min_memory = min(s["process_memory"]["rss"] for s in self.snapshots)
        
        analysis = {
            "memory_growth_mb": memory_growth,
            "max_memory_mb": max_memory,
            "min_memory_mb": min_memory,
            "memory_range_mb": max_memory - min_memory,
            "snapshots_analyzed": len(self.snapshots),
            "potential_leak": memory_growth > 100,  # >100MB growth
        }
        
        if analysis["potential_leak"]:
            analysis["leak_warning"] = (
                f"Potential memory leak detected: {memory_growth:.1f}MB growth"
            )
        
        return analysis
    
    def export_snapshots(self, filepath: str) -> None:
        """Export memory snapshots to file."""
        with open(filepath, 'w') as f:
            json.dump(self.snapshots, f, indent=2)


class BenchmarkRunner:
    """Run performance benchmarks for OSA components."""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
    
    async def benchmark_thinking_speed(self, osa_instance, iterations: int = 10) -> Dict[str, Any]:
        """Benchmark thinking engine performance."""
        times = []
        
        for i in range(iterations):
            start = time.perf_counter()
            await osa_instance.generate_thought(f"Test thought {i}")
            end = time.perf_counter()
            times.append(end - start)
        
        result = {
            "benchmark": "thinking_speed",
            "iterations": iterations,
            "avg_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "total_time": sum(times),
            "thoughts_per_second": iterations / sum(times)
        }
        
        self.results.append(result)
        return result
    
    async def benchmark_memory_usage(self, osa_instance, complexity_levels: List[str]) -> Dict[str, Any]:
        """Benchmark memory usage across different complexity levels."""
        profiler = MemoryProfiler()
        results = {}
        
        for level in complexity_levels:
            profiler.take_snapshot(f"before_{level}")
            
            # Simulate workload
            if level == "simple":
                await osa_instance.think_about("Simple math problem")
            elif level == "medium":
                await osa_instance.think_about("Medium complexity algorithm")
            elif level == "complex":
                await osa_instance.think_about("Complex system design problem")
            
            profiler.take_snapshot(f"after_{level}")
        
        analysis = profiler.analyze_memory_usage()
        
        result = {
            "benchmark": "memory_usage",
            "complexity_levels": complexity_levels,
            "analysis": analysis,
            "snapshots": profiler.snapshots
        }
        
        self.results.append(result)
        return result
    
    def generate_benchmark_report(self) -> str:
        """Generate comprehensive benchmark report."""
        if not self.results:
            return "No benchmark results available"
        
        report = ["# OSA Performance Benchmark Report\n"]
        report.append(f"Generated: {datetime.now().isoformat()}\n")
        
        for result in self.results:
            report.append(f"## {result['benchmark'].replace('_', ' ').title()}\n")
            
            if result['benchmark'] == 'thinking_speed':
                report.append(f"- **Average time per thought**: {result['avg_time']:.4f}s")
                report.append(f"- **Thoughts per second**: {result['thoughts_per_second']:.2f}")
                report.append(f"- **Min/Max time**: {result['min_time']:.4f}s / {result['max_time']:.4f}s")
            
            elif result['benchmark'] == 'memory_usage':
                analysis = result['analysis']
                report.append(f"- **Memory growth**: {analysis['memory_growth_mb']:.1f} MB")
                report.append(f"- **Peak memory**: {analysis['max_memory_mb']:.1f} MB")
                
                if analysis['potential_leak']:
                    report.append(f"- **⚠️ Warning**: {analysis['leak_warning']}")
            
            report.append("\n")
        
        return "\n".join(report)
    
    def export_results(self, filepath: str) -> None:
        """Export benchmark results to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)


def main():
    """Main entry point for performance monitoring."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OSA Performance Monitor")
    parser.add_argument("--monitor", action="store_true", help="Start system monitoring")
    parser.add_argument("--duration", type=int, default=60, help="Monitoring duration (seconds)")
    parser.add_argument("--output", help="Output file for results")
    
    args = parser.parse_args()
    
    if args.monitor:
        print("🔍 Starting performance monitoring...")
        
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        try:
            time.sleep(args.duration)
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring interrupted by user")
        
        report = monitor.stop_monitoring()
        
        print(f"\n📊 Performance Report:")
        print(f"Duration: {report.duration:.2f}s")
        print(f"Metrics collected: {len(report.metrics)}")
        print(f"Bottlenecks found: {len(report.bottlenecks)}")
        
        for bottleneck in report.bottlenecks:
            print(f"  ⚠️ {bottleneck}")
        
        for recommendation in report.recommendations:
            print(f"  💡 {recommendation}")
        
        if args.output:
            monitor.export_metrics(args.output)
            print(f"📁 Results exported to {args.output}")


if __name__ == "__main__":
    main()