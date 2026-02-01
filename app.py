from flask import Flask, render_template_string, request, send_file
import yt_dlp
import os

app = Flask(__name__)

# Giao diện bạn đã chọn (Giữ nguyên giao diện đẹp của bạn)
HTML_CODE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>YT Downloader Pro - Online</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { background: #0b0f1a; font-family: 'Inter', sans-serif; }
        .card-custom { background: #161d2f; border: 1px solid #2d3748; transition: 0.3s; cursor: pointer; }
        .card-custom:hover { border-color: #ef4444; transform: translateY(-5px); }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4 text-white">
    <div class="max-w-3xl w-full">
        <div class="text-center mb-10">
            <h1 class="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-blue-500 mb-2">MY PRIVATE DOWNLOADER</h1>
            <p class="text-slate-400 uppercase tracking-widest text-xs font-bold">Chạy trên PythonAnywhere • No FFmpeg</p>
        </div>

        <form id="dlForm" action="/download" method="post" class="space-y-8">
            <input type="text" name="url" required placeholder="Dán link YouTube tại đây..." 
                class="w-full bg-[#1c2539] border-2 border-slate-700 rounded-3xl px-8 py-5 text-lg outline-none focus:border-red-500 transition-all">
            
            <div class="grid md:grid-cols-2 gap-6">
                <button type="submit" name="format" value="mp3" class="card-custom rounded-[2rem] p-8 text-center group">
                    <i class="fas fa-music text-3xl text-blue-500 mb-4 block"></i>
                    <h2 class="text-xl font-bold">TẢI NHẠC (MP3)</h2>
                </button>

                <button type="submit" name="format" value="mp4" class="card-custom rounded-[2rem] p-8 text-center group">
                    <i class="fas fa-video text-3xl text-red-500 mb-4 block"></i>
                    <h2 class="text-xl font-bold">TẢI VIDEO (MP4)</h2>
                </button>
            </div>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_CODE)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    mode = request.form.get('format')
    
    # PythonAnywhere yêu cầu dùng đường dẫn tuyệt đối cho thư mục tạm
    download_dir = '/home/lyvancuongklbg/mysite/downloads'
    if not os.path.exists(download_dir): os.makedirs(download_dir)

    ydl_opts = {
        'outtmpl': f'{download_dir}/%(title)s.%(ext)s',
        'quiet': True,
        'format': 'best[ext=mp4]/best' if mode == 'mp4' else 'bestaudio/best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            
            if mode == 'mp3':
                new_path = path.rsplit('.', 1)[0] + '.mp3'
                if os.path.exists(new_path): os.remove(new_path)
                os.rename(path, new_path)
                path = new_path
            
            return send_file(path, as_attachment=True)
    except Exception as e:
        return f"Lỗi: {str(e)}", 500

if __name__ == '__main__':
    app.run()