// --- FOLDER SELECTION ---
document.getElementById('selectFolderBtn').addEventListener('click', async () => {
    try {
        const response = await fetch('/select_folder', { method: 'POST' });
        const data = await response.json();
        if (data.status === 'success') {
            // Beautify path: show only last folder
            const parts = data.path.split(/[/\\]/);
            const shortPath = parts[parts.length - 1] || data.path;
            document.getElementById('currentPath').innerText = `... \\ ${shortPath.toUpperCase()}`;
            addLog(`DOSSIER DÉFINI : ${data.path}`, 'info');
        } else if (data.status === 'cancelled') {
            // Do nothing
        }
    } catch (err) {
        addLog(`ERREUR SÉLECTION DOSSIER : ${err}`, 'error');
    }
});

document.getElementById('openFolderBtn').addEventListener('click', async () => {
    try {
        await fetch('/open_folder', { method: 'POST' });
        addLog(`DOSSIER OUVERT`, 'info');
    } catch (err) {
        addLog(`ERREUR OUVERTURE DOSSIER : ${err}`, 'error');
    }
});

// --- DOWNLOAD FORM ---
document.getElementById('downloadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const input = document.getElementById('queryInput');
    const formatSelect = document.getElementById('formatSelect');
    const checkbox = document.getElementById('noCoverCheckbox');
    const btn = document.querySelector('button.main-btn');
    const query = input.value.trim();
    const format = formatSelect.value;
    const noCover = checkbox.checked;

    if (!query) return;

    // Trigger Visuals
    triggerLightning();

    if (query.toLowerCase() === 'marto') {
        addLog('MODE MARTO ACTIVÉ : FRENESIE!', 'warning');
        triggerMartoFrenzy();
        input.value = '';
        return;
    }

    // UI Feedback
    input.disabled = true;
    formatSelect.disabled = true;
    checkbox.disabled = true;
    btn.disabled = true;
    btn.innerText = "INITIALISATION...";
    document.querySelector('.log-container').classList.add('active');

    addLog(`DÉMARRAGE SÉQUENCE : ${query} [Mode Léger: ${noCover ? 'OUI' : 'NON'}]`, 'info');

    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query, no_cover: noCover, format: format })
        });

        const data = await response.json();

        if (data.status === 'success') {
            triggerLightning(); // Success flash
            addLog(`MISSION ACCOMPLIE : ${data.title}`, 'success');
        } else {
            addLog(`ÉCHEC : ${data.message}`, 'error');
        }

    } catch (err) {
        addLog(`ERREUR CRITIQUE SYSTÈME : ${err.message}`, 'error');
    } finally {
        // Reset UI
        input.disabled = false;
        formatSelect.disabled = false;
        checkbox.disabled = false;
        btn.disabled = false;
        btn.innerText = "TÉLÉCHARGER";
        input.value = '';
        input.focus();
        document.querySelector('.log-container').classList.remove('active');
    }
});

function addLog(msg, type) {
    const log = document.getElementById('log');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    const time = new Date().toLocaleTimeString().split(' ')[0];
    entry.innerText = `[${time}] ${msg}`;
    log.prepend(entry);
}

// --- VISUALS: CANVAS STORM ---
const canvas = document.getElementById('stormCanvas');
const ctx = canvas.getContext('2d');

let width, height;
let particles = [];
let mouse = { x: 0, y: 0 };
let lightningFlash = 0;

function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
}
window.addEventListener('resize', resize);
resize();

window.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
    // Add sparkles on mouse move
    if (Math.random() > 0.5) {
        particles.push(new Particle(mouse.x, mouse.y, true));
    }
});

class Particle {
    constructor(x, y, isMouse = false) {
        this.x = x || Math.random() * width;
        this.y = y || Math.random() * height;
        this.vx = (Math.random() - 0.5) * 2;
        this.vy = (Math.random() - 0.5) * 2;
        this.life = 1.0;
        this.isMouse = isMouse;
        this.color = isMouse ? '200, 200, 255' : '100, 100, 120';
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.life -= 0.01;
        if (this.isMouse) this.life -= 0.02; // Fade faster
    }

    draw() {
        ctx.fillStyle = `rgba(${this.color}, ${this.life * 0.5})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.isMouse ? 2 : 1, 0, Math.PI * 2);
        ctx.fill();
    }
}

function triggerLightning() {
    lightningFlash = 1.0;
    setTimeout(() => { lightningFlash = 0.5; }, 50);
    setTimeout(() => { lightningFlash = 0.8; }, 100);
    setTimeout(() => { lightningFlash = 0.0; }, 200);
}

// Lightning Bolts
function drawLightning() {
    if (Math.random() > 0.998) {
        // Random background flash
        ctx.fillStyle = `rgba(255, 255, 255, ${Math.random() * 0.05})`; // Very subtle
        ctx.fillRect(0, 0, width, height);
    }
}



// --- HAMMER LIGHTNING ---
function drawJaggedLine(x1, y1, x2, y2, color) {
    const dist = Math.hypot(x2 - x1, y2 - y1);
    const steps = dist / 10;

    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.shadowBlur = 10;
    ctx.shadowColor = color;

    let cx = x1;
    let cy = y1;
    ctx.moveTo(cx, cy);

    for (let i = 0; i < steps; i++) {
        // Interpolate towards end
        const progress = (i + 1) / steps;
        const targetX = x1 + (x2 - x1) * progress;
        const targetY = y1 + (y2 - y1) * progress;

        // Add jitter
        const jitter = (Math.random() - 0.5) * 50;

        cx = targetX + (Math.random() - 0.5) * 20; // Some drift
        cy = targetY + jitter;

        ctx.lineTo(cx, cy);
    }

    ctx.stroke();
    ctx.shadowBlur = 0; // Reset
}

function spawnHammerLightning() {
    const hammers = document.querySelectorAll('.hammer-decor');
    if (hammers.length === 0) return;

    // Pick random hammer
    const hammer = hammers[Math.floor(Math.random() * hammers.length)];
    const rect = hammer.getBoundingClientRect();

    // Approximate "Head" position - let's say near top center of rect
    // Since they are rotated, it's roughly center
    const startX = rect.left + rect.width / 2;
    const startY = rect.top + rect.height / 3;

    // End point - somewhere random in the sky or ground, but generally outwards
    const endX = startX + (Math.random() - 0.5) * 600;
    const endY = startY + (Math.random() - 0.5) * 600;

    drawJaggedLine(startX, startY, endX, endY, 'rgba(192, 132, 252, 0.8)');

    // Add a flash
    lightningFlash = 0.1; // Purple tinted flash?
}

// Override animate to include hammer lightning
function animate() {
    // Clear with fade effect for trails
    ctx.fillStyle = 'rgba(5, 5, 5, 0.2)';
    ctx.fillRect(0, 0, width, height);

    // Flash
    if (lightningFlash > 0.01) {
        // If it's a big flash, white. If small, maybe purple?
        // Let's keep it white/bluish for general, or use tint
        ctx.fillStyle = `rgba(180, 160, 255, ${lightningFlash * 0.5})`; // Reduce intensity by half
        ctx.fillRect(0, 0, width, height);
        lightningFlash *= 0.80; // Fade faster
    } else {
        lightningFlash = 0;
    }

    // Particles
    if (particles.length < 50) {
        particles.push(new Particle());
    }

    for (let i = particles.length - 1; i >= 0; i--) {
        let p = particles[i];
        p.update();
        p.draw();
        if (p.life <= 0) particles.splice(i, 1);
    }

    drawLightning();

    // Hammer Lightning Chance
    // Much reduced chance: 0.5% per frame instead of 2%
    if (Math.random() > 0.995) {
        spawnHammerLightning();
    }

    requestAnimationFrame(animate);
}

// --- HAMMER INTERACTION ---
document.querySelectorAll('.hammer-decor').forEach(hammer => {
    hammer.addEventListener('click', (e) => {
        // Prevent spamming
        if (hammer.classList.contains('striking')) return;

        hammer.classList.add('striking');

        // Trigger impact effect at 50% of animation (when it hits)
        setTimeout(() => {
            triggerLightning(); // Big flash
            spawnHammerLightning(); // Sparks

            // Shake effect
            document.querySelector('.container').style.transform = `translate(${Math.random() * 10 - 5}px, ${Math.random() * 10 - 5}px)`;
            setTimeout(() => { document.querySelector('.container').style.transform = 'none'; }, 100);

        }, 300); // 300ms is half of 0.6s animation

        // Reset class
        setTimeout(() => {
            hammer.classList.remove('striking');
        }, 650);
    });
});


animate();

function triggerMartoFrenzy() {
    let duration = 60000; // 60 seconds
    let interval = 400; // Strike every 400ms
    let endTime = Date.now() + duration;

    const hammers = document.querySelectorAll('.hammer-decor');

    let frenzyInterval = setInterval(() => {
        if (Date.now() > endTime) {
            clearInterval(frenzyInterval);
            addLog('MODE MARTO TERMINÉ', 'info');
            return;
        }

        // Randomly strike with hammers
        hammers.forEach(h => {
            // Artificial click
            h.click();
        });

    }, interval);
}

// Init: Beautify initial path
(function beautifyInitialPath() {
    const el = document.getElementById('currentPath');
    const fullPath = el.innerText;
    if (fullPath) {
        const parts = fullPath.split(/[/\\]/);
        const shortPath = parts[parts.length - 1] || fullPath;
        el.innerText = `... \\ ${shortPath.toUpperCase()}`;
    }
})();


// --- PLAYER & LIBRARY LOGIC ---

// NAVIGATION
const views = {
    'search-view': document.getElementById('search-view'),
    'library-view': document.getElementById('library-view')
};
const navBtns = document.querySelectorAll('.nav-btn');

navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        // Update buttons
        navBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Update views
        const targetId = btn.getAttribute('data-target');
        Object.values(views).forEach(v => v.classList.remove('active'));
        if (views[targetId]) views[targetId].classList.add('active');

        // If library, refreshIfNeeded
        if (targetId === 'library-view' && !libraryLoaded) {
            fetchLibrary();
        }
    });
});

// LIBRARY
let libraryLoaded = false;
let playlist = [];
let currentTrackIndex = -1;
const libraryList = document.getElementById('libraryList');
const refreshLibraryBtn = document.getElementById('refreshLibraryBtn');

refreshLibraryBtn.addEventListener('click', fetchLibrary);

async function fetchLibrary() {
    libraryList.innerHTML = '<div class="loading">CHARGEMENT...</div>';
    try {
        const res = await fetch('/api/library');
        const data = await res.json();

        if (data.status === 'success') {
            renderLibrary(data.tracks);
            playlist = data.tracks; // Simple playlist = all tracks
            libraryLoaded = true;
        } else {
            libraryList.innerHTML = `<div class="log-entry error">ERREUR: ${data.message}</div>`;
        }
    } catch (e) {
        libraryList.innerHTML = `<div class="log-entry error">ERREUR RESEAU</div>`;
    }
}

function renderLibrary(tracks) {
    libraryList.innerHTML = '';
    if (tracks.length === 0) {
        libraryList.innerHTML = '<div style="text-align:center;color:#666;">AUCUN SON TROUVÉ</div>';
        return;
    }

    let currentFolder = '';

    tracks.forEach((track, index) => {
        // Group by folder? Maybe simple list is better for now
        const el = document.createElement('div');
        el.className = 'track-item';

        // Format title
        let displayTitle = track.title;
        let displayMeta = track.folder === 'Singles' ? '' : track.folder;

        el.innerHTML = `
            <div class="track-info" onclick="playTrack(${index})">
                <div class="track-title">${displayTitle}</div>
                <div class="track-meta">${displayMeta}</div>
            </div>
            <div class="track-actions">
                <button class="action-btn" onclick="playTrack(${index})">▶</button>
                <button class="action-btn" onclick="saveToPhone('${track.path.replace(/'/g, "\\'")}')">💾</button>
            </div>
        `;
        libraryList.appendChild(el);
    });
}

// AUDIO PLAYER
const audioPlayer = document.getElementById('audioPlayer');
const playerBar = document.getElementById('playerBar');
const playBtn = document.getElementById('playBtn');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const progressBar = document.getElementById('progressBar');
const playerTitle = document.getElementById('playerTitle');
const playerArtist = document.getElementById('playerArtist');

window.playTrack = function (index) {
    if (index < 0 || index >= playlist.length) return;

    currentTrackIndex = index;
    const track = playlist[index];

    // Update Player UI
    playerTitle.textContent = track.title;
    playerArtist.textContent = track.folder; // Using folder as artist substitute
    playerBar.classList.remove('hidden');

    // Play
    // Encode path components just in case
    const safePath = track.path.split('/').map(encodeURIComponent).join('/');
    audioPlayer.src = `/stream/${safePath}`;
    audioPlayer.play().catch(e => console.error("Playback failed", e));

    updatePlayBtn(true);
    updateActiveTrack(index);
};

function updatePlayBtn(isPlaying) {
    playBtn.textContent = isPlaying ? '⏸' : '▶';
}

function updateActiveTrack(index) {
    // Highlight in list
    document.querySelectorAll('.track-item').forEach((el, i) => {
        if (i === index) el.classList.add('active');
        else el.classList.remove('active');
    });
}

// Controls
playBtn.addEventListener('click', () => {
    if (audioPlayer.paused) {
        audioPlayer.play();
        updatePlayBtn(true);
    } else {
        audioPlayer.pause();
        updatePlayBtn(false);
    }
});

prevBtn.addEventListener('click', () => {
    playTrack(currentTrackIndex - 1);
});

nextBtn.addEventListener('click', () => {
    playTrack(currentTrackIndex + 1);
});

audioPlayer.addEventListener('ended', () => {
    playTrack(currentTrackIndex + 1); // Auto play next
});

audioPlayer.addEventListener('timeupdate', () => {
    if (audioPlayer.duration) {
        const pct = (audioPlayer.currentTime / audioPlayer.duration) * 100;
        progressBar.style.width = `${pct}%`;
    }
});

// DOWNLOAD
window.saveToPhone = function (path) {
    // Mobile browsers handle this by downloading the file
    const safePath = path.split('/').map(encodeURIComponent).join('/');
    const url = `/download_file/${safePath}`;

    // Create invisible link
    const a = document.createElement('a');
    a.href = url;
    a.download = '';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    addLog(`TELECHARGEMENT DEMARRE: ${path}`, 'success');
};
