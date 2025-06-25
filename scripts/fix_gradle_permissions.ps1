# Script PowerShell para corrigir permissões da pasta .gradle
# Dá controle total ao usuário atual

$gradlePath = "$env:USERPROFILE\.gradle"

if (!(Test-Path $gradlePath)) {
    Write-Host "Criando pasta: $gradlePath"
    New-Item -ItemType Directory -Path $gradlePath | Out-Null
}

Write-Host "Definindo permissões de Controle Total para o usuário atual em: $gradlePath"

$acl = Get-Acl $gradlePath
$user = "$env:USERDOMAIN\$env:USERNAME"
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule($user, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
$acl.SetAccessRule($accessRule)
Set-Acl $gradlePath $acl

Write-Host "Permissões corrigidas com sucesso! Agora execute o Android Studio como administrador e tente novamente." 