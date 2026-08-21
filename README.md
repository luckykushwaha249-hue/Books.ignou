# Books.IGNOU

100% offline Android app — sirf **4 files**:

| File | Kaam |
|---|---|
| `main.py` | Poori app ki logic (Python) |
| `books.kv` | UI design (Kivy auto-load kar leta hai, kyunki App class ka naam `BooksApp` hai) |
| `buildozer.spec` | Android APK banane ki config |
| `README.md` | Yeh file |

## App kya karti hai
- Top-right **3 dot menu** → Home / Settings / Theme
- **Home**: 6 semester cards. Jisme file hai wo card **dark/highlighted**, khaali wala **light**. Tap karte hi file offline open ho jaati hai.
- **Settings**: har semester ke saamne Upload / Change / Delete button.
- **Theme**: Light / Dark / System — turant apply.
- Ek baar file upload karne ke baad **koi internet nahi chahiye**.

## GitHub se APK kaise banayein (Actions ke through)

1. Is folder (`main.py`, `books.kv`, `buildozer.spec`) ko apne repo me push karo.
2. Repo me `.github/workflows/build.yml` naam se yeh file khud bana lo (paste kar do):

```yaml
name: Build APK
on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install system deps
        run: |
          sudo apt update
          sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev cmake libffi-dev libssl-dev
      - name: Install buildozer
        run: pip install buildozer cython
      - name: Build APK
        run: buildozer -v android debug
      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: BooksIgnou-debug-apk
          path: bin/*.apk
```

3. GitHub ke **Actions** tab me jaake workflow run hone do (isme 20–30 min tak lag sakte hain, pehli baar Android SDK/NDK download hota hai).
4. Run complete hone par **Artifacts** section se APK download karo, phone me install karo (Unknown sources allow karna hoga).

## Apne computer (Linux/WSL) par khud build karna

```bash
pip install buildozer cython
buildozer android debug
```
APK `bin/` folder me ban jayega.

## Local test (bina Android ke, seedha computer pe)

```bash
pip install kivy kivymd plyer
python main.py
```

## Notes
- File open / theme-detect wala code Android-specific (`pyjnius`) hai — desktop pe chalane par woh hisse fallback se kaam karenge (file default app se khulegi, theme "Light" rahega jab tak khud na badlo).
- Apna app icon lagane ke liye `icon.png` isi folder me daal do aur `buildozer.spec` me `icon.filename` line ko uncomment kar do.
