import tkinter as tk
from tkinter import messagebox, filedialog
import math
import os
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from fpdf import FPDF

hasil_tes = {}

def penentuan_kategori(prestasi, tempo, konsistensi, ketahanan):
    kat_prestasi = "Kurang" if prestasi < 500 else "Cukup" if prestasi <= 700 else "Baik"
    kat_tempo = "Rendah" if tempo < 15 else "Sedang" if tempo <= 22 else "Cepat"
    kat_konsistensi = "Sedang" if konsistensi < 3.0 else "Buruk" # Semakin kecil nilai, semakin konsisten
    kat_ketahanan = "Sedang" if -0.5 <= ketahanan <= 0.5 else "Baik" if ketahanan > 0.5 else "Buruk"
    
    return kat_prestasi, kat_tempo, kat_konsistensi, kat_ketahanan

def hitung_statistik():
    input_text = entry_data.get()
    input_ketelitian = entry_ketelitian.get()
    
    try:
        data = [int(x) for x in input_text.strip().split()]
        ketelitian = int(input_ketelitian) if input_ketelitian else 0

        prestasi = sum(data)
        tempo = prestasi / len(data)
        variance = sum((x - tempo) ** 2 for x in data) / len(data)
        konsistensi = math.sqrt(variance)
        
        n = len(data)
        if n < 2:
            messagebox.showerror("Error", "Data harus berisi setidaknya 2 nilai untuk menghitung ketahanan.")
            return
        sum_x = sum(range(1, n + 1))
        sum_y = sum(data)
        sum_xy = sum((i + 1) * data[i] for i in range(n))
        sum_xx = sum((i + 1) ** 2 for i in range(n))
        ketahanan = ((n * sum_xy) - (sum_x * sum_y)) / ((n * sum_xx) - (sum_x ** 2))

        
        kat_pres, kat_temp, kat_kon, kat_ket = penentuan_kategori(prestasi, tempo, konsistensi, ketahanan)

       
        global hasil_tes
        hasil_tes = {
            "prestasi": prestasi, "tempo": tempo, "konsistensi": konsistensi,
            "ketahanan": ketahanan, "ketelitian": ketelitian,
            "min": min(data), "max": max(data),
            "kat_prestasi": kat_pres, "kat_tempo": kat_temp,
            "kat_konsistensi": kat_kon, "kat_ketahanan": kat_ket,
            "nama": entry_nama.get().strip(),
            "posisi": entry_posisi.get().strip(),
            "perusahaan": entry_perusahaan.get().strip(),
            "tanggal": entry_tanggal.get().strip()
        }

        
        lbl_hasil.config(text=(
            f"Prestasi: {prestasi} ({kat_pres}) | Tempo: {tempo:.2f} ({kat_temp})\n"
            f"Konsistensi: {konsistensi:.4f} ({kat_kon}) | Ketahanan: {ketahanan:.5f} ({kat_ket})\n"
            f"Ketelitian: {ketelitian} | Min: {min(data)} | Max: {max(data)}"
        ))

        
        #Render Grafik
        ax.clear()
        ax.plot(range(1, n + 1), data, marker='o', color='#c0392b', linestyle='-', markersize=5)
        ax.set_title(f"Prestasi Kerja Tiap 30 Detik (Total: {n} Sesi)", fontsize=10)
        ax.set_xlim(1, 50)
        ax.set_xticks(range(1, 51))
        ax.tick_params(axis='x', labelsize=7) 
        ax.set_ylim(0, 50)               
        ax.set_yticks(range(0, 51, 5))  
        ax.grid(True, linestyle='--', alpha=0.5)
        for i, val in enumerate(data):
            ax.annotate(str(val), (i + 1, val), textcoords="offset points", xytext=(0,5), ha='center', fontsize=7)
        
        
        fig.savefig("temp_grafik.png", dpi=150, bbox_inches='tight')
        canvas.draw()
        
        
        btn_pdf.config(state=tk.NORMAL)

    except ValueError:
        messagebox.showerror("Error", "Pastikan input grafik berisi angka dipisahkan spasi, dan ketelitian berisi angka!")

def ekspor_pdf():
    if not hasil_tes:
        messagebox.showwarning("Peringatan", "Silakan generate laporan terlebih dahulu!")
        return

    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf", 
        filetypes=[("PDF files", "*.pdf")],
        title="Simpan Laporan Tes"
    )
    
    if not file_path:
        return

    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=11)
        waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf.image("temp_grafik.png", x=10, y=25, w=190)

        #Data Peserta 
        pdf.set_y(120)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 12, "DATA PESERTA", ln=True)
        pdf.set_font("Arial", size=10)
        label_w = 35
        pdf.cell(label_w, 6, "Nama", border=0)
        pdf.cell(0, 6, f": {hasil_tes['nama']}", ln=True)
        pdf.cell(label_w, 6, "Posisi", border=0)
        pdf.cell(0, 6, f": {hasil_tes['posisi']}", ln=True)
        pdf.cell(label_w, 6, "Perusahaan", border=0)
        pdf.cell(0, 6, f": {hasil_tes['perusahaan']}", ln=True)
        pdf.cell(label_w, 6, "Tanggal Ujian", border=0)
        pdf.cell(0, 6, f": {hasil_tes['tanggal']}", ln=True)

        pdf.set_y(170)
        col1, col2, col3 = 80, 50, 60
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(col1, 8, "Aspek", border=1)
        pdf.cell(col2, 8, "Nilai", border=1)
        pdf.cell(col3, 8, "Kategori", border=1, ln=True)
        pdf.set_font("Arial", size=10)
        
        data_tabel = [
            ("Jumlah (Prestasi Kerja)", str(hasil_tes['prestasi']), hasil_tes['kat_prestasi']),
            ("Rata-rata (Tempo Kerja)", f"{hasil_tes['tempo']:.2f}", hasil_tes['kat_tempo']),
            ("Ketelitian", str(hasil_tes['ketelitian']), "Sangat Buruk" if hasil_tes['ketelitian'] > 20 else "Baik"),
            ("Konsistensi", f"{hasil_tes['konsistensi']:.4f}", hasil_tes['kat_konsistensi']),
            ("Ketahanan", f"{hasil_tes['ketahanan']:.5f}", hasil_tes['kat_ketahanan']),
            ("Nilai Minimal", str(hasil_tes['min']), ""),
            ("Nilai Maksimal", str(hasil_tes['max']), "")
        ]
        
        for item in data_tabel:
            pdf.cell(col1, 8, item[0], border=1)
            pdf.cell(col2, 8, item[1], border=1)
            pdf.cell(col3, 8, item[2], border=1, ln=True)
            
        
        pdf.output(file_path)
        
        
        if os.path.exists("temp_grafik.png"):
            os.remove("temp_grafik.png")
            
        messagebox.showinfo("Sukses", f"Laporan PDF berhasil disimpan di:\n{file_path}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Gagal membuat PDF:\n{str(e)}")

#ui
root = tk.Tk()
root.title("Evaluator Kraepelin Internal HR - PDF Ready")
root.geometry("850x650")

frame_top = tk.Frame(root, pady=10)
frame_top.pack(fill=tk.X)

#Baris 0 - Identitas Peserta
frame_identitas = tk.Frame(frame_top)
frame_identitas.pack(pady=5)

tk.Label(frame_identitas, text="Nama:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="e", padx=5, pady=2)
entry_nama = tk.Entry(frame_identitas, width=30)
entry_nama.grid(row=0, column=1, padx=5, pady=2)

tk.Label(frame_identitas, text="Posisi:", font=("Arial", 9, "bold")).grid(row=0, column=2, sticky="e", padx=5, pady=2)
entry_posisi = tk.Entry(frame_identitas, width=30)
entry_posisi.grid(row=0, column=3, padx=5, pady=2)

tk.Label(frame_identitas, text="Perusahaan:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky="e", padx=5, pady=2)
entry_perusahaan = tk.Entry(frame_identitas, width=30)
entry_perusahaan.grid(row=1, column=1, padx=5, pady=2)

tk.Label(frame_identitas, text="Tanggal Ujian:", font=("Arial", 9, "bold")).grid(row=1, column=2, sticky="e", padx=5, pady=2)
entry_tanggal = tk.Entry(frame_identitas, width=30)
entry_tanggal.grid(row=1, column=3, padx=5, pady=2)

#Baris 1
tk.Label(frame_top, text="Masukkan 50 Nilai Puncak (Spasi):", font=("Arial", 9, "bold")).pack()
entry_data = tk.Entry(frame_top, width=100)
entry_data.pack(pady=3)
entry_data.insert(0, "6 11 6 8 8 9 9 8 6 6 4 5 4 6 7 4 8 7 10 7 7 5 6 8 5 11 8 9 10 8 7 10 5 10 7 7 8 5 5 11 11 8 6 6 7 8 10 10 8 7")

#Baris 2
tk.Label(frame_top, text="Jumlah Kesalahan/Terlewat (Ketelitian):", font=("Arial", 9, "bold")).pack()
entry_ketelitian = tk.Entry(frame_top, width=20)
entry_ketelitian.pack(pady=3)
entry_ketelitian.insert(0, "26")
#Baris 3
frame_btn = tk.Frame(frame_top)
frame_btn.pack(pady=5)
tk.Button(frame_btn, text="Generate Laporan", command=hitung_statistik, bg="#3498db", fg="white", width=20).pack(side=tk.LEFT, padx=10)
btn_pdf = tk.Button(frame_btn, text="Simpan PDF Laporan", command=ekspor_pdf, bg="#2ecc71", fg="white", width=20, state=tk.DISABLED)
btn_pdf.pack(side=tk.LEFT, padx=10)
lbl_hasil = tk.Label(root, text="Hasil statistik akan muncul di sini.", font=("Consolas", 10), bg="#f0f0f0", relief="sunken", padx=10, pady=10)
lbl_hasil.pack(fill=tk.X, padx=20, pady=5)
fig = Figure(figsize=(8, 3.5), dpi=100)
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

root.mainloop()