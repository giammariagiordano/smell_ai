import argparse
import logging
import os
from dotenv import load_dotenv
from data_preparation.repository_downloader import RepositoryDownloader
from data_preparation.function_dataset_builder import FunctionDatasetBuilder
from data_preparation.code_smell_analyzer import CodeSmellAnalyzer
from data_preparation.injected_smells_dataset_builder import (
    InjectedSmellsDatasetBuilder,
)
from data_preparation.balanced_dataset_builder import BalancedDatasetBuilder
from data_preparation.qwen_llm import QwenLLM
from data_preparation.code_smell_injector import CodeSmellInjector


def main(args):
    if args.step1:
        # Step 1: Download repositories from GitHub
        logging.info("Step 1: Downloading repositories...")
        load_dotenv()
        GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
        if not GITHUB_TOKEN:
            raise ValueError(
                "GITHUB_TOKEN is not set in the environment variables."
            )

        downloader = RepositoryDownloader(token=GITHUB_TOKEN)
        topics = [
            "machine-learning",
            "deep-learning",
            "data-science",
            "pandas",
            "tensorflow",
            "sklearn",
            "torch",
            "transformers",
        ]
        downloader.search_and_process_topics(
            topics=topics,
            max_repos_per_topic=20,
            stars=">=100",
            pushed=">2023-06-01",
            language="Python",
            download=True,
        )

    if args.step2:
        # Step 2: Extract functions from downloaded repositories
        logging.info("Step 2: Extracting functions from repositories...")
        repo_path = "datasets/raw"
        function_builder = FunctionDatasetBuilder(repo_path=repo_path)
        function_dataset = function_builder.build_dataset()
        function_builder.save_dataset(
            function_dataset, "datasets/function_extracted.json"
        )

    if args.step3:
        # Step 3: Analyze functions for code smells
        logging.info("Step 3: Analyzing functions for code smells...")
        dataset_path = "datasets/function_extracted.json"
        output_analysis_dir = "datasets/output_analysis"
        analyzer = CodeSmellAnalyzer(
            dataset_path=dataset_path,
            output_dir=output_analysis_dir,
            max_workers=16,
        )
        analyzer.run()

    if args.step4:
        # Step 4: Inject code smells into clean functions
        logging.info("Step 4: Injecting code smells into clean functions...")
        llm_model = QwenLLM()
        injector = CodeSmellInjector(llm_model, max_smells=1)
        injected_builder = InjectedSmellsDatasetBuilder(
            injector=injector,
            checkpoint_path="datasets/output_analysis/checkpoint.json",
            output_path="datasets/output_analysis/injected_functions.json",
            input_path="datasets/output_analysis/clean_functions.json",
        )
        injected_builder.process_dataset()

    if args.step5:
        # Step 5: Build unified and balanced datasets
        logging.info("Step 5: Building balanced datasets...")
        clean_path = "datasets/output_analysis/clean_functions.json"
        smelly_path = "datasets/output_analysis/smelly_functions.json"
        injected_path = "datasets/output_analysis/injected_functions.json"
        output_path = "datasets/unified_balanced_dataset.json"
        balanced_builder = BalancedDatasetBuilder(
            clean_path=clean_path,
            smelly_path=smelly_path,
            injected_path=injected_path,
            output_path=output_path,
        )

        # Full dataset with smelly and injected functions
        balanced_builder.build_full_dataset(
            target_clean=14000, target_per_smell=700, max_injected=12000
        )

        # Injected-only dataset
        balanced_builder.build_injected_only_dataset(
            max_clean=10000, max_injected=10000
        )

    logging.info("Selected steps completed successfully!")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Argument parser
    parser = argparse.ArgumentParser(
        description="Run selective steps of the tool."
    )
    parser.add_argument(
        "--step1",
        action="store_true",
        help="Run step 1: Download repositories from GitHub.",
    )
    parser.add_argument(
        "--step2",
        action="store_true",
        help="Run step 2: Extract functions from repositories.",
    )
    parser.add_argument(
        "--step3",
        action="store_true",
        help="Run step 3: Analyze functions for code smells.",
    )
    parser.add_argument(
        "--step4",
        action="store_true",
        help="Run step 4: Inject code smells into clean functions.",
    )
    parser.add_argument(
        "--step5",
        action="store_true",
        help="Run step 5: Build unified and balanced datasets.",
    )

    args = parser.parse_args()
    main(args)
