$content = Get-Content -Raw -Path "C:\git\voynich\_template_source.py" -Encoding UTF8
Set-Content -Path "C:\git\voynich\phases\RI_FUNCTIONAL_IDENTITY\scripts\line_type_comparison.py" -Value $content -Encoding UTF8 -NoNewline
Write-Host "Script written"
