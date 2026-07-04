from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageStat
import textwrap

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'

def font(size=18, mono=False, bold=False):
    candidates = []
    if mono:
        candidates += ['/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf']
    if bold:
        candidates += ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']
    candidates += ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            pass
    return ImageFont.load_default()


def console_screenshots(log_path):
    text = Path(log_path).read_text(encoding='utf-8')
    lines = text.splitlines()
    chunks = [lines[i:i+34] for i in range(0, len(lines), 34)]
    paths = []
    for idx, chunk in enumerate(chunks, 1):
        w, h = 1500, 900
        img = Image.new('RGB', (w, h), (20, 24, 28))
        d = ImageDraw.Draw(img)
        title_font = font(24, mono=True, bold=True)
        line_font = font(18, mono=True)
        d.text((24, 18), f'Bukti Eksekusi Program - Bagian {idx}', font=title_font, fill=(235,235,235))
        y = 64
        for line in chunk:
            # shorten long lines
            if len(line) > 140:
                line = line[:137] + '...'
            fill = (205, 235, 205) if 'true' in line or 'valid' in line or 'same_content' in line or 'match' in line else (230,230,230)
            d.text((24, y), line, font=line_font, fill=fill)
            y += 23
        out = DOCS / f'console_log_part_{idx}.png'
        img.save(out)
        paths.append(out)
    return paths


def flow_diagram(path):
    w, h = 1600, 1000
    img = Image.new('RGB', (w, h), 'white')
    d = ImageDraw.Draw(img)
    title = font(34, bold=True)
    body = font(22)
    small = font(18)
    d.text((50, 35), 'Alur Sistem Kriptografi Hibrida + Steganografi', font=title, fill=(30,60,100))
    boxes = [
        (80,140,410,250,'Plaintext File','Hitung SHA-256'),
        (505,140,835,250,'AES-256-GCM','Enkripsi isi file'),
        (930,140,1260,250,'RSA-OAEP','Lindungi kunci AES'),
        (80,360,410,470,'DSA-SHA256','Tanda tangani paket'),
        (505,360,835,470,'Diffie-Hellman','Turunkan seed LSB'),
        (930,360,1260,470,'Modified LSB','Sisipkan paket ke gambar'),
        (505,600,835,710,'Stego PNG','File output rahasia'),
        (930,600,1260,710,'Dekripsi','Ekstrak, verifikasi, buka'),
    ]
    for x1,y1,x2,y2,t,sub in boxes:
        d.rounded_rectangle((x1,y1,x2,y2), radius=16, outline=(30,60,100), width=3, fill=(242,246,252))
        d.text((x1+20,y1+22), t, font=body, fill=(20,45,80))
        d.text((x1+20,y1+58), sub, font=small, fill=(60,60,60))
    def arrow(a,b):
        x1,y1=a; x2,y2=b
        d.line((x1,y1,x2,y2), fill=(150,40,40), width=4)
        # triangle
        import math
        angle=math.atan2(y2-y1,x2-x1)
        L=16
        pts=[]
        for da in [0, 2.6, -2.6]:
            pts.append((x2-L*math.cos(angle+da), y2-L*math.sin(angle+da)))
        d.polygon([(x2,y2), pts[1], pts[2]], fill=(150,40,40))
    arrow((410,195),(505,195)); arrow((835,195),(930,195)); arrow((670,250),(670,360)); arrow((410,415),(505,415)); arrow((835,415),(930,415)); arrow((1095,470),(670,600)); arrow((835,655),(930,655))
    d.text((80,820), 'Keluaran utama: gambar stego PNG. File asli hanya dapat dipulihkan jika kunci RSA, DSA, dan pasangan DH benar.', font=body, fill=(40,40,40))
    img.save(path)


def cover_vs_stego(path):
    cover = Image.open(ROOT/'samples/cover.png').convert('RGB').resize((620,413))
    stego = Image.open(ROOT/'docs/stego_raihan_demo.png').convert('RGB').resize((620,413))
    w,h = 1320,560
    img = Image.new('RGB',(w,h),'white')
    d=ImageDraw.Draw(img)
    title_font=font(30,bold=True); body=font(20)
    d.text((40,25),'Perbandingan Visual Cover Image dan Stego Image',font=title_font,fill=(30,60,100))
    img.paste(cover,(40,90)); img.paste(stego,(700,90))
    d.rectangle((40,90,660,503),outline=(30,60,100),width=3)
    d.rectangle((700,90,1320,503),outline=(30,60,100),width=3)
    d.text((40,515),'Cover image asli',font=body,fill=(40,40,40))
    d.text((700,515),'Stego image setelah payload disisipkan',font=body,fill=(40,40,40))
    img.save(path)


def lsb_diagram(path):
    w,h=1600,800
    img=Image.new('RGB',(w,h),'white'); d=ImageDraw.Draw(img)
    title=font(34,bold=True); body=font(24); mono=font(22,mono=True); small=font(19)
    d.text((60,40),'Konsep Modified Randomized LSB 2-bit',font=title,fill=(30,60,100))
    d.text((60,120),'Contoh satu byte piksel RGB sebelum penyisipan:',font=body,fill=(40,40,40))
    d.text((60,165),'11010110',font=mono,fill=(0,0,0))
    d.text((250,165),'LSB 2-bit lama = 10',font=small,fill=(90,90,90))
    d.text((60,240),'Potongan payload 2-bit yang akan disisipkan:',font=body,fill=(40,40,40))
    d.text((60,285),'01',font=mono,fill=(160,40,40))
    d.text((60,360),'Byte setelah penyisipan:',font=body,fill=(40,40,40))
    d.text((60,405),'11010101',font=mono,fill=(0,0,0))
    d.text((250,405),'LSB 2-bit baru = 01',font=small,fill=(90,90,90))
    d.rounded_rectangle((820,125,1500,560), radius=24, outline=(30,60,100), width=3, fill=(242,246,252))
    txt = [
        'Modifikasi yang digunakan:',
        '1. Posisi byte carrier tidak berurutan.',
        '2. Urutan carrier diacak memakai seed hasil DH-HKDF-SHA256.',
        '3. Setiap byte RGB membawa 2 bit payload.',
        '4. Payload dibingkai dengan magic bytes dan panjang data.',
        '5. Ekstraksi gagal jika seed/kunci DH salah.'
    ]
    y=155
    for i,line in enumerate(txt):
        d.text((850,y),line,font=body if i==0 else small,fill=(20,45,80) if i==0 else (40,40,40))
        y+=58 if i==0 else 46
    img.save(path)

console_screenshots(ROOT/'docs/demo_execution_log.txt')
flow_diagram(DOCS/'architecture_flow.png')
cover_vs_stego(DOCS/'cover_vs_stego.png')
lsb_diagram(DOCS/'lsb_diagram.png')
print('images created')
