Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Get raw clipboard data
$data = [System.Windows.Forms.Clipboard]::GetDataObject()
if ($data.GetDataPresent([System.Windows.Forms.DataFormats]::Bitmap)) {
    $bitmap = $data.GetData([System.Windows.Forms.DataFormats]::Bitmap)
    $path = "$env:USERPROFILE\Desktop\clipboard_test2.png"
    $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    Write-Host "saved:$path"
    Write-Host "size:$($bitmap.Width)x$($bitmap.Height)"
} elseif ($data.GetDataPresent([System.Windows.Forms.DataFormats]::Dib)) {
    $dib = $data.GetData([System.Windows.Forms.DataFormats]::Dib)
    $ms = New-Object System.IO.MemoryStream
    $ms.Write($dib, 0, $dib.Length)
    $bitmap = New-Object System.Drawing.Bitmap($ms)
    $path = "$env:USERPROFILE\Desktop\clipboard_test2.png"
    $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    Write-Host "saved_from_dib:$path"
    Write-Host "size:$($bitmap.Width)x$($bitmap.Height)"
} else {
    $formats = $data.GetFormats()
    Write-Host "available_formats: $($formats -join ', ')"
}
