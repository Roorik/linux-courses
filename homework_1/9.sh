#!/bin/bash

# Напишите скрипт, который добавляет суффикс _backup ко всем файлам в текущей директории. 
# Например, файл example.txt будет переименован в example_backup.txt.

for file in *.*; do
    base_name=${file%.*}
    extension=${file##*.}
    
    mv "$file" "${base_name}_backup.${extension}"
    
    done
