document.getElementById('uploadForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const file = document.getElementById('fileInput').files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);

  // 注意：若你把前端托管在 GitHub Pages，请把下面的 URL 换成 Render 给的完整地址
  const apiUrl = '/api/v1/process';      // Render 上直接使用根路径即可
  // const apiUrl = 'https://ai-cleaner.onrender.com/api/v1/process'; // 如需硬编码，请改成你的 Render URL

  const resp = await fetch(apiUrl, {
    method: 'POST',
    body: formData
  });

  if (!resp.ok) {
    alert('处理出错，请打开浏览器控制台查看详情');
    console.error(await resp.text());
    return;
  }

  const data = await resp.json();

  // 填充结果
  document.getElementById('origScore').textContent = (data.ai_prob_original * 100).toFixed(1) + '%';
  document.getElementById('refinedScore').textContent = (data.ai_prob_refined * 100).toFixed(1) + '%';
  document.getElementById('origText').textContent = data.original_text;
  document.getElementById('refinedText').textContent = data.refined_text;

  const dl = document.getElementById('downloadLink');
  dl.href = data.download_url;
  dl.textContent = `下载（约 ${data.token_usage} token）`;

  document.getElementById('resultSection').style.display = 'block';
});