@echo off
nuitka ^
--msvc="latest" ^
--standalone ^
--remove-output ^
--include-data-file="string_records.json=." ^
--company-name="Cutleast" ^
--product-name="DSD Converter" ^
--file-version="1.2" ^
--product-version="1.2" ^
--file-description="DSD Converter" ^
--copyright="Attribution-NonCommercial-NoDerivatives 4.0 International" ^
--output-filename="esp2dsd.exe" ^
"converter.py"
