# GEMA — Game Design Document

> Versi 1.0 · 24 September 2026 · Status: menunggu review

**Dalam satu kalimat:** di labirin yang gelap total, melihat berarti terdengar.

---

## 1. Ringkasan

| | |
|---|---|
| Genre | Horor psikologis top-down, roguelite pendek |
| Platform | PC (Windows, macOS, Linux) |
| Teknologi | Python 3.10+, pygame-ce, numpy |
| Durasi satu run | 15–25 menit (5 lantai + lantai terakhir) |
| Bahasa | Indonesia |
| Aset | Tanpa file gambar atau suara. Semua visual digambar dengan kode, semua suara dibuat dengan numpy. |

**Premis.** Pemain terbangun di labirin gelap dengan senter tua dan alat sonar. Untuk melihat, ia harus mengirim sonar, padahal sonar itu terdengar oleh makhluk-makhluk yang berburu dengan telinga. Di setiap lantai ia harus menemukan tiga fragmen berisi catatan tulisan tangannya sendiri. Setelah ketiganya terkumpul, pintu keluar terbuka.

---

## 2. Pilar desain

1. **Ketidakpastian.** Pemain tidak bisa sepenuhnya percaya pada inderanya. Sonar bisa berbohong, peta di kepala bisa salah, dan ada suara yang bukan miliknya.
2. **Ketidakberdayaan.** Pemain bukan pemburu dan tidak punya senjata. Setiap alat ada harganya: sonar berisik, senter menguras baterai, lari mengundang monster.
3. **Antisipasi.** Yang ditunggu lebih seram daripada yang datang. Ancaman lebih sering terdengar dan terasa daripada terlihat.

### Aturan keras

Aturan ini tidak boleh dilanggar oleh fitur apa pun.

- **Tidak ada jumpscare.** Tidak ada gambar yang muncul tiba-tiba disertai suara keras, dan tidak ada suara yang jauh lebih keras daripada suasana di sekitarnya.
- **Monster tidak pernah terlihat utuh.**
- **Tidak ada angka di layar selama bermain.** Nyawa hanya ditampilkan di layar antar-lantai, layar kematian, dan menu jeda.
- **Game boleh berbohong soal informasi, tapi tidak boleh curang soal aturan.** Kematian selalu disebabkan monster sungguhan yang sebenarnya bisa dihindari (lihat §6.3).
- **Cerita tidak pernah dijelaskan terang-terangan.**

---

## 3. Alur permainan

### Detik ke detik

```
            dengarkan sekeliling
                     │
                     ▼
     ┌──────── ambil keputusan ────────┐
     │               │                 │
   SONAR           SENTER        DIAM / JALAN PELAN
  bisa melihat,   aman,          aman dari telinga,
  tapi berisik    tapi baterai   tapi buta
     │               │                 │
     └───────────────┼─────────────────┘
                     ▼
          bergerak, lalu dengarkan lagi
```

### Per lantai (3–5 menit)

1. Pemain muncul di pintu masuk.
2. Menjelajah labirin sambil mengikuti dengung fragmen.
3. Mengambil 3 fragmen. Setiap fragmen memunculkan satu catatan.
4. Pintu keluar terbuka. Suasana berubah: hening sejenak, lalu monster menjadi lebih ganas.
5. Pemain lari ke pintu keluar dan turun ke lantai berikutnya.

### Per run

Lantai 1 sampai 5, lalu lantai terakhir tanpa nomor, lalu ending. Kalau nyawa habis, run berakhir dan pemain kembali ke layar judul. Percobaan berikutnya dimulai lagi dari Lantai 1 dengan labirin baru.

### Antar-sesi

Game menyimpan jumlah percobaan, kematian, dan ending yang pernah dicapai. Angka-angka ini muncul di catatan dan di layar judul (lihat §10.5 dan §10.7).

---

## 4. Kontrol

| Input | Aksi |
|---|---|
| `W` `A` `S` `D` | Bergerak (jalan pelan) |
| `Shift` (tahan) | Lari: cepat tapi berisik |
| Mouse | Mengarahkan senter |
| Klik kiri (tahan) | Menyalakan senter |
| Klik kanan / `Space` | Sonar |
| `Esc` | Jeda |
| `F11` | Layar penuh |

Petunjuk kontrol muncul samar di awal Lantai 1 selama beberapa detik lalu menghilang. Daftar lengkapnya ada di menu jeda.

---

## 5. Mekanik inti

Semua angka di dokumen ini adalah **nilai awal**. Nilai-nilai ini disimpan di `gema/config.py` dan akan disetel ulang setelah playtest.

### 5.1 Pemain

- Digambar sebagai lingkaran kecil pucat dengan satu takik yang menunjuk ke arah senter.
- Selalu ada **aura redup** kecil di sekeliling pemain (radius ±40 px), supaya pemain tetap bisa melihat dinding tepat di sebelahnya.
- Ada tiga cara bergerak:

| | Kecepatan | Radius suara |
|---|---|---|
| Diam | 0 | 0 (sunyi total) |
| Jalan | 80 px/dtk | 70 px (±2 petak) |
| Lari | 150 px/dtk | 220 px (±7 petak) |

Selama pemain bergerak, suara langkah dikirim setiap ±0,4 detik.

### 5.2 Sonar

- Klik kanan atau `Space` mengirim gelombang yang melebar dari posisi pemain sampai radius 420 px dalam ±0,8 detik.
- Gelombang dipantulkan dinding. Sebanyak 360 sinar menghasilkan **titik-titik cahaya** di permukaan dinding, sehingga dinding tampak seperti awan titik hasil pemindai. Titik-titik ini terang sesaat lalu memudar dalam ±2,5 detik.
- **Jejak ingatan.** Titik yang sudah memudar tidak hilang total. Sisanya tetap terlihat sangat samar (±15%), jadi pemain punya peta ingatan kasar. Peta ini **tidak ikut berubah saat labirin bergeser** (§6.5), sehingga ingatan pemain bisa salah. Area yang dipindai ulang akan memperbarui ingatannya.
- Objek yang terkena gelombang meninggalkan **tanda di posisi saat terkena**, bukan posisi terkininya. Artinya informasi ini cepat basi.

| Objek | Tanda | Lama tampil |
|---|---|---|
| Pendengar | Titik merah kusam | 1,5 dtk |
| Pengamat | Bentuk yang sama persis dengan pemain | 1,5 dtk |
| Fragmen | Belah ketupat ungu pucat | 3 dtk |
| Baterai | Titik hijau kecil | 3 dtk |
| Pintu keluar | Garis vertikal | 3 dtk |

- **Garis pandang.** Objek yang terlihat langsung diberi tanda yang tajam. Objek di balik tikungan yang masih terjangkau lewat lorong diberi tanda yang buram dan lebih besar, karena suara merambat lewat lorong.
- **Harga.** Sonar adalah suara dengan radius 400 px. Pendengar dalam radius itu akan datang.
- **Jeda.** 2 / 3 / 4,5 detik, tergantung tingkat kesulitan.

### 5.3 Senter

- Tahan klik kiri untuk menyalakan. Bentuknya kerucut 50° dengan jangkauan 230 px, dan cahayanya terhalang dinding.
- **Pendengar yang terkena cahaya membeku.** Mereka tidak pergi, hanya diam. Menyentuh Pendengar yang sedang membeku tetap mematikan.
- **Pengamat yang terkena cahaya berhenti.** Kalau disorot terus selama 2 detik, ia memudar dan pergi untuk sementara (§7.2).
- **Baterai** bernilai 0–100, tapi tidak pernah ditampilkan sebagai angka:
  - Jangkauan cahaya menyusut seiring berkurangnya baterai, dari 230 px sampai 170 px.
  - Di bawah 20%, cahaya mulai berkedip. Selama padam sekejap itu, monster tidak membeku.
  - Baterai **tidak** terisi ulang saat pindah lantai. Satu-satunya cara mengisi adalah baterai cadangan (+35).
- Senter tidak bersuara, kecuali bunyi klik kecil yang hanya didengar pemain. Senter adalah alat yang tenang tapi terbatas.

### 5.4 Suara dan pendengaran

- Setiap aksi yang berisik (langkah, lari, sonar, mengambil fragmen, ping peniru) dikirim ke **bus suara** sebagai sebuah kejadian berisi posisi dan radius.
- Pendengar mendengar kejadian yang berada dalam radiusnya. Jaraknya dihitung lurus dan menembus dinding. Setelah mendengar, Pendengar mencari jalan lewat lorong menuju sumber suara.

### 5.5 Fragmen

- Ada 3 fragmen per lantai. Letaknya di ujung jalan buntu atau di ruangan kecil, saling berjauhan, dan jauh dari pintu masuk.
- Setiap fragmen mengeluarkan **dengung pelan** dalam stereo. Makin dekat, makin keras, dan mulai terdengar dari jarak ±400 px. Jadi pemain bisa mencarinya dengan telinga.
- Fragmen diambil dengan menyentuhnya. Catatan lalu muncul di bagian bawah layar dengan efek mesin ketik. **Permainan tidak berhenti** selama catatan tampil.
- Mengambil fragmen menimbulkan suara kecil (radius 150 px) dan menurunkan stres, jadi pemain merasa lega sesaat.

### 5.6 Pintu keluar

- Letaknya di titik terjauh dari pintu masuk.
- Pintu terkunci sampai ketiga fragmen terkumpul.
- Begitu terbuka, terjadi urutan berikut:
  1. Terdengar dentuman berat tapi pelan dari arah pintu.
  2. **Hening total ±6 detik**, karena dengung latar berhenti.
  3. Pendengar menjadi **gelisah**: kecepatan ×1,25 dan jangkauan pendengaran ×1,4 sampai pemain keluar.
  4. Pintu mengeluarkan dengung rendah dan celah cahaya tipis, supaya bisa ditemukan.

### 5.7 Baterai cadangan

Baterai cadangan tersebar di jalan buntu yang tersisa. Jumlahnya per lantai tergantung tingkat kesulitan. Baterai terlihat lewat sonar, aura, dan cahaya senter, lalu diambil dengan menyentuhnya.

### 5.8 Nyawa dan kematian

- Pemain kehilangan satu nyawa kalau disentuh Pendengar atau Pengamat.
- **Urutan kematian** dibuat jelas tapi tanpa jumpscare:
  1. **Waktu berhenti** ±0,9 detik. Dunia diam, dan layar bergetar lalu mereda.
  2. **Makhluk yang menangkap terlihat**, walaupun ada di kegelapan. Pendengar tampil sebagai siluet berpinggiran merah dengan cahaya merah redup. Pengamat tampil sebagai sosok yang sama persis dengan pemain, bersentuhan dengan pemain.
  3. Semua suara hilang, lalu terdengar satu hantaman tumpul dan **satu detak jantung terakhir**. Setelah itu jantung diam.
  4. Pinggiran layar berdenyut merah lalu memudar.
  5. Layar memudar ke hitam, lalu muncul tulisan kecil secara acak: *"Belum."*, *"Lagi."*, atau *"Bangun."*
  6. Pemain muncul lagi di pintu masuk lantai yang sama.
- Setelah mati, fragmen yang sudah diambil tetap tersimpan, dan monster dipindahkan jauh dari pintu masuk. Stres tidak kembali ke nol (§6.1).
- Kalau nyawa habis, muncul tulisan *"Percobaan ke-N berakhir."* lalu game kembali ke layar judul.

---

## 6. Sistem horor

### 6.1 Stres (tersembunyi)

Stres adalah meter 0–100 yang **tidak pernah ditampilkan**. Pemain hanya merasakan efeknya.

**Yang menaikkan stres:**

| Penyebab | Jumlah |
|---|---|
| Ada Pendengar dalam 150 px | Sampai +8/dtk (makin dekat, makin besar) |
| Gelap terlalu lama (senter mati dan sonar terakhir lebih dari 8 detik lalu) | +0,8/dtk |
| Menatap Pengamat | +8/dtk |
| Mendengar ping peniru | +10 |
| Mendengar dinding bergeser | +3 |
| Kehilangan nyawa | +20 |

**Yang menurunkan stres:**

| Penyebab | Jumlah |
|---|---|
| Aman (tidak ada Pendengar dalam 250 px, dan senter menyala atau sonar dipakai dalam 8 detik terakhir) | −3/dtk |
| Mengambil fragmen | −15 |
| Masuk lantai baru | Kembali ke batas bawah |

**Batas bawah stres** = 10 × jumlah nyawa yang hilang di run ini, maksimal 40.

Akibatnya, informasi membuat pemain lebih tenang tapi ada harganya. Pemain yang sering memakai sonar stresnya turun, tapi ia lebih sering didatangi monster.

**Efek stres:**

| Stres | Yang terjadi |
|---|---|
| 0–30 | Normal |
| 30–60 | Vignette mulai menyempit, dan sesekali muncul gema palsu |
| 60–85 | Detak jantung lebih keras, terdengar bisikan samar dari kiri atau kanan, jejak ingatan berkedip, gema palsu makin sering, dan gema asli bisa hilang |
| 85–100 | Kamera sedikit bergoyang, gelombang sonar tampak bergelombang, dan muncul bayangan palsu di tepi cahaya senter |

**Lantai 1 bebas trik persepsi.** Di Lantai 1 efek stres hanya berupa vignette dan detak jantung. Game mulai berbohong di Lantai 2, jadi pemain mungkin merasa ada yang janggal sebelum ada catatan yang membenarkannya.

### 6.2 Detak jantung

- Kecepatan detak jantung (60–150 BPM) dan volumenya mengikuti nilai **bahaya**, yaitu yang lebih besar antara kedekatan monster terdekat (dihitung dalam 240 px) dan stres × 0,4.
- Detak jantung mulai terdengar saat bahaya di atas 0,2.
- Detak jantung **sengaja mono**, tidak stereo. Pemain tahu bahaya sudah dekat, tapi tidak tahu dari arah mana.

### 6.3 Gema palsu dan gema hilang

- **Gema palsu:** titik merah di sonar padahal tidak ada monster. Rata-rata jumlahnya per ping = stres/100 × 2 × pengali kesulitan. Mulai muncul di Lantai 2.
- **Gema hilang:** saat stres di atas 60, setiap Pendengar yang lebih jauh dari 200 px punya peluang 25% (× pengali kesulitan) untuk tidak tertangkap sonar.
- **Aturan keadilan:**
  - Gema palsu tidak pernah muncul dalam jarak 150 px dari pemain.
  - Pendengar dalam jarak 200 px selalu tertangkap sonar.
  - **Pusat cahaya senter tidak pernah berbohong.** Bayangan palsu hanya muncul di tepi kerucut cahaya dan langsung hilang saat disorot langsung.
  - Suara seretan Pendengar selalu jujur.

### 6.4 Bisikan dan bayangan

- **Bisikan** (stres ≥ 60, mulai Lantai 2): desis berbentuk suara orang yang sangat pelan, terdengar dari kiri atau kanan secara acak.
- **Bayangan palsu** (stres ≥ 85, mulai Lantai 3): siluet mirip Pendengar di tepi kerucut senter. Siluet ini hilang begitu diarahkan ke tengah cahaya.

### 6.5 Labirin bergeser (mulai Lantai 3)

- Secara berkala, satu dinding di antara dua sel dibuka atau ditutup diam-diam. Jaraknya setiap 25–45 detik di Lantai 3–4, dan 15–30 detik di Lantai 5.
- Perubahan hanya terjadi di tempat yang **tidak sedang diamati**: lebih dari 160 px dari pemain, di luar kerucut senter, dan tidak terkena sonar dalam 3 detik terakhir.
- **Labirin selalu terhubung.** Dinding hanya boleh ditutup kalau semua lantai labirin tetap terhubung, dan tidak ada monster atau benda di petak itu.
- Pemain mendengar gesekan batu yang sangat pelan dari arah perubahan.
- Jejak ingatan sonar tidak ikut berubah, jadi peta di kepala pemain bisa salah.

### 6.6 Ping peniru (mulai Lantai 4)

- Pengamat sesekali memakai "sonarnya" sendiri. Jaraknya setiap 40–70 detik di Lantai 4 dan setiap 25–45 detik di Lantai 5, dan makin sering saat stres tinggi.
- Pemain mendengar bunyi ping yang **hampir** sama dengan miliknya, hanya sedikit lebih rendah dan bergetar. Bunyinya datang dari arah Pengamat, disertai lingkaran tipis samar yang melebar dari titik itu di kegelapan.
- Ping ini juga masuk ke bus suara, jadi Pendengar ikut datang ke lokasi Pengamat, yang biasanya tidak jauh dari pemain.
- Kalau Pengamat sedang pergi, ping datang dari titik acak sejauh ±300 px.

### 6.7 Pengatur tempo (director)

- Satu sistem pusat yang menjadwalkan semua kejadian horor, supaya kejadian-kejadian itu tidak menumpuk.
- Jarak minimal antar kejadian besar (ping peniru, dinding bergeser yang terdengar, bayangan) adalah 8 detik.
- Setelah momen puncak, misalnya baru lolos dari kejaran, director memberi jeda yang lebih panjang.
- Ritme tegang dan lega itu penting. Ketegangan yang tidak pernah reda justru membuat pemain mati rasa.

---

## 7. Musuh

### 7.1 Pendengar

- **Buta dan berburu dengan telinga.** Wujudnya siluet gelap bergerigi yang tepinya bergetar, dan hanya terlihat samar di dalam cahaya. Saat membeku, getarannya berhenti total. Diamnya itu yang membuat seram.
- **Suara:** seretan pelan yang terdengar dari jarak ±250 px, dalam stereo. Suara ini selalu jujur.
- **Menyentuh pemain berarti pemain kehilangan satu nyawa.**

| Keadaan | Perilaku | Kecepatan (Gelap) |
|---|---|---|
| Berkeliaran | Berjalan acak di lorong | 35 px/dtk |
| Menyelidik | Menuju sumber suara terakhir lewat lorong | 65 px/dtk |
| Mendengarkan | Diam 1,5–3 detik di lokasi suara | 0 |
| Mencari | Berkeliaran di sekitar lokasi (±4 sel) selama 8 detik | 45 px/dtk |
| Memburu | Mendengar suara dalam jarak 120 px, lalu mengejar sumbernya | 95 px/dtk |
| Membeku | Terkena cahaya senter | 0 |

Kecepatan jalan pemain (80) lebih lambat dari Pendengar yang sedang memburu (95). Lari (150) lebih cepat, tapi berisik dan membuat perburuan berlangsung lebih lama. Ada dua cara lolos:
- Bekukan Pendengar dengan senter, lalu menjauh pelan-pelan.
- Lari sejauh mungkin, lalu diam.

### 7.2 Pengamat

- **Bentuk dan warnanya persis seperti pemain.**
- Muncul mulai Lantai 2 (di Pekat sejak Lantai 1), 20–30 detik setelah lantai dimulai, di belakang pemain dan di luar pandangan.
- Ia menjaga **jarak nyaman** dari pemain, awalnya 260 px. Setiap detik ia tidak diamati, jarak nyaman itu menyusut 4 px. Kalau tidak pernah dilihat sama sekali, ia akan menyentuh pemain dalam sekitar satu menit.
- **Saat diamati**, yaitu terkena senter atau tertangkap sonar dalam 0,5 detik terakhir, ia berhenti bergerak. Menatapnya menaikkan stres.
- **Kalau disorot senter terus selama 2 detik**, ia memudar dan pergi selama 25–40 detik. Setelah itu ia muncul lagi di belakang pemain dengan jarak nyaman kembali ke 260 px.
- Kecepatannya 45 px/dtk, lebih lambat dari jalan. Tanpa baterai, pemain masih bisa menjauh asal terus bergerak.
- **Tanda peringatan:** selama ia ada, terdengar **detak kedua** dari arahnya (sampai 400 px): jantung yang bukan milik pemain, lebih lambat dan teredam. Setiap 6–12 detik terdengar juga klik senter mati dari arahnya (*klik… klik-klik*): ia pernah memegang senter yang sama, dan baterainya sudah habis. Dalam jarak 110 px terdengar juga napas pelan, dan detak jantung pemain menguat.
- Menyentuh pemain berarti pemain kehilangan satu nyawa.
- Mulai Lantai 4, ia melakukan ping peniru (§6.6).

Pengamat membuat baterai jadi rebutan. Pemain harus sesekali berbalik dan menyorotnya, padahal baterai yang sama ia butuhkan untuk membekukan Pendengar.

---

## 8. Labirin acak

### 8.1 Cara pembuatan

1. Membuat **labirin sempurna** dengan *recursive backtracker* di atas grid sel.
2. **Braiding:** sebagian jalan buntu dibuka supaya ada jalur memutar untuk kabur. Porsinya 40% di Lantai 1 dan turun sampai 20% di Lantai 5, jadi makin dalam, makin banyak jalan buntu.
3. Memahat 2–3 ruangan kecil berukuran 2×2 sel.
4. **Penempatan:**
   - Pintu masuk di salah satu sudut.
   - Pintu keluar di sel terjauh dari pintu masuk (dihitung dengan BFS).
   - Fragmen di jalan buntu atau ruangan, minimal 6 sel dari pintu masuk dan saling berjauhan.
   - Baterai di jalan buntu yang tersisa.
   - Pendengar muncul minimal 8 sel dari pintu masuk.
5. Setiap run memakai seed acak. Seed bisa dikunci untuk keperluan debug.

Satu sel sama dengan satu petak 32 px, jadi lorong hanya selebar satu petak. Sempit dan menekan.

### 8.2 Perkembangan per lantai (tingkat Gelap)

| Lantai | Ukuran (sel) | Pendengar | Pengamat | Labirin bergeser | Ping peniru | Jalan buntu dibuka |
|---|---|---|---|---|---|---|
| 1 | 12×9 | 1 | – | – | – | 40% |
| 2 | 14×10 | 2 | ✓ | – | – | 35% |
| 3 | 16×11 | 2 | ✓ | ✓ | – | 30% |
| 4 | 18×12 | 3 | ✓ | ✓ | ✓ | 25% |
| 5 | 20×13 | 3 | ✓ | ✓ lebih sering | ✓ lebih sering | 20% |
| Terakhir | Lorong panjang | 0 | – | – | – | – |

Setiap lantai memperkenalkan satu hal baru, jadi pemain tidak kewalahan sekaligus.

### 8.3 Lantai terakhir

Lantai ini berupa lorong panjang yang berkelok, tanpa monster, tanpa fragmen, dan tanpa dengung. Satu-satunya suara adalah langkah pemain sendiri. Di ujungnya ada pintu dengan celah cahaya. Di layar intronya tertulis *"Lantai"* saja, tanpa angka.

---

## 9. Tingkat kesulitan

| Parameter | Redup | Gelap | Pekat |
|---|---|---|---|
| Nyawa | 3 | 2 | 1 |
| Kecepatan Pendengar | ×0,8 | ×1,0 | ×1,2 |
| Jangkauan pendengaran Pendengar | ×0,85 | ×1,0 | ×1,15 |
| Pengurasan baterai | 5/dtk (±20 dtk penuh) | 7/dtk (±14 dtk) | 10/dtk (±10 dtk) |
| Baterai cadangan per lantai | 4 | 3 | 2 |
| Jeda sonar | 2 dtk | 3 dtk | 4,5 dtk |
| Pengali gema palsu | ×0,5 | ×1,0 | ×1,5 |
| Pengamat mulai muncul | Lantai 2 | Lantai 2 | Lantai 1 |
| Pendengar tambahan | – | – | +1 di Lantai 3–5 |
| Aura di sekitar pemain | 88 px | 44 px | 44 px |
| Gema sonar memudar dalam | 4,5 dtk | 2,5 dtk | 2,5 dtk |
| Ingatan sonar (dinding yang pernah terlihat) | ×3,4 lebih terang | biasa | biasa |

---

## 10. Cerita

### 10.1 Premis (yang dilihat pemain)

Pemain terbangun di labirin gelap, memegang senter tua dan alat sonar, tanpa ingatan bagaimana ia bisa sampai di sana. Cerita hanya disampaikan lewat catatan di fragmen. Tidak ada cutscene dan tidak ada dialog.

### 10.2 Kebenarannya (untuk kita, tidak pernah ditulis di dalam game)

- Pemain terjebak dalam sebuah loop. Setiap percobaan adalah "dirinya" yang baru.
- **Pengamat adalah dirinya dari percobaan sebelumnya.** Ping peniru adalah Pengamat yang memakai sonarnya.
- **Pendengar adalah sisa dari setiap kali ia gagal.**
- Catatan di fragmen ditulis oleh dirinya sendiri di percobaan-percobaan sebelumnya, dan nadanya makin lama makin putus asa.
- Pintu terakhir tidak mengarah keluar. Di baliknya, pemain menulis catatan pertama untuk percobaan berikutnya.

### 10.3 Aturan menulis catatan

- Maksimal ±15 kata, dengan bahasa sehari-hari.
- Ditulis oleh "aku" untuk "kamu", yaitu dirinya di masa depan.
- Catatan di lantai-lantai awal sekaligus berfungsi sebagai tutorial terselubung.
- Nadanya bergerak dari praktis, ke gelisah, ke saling bertentangan, ke putus asa, lalu pasrah.
- **Urutan catatan mengikuti urutan pengambilan**, bukan posisi fragmen. Fragmen pertama yang diambil di Lantai 2 selalu memunculkan catatan #4, jadi cerita selalu runtut.

### 10.4 Isi catatan

| # | Lantai | Catatan | Fungsi |
|---|---|---|---|
| 1 | 1 | *Kalau kamu baca ini, berarti alatnya masih nyala. Bagus.* | Pembuka, dan kalimat yang sama muncul lagi di ending |
| 2 | 1 | *Sonar memperlihatkan jalan. Tapi mereka juga dengar. Pakai seperlunya.* | Tutorial sonar |
| 3 | 1 | *Cahaya membuat mereka diam. Bukan pergi. Diam.* | Tutorial senter |
| 4 | 2 | *Mereka tidak bisa melihat. Mereka mendengar. Jangan lari kalau tidak perlu.* | Tutorial suara |
| 5 | 2 | *Ada yang berdiri di ujung cahaya. Selama kamu lihat, dia tidak bergerak.* | Memperkenalkan Pengamat |
| 6 | 2 | *(dinamis, lihat §10.5)* | Meta: jumlah percobaan |
| 7 | 3 | *Jangan percaya ingatanmu soal jalan. Dindingnya pindah waktu tidak dilihat.* | Memperkenalkan labirin bergeser |
| 8 | 3 | *Yang berdiri di pinggir cahaya itu tidak berbahaya.* | Kontradiksi |
| 9 | 3 | *Jangan percaya catatan yang bilang dia tidak berbahaya.* | Kontradiksi |
| 10 | 4 | *Kalau ada bunyi sonar padahal kamu tidak menekannya, itu bukan kamu.* | Memperkenalkan ping peniru |
| 11 | 4 | *Tidak semua yang muncul di sonar itu nyata. Tidak semua yang nyata muncul di sonar.* | Membenarkan gema palsu |
| 12 | 4 | *Tulisan ini mirip tulisanku. Tapi aku tidak ingat pernah menulisnya.* | Gelisah (ada varian) |
| 13 | 5 | *Sudah sadar belum? Bentuknya sama persis kayak kamu.* | Pengungkapan |
| 14 | 5 | *Mereka yang di sini semuanya pernah memegang senter ini.* | Pengungkapan |
| 15 | 5 | *Pintu terakhir tidak mengarah keluar. Aku tetap akan membukanya. Kamu juga.* | Pasrah |

### 10.5 Varian dinamis

Ini trik psikologis bahwa game "kenal" pemain.

- **Catatan #6:**
  - Percobaan pertama: *"Ini percobaan pertama. Setidaknya itu yang tertulis."*
  - Percobaan berikutnya: *"Ini percobaan ke-{n}. Kali ini jangan lari."*
- **Catatan #12**, mulai percobaan ke-3: *"Sudah berapa kali kamu membaca kalimat ini?"*

### 10.6 Ending

Setelah pemain masuk pintu di lantai terakhir, layar menjadi hitam dan tulisan muncul perlahan seperti sedang ditulis:

> *Catatan pertama.*
>
> *Kalau kamu baca ini, berarti alatnya masih nyala.*
>
> *Bagus.*

Setelah jeda, muncul *"Percobaan ke-{n+1}."*, lalu kredit singkat (*GEMA, oleh v.obscura*), lalu layar judul. Kalimat di ending ini sama persis dengan catatan #1, jadi loop-nya tertutup.

### 10.7 Layar judul dinamis

| Kondisi | Tombol mulai bertuliskan |
|---|---|
| Belum pernah mati | *Mulai* |
| Pernah mati minimal sekali | *Kamu kembali.* |
| Pernah mencapai ending | *Kamu kembali. Lagi.* |

---

## 11. Visual

Semua visual digambar dengan kode dari bentuk dasar. Kesannya minimalis, gelap, dan sebagian besar layar hitam.

| Unsur | Warna | Keterangan |
|---|---|---|
| Latar | `#050507` | Hampir hitam |
| Lantai (dalam cahaya) | `#1c1b19` | |
| Dinding (dalam cahaya) | `#3d3a35` | |
| Titik sonar | `#a8e0ee` | Cyan pucat. Jejak ingatan memakai warna yang sama dengan transparansi ±15% |
| Cahaya senter | `#f4e4b8` | Hangat, meredup dari tengah ke tepi |
| Tanda Pendengar | `#b0413e` | Merah kusam |
| Pemain dan Pengamat | `#d9d6cc` | Sengaja sama persis |
| Fragmen | `#b9a8ff` | Ungu pucat |
| Baterai | `#8fc79a` | |
| Pintu keluar | `#fff1cf` | Celah cahaya |
| Teks | `#cfcac0` | |

**Menggambar monster.** Pendengar digambar sebagai poligon hitam yang lebih gelap dari sekitarnya, dengan titik-titik sudut yang bergetar. Ia hanya terlihat di dalam cahaya, seolah cahaya tidak sanggup menyentuhnya.

**Efek layar:**
- Vignette yang menyempit mengikuti stres.
- Film grain tipis.
- Goyangan kamera halus saat stres sangat tinggi.
- Fade hitam untuk setiap transisi.

**Teks** memakai font monospace sistem, dengan font bawaan pygame sebagai cadangan. Catatan tampil dengan efek mesin ketik.

**Resolusi logis** 960×540, diskalakan otomatis mengikuti ukuran layar.

---

## 12. Audio

Semua suara dibuat dengan numpy saat game dimulai.

| Suara | Karakter | Kapan dan di mana |
|---|---|---|
| Dengung latar | Dua nada rendah (55 dan 82 Hz) ditambah desis, bergelombang pelan | Selalu ada, kecuali saat momen hening |
| Dengung latar sumbang | Versi yang sedikit fals | Dicampurkan saat stres tinggi |
| Ping sonar | Nada turun 1200→800 Hz dengan gema | Saat pemain memakai sonar |
| Ping peniru | Hampir sama dengan ping sonar, sedikit lebih rendah dan bergetar | Stereo, dari arah Pengamat |
| Langkah | Desis pendek. Saat lari lebih keras dan lebih rapat | Saat pemain bergerak |
| Detak jantung | Dua dentum rendah (lub-dub) | Mono, saat bahaya di atas 0,2 |
| Seretan Pendengar | Desis rendah yang bergelombang | Stereo, dalam jarak 250 px |
| Detak kedua (Pengamat) | Detak jantung yang teredam, 46 bpm | Stereo, dari arah Pengamat, dalam jarak 400 px |
| Napas Pengamat | Desis lembut yang naik-turun | Stereo, dalam jarak 110 px |
| Senter mati (Pengamat) | *Klik… klik-klik*, seperti senter yang baterainya habis | Stereo, dari arah Pengamat, setiap 6–12 detik |
| Dengung fragmen | Nada 220 + 330 Hz yang bergetar | Stereo, dalam jarak 400 px |
| Dengung pintu | Nada sangat rendah | Setelah pintu terbuka |
| Pintu terbuka | Dentuman berat, tapi pelan dan terdengar jauh | Stereo |
| Ambil fragmen | Denting lembut | |
| Ambil baterai / senter | Klik | |
| Dinding bergeser | Gesekan batu yang sangat pelan dari kejauhan | Stereo |
| Bisikan | Desis dengan warna suara orang | Kiri atau kanan secara acak |
| Tertangkap | Semua suara hilang, satu hantaman tumpul, lalu satu detak jantung terakhir | |

**Prinsip audio:**
- **Batas kekerasan suara.** Tidak ada efek suara yang lebih dari ±2× kerasnya dengung latar. Ini menjaga aturan tanpa jumpscare.
- **Hening dipakai sebagai alat.** Hilangnya suara adalah pertanda.
- Layar judul menyarankan pemain memakai earphone.
- Kalau perangkat audio tidak tersedia, game tetap berjalan tanpa suara.

---

## 13. Alur layar

```
Judul ──► Pilih kesulitan ──► Intro lantai ──► MAIN ◄──► Jeda (Lanjut / Catatan / Ke judul)
  ▲                                ▲             │
  │                                │             ├─ mati, nyawa masih ada ──► muncul lagi di pintu masuk
  │                                │             ├─ nyawa habis ──► "Percobaan ke-N berakhir." ──► Judul
  │                                └─────────────┤
  │                                              └─ masuk pintu keluar ──► lantai berikutnya
  │
  └──── Ending ◄── Lantai terakhir ◄── (setelah Lantai 5)
```

- **Intro lantai:** layar hitam dengan tulisan *"Lantai N"* dan sisa nyawa, masing-masing ±2 detik.
- **Menu jeda:** berisi daftar kontrol, catatan yang sudah ditemukan di run ini, dan sisa nyawa.

---

## 14. Data simpanan

Data disimpan di `~/.gema/save.json`:

- `percobaan`: jumlah run yang pernah dimulai
- `kematian`: jumlah nyawa yang pernah hilang
- `ending`: berapa kali ending pernah dicapai
- `lantai_terbaik`: lantai terdalam yang pernah dicapai, per tingkat kesulitan

Kalau file rusak, game diam-diam mulai dari awal lagi tanpa crash.

---

## 15. Scope

**Masuk:** semua yang tertulis di dokumen ini.

**Tidak masuk (untuk sekarang):**
- Aset gambar atau suara dari luar
- Dukungan controller
- Menu pengaturan (volume, kontrol)
- Bahasa lain selain Indonesia
- Lebih dari satu ending
- Checkpoint di tengah run
- Papan skor

---

## 16. Hal yang masih terbuka

- ~~**Nama di kredit.**~~ Sudah diputuskan: *v.obscura*.
- **Mengulang dari Lantai 1 saat nyawa habis.** Ini cukup kejam, terutama di Pekat. Kita pertahankan dulu, lalu dievaluasi saat playtest.
- **Semua angka di dokumen ini** akan disetel setelah playtest pertama (lihat checklist di `docs/PLAN.md`).
