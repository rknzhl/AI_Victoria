#!/bin/bash

# Получаем путь к исходному .docx файлу
docx_file="$1"

# Извлекаем директорию, в которой находится .docx файл
docx_dir=$(dirname "$docx_file")

# Формируем имя выходного файла
pdf_file="${docx_file%.docx}.pdf"

# Переходим в директорию, где находится .docx файл
cd "$docx_dir"

# Конвертируем .docx в .pdf
soffice --headless --convert-to pdf "$(basename "$docx_file")" --outdir .

echo "Файл $docx_file успешно преобразован в $pdf_file"
