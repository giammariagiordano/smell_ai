import os
import re
import json
from matplotlib import pyplot as plt
import numpy as np
from components.inspector import Inspector
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class DatasetEvaluator:
    def __init__(self, dataset_path, output_path):
        self.dataset = self.load_dataset(dataset_path)
        self.output_path = output_path

        self.inspector = Inspector(
            output_path=output_path,
            dataframe_dict_path="obj_dictionaries/dataframes.csv",
            model_dict_path="obj_dictionaries/models.csv",
            tensor_dict_path="obj_dictionaries/tensors.csv",
        )
        self.temp_dir = "temp_files"
        os.makedirs(self.temp_dir, exist_ok=True)

    def load_smell_definitions(self, path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def load_dataset(self, path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def extract_python_code(self, input_string):
        pattern = r"```python\s+(.*?)```"
        matches = re.findall(pattern, input_string, re.DOTALL)
        python_code = "\n".join(matches) if matches else input_string
        python_code = re.sub(r"#.*", "", python_code)
        python_code = re.sub(r"'''(.*?)'''", "", python_code, flags=re.DOTALL)
        python_code = re.sub(r'"""(.*?)"""', "", python_code, flags=re.DOTALL)
        python_code = "\n".join(
            [line for line in python_code.splitlines() if line.strip()]
        )
        return python_code

    def is_valid_syntax_using_inspector(self, code):
        extracted_code = self.extract_python_code(code)
        temp_file = os.path.join(self.temp_dir, "temp_code.py")
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(extracted_code)

        try:
            self.inspector.inspect(temp_file)
            return True
        except SyntaxError:
            return False
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def exclude_invalid_syntax(self):
        valid_entries = []
        invalid_entries = []
        for entry in self.dataset:
            code = entry["code"]
            if self.is_valid_syntax_using_inspector(code):
                valid_entries.append(entry)
            else:
                invalid_entries.append(entry)
        return valid_entries, invalid_entries

    def save_invalid_entries(self, invalid_entries):
        with open(
            os.path.join(self.output_path, "invalid_entries.json"),
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(invalid_entries, file, indent=4)

    def compute_code_similarity(self, dataset):
        """
        Calcola la similarità tra i blocchi di codice
        usando TF-IDF e cosine similarity.
        """
        corpus = [entry["code"] for entry in dataset]
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(corpus)
        similarity_matrix = cosine_similarity(tfidf_matrix)
        similarity_matrix = np.clip(similarity_matrix, 0, 1)
        return similarity_matrix

    def analyze_code_similarity(self, similarity_matrix, threshold=0.8):
        """
        Analizza la similarità tra i blocchi di codice
        e identifica quelli simili.
        """
        similar_blocks = []
        for i in range(len(similarity_matrix)):
            for j in range(i + 1, len(similarity_matrix)):
                if similarity_matrix[i, j] > threshold:
                    similar_blocks.append((i, j))
        return similar_blocks

    def compute_similarity_distribution(self, similarity_matrix):
        """
        Calcola la distribuzione delle similarità.
        Ritorna statistiche e un array con tutte le similarità.
        """
        # Estraggo tutte le similarità (triangolo superiore della matrice)
        similarities = similarity_matrix[np.triu_indices(
            len(similarity_matrix), k=1)]

        # Calcolo statistiche
        stats = {
            "mean": float(np.mean(similarities)),
            "median": float(np.median(similarities)),
            "std_dev": float(np.std(similarities)),
            "max": float(np.max(similarities)),
            "min": float(np.min(similarities)),
        }
        return stats, similarities.tolist()

    def plot_similarity_distribution(self, similarity_matrix):
        """
        Traccia un istogramma per visualizzare
        la distribuzione delle similarità.
        """
        # Appiattisci la matrice per considerare
        # solo i valori superiori alla diagonale
        upper_triangle_values = similarity_matrix[np.triu_indices_from(
            similarity_matrix, k=1)]

        # Traccia l'istogramma
        plt.figure(figsize=(10, 6))
        plt.hist(upper_triangle_values,
                 bins=30,
                 color='blue',
                 alpha=0.7,
                 edgecolor='black')
        plt.title('Distribuzione delle Similarità tra Blocchi di Codice',
                  fontsize=14)
        plt.xlabel('Similarità (Cosine Similarity)', fontsize=12)
        plt.ylabel('Frequenza', fontsize=12)
        plt.grid(axis='y', alpha=0.75)

        # Salva o mostra l'istogramma
        output_file = os.path.join(self.output_path,
                                   'similarity_distribution.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.show()

        print(f"Istogramma salvato in: {output_file}")

    def process_and_save_results(self):
        valid_entries, invalid_entries = self.exclude_invalid_syntax()
        self.save_invalid_entries(invalid_entries)

        excluded_percentage = (
            (len(invalid_entries) / len(self.dataset)) * 100
            if len(self.dataset) > 0
            else 0
        )
        print(
            f"""Percentuale di blocchi esclusi per errore di sintassi:
            {excluded_percentage:.2f}%"""
        )

        with open(
            os.path.join(self.output_path, "valid_entries.json"), "w",
            encoding="utf-8"
        ) as file:
            json.dump(valid_entries, file, indent=4)

        # Calcolo della similarità TF-IDF
        print("Calcolo della similarità tra i blocchi di codice...")
        similarity_matrix = self.compute_code_similarity(valid_entries)

        # Analisi dei blocchi di codice simili
        similar_threshold = 0.8  # Soglia per la similarità
        similar_blocks = self.analyze_code_similarity(
            similarity_matrix, similar_threshold
        )

        # Calcolo della distribuzione della similarità
        similarity_stats, similarity_distribution = (
            self.compute_similarity_distribution(similarity_matrix)
        )

        # Statistiche sulla similarità
        num_similar_pairs = len(similar_blocks)
        total_blocks = len(valid_entries)
        total_pairs = (total_blocks * (total_blocks - 1)) / 2
        percentage_similar = (
            (num_similar_pairs / total_pairs) * 100 if total_pairs > 0 else 0
        )

        print(f"Numero di coppie possibili: {total_pairs}")
        print(f"Numero di coppie simili: {num_similar_pairs}")
        print(
            f"""Percentuale di coppie simili rispetto al totale
              delle coppie possibili: {percentage_similar:.2f}%"""
        )
        print(f"Statistiche della distribuzione: {similarity_stats}")

        # Salvataggio dei risultati della similarità
        similarity_results = {
            "similar_blocks": similar_blocks,
            "percentage_similar": percentage_similar,
            "distribution_stats": similarity_stats,
            "similarity_distribution": similarity_distribution,
        }
        with open(
            os.path.join(self.output_path, "similarity_results.json"),
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(similarity_results, file, indent=4)

        # Traccia l'istogramma della distribuzione
        self.plot_similarity_distribution(similarity_matrix)


def main():
    # Percorsi di input e output
    dataset_path = "datasets/injected.json"
    output_path = "C:/Users/Xzeni/Desktop/results"

    # Inizializzazione e valutazione
    evaluator = DatasetEvaluator(
        dataset_path=dataset_path, output_path=output_path)
    evaluator.process_and_save_results()


if __name__ == "__main__":
    main()
