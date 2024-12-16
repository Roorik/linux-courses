#!/bin/bash

#У вас есть три текстовых файла: file1.txt, file2.txt и file3.txt. Напишите команду, которая объединит содержимое этих файлов в один новый файл под названием combined.txt.
file1="example-files/file1.txt"
file2="example-files/file2.txt"
file3="example-files/file3.txt"

cat "$file1" "$file2" "$file3" > ./example-files/combined.txt