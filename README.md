## **Rozpoznávání textu v komixech**

###### **Lukáš Vlček, Bakalářská práce 2021**

### **O programu**

Navržený a implementovaný program slouží k automatické detekci komixových bublin v obrázku a následnému provedení
rozpoznání textu (OCR). Program vznikl jako bakalářská práce.

### **Popis spuštění programu**

Program je vytvořen jako Python skript. Po dokončení instalace všech částí (viz sekce Instalace) je možné jej spustit
následujícím příkazem:

`python main.py <input_file> <output_mask> <output_json>`

kde:  
`<input_file>` je cesta ke vstupnímu souboru (obrázku komixové stránky),  
`<output_mask>` je cesta, kam bude uložena maska detekovaných komixových bublin,  
`<output_json>` je cesta, kam bude uložen výsledný datový soubor ve formátu JSON

Ke spuštění je možné zároveň přidat některý z nepovinných parametrů:  
`--verbose-level <level>`: nastaví intenzitu výstupů, povolené levely: 0 - None (žádný výstup), 1 - Warning (chybové
hlášení a varování), 2 - Info (info o průběhu zpracování), 3 - Debug (informace o důvodu vyřazení každého kandidáta na
bublinu)   
`--verbose`: nastaví level intenzity výstupů na 3 (Debug)     
`--save-bubbles <directory>` po rozpoznání komixových bublin budou jednotlivé komixové bubliny uloženy do uvedené složky

Příkaz spuštění programu byl navržen s ohledem na předpokládané využití ve skriptech.

### **Konfigurace**

Konfiguraci parametrů používaných pro účely filtrování kandidátů na komixové bubliny a OCR je možné provést v
souboru `config.py`. V tomto souboru neprovádějte žádné jiné změny než změny číselných parametrů. Odebrání některých
konfigurací či změnou jejich názvů může dojít k nepředvídatelnému chování aplikace či pádu.

### **Instalace**

- Nainstalujte `Python3` (testováno v verzi 3.8.6).
- Nainstalujte Python knihovny `OpenCV`, `Numpy`, `pytesseract` a pro validační skripty `editdistance`. Instalaci
  potřebných knihoven je možné provést příkazem `python -m pip install -r requirements.txt`
- Nainstalujte `Tesseract` (viz https://tesseract-ocr.github.io/tessdoc/Installation.html)
- Do složky s konfiguracemi Tesseractu zkopírujte soubor `tesseract-config/comics` (složka konfigurací Tesseractu se
  obvykle nachází v cestě /usr/share/tesseract-ocr/4.00/tessdata/configs)

### **Validace výsledků**

Pro ověření úspěšnosti navrženého programu je možné zvalidovat výsledky oproti ručně anotovanému gt. K tomuto účelu je
navržen skript `validation.py` s očekávaným spuštěním:

`python validation.py <test_images_dir> <results_base_dir> <masks_base_dir> <ocr_base_dir>`

kde:  
`<test_images_dir>` je cesta složky, ve které se nacházejí původní komixové stránky (1 soubor = 1 stránka),  
`<results_base_dir>` je cesta složky, do které budou uloženy výsledky validace, pro každou vstupní stránku bude
vytvořena jedna podsložka obsahující veškerá naměřená data,  
`<masks_base_dir>` je cesta složky, ve které se nacházejí anotované bublinové masky odpovídající vstupním stránkám.
Program očekává, že název souboru anotované bublinové masky odpovídá názvu vstupního obrázku (s moností suffixu _
bubble_gt)  
`<ocr_base_dir>` je cesta složky, ve které se nacházejí anotované texty v bublinách. Program v této složce očekává pro
každý vstupní soubor podsložku s názvem odpovídajícím vstupnímu souboru bez přípony, ve které se nachází soubor
odpovídající názvu vstupního souboru s příponou .txt, tedy například pro vstupní soubor image.png očekává existenci
souboru <ocr_base_dir>/image/image.txt

#### **Formát anotovaných dat**

**Anotované bubliny:** Obrázek o stejné velikosti, jako je velikost obrázku ve vstupním souboru, pixely, které náleží
bublině (včetně textu) jsou označeny bílou barvou (8bitová barevná hloubka, 1 barevný kanál, tedy bílá má hodnotu 255) a
pixely, které bublině nenáleží jsou označeny černou barvou (hodnota pixelu 0).

**Anotovaný text v bublinách:** Soubor ve formátu JSON, který obsahuje pole textů a pozice (x,y, width, height) opsaného
obdélníku. Například tedy:
`[
{
"baloonTextId": 0,
"text": "BUT I HAVE A\nBAD FEELING...\n",
"emotionType": "NEUTRAL",
"dialogAct": "FEEDBACK",
"markableObject": "BALOON_TEXT",
"coordX": 217,
"coordY": 56,
"pixelWidth": 204,
"pixelHeight": 75 } , ...
]
`