# -*- coding: utf-8 -*-
"""Compile all excel files, remove duplicates, save master file"""

import pandas as pd
import glob
import os
from datetime import datetime

def convert_to_iso(date_str):
        """
        Convert from 'Minggu, 26 April 2026 | 16:15'
        to '2026-04-26 16:15:00'
        """

        if pd.isna(date_str) or not isinstance(date_str, str):
            return date_str
        
        try:
            # Split tanggal dan jam (dipisah oleh '|')
            date_part, time_part = date_str.split(' | ')

            # Pisahkan hari, tanggal, bulan, tahun
            parts = date_part.split(', ')
            day_month_year = parts[1].split(' ')
            day = day_month_year[0]
            month_name = day_month_year[1]
            year = day_month_year[2]

            # Konversi nama bulan ke angka
            month_map = {
                'Januari': '01', 'Februari': '02', 'Maret': '03',
                'April': '04', 'Mei': '05', 'Juni': '06',
                'Juli': '07', 'Agustus': '08', 'September': '09',
                'Oktober': '10', 'November': '11', 'Desember': '12'
            }
            month = month_map[month_name]

            # Format jam
            hour_minute = time_part.strip()

            # Gabungkan ke ISO format
            iso_date = f"{year}-{month}-{int(day):02d} {hour_minute}:00"
            return iso_date
        except Exception as e:
            return date_str

def compile_and_clean():
    # Cari semua file excel hasil scraping
    excel_files = glob.glob("Bisnis_*.xlsx")
    
    # Filter file master (jangan diikutkan)
    excel_files = [f for f in excel_files if "Bisnis_Master" not in f]
    
    if not excel_files:
        print("Tidak ada file Excel untuk digabung.")
        return
    
    print(f"Menemukan {len(excel_files)} file Excel")
    
    # Gabungkan semua file
    all_data = []
    for file in excel_files:
        try:
            df = pd.read_excel(file)
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
            #Konversi teks ke iso string
            df_master['Tanggal_Clean'] = df_master['Tanggal'].apply(convert_to_iso)

            #konversi iso string ke datetime
            df_master['Tanggal_Clean'] = pd.to_datetime(df_master['Tanggal_Clean'], errors='coerce')

            #sorting descending
            df_master = df_master.sort_values('Tanggal_Clean', ascending=False)

            #Delete tanggal clean
            df_master  df_master.drop(colums=['Tanggal_Clean'])
        except Exception as e:
            print(f"Can't sort date: {e}")

    # Simpan ke file master
    filename = "Bisnis_Master.xlsx"
    df_master.to_excel(filename, index=False)
    print(f"\nSelesai! {len(df_master)} artikel unik disimpan ke {filename}")
    
    # Juga simpan dengan timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    backup_filename = f"Bisnis_Master_{timestamp}.xlsx"
    df_master.to_excel(backup_filename, index=False)
    print(f"Backup: {backup_filename}")

if __name__ == "__main__":
    compile_and_clean()
