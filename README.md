# Quick Sort Ödevi

Quick Sort algoritmasının Haskell, C++ ve Python uygulamalarının performans karşılaştırması.

## Dosya yapısı

- `quick_sort_odev.ipynb`: Yalnızca açıklama ve rapor metni; çalıştırılabilir kod hücresi içermez.
- `benchmark.py`: Derleme, doğruluk kontrolü, performans ölçümü ve grafik üretimi.
- `src/QuickSort.hs`: Haskell kaynak kodu.
- `src/quicksort.cpp`: C++ kaynak kodu.
- `src/quicksort.py`: Python kaynak kodu.
- `results/`: Çalıştırma sonrasında oluşan CSV ve grafikler.

## Gereksinimler

- Python 3
- `pandas`, `matplotlib`
- İsteğe bağlı bellek ölçümü için `psutil`
- Haskell testi için GHC
- C++ testi için `g++` veya `clang++`

Paketleri kurmak için: `pip install pandas matplotlib psutil`

## Çalıştırma

Proje ana klasöründe `python benchmark.py` komutunu çalıştırın. Sonuçlar `results` klasörüne kaydedilir.
