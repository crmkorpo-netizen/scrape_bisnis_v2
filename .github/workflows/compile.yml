# -*- coding: utf-8 -*-
"""Compile all CSV files, remove duplicates, save master file"""

import pandas as pd
import glob
import os
from datetime import datetime

def compile_and_clean():
    # Cari semua file CSV hasil scraping
    csv_files = glob.glob("Bisnis_*.csv")
    
    # Filter file master (jangan diikutkan)
    csv_files = [f for f in csv_files if "Bisnis_Master" not in f]
    
    if not csv_files:
        print("Tidak ada file CSV untuk digabung.")
        return
    
    print(f"Menemukan {len(csv_files)} file CSV")
    
    # Gabungkan semua file
    all_data = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            print(f"   - {file}: {len(df)} baris")
            all_data.append(df)
        except Exception as e:
            print(f"Error baca {file}: {e}")
    
    if not all_data:
        print("Tidak ada data yang bisa digabung.")
        return
    
    # Gabungkan semua DataFrame
    df_master = pd.concat(all_data, ignore_index=True)
    print(f"\nTotal sebelum hapus duplikat: {len(df_master)} baris")
    
    df_master['Source'] = "Bisnis"
    df_master["Crawled Date"] = datetime.now().isoformat(sep=' ', timespec='seconds')

    # Hapus duplikat berdasarkan Link (pertahankan yang pertama muncul)
    before = len(df_master)
    df_master = df_master.drop_duplicates(subset=['Link'], keep='first')
    after = len(df_master)
    print(f"Hapus duplikat: {before - after} baris terhapus")
    
    # Sortir berdasarkan tanggal (jika kolom Tanggal ada)
    if 'Tanggal' in df_master.columns:
        try:
            df_master['Tanggal'] = pd.to_datetime(df_master['Tanggal'], errors='coerce')
            df_master = df_master.sort_values('Tanggal', ascending=False)
            print(f"Data diurutkan berdasarkan tanggal (terbaru ke terbaru?)")
        except Exception as e:
            print(f"Tidak bisa sortir tanggal: {e}")
    
    # Simpan ke file master
    filename = "Bisnis_Master.csv"
    df_master.to_csv(filename, index=False)
    print(f"\nSelesai! {len(df_master)} artikel unik disimpan ke {filename}")
    
    # Juga simpan dengan timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    backup_filename = f"Bisnis_Master_{timestamp}.csv"
    df_master.to_csv(backup_filename, index=False)
    print(f"Backup: {backup_filename}")

if __name__ == "__main__":
    compile_and_clean()
