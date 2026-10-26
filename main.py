import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

# File data disimpan di folder yang sama dengan program ini
FILE_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stok_toko.json")

DATA_CONTOH = [
    {"nama": "Indomie Goreng", "harga": 3500,  "masuk": 120, "terjual": 87},
    {"nama": "Minyak Goreng",  "harga": 18000, "masuk": 24,  "terjual": 19},
    {"nama": "Gula",           "harga": 17000, "masuk": 30,  "terjual": 30},
    {"nama": "Kopi",           "harga": 1500,  "masuk": 80,  "terjual": 41},
    {"nama": "Tepung",         "harga": 13000, "masuk": 20,  "terjual": 17},
]

BATAS_MENIPIS = 5


# ---------- Data ----------
def muat_data():
    if os.path.exists(FILE_DATA):
        try:
            with open(FILE_DATA, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return [b.copy() for b in DATA_CONTOH]


def simpan_data(barang):
    with open(FILE_DATA, "w", encoding="utf-8") as f:
        json.dump(barang, f, indent=2, ensure_ascii=False)


def hitung_sisa(b):
    return b["masuk"] - b["terjual"]


def hitung_status(b):
    sisa = hitung_sisa(b)
    if sisa <= 0:
        return "HABIS"
    if sisa <= BATAS_MENIPIS:
        return "MENIPIS"
    return "AMAN"


def rupiah(angka):
    return "Rp " + f"{angka:,}".replace(",", ".")


# ---------- Aplikasi ----------
class AplikasiStok:
    def __init__(self, root):
        self.root = root
        self.barang = muat_data()
        self.var_jumlah = tk.StringVar(value="1")
        self.var_cari = tk.StringVar()
        self.var_pesan = tk.StringVar(value="Pilih barang di tabel, isi jumlah, lalu tekan Jual atau Tambah Stok.")

        root.title("Stok Toko")
        root.geometry("900x560")
        root.minsize(760, 480)

        self.buat_ringkasan()
        self.buat_tabel()
        self.buat_tombol()
        ttk.Label(root, textvariable=self.var_pesan, padding=(12, 6)).pack(fill="x")

        self.var_cari.trace_add("write", lambda *a: self.refresh())
        self.refresh()

    # ----- Tampilan -----
    def buat_ringkasan(self):
        bingkai = ttk.Frame(self.root, padding=(12, 12, 12, 4))
        bingkai.pack(fill="x")
        self.label_ringkasan = {}
        for kunci, judul in [("jenis", "Jenis barang"), ("sisa", "Total sisa"),
                             ("terjual", "Total terjual"), ("habis", "Barang habis")]:
            kotak = ttk.LabelFrame(bingkai, text=judul, padding=10)
            kotak.pack(side="left", expand=True, fill="x", padx=4)
            lbl = ttk.Label(kotak, text="0", font=("Arial", 20, "bold"))
            lbl.pack()
            self.label_ringkasan[kunci] = lbl

    def buat_tabel(self):
        atas = ttk.Frame(self.root, padding=(12, 8, 12, 0))
        atas.pack(fill="x")
        ttk.Label(atas, text="Cari barang:").pack(side="left")
        ttk.Entry(atas, textvariable=self.var_cari, width=28).pack(side="left", padx=6)

        bingkai = ttk.Frame(self.root, padding=(12, 8))
        bingkai.pack(fill="both", expand=True)

        kolom = ("nama", "harga", "masuk", "terjual", "sisa", "status")
        self.tabel = ttk.Treeview(bingkai, columns=kolom, show="headings", selectmode="browse")
        judul = {"nama": "Barang", "harga": "Harga", "masuk": "Masuk",
                 "terjual": "Terjual", "sisa": "Sisa", "status": "Status"}
        lebar = {"nama": 240, "harga": 120, "masuk": 90, "terjual": 90, "sisa": 90, "status": 100}
        for k in kolom:
            self.tabel.heading(k, text=judul[k])
            self.tabel.column(k, width=lebar[k], anchor="w" if k == "nama" else "center")

        self.tabel.tag_configure("HABIS", foreground="#c0392b")
        self.tabel.tag_configure("MENIPIS", foreground="#b9770e")
        self.tabel.tag_configure("AMAN", foreground="#1e8449")

        gulir = ttk.Scrollbar(bingkai, orient="vertical", command=self.tabel.yview)
        self.tabel.configure(yscrollcommand=gulir.set)
        self.tabel.pack(side="left", fill="both", expand=True)
        gulir.pack(side="right", fill="y")

    def buat_tombol(self):
        bingkai = ttk.Frame(self.root, padding=(12, 4))
        bingkai.pack(fill="x")
        ttk.Label(bingkai, text="Jumlah:").pack(side="left")
        ttk.Spinbox(bingkai, from_=1, to=100000, width=8, textvariable=self.var_jumlah).pack(side="left", padx=6)
        ttk.Button(bingkai, text="Jual", command=self.jual).pack(side="left", padx=4)
        ttk.Button(bingkai, text="Tambah Stok", command=self.tambah_stok).pack(side="left", padx=4)
        ttk.Button(bingkai, text="Hapus Barang", command=self.hapus_barang).pack(side="right", padx=4)
        ttk.Button(bingkai, text="+ Barang Baru", command=self.dialog_barang_baru).pack(side="right", padx=4)

    # ----- Isi tabel -----
    def refresh(self):
        terpilih = self.tabel.selection()
        kata = self.var_cari.get().strip().lower()

        self.tabel.delete(*self.tabel.get_children())
        for i, b in enumerate(self.barang):
            if kata and kata not in b["nama"].lower():
                continue
            st = hitung_status(b)
            self.tabel.insert("", "end", iid=str(i), tags=(st,), values=(
                b["nama"], rupiah(b["harga"]), b["masuk"], b["terjual"], hitung_sisa(b), st))

        if terpilih and self.tabel.exists(terpilih[0]):
            self.tabel.selection_set(terpilih[0])

        self.label_ringkasan["jenis"].config(text=str(len(self.barang)))
        self.label_ringkasan["sisa"].config(text=str(sum(max(0, hitung_sisa(b)) for b in self.barang)))
        self.label_ringkasan["terjual"].config(text=str(sum(b["terjual"] for b in self.barang)))
        self.label_ringkasan["habis"].config(text=str(sum(1 for b in self.barang if hitung_sisa(b) <= 0)))

    # ----- Bantu -----
    def barang_terpilih(self):
        pilih = self.tabel.selection()
        if not pilih:
            messagebox.showwarning("Pilih barang", "Klik salah satu barang di tabel dulu.")
            return None
        return int(pilih[0])

    def ambil_jumlah(self):
        try:
            jumlah = int(self.var_jumlah.get())
        except ValueError:
            jumlah = 0
        if jumlah < 1:
            messagebox.showwarning("Jumlah salah", "Isi jumlah berupa angka minimal 1.")
            return None
        return jumlah

    # ----- Fitur -----
    def jual(self):
        i = self.barang_terpilih()
        if i is None:
            return
        jumlah = self.ambil_jumlah()
        if jumlah is None:
            return
        b = self.barang[i]
        if jumlah > hitung_sisa(b):
            messagebox.showerror("Stok tidak cukup",
                                 f"Sisa {b['nama']} hanya {hitung_sisa(b)}.")
            return
        b["terjual"] += jumlah
        simpan_data(self.barang)
        self.refresh()
        self.var_pesan.set(f"Terjual {jumlah} {b['nama']}. Sisa sekarang {hitung_sisa(b)}.")

    def tambah_stok(self):
        i = self.barang_terpilih()
        if i is None:
            return
        jumlah = self.ambil_jumlah()
        if jumlah is None:
            return
        b = self.barang[i]
        b["masuk"] += jumlah
        simpan_data(self.barang)
        self.refresh()
        self.var_pesan.set(f"Stok masuk {jumlah} {b['nama']}. Sisa sekarang {hitung_sisa(b)}.")

    def hapus_barang(self):
        i = self.barang_terpilih()
        if i is None:
            return
        nama = self.barang[i]["nama"]
        if messagebox.askyesno("Hapus barang", f"Hapus {nama} dari daftar?"):
            self.barang.pop(i)
            simpan_data(self.barang)
            self.refresh()
            self.var_pesan.set(f"{nama} dihapus.")

    def dialog_barang_baru(self):
        jendela = tk.Toplevel(self.root)
        jendela.title("Barang Baru")
        jendela.resizable(False, False)
        jendela.transient(self.root)
        jendela.grab_set()

        isi = ttk.Frame(jendela, padding=16)
        isi.pack()
        entri = {}
        for baris, (kunci, judul) in enumerate([("nama", "Nama barang"),
                                                ("harga", "Harga jual (Rp)"),
                                                ("stok", "Stok awal")]):
            ttk.Label(isi, text=judul).grid(row=baris, column=0, sticky="w", pady=4)
            e = ttk.Entry(isi, width=26)
            e.grid(row=baris, column=1, padx=(10, 0), pady=4)
            entri[kunci] = e
        entri["nama"].focus()

        def simpan():
            nama = entri["nama"].get().strip()
            try:
                harga = int(entri["harga"].get())
                stok = int(entri["stok"].get())
            except ValueError:
                messagebox.showerror("Data salah", "Harga dan stok harus berupa angka.", parent=jendela)
                return
            if not nama or harga < 0 or stok < 0:
                messagebox.showerror("Data salah", "Isi nama, dan angka tidak boleh negatif.", parent=jendela)
                return
            self.barang.append({"nama": nama, "harga": harga, "masuk": stok, "terjual": 0})
            simpan_data(self.barang)
            self.refresh()
            self.var_pesan.set(f"{nama} ditambahkan dengan stok {stok}.")
            jendela.destroy()

        ttk.Button(isi, text="Simpan", command=simpan).grid(row=3, column=0, columnspan=2, pady=(12, 0), sticky="e")
        jendela.bind("<Return>", lambda e: simpan())


if __name__ == "__main__":
    root = tk.Tk()
    AplikasiStok(root)
    root.mainloop()