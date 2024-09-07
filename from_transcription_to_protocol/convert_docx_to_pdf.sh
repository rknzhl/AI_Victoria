#!/bin/bash

docx_file="$1"
pdf_file="${docx_file%.docx}.pdf"
soffice --headless --convert-to pdf "$docx_file" --outdir .

echo "Файл $docx_file успешно преобразован в $pdf_file"