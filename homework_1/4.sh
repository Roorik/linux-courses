#!/bin/bash

# Напишите скрипт, который находит и удаляет все файлы старше 5 дней в указанной директории.

dir=$1

find $dir -mindepth 1 -mtime +5 -delete