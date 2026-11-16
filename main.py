import json, os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stok.json")

stok_toko = [
    ["Indomie Goreng", 3500, 120, 87],
    ["Minyak Goreng", 18000, 24, 19],
    ["Gula", 17000, 30, 30],
    ["Kopi", 1500, 80, 41],
    ["Tepung", 13000, 20, 17],
]


def baca():
    try:
        with open(FILE) as f:
            return json.load(f)
    except Exception:
        return [b[:] for b in stok_toko]


def tulis(data):
    with open(FILE, "w") as f:
        json.dump(data, f)


def rp(x):
    return "Rp " + format(x, ",").replace(",", ".")


data = baca()

win = tk.Tk()
win.title("Stok Barang Toko")
win.geometry("720x460")
win.configure(bg="#e8e8e8")

# judul
atas = tk.Frame(win, bg="#2b4a6f")
atas.pack(fill="x")
tk.Label(atas, text="STOK BARANG TOKO", bg="#2b4a6f", fg="white",
         font=("Arial", 14, "bold"), pady=8).pack(side="left", padx=12)
info = tk.Label(atas, text="", bg="#2b4a6f", fg="white", font=("Arial", 10))
info.pack(side="right", padx=12)

# tabel
kol = ("nama", "harga", "masuk", "terjual", "sisa", "ket")
tabel = ttk.Treeview(win, columns=kol, show="headings", height=12)
for k, t, w in [("nama", "Nama Barang", 200), ("harga", "Harga", 90), ("masuk", "Masuk", 70),
                ("terjual", "Terjual", 70), ("sisa", "Sisa", 70), ("ket", "Keterangan", 120)]:
    tabel.heading(k, text=t)
    tabel.column(k, width=w, anchor="w" if k == "nama" else "center")
tabel.tag_configure("habis", background="#f6c9c9")
tabel.tag_configure("dikit", background="#fbeab8")
tabel.pack(fill="both", expand=True, padx=10, pady=(10, 4))


def isi():
    tabel.delete(*tabel.get_children())
    habis = 0
    for i, (n, h, m, t) in enumerate(data):
        s = m - t
        tag, ket = "", "ada"
        if s <= 0:
            tag, ket = "habis", "HABIS"
            habis += 1
        elif s <= 5:
            tag, ket = "dikit", "hampir habis"
        tabel.insert("", "end", iid=i, tags=(tag,), values=(n, rp(h), m, t, s, ket))
    uang = sum(b[1] * b[3] for b in data)
    info.config(text="%d barang | %d habis | terjual %s" % (len(data), habis, rp(uang)))


def dipilih():
    p = tabel.selection()
    if not p:
        messagebox.showinfo("Info", "Pilih barangnya dulu di tabel.")
        return None
    return int(p[0])


def jual():
    i = dipilih()
    if i is None:
        return
    b = data[i]
    n = simpledialog.askinteger("Jual", "Berapa %s yang terjual?" % b[0], minvalue=1, parent=win)
    if not n:
        return
    if n > b[2] - b[3]:
        messagebox.showerror("Gagal", "Stok tinggal %d." % (b[2] - b[3]))
        return
    b[3] += n
    tulis(data)
    isi()


def masuk():
    i = dipilih()
    if i is None:
        return
    n = simpledialog.askinteger("Stok masuk", "Berapa %s yang datang?" % data[i][0], minvalue=1, parent=win)
    if n:
        data[i][2] += n
        tulis(data)
        isi()


def baru():
    nama = simpledialog.askstring("Barang baru", "Nama barang:", parent=win)
    if not nama or not nama.strip():
        return
    harga = simpledialog.askinteger("Barang baru", "Harga jual (Rp):", minvalue=0, parent=win)
    if harga is None:
        return
    stok = simpledialog.askinteger("Barang baru", "Stok awal:", minvalue=0, parent=win)
    if stok is None:
        return
    data.append([nama.strip(), harga, stok, 0])
    tulis(data)
    isi()


def hapus():
    i = dipilih()
    if i is None:
        return
    if messagebox.askyesno("Hapus", "Hapus %s?" % data[i][0]):
        data.pop(i)
        tulis(data)
        isi()


# ===== TAMBAHAN (kode asli di atas tidak diubah) =====
from datetime import datetime

FOLDER = os.path.dirname(os.path.abspath(__file__))
FILE_JUAL = os.path.join(FOLDER, "penjualan.json")
FILE_KELUAR = os.path.join(FOLDER, "stok_keluar.json")
BATAS_MENIPIS = 5  # sama dengan batas "hampir habis" di tabel


def baca_log(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception:
        # file rusak: simpan sebagai cadangan supaya tidak tertimpa
        os.replace(path, path + ".rusak")
        return []


def tulis_log(path, catatan):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(catatan, f, indent=2, ensure_ascii=False)


def sekarang():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


log = baca_log(FILE_JUAL)            # catatan penjualan
log_keluar = baca_log(FILE_KELUAR)   # catatan stok keluar (rusak, kadaluarsa, dll)


# ---------- NOTIFIKASI STOK MENIPIS / HABIS ----------
def daftar_stok_rendah():
    habis, dikit = [], []
    for n, h, m, t in data:
        s = m - t
        if s <= 0:
            habis.append(n)
        elif s <= BATAS_MENIPIS:
            dikit.append("%s (sisa %d)" % (n, s))
    return habis, dikit


def peringatan_stok(i):
    # popup untuk satu barang, dipanggil setelah jual / stok keluar
    b = data[i]
    s = b[2] - b[3]
    if s <= 0:
        messagebox.showwarning("Stok HABIS", "%s sudah HABIS!" % b[0], parent=win)
    elif s <= BATAS_MENIPIS:
        messagebox.showwarning("Stok menipis", "%s hampir habis, sisa %d." % (b[0], s), parent=win)


def tampil_peringatan():
    habis, dikit = daftar_stok_rendah()
    if not habis and not dikit:
        messagebox.showinfo("Stok", "Semua stok masih aman.", parent=win)
        return
    teks = []
    if habis:
        teks.append("HABIS:\n- " + "\n- ".join(habis))
    if dikit:
        teks.append("HAMPIR HABIS:\n- " + "\n- ".join(dikit))
    messagebox.showwarning("Peringatan stok", "\n\n".join(teks), parent=win)


def cek_awal():
    # dipanggil sekali saat program dibuka
    habis, dikit = daftar_stok_rendah()
    if habis or dikit:
        tampil_peringatan()


# panel merah/oranye di atas tabel (klik untuk detail)
lbl_notif = tk.Label(win, text="", fg="white", font=("Arial", 10, "bold"), pady=4, cursor="hand2")
lbl_notif.bind("<Button-1>", lambda e: tampil_peringatan())

 
def perbarui_notif():
    habis, dikit = daftar_stok_rendah()
    if not habis and not dikit:
        lbl_notif.pack_forget()
        return
    bagian = []
    if habis:
        bagian.append("%d barang HABIS" % len(habis))
    if dikit:
        bagian.append("%d barang hampir habis" % len(dikit))
    lbl_notif.config(text="PERHATIAN: " + ", ".join(bagian) + "  (klik untuk detail)",
                     bg="#c0392b" if habis else "#d68910")
    lbl_notif.pack(fill="x", padx=10, pady=(8, 0), before=cari_frame)


# ---------- PENCARIAN BARANG ----------
cari_var = tk.StringVar()
cari_frame = tk.Frame(win, bg="#e8e8e8")
cari_frame.pack(fill="x", padx=10, pady=(8, 0), before=tabel)
tk.Label(cari_frame, text="Cari barang:", bg="#e8e8e8").pack(side="left")
tk.Entry(cari_frame, textvariable=cari_var, width=30).pack(side="left", padx=6)
tk.Button(cari_frame, text="Reset", command=lambda: cari_var.set("")).pack(side="left")
lbl_hasil = tk.Label(cari_frame, text="", bg="#e8e8e8", fg="#555555")
lbl_hasil.pack(side="right")


def saring():
    kata = cari_var.get().strip().lower()
    if not kata:
        lbl_hasil.config(text="")
        return
    for iid in tabel.get_children():
        if kata not in data[int(iid)][0].lower():
            tabel.delete(iid)
    lbl_hasil.config(text="%d barang ditemukan" % len(tabel.get_children()))


# bungkus isi() yang asli: setelah tabel diisi, terapkan pencarian + perbarui notifikasi
isi_asli = isi


def isi():
    isi_asli()
    saring()
    perbarui_notif()


cari_var.trace_add("write", lambda *a: isi())


# ---------- PENJUALAN (dicatat) ----------
# bungkus jual() yang asli supaya setiap penjualan ikut tercatat
jual_asli = jual


def jual():
    p = tabel.selection()
    if not p:
        jual_asli()
        return
    i = int(p[0])
    nama, harga, sebelum = data[i][0], data[i][1], data[i][3]
    jual_asli()
    n = data[i][3] - sebelum
    if n > 0:
        log.append({"waktu": sekarang(), "barang": nama, "jumlah": n,
                    "harga": harga, "total": n * harga})
        tulis_log(FILE_JUAL, log)
        peringatan_stok(i)


# ---------- STOK KELUAR ----------
def stok_keluar():
    i = dipilih()
    if i is None:
        return
    b = data[i]
    sisa = b[2] - b[3]
    if sisa <= 0:
        messagebox.showerror("Gagal", "Stok %s sudah habis." % b[0])
        return
    n = simpledialog.askinteger("Stok keluar", "Berapa %s yang keluar? (sisa %d)" % (b[0], sisa),
                                minvalue=1, parent=win)
    if not n:
        return
    if n > sisa:
        messagebox.showerror("Gagal", "Stok tinggal %d." % sisa)
        return
    alasan = simpledialog.askstring("Stok keluar", "Alasan (rusak, kadaluarsa, dipakai sendiri, dll):",
                                    initialvalue="Rusak", parent=win)
    if alasan is None:
        return
    b[2] -= n   # sisa berkurang, tapi tidak dihitung sebagai penjualan
    log_keluar.append({"waktu": sekarang(), "barang": b[0], "jumlah": n,
                       "alasan": alasan.strip() or "-"})
    tulis(data)
    tulis_log(FILE_KELUAR, log_keluar)
    isi()
    peringatan_stok(i)


# ---------- LAPORAN ----------
def buat_tabel(induk, kolom):
    wadah = tk.Frame(induk)
    wadah.pack(fill="both", expand=True)
    tv = ttk.Treeview(wadah, columns=[k[0] for k in kolom], show="headings")
    for k, t, w, a in kolom:
        tv.heading(k, text=t)
        tv.column(k, width=w, anchor=a)
    sb = ttk.Scrollbar(wadah, orient="vertical", command=tv.yview)
    tv.configure(yscrollcommand=sb.set)
    tv.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return tv


def hasil_penjualan():
    w = tk.Toplevel(win)
    w.title("Hasil Penjualan")
    w.geometry("660x470")
    w.configure(bg="#e8e8e8")

    atas_w = tk.Frame(w, bg="#e8e8e8")
    atas_w.pack(fill="x", padx=10, pady=(10, 4))
    tk.Label(atas_w, text="Periode:", bg="#e8e8e8").pack(side="left")
    periode = ttk.Combobox(atas_w, values=["Hari ini", "Semua"], state="readonly", width=12)
    periode.current(0)
    periode.pack(side="left", padx=6)

    ringkas = tk.Label(w, text="", bg="#e8e8e8", font=("Arial", 10, "bold"), anchor="w")
    ringkas.pack(fill="x", padx=10, pady=(2, 0))

    nb = ttk.Notebook(w)
    nb.pack(fill="both", expand=True, padx=10, pady=8)
    f1, f2, f3 = tk.Frame(nb), tk.Frame(nb), tk.Frame(nb)
    nb.add(f1, text="Per Barang")
    nb.add(f2, text="Riwayat Penjualan")
    nb.add(f3, text="Stok Keluar")

    t1 = buat_tabel(f1, [("nama", "Nama Barang", 240, "w"), ("jumlah", "Terjual", 100, "center"),
                         ("uang", "Pendapatan", 160, "center")])
    t2 = buat_tabel(f2, [("waktu", "Waktu", 150, "center"), ("nama", "Barang", 160, "w"),
                         ("jumlah", "Jumlah", 60, "center"), ("harga", "Harga", 90, "center"),
                         ("total", "Total", 100, "center")])
    t3 = buat_tabel(f3, [("waktu", "Waktu", 150, "center"), ("nama", "Barang", 180, "w"),
                         ("jumlah", "Jumlah", 70, "center"), ("alasan", "Alasan", 200, "w")])

    def refresh(*_):
        hari = datetime.now().strftime("%Y-%m-%d")
        semua = periode.get() == "Semua"
        rows = [x for x in log if semua or x["waktu"].startswith(hari)]
        keluar = [x for x in log_keluar if semua or x["waktu"].startswith(hari)]
        for tv in (t1, t2, t3):
            tv.delete(*tv.get_children())
        per = {}
        for x in rows:
            p = per.setdefault(x["barang"], [0, 0])
            p[0] += x["jumlah"]
            p[1] += x["total"]
        for nama, (j, u) in sorted(per.items(), key=lambda kv: -kv[1][1]):
            t1.insert("", "end", values=(nama, j, rp(u)))
        for x in reversed(rows):
            t2.insert("", "end", values=(x["waktu"], x["barang"], x["jumlah"],
                                         rp(x["harga"]), rp(x["total"])))
        for x in reversed(keluar):
            t3.insert("", "end", values=(x["waktu"], x["barang"], x["jumlah"], x["alasan"]))
        ringkas.config(text="%d transaksi | %d item terjual | Omzet %s | %d item keluar"
                       % (len(rows), sum(x["jumlah"] for x in rows),
                          rp(sum(x["total"] for x in rows)), sum(x["jumlah"] for x in keluar)))

    periode.bind("<<ComboboxSelected>>", refresh)
    refresh()
# ===== AKHIR TAMBAHAN =====


bawah = tk.Frame(win, bg="#e8e8e8")
bawah.pack(fill="x", padx=10, pady=(4, 10))
for teks, fn in [("Jual", jual), ("Stok Masuk", masuk), ("Barang Baru", baru), ("Hapus", hapus)]:
    tk.Button(bawah, text=teks, command=fn, width=12, pady=4).pack(side="left", padx=(0, 6))
tk.Button(bawah, text="Stok Keluar", command=stok_keluar, width=12, pady=4).pack(side="left", padx=(0, 6))  # TAMBAHAN
tk.Button(bawah, text="Hasil Penjualan", command=hasil_penjualan, width=16, pady=4,
          bg="#2b4a6f", fg="white").pack(side="right")  # TAMBAHAN
win.after(400, cek_awal)  # TAMBAHAN: popup peringatan saat program dibuka

tabel.bind("<Double-1>", lambda e: jual())
isi()
win.mainloop()