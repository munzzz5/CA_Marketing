async function fetchJSON(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || `Request failed: ${response.status}`);
  }
  if (response.status === 204) return null;
  return response.json();
}

async function loadKeywords() {
  const keywords = await fetchJSON('/keywords');
  const list = document.getElementById('keyword-list');
  list.innerHTML = '';

  keywords.forEach((k) => {
    const li = document.createElement('li');
    li.innerHTML = `${k.keyword} [${k.category ?? 'Custom'}] priority:${k.priority} active:${k.is_active}
      <button data-id="${k.id}" class="delete-btn">Delete</button>`;
    list.appendChild(li);
  });

  document.querySelectorAll('.delete-btn').forEach((btn) => {
    btn.addEventListener('click', async () => {
      await fetchJSON(`/keywords/${btn.dataset.id}`, { method: 'DELETE' });
      await loadKeywords();
    });
  });
}

async function loadContent() {
  const content = await fetchJSON('/content');
  const list = document.getElementById('content-list');
  list.innerHTML = '';

  content.forEach((c) => {
    const li = document.createElement('li');
    li.innerHTML = `<b>${c.title}</b> (${c.content_type}, score:${c.relevance_score})
      <button data-id="${c.id}" class="idea-btn">Generate Ideas</button>`;
    list.appendChild(li);
  });

  document.querySelectorAll('.idea-btn').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const ideas = await fetchJSON(`/ideas/generate/${btn.dataset.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea_type: 'CampaignIdea', max_ideas: 2 }),
      });
      alert(`Generated ${ideas.length} ideas`);
    });
  });
}

async function loadDigest() {
  const digest = await fetchJSON('/digest/preview');
  document.getElementById('digest-view').textContent = JSON.stringify(digest, null, 2);
}

document.getElementById('keyword-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    keyword: document.getElementById('keyword').value,
    category: document.getElementById('category').value,
    priority: Number(document.getElementById('priority').value),
    is_active: true,
  };

  await fetchJSON('/keywords', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  e.target.reset();
  document.getElementById('priority').value = 1;
  await loadKeywords();
});

document.getElementById('refresh-keywords').addEventListener('click', loadKeywords);
document.getElementById('run-scrape').addEventListener('click', async () => {
  const result = await fetchJSON('/scrape/run', { method: 'POST' });
  alert(`Processed ${result.processed_keywords} keywords`);
});
document.getElementById('run-classify').addEventListener('click', async () => {
  const result = await fetchJSON('/classify/run', { method: 'POST' });
  alert(`Classified ${result.classified_records} rows`);
});
document.getElementById('load-content').addEventListener('click', loadContent);
document.getElementById('load-digest').addEventListener('click', loadDigest);

loadKeywords();
