import json, os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stok.json")

stok_toko = [
    ["Indomie Goreng", 3500, 120, 87],
    ["Minyak Goreng", 18000, 24, 19],
    ["Gula", 5000, 30, 30],
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


bawah = tk.Frame(win, bg="#e8e8e8")
bawah.pack(fill="x", padx=10, pady=(4, 10))
for teks, fn in [("Jual", jual), ("Stok Masuk", masuk), ("Barang Baru", baru), ("Hapus", hapus)]:
    tk.Button(bawah, text=teks, command=fn, width=12, pady=4).pack(side="left", padx=(0, 6))

tabel.bind("<Double-1>", lambda e: jual())
isi()
win.mainloop()