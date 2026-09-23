import serial
import csv
from datetime import datetime
from pathlib import Path

SERIAL_PORT = "COM5"
BAUD_RATE = 115200

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

condition = input("Enter recording condition (rest/contraction): ").strip()
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = OUTPUT_DIRECTORY / f"emg_{condition}_{timestamp}.csv"


def read_parameter(line, parameter_name):
    prefix = f"{parameter_name}="

    if not line.startswith(prefix):
        raise ValueError(f"Expected {parameter_name}, received: {line}")

    return int(line[len(prefix) :])


def acquire_data():
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)

    try:
        sample_rate = read_parameter(
            arduino.readline().decode("utf-8").strip(), "SAMPLE_RATE_HZ"
        )

        total_samples = read_parameter(
            arduino.readline().decode("utf-8").strip(), "TOTAL_SAMPLES"
        )

        start_message = arduino.readline().decode("utf-8").strip()

        if start_message != "START":
            raise ValueError(f"Expected START, received: {start_message}")

        with open(output_file, "w", newline="") as file:
            writer = csv.writer(file)

            writer.writerow(["condition", condition])
            writer.writerow(["timestamp", timestamp])
            writer.writerow(["sample_rate_hz", sample_rate])
            writer.writerow(["total_samples", total_samples])
            writer.writerow([])

            writer.writerow(["sample", "adc_value"])

            for sample_number in range(total_samples):
                value = int(arduino.readline().decode("utf-8").strip())

                writer.writerow([sample_number, value])

        print(f"Sampling rate: {sample_rate} Hz")
        print(f"Samples acquired: {total_samples}")

    finally:
        arduino.close()


if __name__ == "__main__":
    acquire_data()
