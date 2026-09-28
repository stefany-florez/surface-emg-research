import csv
from pathlib import Path
from statistics import mean, stdev
import matplotlib.pyplot as plt

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIRECTORY = PROJECT_ROOT / "data" / "raw"
FIGURE_DIRECTORY = PROJECT_ROOT / "data" / "processed" / "figures"
FIGURE_DIRECTORY.mkdir(parents=True, exist_ok=True)

REST_FILE = DATA_DIRECTORY / "emg_rest_20260922_202220.csv"
CONTRACTION_FILE = DATA_DIRECTORY / "emg_contraction_20260922_202403.csv"


def load_emg_data(file_path):
    metadata = {}
    adc_values = []

    with open(file_path, "r", newline="") as file:
        reader = csv.reader(file)

        for row in reader:
            if not row:
                continue

            if row[0] == "sample":
                break

            key, value = row
            metadata[key] = value

        for row in reader:
            sample, adc_value = row

            adc_values.append(int(adc_value))

    metadata["sample_rate_hz"] = int(metadata["sample_rate_hz"])
    metadata["total_samples"] = int(metadata["total_samples"])

    if len(adc_values) != metadata["total_samples"]:
        raise ValueError(
            f"Expected {metadata['total_samples']} samples, "
            f"but found {len(adc_values)} in {file_path.name}."
        )

    return metadata, adc_values


def calculate_statistics(adc_values, sample_rate_hz):
    return {
        "samples": len(adc_values),
        "duration_s": len(adc_values) / sample_rate_hz,
        "minimum": min(adc_values),
        "maximum": max(adc_values),
        "mean": mean(adc_values),
        "standard_deviation": stdev(adc_values),
        "peak_to_peak": max(adc_values) - min(adc_values),
    }


def plot_recording(metadata, adc_values, output_file, start_time=0, end_time=None):
    sample_rate_hz = metadata["sample_rate_hz"]

    time_seconds = [
        sample_number / sample_rate_hz for sample_number in range(len(adc_values))
    ]

    plt.figure(figsize=(10, 4))
    plt.plot(time_seconds, adc_values)

    plt.xlabel("Time (s)")
    plt.ylabel("ADC value")
    plt.title(f"Raw EMG signal during {metadata['condition']}")

    if end_time is not None:
        plt.xlim(start_time, end_time)

    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()


def print_statistics(metadata, statistics):
    print(f"\nCondition: {metadata['condition']}")
    print("-" * 30)
    print(f"Timestamp:            {metadata['timestamp']}")
    print(f"Sampling rate:        {metadata['sample_rate_hz']} Hz")
    print(f"Expected samples:     {metadata['total_samples']}")
    print(f"Actual samples:       {statistics['samples']}")
    print(f"Duration:             {statistics['duration_s']:.2f} s")
    print(f"Minimum ADC value:    {statistics['minimum']}")
    print(f"Maximum ADC value:    {statistics['maximum']}")
    print(f"Mean ADC value:       {statistics['mean']:.2f}")
    print(f"Standard deviation:   {statistics['standard_deviation']:.2f}")
    print(f"Peak-to-peak:         {statistics['peak_to_peak']}")


def analyze_recording(file_path):
    metadata, adc_values = load_emg_data(file_path)

    timestamp = metadata["timestamp"]
    condition = metadata["condition"]

    statistics = calculate_statistics(
        adc_values,
        metadata["sample_rate_hz"],
    )

    print_statistics(metadata, statistics)

    full_file = FIGURE_DIRECTORY / f"emg_{condition}_{timestamp}_full.png"
    zoom_file = FIGURE_DIRECTORY / f"emg_{condition}_{timestamp}_100ms.png"

    plot_recording(metadata, adc_values, full_file)
    plot_recording(metadata, adc_values, zoom_file, end_time=0.1)


def main():
    analyze_recording(REST_FILE)
    analyze_recording(CONTRACTION_FILE)


if __name__ == "__main__":
    main()
