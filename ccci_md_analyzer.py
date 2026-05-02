import os
import sys
import re
import glob
from datetime import datetime

# Deine Liste bleibt gleich
DEVICE_FILES = [
    "/dev/ccci_md*",
    "/dev/ccci_md1_sta",
    "/dev/ccci_mdl_monitor",
    "/dev/ccci_md_log_ctrl",
    "/dev/ccci_mdx_sta",
    "/dev/ccci_md_post_dump",
]

# Schlüsselwörter für die verschiedenen Stacks
STACK_KEYWORDS = {
    "LTE/3GPP": [b"RRC", b"NAS", b"TAC", b"EARFCN", b"LTE"],
    "CDMA/3GPP2": [b"SID", b"NID", b"1xRTT", b"EvDo", b"MEID", b"CDMA"],
}


def get_msisdn():
    msisdn = ""
    msisdn_pattern = re.compile(r"^\+\d{1,15}$")
    while not msisdn_pattern.match(msisdn):
        msisdn = input("Bitte MSISDN im Format +4178... eingeben: ").strip()
    return msisdn


def collect_data_from_device(device_path, msisdn, output_dir="collected_data"):
    if not os.path.exists(device_path):
        return

    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = device_path.replace("/", "_").replace("*", "wildcard")
        output_filename = os.path.join(
            output_dir, f"msisdn_{msisdn[1:]}_{safe_name}_{timestamp}.txt"
        )

        print(f"--- Suche in '{device_path}' ---")

        with open(device_path, "rb") as infile, open(
            output_filename, "w", encoding="utf-8", errors="replace"
        ) as outfile:
            chunk_size = 4096
            while True:
                chunk = infile.read(chunk_size)
                if not chunk:
                    break

                # Keyword-Analyse
                for stack, keywords in STACK_KEYWORDS.items():
                    for kw in keywords:
                        if kw in chunk:
                            print(
                                f"  [!] {stack}-Signal entdeckt: {kw.decode()} in {device_path}"
                            )
                            outfile.write(chunk.decode("utf-8", errors="replace"))

        print(f"Fertig: {output_filename}\n")

    except OSError as e:
        if e.errno == 16:  # EBUSY
            print(
                f"Übersprungen: {device_path} wird gerade vom System (Modem) genutzt.\n"
            )
        else:
            print(f"Fehler bei {device_path}: {e}\n")


def main():
    print("--- CCCI MD Stack-Analyzer & Collector ---")
    if os.geteuid() != 0:
        print("Hinweis: Root-Rechte erforderlich.")

    msisdn = get_msisdn()

    actual_paths = []
    for pattern in DEVICE_FILES:
        actual_paths.extend(
            glob.glob(pattern) if "*" in pattern else [pattern]
        )

    for device in actual_paths:
        collect_data_from_device(device, msisdn)


if __name__ == "__main__":
    main()
