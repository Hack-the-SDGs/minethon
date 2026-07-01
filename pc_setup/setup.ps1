# minethon setup — encrypted, password-gated. Run once per student PC.
$ErrorActionPreference = 'Stop'
$sec = Read-Host -AsSecureString "Password"
$pw = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
$blob = [Convert]::FromBase64String('U2FsdGVkX1/Bwjhj7M35V0MNiWx3Lj87qs20BZcyKdfjXOd03VUSUCwUJ0UbergBgTs9i2s753SQwzt3KQHNK6mSZD68yN3v1+QqGuD7cFEqrEyOk0P7X5q+4KNWyA0mDZQCnBr20VDnOSkUwVFUB2JHZW0yk6qSnS2WHPcfj7T3E11jgOGoZKHvthRcOIPmPxkN6Ae2lLN5/VNc5oUX0R2auJfJITOqbQ2vQLQtB5aDnr5wO11IK5CwCAYVDA2qeiHPvcN+Cphoivmma7ecD5KbztG3NQ9Rjz3W9Rfl+XgYnI3YYHxRaFBvA4DpKlI/1nUBaYpygJYY0Q/Bc6zMDTGpFlBAdx3bfpOWY2dumhz6EM8vNQDOMseaWyHJVUDR4ubdZx2kDnsRHvA7d6zl/1IYdjZH3QcZSFUu4YEASOgOpEaJWBMY+z1NVS74koR+4MUI0rhwLyFLwkwYeV4/zyKNCXOFdGMSa9tQFBSRD0wibpVCAlAFikjiJ18m2RUuoSOgRKUSU+WB2+aDNkbIBGBxovl0K4Uoq1vJo1VqLo8=')
# openssl "Salted__" format: magic(8) + salt(8) + ciphertext
$salt = $blob[8..15]
$ct = [byte[]]($blob[16..($blob.Length - 1)])
$kdf = New-Object System.Security.Cryptography.Rfc2898DeriveBytes(
    $pw, [byte[]]$salt, 100000, [System.Security.Cryptography.HashAlgorithmName]::SHA256)
$keyiv = $kdf.GetBytes(48)
$aes = [System.Security.Cryptography.Aes]::Create()
$aes.Key = $keyiv[0..31]; $aes.IV = $keyiv[32..47]
$aes.Mode = 'CBC'; $aes.Padding = 'PKCS7'
try {
    $plain = [Text.Encoding]::UTF8.GetString(
        $aes.CreateDecryptor().TransformFinalBlock($ct, 0, $ct.Length))
} catch {
    Write-Error "密碼錯誤或解密失敗"; exit 1
}
Invoke-Expression $plain
