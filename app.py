from flask import Flask, render_template_string, request, send_file, after_this_request
import yt_dlp
import os

app = Flask(__name__)

# Giao diện đồng bộ với phong cách bạn đã chọn
HTML_CODE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MY DOWNLOADER - RENDER</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { background: #0b0f1a; font-family: 'Inter', sans-serif; color: white; }
        .card { background: #161d2f; border: 1px solid #2d3748; transition: 0.3s; cursor: pointer; border-radius: 2rem; }
        .card:hover { border-color: #ef4444; transform: translateY(-5px); }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
    <div class="max-w-3xl w-full">
        <div class="text-center mb-10">
            <h1 class="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-blue-500 mb-2">MY DOWNLOADER</h1>
            <p class="text-slate-400 text-xs font-bold uppercase tracking-widest italic">Render Engine • No FFmpeg</p>
        </div>

        <form action="/download" method="post" class="space-y-8">
            <input type="text" name="url" required placeholder="Dán link YouTube tại đây..." 
                class="w-full bg-[#1c2539] border-2 border-slate-700 rounded-3xl px-8 py-5 text-lg outline-none focus:border-red-500 transition-all">
            
            <div class="grid md:grid-cols-2 gap-6">
                <button type="submit" name="format" value="mp3" class="card p-8 text-center group">
                    <i class="fas fa-music text-3xl text-blue-500 mb-4 block"></i>
                    <h2 class="text-xl font-bold">TẢI NHẠC (MP3)</h2>
                </button>
                <button type="submit" name="format" value="mp4" class="card p-8 text-center group">
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
    
    # Render sử dụng thư mục /tmp để lưu file tạm
    tmp_dir = '/tmp/downloads'
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    ydl_opts = {
        'outtmpl': f'{tmp_dir}/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        # Sử dụng cookies để tránh bot detection
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
        # 'b' chọn định dạng tốt nhất có sẵn cả hình và tiếng (thường là 720p)
        # 'bestaudio' chọn âm thanh tốt nhất
        'format': 'b/best' if mode == 'mp4' else 'bestaudio/best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            original_path = ydl.prepare_filename(info)
            
            # Xử lý đổi tên file để đảm bảo đúng đuôi người dùng muốn (No-FFmpeg hack)
            base, ext = os.path.splitext(original_path)
            target_ext = '.mp3' if mode == 'mp3' else '.mp4'
            final_path = base + target_ext
            
            if os.path.exists(final_path):
                os.remove(final_path)
            os.rename(original_path, final_path)

            @after_this_request
            def cleanup(response):
                try:
                    if os.path.exists(final_path):
                        os.remove(final_path)
                except Exception:
                    pass
                return response

            return send_file(final_path, as_attachment=True)
            
    except Exception as e:
        return f"<body style='background:#0b0f1a;color:#ef4444;padding:20px;font-family:sans-serif'><h2>Lỗi hệ thống:</h2><p>{str(e)}</p><a href='/' style='color:white'>Quay lại</a></body>", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
