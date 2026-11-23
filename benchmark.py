"""Quick Sort performans karşılaştırması.

Proje ana klasöründen çalıştırın: python benchmark.py
"""
import platform
import random
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "src"
OUTPUT_DIR = ROOT / "results"
OUTPUT_DIR.mkdir(exist_ok=True)

SIZES = [10_000, 100_000, 1_000_000]
REPEATS = 5
RANDOM_SEED = 2026


def run_program(command, values, sample_memory=False):
    input_text = " ".join(map(str, values))
    proc = subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True
    )

    peak_rss = None
    if sample_memory and PSUTIL_AVAILABLE:
        process = psutil.Process(proc.pid)
        peak_rss = 0
        import threading
        stop_sampling = threading.Event()

        def sampler():
            nonlocal peak_rss
            while not stop_sampling.is_set():
                try:
                    peak_rss = max(peak_rss, process.memory_info().rss)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                stop_sampling.wait(0.005)

        thread = threading.Thread(target=sampler, daemon=True)
        thread.start()
    else:
        thread = None
        stop_sampling = None

    start = time.perf_counter()
    stdout, stderr = proc.communicate(input_text)
    elapsed = time.perf_counter() - start

    if thread is not None:
        stop_sampling.set()
        thread.join()

    if proc.returncode != 0:
        raise RuntimeError(f"Program hata verdi: {command}\n{stderr[-2000:]}")

    parts = stdout.strip().split()
    if len(parts) != 2:
        raise RuntimeError(f"Beklenmeyen çıktı: {stdout!r}")
    count, checksum = map(int, parts)
    return elapsed, count, checksum, peak_rss


def compile_programs():
    executables = {}

    ghc = shutil.which("ghc")
    if ghc:
        target = OUTPUT_DIR / "quicksort_hs"
        result = subprocess.run(
            [ghc, "-O2", str(SOURCE_DIR / "QuickSort.hs"), "-o", str(target)],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            executables["Haskell"] = [str(target)]
            print("Haskell derlendi.")
        else:
            print("Haskell derleme hatası:\n", result.stderr[-3000:])
    else:
        print("GHC bulunamadı; Haskell testi atlanacak.")

    compiler = shutil.which("g++") or shutil.which("clang++")
    if compiler:
        target = OUTPUT_DIR / "quicksort_cpp"
        result = subprocess.run(
            [compiler, "-O2", "-std=c++17", str(SOURCE_DIR / "quicksort.cpp"),
             "-o", str(target)],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            executables["C++"] = [str(target)]
            print("C++ derlendi:", compiler)
        else:
            print("C++ derleme hatası:\n", result.stderr[-3000:])
    else:
        print("C++ derleyicisi bulunamadı; C++ testi atlanacak.")

    executables["Python"] = [sys.executable, str(SOURCE_DIR / "quicksort.py")]
    return executables


def main():
    print("İşletim sistemi:", platform.platform())
    print("İşlemci:", platform.processor() or "Bilgi alınamadı")
    print("Python:", sys.version.split()[0])
    print("psutil bellek ölçümü:", "Açık" if PSUTIL_AVAILABLE else "Kapalı")

    executables = compile_programs()
    print("Çalıştırılabilir testler:", list(executables))

    test_values = [8, 3, 7, 4, 9, 2, 6, 4, 1, 5]
    expected = sorted(test_values)
    expected_check = (len(expected), sum(expected))

    for language, command in executables.items():
        _, count, checksum, _ = run_program(command, test_values)
        assert (count, checksum) == expected_check, f"{language} doğrulama başarısız"
        print(f"{language}: doğrulama başarılı")

    rng = random.Random(RANDOM_SEED)
    results = []

    for n in SIZES:
        values = [rng.randint(-1_000_000, 1_000_000) for _ in range(n)]
        expected_checksum = (n, sum(values))
        print(f"\nVeri boyutu: {n:,}")

        for language, command in executables.items():
            times = []
            memory_samples = []

            for _ in range(REPEATS):
                elapsed, count, checksum, peak_rss = run_program(
                    command, values, sample_memory=PSUTIL_AVAILABLE
                )
                if (count, checksum) != expected_checksum:
                    raise AssertionError(f"{language} sonucu doğrulanamadı.")
                times.append(elapsed)
                if peak_rss is not None:
                    memory_samples.append(peak_rss)

            results.append({
                "Dil": language,
                "Eleman Sayısı": n,
                "Ortalama Süre (s)": statistics.mean(times),
                "En İyi Süre (s)": min(times),
                "Süre Std. Sapma (s)": statistics.stdev(times) if len(times) > 1 else 0.0,
                "Ortalama Tepe RSS (MB)": (
                    statistics.mean(memory_samples) / (1024 * 1024)
                    if memory_samples else None
                ),
            })
            print(f"  {language}: ortalama {statistics.mean(times):.6f} saniye")

    try:
        import pandas as pd
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit("Sonuçları kaydetmek için pandas ve matplotlib kurun.") from exc

    frame = pd.DataFrame(results)
    csv_path = OUTPUT_DIR / "benchmark_results.csv"
    frame.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print("\nSonuç tablosu kaydedildi:", csv_path)

    pivot = frame.pivot(index="Eleman Sayısı", columns="Dil", values="Ortalama Süre (s)")
    ax = pivot.plot(kind="bar", figsize=(10, 5))
    ax.set_title("Quick Sort – Ortalama Çalışma Süresi")
    ax.set_xlabel("Eleman sayısı")
    ax.set_ylabel("Süre (saniye)")
    ax.set_yscale("log")
    ax.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=0)
    plt.tight_layout()
    chart_path = OUTPUT_DIR / "runtime_comparison.png"
    plt.savefig(chart_path, dpi=150)
    plt.close()
    print("Süre grafiği kaydedildi:", chart_path)

    if frame["Ortalama Tepe RSS (MB)"].notna().any():
        memory_pivot = frame.pivot(
            index="Eleman Sayısı", columns="Dil", values="Ortalama Tepe RSS (MB)"
        )
        ax = memory_pivot.plot(kind="bar", figsize=(10, 5))
        ax.set_title("Quick Sort – Ortalama Tepe Bellek Kullanımı")
        ax.set_xlabel("Eleman sayısı")
        ax.set_ylabel("Bellek (MB)")
        ax.grid(axis="y", alpha=0.3)
        plt.xticks(rotation=0)
        plt.tight_layout()
        memory_path = OUTPUT_DIR / "memory_comparison.png"
        plt.savefig(memory_path, dpi=150)
        plt.close()
        print("Bellek grafiği kaydedildi:", memory_path)
    else:
        print("Bellek grafiği oluşturulmadı (psutil yok veya ölçüm alınamadı).")


if __name__ == "__main__":
    main()
