#!/bin/bash

# Solicita a mensagem de commit
echo "Digite a mensagem do commit:"
read mensagem

# Adiciona mudanças, faz o commit e envia para o GitHub
git add .
git commit -m "$mensagem"
git push origin master
