if (-Not (Test-Path .\ffmpeg))
{
	$ProgressPreference = 'SilentlyContinue'
	Invoke-WebRequest 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip' -OutFile .\ffmpeg.zip

	Expand-Archive .\ffmpeg.zip .\
	Rename-Item .\ffmpeg-master-latest-win64-gpl-shared .\ffmpeg
	Remove-Item .\ffmpeg.zip
}
