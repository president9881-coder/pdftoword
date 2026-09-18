import os
import random
from flask import Flask, request, render_template_string, send_file
from pdf2docx import Converter

app = Flask(__name__)
os.makedirs('uploads', exist_ok=True)

# A list of high quality technology images from Unsplash
TECH_IMAGES = [
    "https://images.unsplash.com/photo-1518770660439-4636190af475?w=500&q=80",
    "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=500&q=80",
    "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=500&q=80",
    "https://images.unsplash.com/photo-1517433670267-08bbd4be890f?w=500&q=80",
    "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=500&q=80"
]

# Updated HTML layout with a responsive sidebar for tech images
HTML_PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PDF2WORD Converter</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    .loader {
      border-top-color: #3498db;
      -webkit-animation: spinner 1.5s linear infinite;
      animation: spinner 1.5s linear infinite;
    }
    @keyframes spinner {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  </style>
</head>
<body class="bg-gray-50 min-h-screen font-sans">
  
  <div class="max-w-6xl mx-auto px-4 py-12 flex flex-col md:flex-row gap-8 items-start">
    
    <!-- Main Converter Column -->
    <div class="w-full md:w-2/3 lg:w-3/4">
      <div class="bg-white p-10 rounded-2xl shadow-xl border border-gray-100 text-center">
        <!-- Branding -->
        <div class="flex justify-center mb-4">
          <div class="bg-blue-600 text-white font-black text-2xl px-4 py-2 rounded-lg tracking-wider">
            PDF<span class="text-blue-200">2</span>WORD
          </div>
        </div>
        
        <p class="text-gray-500 mb-8 font-medium">Instantly convert your PDF documents to editable Word files.</p>
        
        <!-- Upload Form -->
        <form method="post" enctype="multipart/form-data" class="space-y-6" onsubmit="document.getElementById('loading').style.display='block'; document.getElementById('submit-btn').style.display='none';">
          
          <div class="border-2 border-dashed border-blue-300 rounded-xl p-8 bg-blue-50 hover:bg-blue-100 transition duration-300 relative group cursor-pointer">
            <input type="file" name="file" accept=".pdf" required 
                   class="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
                   onchange="document.getElementById('file-name').innerText = this.files[0].name">
            <div class="text-blue-600">
              <svg class="mx-auto h-12 w-12 mb-3" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
              <span id="file-name" class="font-semibold text-lg">Click to browse or drag PDF here</span>
            </div>
          </div>

          <button id="submit-btn" type="submit" 
                  class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-4 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 text-lg">
            Convert to Word
          </button>

          <!-- Loading Spinner -->
          <div id="loading" class="hidden">
            <div class="flex justify-center items-center space-x-3">
              <div class="loader ease-linear rounded-full border-4 border-t-4 border-gray-200 h-8 w-8"></div>
              <span class="text-blue-600 font-semibold animate-pulse">Converting... Please wait.</span>
            </div>
          </div>

        </form>
        
        <p class="text-xs text-gray-400 mt-8">Files are processed securely and deleted automatically.</p>
      </div>
    </div>

    <!-- Sidebar Column for Tech Images -->
    <div class="w-full md:w-1/3 lg:w-1/4 flex flex-col gap-6">
      <div class="text-xs text-gray-400 uppercase tracking-widest font-bold mb-2"></div>
      
      <!-- Jinja2 Loop to display the randomly selected images -->
      {% for img_url in images %}
      <div class="bg-white border border-gray-200 rounded-xl p-2 shadow-sm flex flex-col items-center justify-center relative overflow-hidden group">
        <img src="{{ img_url }}" alt="Technology Scene" class="w-full h-48 object-cover rounded-lg group-hover:scale-105 transition-transform duration-500">
      </div>
      {% endfor %}
      
    </div>

  </div>

</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.pdf'):
            pdf_path = os.path.join('uploads', file.filename)
            docx_filename = file.filename.rsplit('.', 1)[0] + '.docx'
            docx_path = os.path.join('uploads', docx_filename)
            
            # Save the uploaded PDF
            file.save(pdf_path)
            
            # Use the pdf2docx tool to convert it
            cv = Converter(pdf_path)
            cv.convert(docx_path)
            cv.close()
            
            # Send the finished DOCX back to the user to download
            return send_file(docx_path, as_attachment=True)
            
    # Randomly select 1 or 2 unique images from the list on each page load
    image_count = random.randint(1, 2)
    selected_images = random.sample(TECH_IMAGES, image_count)
    
    return render_template_string(HTML_PAGE, images=selected_images)

if __name__ == '__main__':
    # Dynamically bind to the port Render provides
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
