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
FILE_KAS = os.path.join(FOLDER, "kas.json")
FILE_SATUAN = os.path.join(FOLDER, "satuan.json")
FILE_SESI = os.path.join(FOLDER, "sesi.json")
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


def rp_tanda(x):
    return ("+" if x >= 0 else "-") + rp(abs(x))


log = baca_log(FILE_JUAL)            # catatan penjualan
log_keluar = baca_log(FILE_KELUAR)   # catatan stok keluar (rusak, kadaluarsa, dll)


# ---------- SATUAN PER BARANG (dus, karung, dll) ----------
# disimpan di satuan.json (terpisah dari stok.json) supaya data stok aslimu tidak berubah:
#   {"Indomie Goreng": {"s": "pcs", "u": "dus", "i": 40}}   artinya 1 dus = 40 pcs
# stok tetap dihitung dalam satuan terkecil (pcs); dus hanya untuk memudahkan input dan tampilan
def baca_satuan():
    try:
        with open(FILE_SATUAN, encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except FileNotFoundError:
        return {}
    except Exception:
        os.replace(FILE_SATUAN, FILE_SATUAN + ".rusak")
        return {}


satuan = baca_satuan()


def tulis_satuan():
    with open(FILE_SATUAN, "w", encoding="utf-8") as f:
        json.dump(satuan, f, indent=2, ensure_ascii=False)


def info_satuan(nama):
    return satuan.get(nama) or {"s": "pcs", "u": "", "i": 0}


def punya_dus(nama):
    s = info_satuan(nama)
    return bool(s["u"]) and s["i"] > 1


def faktor(nama, unit):
    # berapa satuan terkecil dalam 1 "unit" yang dipilih (dus = isi per dus, pcs = 1)
    return info_satuan(nama)["i"] if punya_dus(nama) and unit == info_satuan(nama)["u"] else 1


def fmt_stok(nama, x):
    # 113 -> "2 dus 33 pcs" (kalau barang punya dus), selain itu "113 pcs"
    s = info_satuan(nama)
    if punya_dus(nama) and x >= s["i"]:
        dus, sisa = divmod(x, s["i"])
        return "%d %s" % (dus, s["u"]) + (" %d %s" % (sisa, s["s"]) if sisa else "")
    return "%d %s" % (x, s["s"])


def angka(teks):
    try:
        return int(str(teks).replace(".", "").replace(",", "").strip())
    except ValueError:
        return None


def form(judul, kolom, tombol="OK"):
    # dialog dengan beberapa isian. kolom = [(label, nilai_awal, daftar_pilihan_atau_None)]
    # hasil: list isian (teks), atau None kalau dibatalkan
    d = tk.Toplevel(win)
    d.title(judul)
    d.transient(win)
    d.resizable(False, False)
    d.configure(bg="#e8e8e8", padx=14, pady=10)
    kotak = []
    for label, awal, pilihan in kolom:
        tk.Label(d, text=label, bg="#e8e8e8", anchor="w", justify="left").pack(fill="x", pady=(6, 0))
        if pilihan:
            w = ttk.Combobox(d, values=pilihan, state="readonly", width=38)
            w.set(awal)
        else:
            w = tk.Entry(d, width=40)
            w.insert(0, awal)
        w.pack(fill="x")
        kotak.append(w)
    hasil = {"v": None}

    def ok(*_):
        hasil["v"] = [w.get() for w in kotak]
        d.destroy()

    bar = tk.Frame(d, bg="#e8e8e8")
    bar.pack(fill="x", pady=(12, 0))
    tk.Button(bar, text="Batal", width=10, command=d.destroy).pack(side="right")
    tk.Button(bar, text=tombol, width=10, command=ok).pack(side="right", padx=6)
    d.bind("<Return>", ok)
    d.bind("<Escape>", lambda e: d.destroy())
    kotak[0].focus_set()
    d.wait_visibility()
    d.grab_set()
    win.wait_window(d)
    return hasil["v"]


# ---------- UANG YANG DIMILIKI (KAS) ----------
def baca_kas():
    try:
        with open(FILE_KAS, encoding="utf-8") as f:
            d = json.load(f)
        return {"saldo": int(d.get("saldo", 0)), "riwayat": d.get("riwayat", [])}
    except FileNotFoundError:
        return {"saldo": 0, "riwayat": []}
    except Exception:
        os.replace(FILE_KAS, FILE_KAS + ".rusak")
        return {"saldo": 0, "riwayat": []}


kas = baca_kas()


def simpan_kas():
    with open(FILE_KAS, "w", encoding="utf-8") as f:
        json.dump(kas, f, indent=2, ensure_ascii=False)


def perbarui_kas():
    lbl_kas.config(text="Uang dimiliki: " + rp(kas["saldo"]))


def ubah_kas(jumlah, ket):
    # jumlah positif = uang masuk, negatif = uang keluar
    kas["saldo"] += jumlah
    kas["riwayat"].append({"waktu": sekarang(), "ket": ket, "jumlah": jumlah, "saldo": kas["saldo"]})
    simpan_kas()
    perbarui_kas()


def cukup_uang(total):
    if total > kas["saldo"]:
        messagebox.showerror("Uang tidak cukup",
                             "Uang dimiliki %s, butuh %s.\nPenambahan stok dibatalkan."
                             % (rp(kas["saldo"]), rp(total)), parent=win)
        return False
    return True


def tambah_kas():
    n = simpledialog.askinteger("Tambah uang", "Jumlah uang yang ditambahkan (Rp):", minvalue=1, parent=win)
    if n:
        ubah_kas(n, "Tambah uang")


def atur_kas():
    s = simpledialog.askinteger("Atur saldo", "Uang yang dimiliki sekarang (Rp):", minvalue=0,
                                initialvalue=kas["saldo"], parent=win)
    if s is None:
        return
    if s != kas["saldo"]:
        ubah_kas(s - kas["saldo"], "Atur saldo")


def awal():
    # dipanggil sekali saat program dibuka: tanya saldo awal (kalau belum pernah), lalu cek stok
    if not os.path.exists(FILE_KAS):
        s = simpledialog.askinteger("Uang dimiliki", "Masukkan uang yang kamu miliki saat ini (Rp):",
                                    minvalue=0, parent=win)
        if s is not None:
            kas["saldo"] = s
            kas["riwayat"].append({"waktu": sekarang(), "ket": "Saldo awal", "jumlah": s, "saldo": s})
            simpan_kas()
            perbarui_kas()
    cek_awal()


# ---------- NOTIFIKASI STOK MENIPIS / HABIS ----------
def daftar_stok_rendah():
    habis, dikit = [], []
    for n, h, m, t in data:
        s = m - t
        if s <= 0:
            habis.append(n)
        elif s <= BATAS_MENIPIS:
            dikit.append("%s (sisa %s)" % (n, fmt_stok(n, s)))
    return habis, dikit


def peringatan_stok(i):
    # popup untuk satu barang, dipanggil setelah jual / stok keluar
    b = data[i]
    s = b[2] - b[3]
    if s <= 0:
        messagebox.showwarning("Stok HABIS", "%s sudah HABIS!" % b[0], parent=win)
    elif s <= BATAS_MENIPIS:
        messagebox.showwarning("Stok menipis", "%s hampir habis, sisa %s." % (b[0], fmt_stok(b[0], s)), parent=win)


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

# panel uang yang dimiliki (di atas panel peringatan dan pencarian)
kas_frame = tk.Frame(win, bg="#dfe8f1")
kas_frame.pack(fill="x", padx=10, pady=(8, 0), before=cari_frame)
lbl_kas = tk.Label(kas_frame, text="", bg="#dfe8f1", fg="#1e5631", font=("Arial", 11, "bold"))
lbl_kas.pack(side="left", padx=8, pady=4)
tk.Button(kas_frame, text="Atur Saldo", command=atur_kas).pack(side="right", padx=(0, 6))
tk.Button(kas_frame, text="Tambah Uang", command=tambah_kas).pack(side="right", padx=6)

tabel.config(height=6)   # tabel tetap melebar mengisi ruang; ini supaya tombol bawah tidak terpotong


def saring():
    kata = cari_var.get().strip().lower()
    if not kata:
        lbl_hasil.config(text="")
        return
    for iid in tabel.get_children():
        if kata not in data[int(iid)][0].lower():
            tabel.delete(iid)
    lbl_hasil.config(text="%d barang ditemukan" % len(tabel.get_children()))


# bungkus isi() yang asli: setelah tabel diisi, terapkan pencarian + perbarui notifikasi & uang
def tampil_satuan():
    # tampilkan stok dalam dus (mis. "2 dus 33 pcs") dan isi per dus di samping nama barang
    for iid in tabel.get_children():
        b = data[int(iid)]
        s = info_satuan(b[0])
        tabel.set(iid, "sisa", fmt_stok(b[0], b[2] - b[3]))
        if punya_dus(b[0]):
            tabel.set(iid, "nama", "%s  (1 %s = %d %s)" % (b[0], s["u"], s["i"], s["s"]))


# lebarkan kolom supaya teks satuan muat
for _k, _w in [("nama", 230), ("harga", 90), ("masuk", 60), ("terjual", 60), ("sisa", 130), ("ket", 100)]:
    tabel.column(_k, width=_w)
tabel.heading("harga", text="Harga/satuan")

isi_asli = isi


def isi():
    isi_asli()
    saring()
    tampil_satuan()
    perbarui_notif()
    perbarui_kas()


cari_var.trace_add("write", lambda *a: isi())


# ---------- PENJUALAN (dicatat, uang bertambah) ----------
jual_asli = jual


def catat_jual(i, n, ket):
    nama, harga = data[i][0], data[i][1]
    log.append({"waktu": sekarang(), "barang": nama, "jumlah": n,
                "harga": harga, "total": n * harga})
    tulis_log(FILE_JUAL, log)
    ubah_kas(n * harga, "Jual %s %s" % (nama, ket))
    peringatan_stok(i)


def jual():
    p = tabel.selection()
    if not p:
        jual_asli()
        return
    i = int(p[0])
    nama, sebelum = data[i][0], data[i][3]
    if punya_dus(nama):
        # barang punya satuan besar: pilih jumlah + satuan (pcs / dus)
        s = info_satuan(nama)
        stok = data[i][2] - data[i][3]
        v = form("Jual", [("Berapa %s yang terjual? (sisa %s)" % (nama, fmt_stok(nama, stok)), "1", None),
                          ("Satuan", s["s"], [s["s"], s["u"]])], "Jual")
        if not v:
            return
        q = angka(v[0])
        if not q or q < 1:
            messagebox.showerror("Gagal", "Jumlah harus berupa angka lebih dari 0.", parent=win)
            return
        n = q * faktor(nama, v[1])
        if n > stok:
            messagebox.showerror("Gagal", "Stok tinggal %s." % fmt_stok(nama, stok), parent=win)
            return
        data[i][3] += n
        tulis(data)
        isi()
        catat_jual(i, n, "x%d %s" % (q, v[1]))
        return
    jual_asli()
    n = data[i][3] - sebelum
    if n > 0:
        catat_jual(i, n, "x%d" % n)


# ---------- STOK MASUK (uang berkurang) ----------
masuk_asli = masuk


def masuk():
    p = tabel.selection()
    if not p:
        masuk_asli()
        return
    i = int(p[0])
    nama, sebelum = data[i][0], data[i][2]
    if punya_dus(nama):
        # barang punya satuan besar: jumlah + satuan (dus dulu) + harga beli per satuan itu
        s = info_satuan(nama)
        v = form("Stok masuk", [("Berapa %s yang datang?" % nama, "1", None),
                                ("Satuan", s["u"], [s["u"], s["s"]]),
                                ("Harga beli per satuan di atas (Rp)", "", None)], "Tambah")
        if not v:
            return
        q, harga = angka(v[0]), angka(v[2])
        if not q or q < 1 or harga is None:
            messagebox.showerror("Gagal", "Jumlah dan harga beli harus berupa angka.", parent=win)
            return
        if not cukup_uang(q * harga):
            return
        data[i][2] += q * faktor(nama, v[1])
        tulis(data)
        isi()
        ubah_kas(-q * harga, "Beli stok %s x%d %s @ %s" % (nama, q, v[1], rp(harga)))
        return
    masuk_asli()
    n = data[i][2] - sebelum
    if n <= 0:
        return
    harga = simpledialog.askinteger("Harga beli", "Harga beli %s per %s (Rp):" % (nama, info_satuan(nama)["s"]),
                                    minvalue=0, parent=win)
    if harga is None or not cukup_uang(n * harga):
        data[i][2] -= n   # batalkan stok yang barusan ditambahkan
        tulis(data)
        isi()
        if harga is None:
            messagebox.showinfo("Dibatalkan", "Harga beli tidak diisi, stok masuk dibatalkan.", parent=win)
        return
    ubah_kas(-n * harga, "Beli stok %s x%d @ %s" % (nama, n, rp(harga)))


# ---------- BARANG BARU (stok awal juga memakai uang) ----------
baru_asli = baru


def baru():
    jumlah_sebelum = len(data)
    baru_asli()
    if len(data) <= jumlah_sebelum:
        return
    b = data[-1]
    if b[2] > 0:
        harga = simpledialog.askinteger("Harga beli", "Harga beli %s per satuan terkecil (Rp):" % b[0],
                                        minvalue=0, parent=win)
        if harga is None or not cukup_uang(b[2] * harga):
            data.pop()   # batalkan barang yang barusan ditambahkan
            tulis(data)
            isi()
            if harga is None:
                messagebox.showinfo("Dibatalkan", "Harga beli tidak diisi, barang baru dibatalkan.", parent=win)
            return
        ubah_kas(-b[2] * harga, "Beli stok awal %s x%d @ %s" % (b[0], b[2], rp(harga)))
    atur_satuan_item(len(data) - 1)   # isi satuan (dus, dll); boleh dikosongkan / dibatalkan


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
    if punya_dus(b[0]):
        s = info_satuan(b[0])
        v = form("Stok keluar", [("Berapa %s yang keluar? (sisa %s)" % (b[0], fmt_stok(b[0], sisa)), "1", None),
                                 ("Satuan", s["s"], [s["s"], s["u"]])], "Lanjut")
        if not v:
            return
        q = angka(v[0])
        if not q or q < 1:
            messagebox.showerror("Gagal", "Jumlah harus berupa angka lebih dari 0.", parent=win)
            return
        n = q * faktor(b[0], v[1])
    else:
        n = simpledialog.askinteger("Stok keluar", "Berapa %s yang keluar? (sisa %d)" % (b[0], sisa),
                                    minvalue=1, parent=win)
        if not n:
            return
    if n > sisa:
        messagebox.showerror("Gagal", "Stok tinggal %s." % fmt_stok(b[0], sisa))
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


# ---------- HAPUS (satuannya ikut dihapus) ----------
hapus_asli = hapus


def hapus():
    p = tabel.selection()
    nama = data[int(p[0])][0] if p else None
    jumlah_sebelum = len(data)
    hapus_asli()
    if nama in satuan and len(data) < jumlah_sebelum:
        del satuan[nama]
        tulis_satuan()


# ---------- ATUR SATUAN (dus, karung, dll) ----------
def atur_satuan_item(i):
    nama = data[i][0]
    s = info_satuan(nama)
    v = form("Atur satuan: " + nama, [
        ("Satuan terkecil (pcs, botol, kg, dll)", s["s"], None),
        ("Satuan besar, kosongkan jika tidak ada (dus, karung, dll)", s["u"], None),
        ("Isi per satuan besar (jumlah satuan terkecil)", str(s["i"]) if s["i"] else "", None)], "Simpan")
    if not v:
        return
    kecil, besar, banyak = v[0].strip() or "pcs", v[1].strip(), angka(v[2]) or 0
    if besar and (banyak < 2 or besar.lower() == kecil.lower()):
        messagebox.showerror("Gagal", "Satuan besar harus berbeda dari satuan terkecil dan isinya minimal 2.",
                             parent=win)
        return
    satuan[nama] = {"s": kecil, "u": besar, "i": banyak if besar else 0}
    tulis_satuan()
    isi()


def atur_satuan():
    i = dipilih()
    if i is not None:
        atur_satuan_item(i)


# ---------- MULAI JUALAN / SELESAI JUALAN ----------
# sesi disimpan di sesi.json: {"aktif": {"mulai": ..., "kas_awal": ...} atau null, "riwayat": [ringkasan sesi]}
def baca_sesi():
    try:
        with open(FILE_SESI, encoding="utf-8") as f:
            d = json.load(f)
        return {"aktif": d.get("aktif"), "riwayat": d.get("riwayat", [])}
    except FileNotFoundError:
        return {"aktif": None, "riwayat": []}
    except Exception:
        os.replace(FILE_SESI, FILE_SESI + ".rusak")
        return {"aktif": None, "riwayat": []}


sesi = baca_sesi()


def simpan_sesi():
    with open(FILE_SESI, "w", encoding="utf-8") as f:
        json.dump(sesi, f, indent=2, ensure_ascii=False)


def hitung_sesi(mulai, selesai=None):
    # rekap penjualan, pembelian stok, dan stok keluar antara waktu mulai dan selesai
    def dalam(w):
        return w >= mulai and (selesai is None or w <= selesai)
    jual_ = [x for x in log if dalam(x["waktu"])]
    beli = -sum(x["jumlah"] for x in kas["riwayat"]
                if dalam(x["waktu"]) and x["ket"].startswith("Beli stok"))
    per = {}
    for x in jual_:
        per[x["barang"]] = per.get(x["barang"], 0) + x["jumlah"]
    terlaris = max(per.items(), key=lambda kv: kv[1]) if per else None
    return {"transaksi": len(jual_), "item": sum(x["jumlah"] for x in jual_),
            "omzet": sum(x["total"] for x in jual_), "pembelian": beli,
            "keluar": sum(x["jumlah"] for x in log_keluar if dalam(x["waktu"])),
            "terlaris": terlaris}


def lama_sesi(mulai, selesai):
    d = datetime.strptime(selesai, "%Y-%m-%d %H:%M:%S") - datetime.strptime(mulai, "%Y-%m-%d %H:%M:%S")
    menit = int(d.total_seconds() // 60)
    return "%d jam %d menit" % (menit // 60, menit % 60) if menit >= 60 else "%d menit" % menit


lbl_sesi = tk.Label(kas_frame, text="", bg="#dfe8f1", font=("Arial", 10, "bold"))
lbl_sesi.pack(side="left", padx=14)
btn_sesi = None   # tombol Mulai/Selesai, dibuat di bagian bawah


def perbarui_sesi():
    if sesi["aktif"]:
        lbl_sesi.config(text="BUKA sejak " + sesi["aktif"]["mulai"][11:16], fg="#1e5631")
        if btn_sesi:
            btn_sesi.config(text="Selesai Jualan", bg="#c0392b", fg="white")
    else:
        lbl_sesi.config(text="TUTUP", fg="#c0392b")
        if btn_sesi:
            btn_sesi.config(text="Mulai Jualan", bg="#1e8449", fg="white")


def mulai_jualan(tanya=True):
    if sesi["aktif"]:
        messagebox.showinfo("Jualan", "Jualan sudah dimulai sejak %s." % sesi["aktif"]["mulai"], parent=win)
        return True
    if tanya and not messagebox.askyesno(
            "Mulai jualan", "Mulai jualan sekarang?\nUang awal: %s" % rp(kas["saldo"]), parent=win):
        return False
    sesi["aktif"] = {"mulai": sekarang(), "kas_awal": kas["saldo"]}
    simpan_sesi()
    perbarui_sesi()
    return True


def selesai_jualan():
    a = sesi["aktif"]
    if not a:
        messagebox.showinfo("Jualan", "Belum mulai jualan.", parent=win)
        return
    if not messagebox.askyesno("Selesai jualan", "Akhiri jualan sekarang dan tutup rekap?", parent=win):
        return
    akhir = sekarang()
    r = hitung_sesi(a["mulai"], akhir)
    r.update({"mulai": a["mulai"], "selesai": akhir, "kas_awal": a["kas_awal"], "kas_akhir": kas["saldo"]})
    sesi["riwayat"].append(r)
    sesi["aktif"] = None
    simpan_sesi()
    perbarui_sesi()
    teks = ("Jualan: %s s/d %s (%s)\n\nTransaksi: %d\nItem terjual: %d\nOmzet: %s\nPembelian stok: %s\n"
            "Item keluar: %d\n\nUang awal: %s\nUang akhir: %s\nSelisih: %s"
            % (a["mulai"][11:16], akhir[11:16], lama_sesi(a["mulai"], akhir), r["transaksi"], r["item"],
               rp(r["omzet"]), rp(r["pembelian"]), r["keluar"], rp(r["kas_awal"]), rp(r["kas_akhir"]),
               rp_tanda(r["kas_akhir"] - r["kas_awal"])))
    if r["terlaris"]:
        teks += "\n\nTerlaris: %s (%s)" % (r["terlaris"][0], fmt_stok(r["terlaris"][0], r["terlaris"][1]))
    habis, dikit = daftar_stok_rendah()
    if habis or dikit:
        teks += "\n\nPerlu restok: %s" % ", ".join(habis + dikit)
    messagebox.showinfo("Rekap jualan", teks, parent=win)


def tombol_sesi():
    if sesi["aktif"]:
        selesai_jualan()
    else:
        mulai_jualan()


# penjualan hanya boleh saat jualan sudah dimulai (kalau belum, ditawari untuk memulai)
jual_tanpa_sesi = jual


def jual():
    if not sesi["aktif"]:
        if not messagebox.askyesno("Belum mulai jualan",
                                   "Jualan belum dimulai. Mulai jualan sekarang?", parent=win):
            return
        mulai_jualan(tanya=False)
    jual_tanpa_sesi()


# tambahkan perbarui_sesi() ke isi() supaya status buka/tutup selalu tampil
isi_sebelum_sesi = isi


def isi():
    isi_sebelum_sesi()
    perbarui_sesi()


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
    w.geometry("680x470")
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
    f1, f2, f3, f4, f5 = tk.Frame(nb), tk.Frame(nb), tk.Frame(nb), tk.Frame(nb), tk.Frame(nb)
    nb.add(f1, text="Per Barang")
    nb.add(f2, text="Riwayat Penjualan")
    nb.add(f3, text="Stok Keluar")
    nb.add(f4, text="Riwayat Uang")
    nb.add(f5, text="Riwayat Sesi")

    t1 = buat_tabel(f1, [("nama", "Nama Barang", 240, "w"), ("jumlah", "Terjual", 100, "center"),
                         ("uang", "Pendapatan", 160, "center")])
    t2 = buat_tabel(f2, [("waktu", "Waktu", 150, "center"), ("nama", "Barang", 160, "w"),
                         ("jumlah", "Jumlah", 60, "center"), ("harga", "Harga", 90, "center"),
                         ("total", "Total", 100, "center")])
    t3 = buat_tabel(f3, [("waktu", "Waktu", 150, "center"), ("nama", "Barang", 180, "w"),
                         ("jumlah", "Jumlah", 70, "center"), ("alasan", "Alasan", 200, "w")])
    t4 = buat_tabel(f4, [("waktu", "Waktu", 140, "center"), ("ket", "Keterangan", 250, "w"),
                         ("jumlah", "Jumlah", 110, "center"), ("saldo", "Saldo", 110, "center")])
    t5 = buat_tabel(f5, [("mulai", "Mulai", 130, "center"), ("selesai", "Selesai", 130, "center"),
                         ("trx", "Transaksi", 70, "center"), ("omzet", "Omzet", 100, "center"),
                         ("awal", "Uang awal", 100, "center"), ("akhir", "Uang akhir", 100, "center")])

    def refresh(*_):
        hari = datetime.now().strftime("%Y-%m-%d")
        semua = periode.get() == "Semua"
        rows = [x for x in log if semua or x["waktu"].startswith(hari)]
        keluar = [x for x in log_keluar if semua or x["waktu"].startswith(hari)]
        uang = [x for x in kas["riwayat"] if semua or x["waktu"].startswith(hari)]
        for tv in (t1, t2, t3, t4, t5):
            tv.delete(*tv.get_children())
        per = {}
        for x in rows:
            p = per.setdefault(x["barang"], [0, 0])
            p[0] += x["jumlah"]
            p[1] += x["total"]
        for nama, (j, u) in sorted(per.items(), key=lambda kv: -kv[1][1]):
            t1.insert("", "end", values=(nama, fmt_stok(nama, j), rp(u)))
        for x in reversed(rows):
            t2.insert("", "end", values=(x["waktu"], x["barang"], x["jumlah"],
                                         rp(x["harga"]), rp(x["total"])))
        for x in reversed(keluar):
            t3.insert("", "end", values=(x["waktu"], x["barang"], fmt_stok(x["barang"], x["jumlah"]), x["alasan"]))
        for x in reversed(uang):
            t4.insert("", "end", values=(x["waktu"], x["ket"], rp_tanda(x["jumlah"]), rp(x["saldo"])))
        for x in reversed(sesi["riwayat"]):
            if semua or x["mulai"].startswith(hari):
                t5.insert("", "end", values=(x["mulai"][:16], x["selesai"][:16], x["transaksi"],
                                             rp(x["omzet"]), rp(x["kas_awal"]), rp(x["kas_akhir"])))
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
tk.Button(bawah, text="Satuan", command=atur_satuan, width=12, pady=4).pack(side="left", padx=(0, 6))  # TAMBAHAN
btn_sesi = tk.Button(bawah, text="Mulai Jualan", command=tombol_sesi, width=14, pady=4)  # TAMBAHAN
btn_sesi.pack(side="left", padx=(0, 6))  # TAMBAHAN
perbarui_sesi()  # TAMBAHAN
tk.Button(bawah, text="Hasil Penjualan", command=hasil_penjualan, width=16, pady=4,
          bg="#2b4a6f", fg="white").pack(side="right")  # TAMBAHAN
win.geometry("1000x480")  # TAMBAHAN: jendela dilebarkan karena tombol bertambah
win.after(400, awal)  # TAMBAHAN: tanya saldo awal (sekali) + popup peringatan stok

tabel.bind("<Double-1>", lambda e: jual())
isi()
win.mainloop()